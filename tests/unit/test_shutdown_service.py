"""Unit tests for ShutdownService and melatonin gate calculation."""
from __future__ import annotations

import pytest

from src.models.energy import (
    CognitiveLoad,
    EnergyProfile,
    ShutdownSummaryRequest,
    Task,
    TimeInterval,
)
from src.services.shutdown_service import ShutdownService


@pytest.fixture
def standard_profile():
    return EnergyProfile(
        wake_time="07:00",
        sleep_time="23:00",
        peak_hours=[
            TimeInterval(start="09:00", end="11:30"),
            TimeInterval(start="16:30", end="18:30"),
        ],
        dip_hours=[
            TimeInterval(start="13:30", end="15:00"),
        ],
    )


def test_shutdown_summary_melatonin_gate(standard_profile):
    """Verify that melatonin gate is calculated as sleep_time - 60 minutes."""
    completed = [
        Task(id="c1", title="Backend dev", duration_minutes=90, load_type=CognitiveLoad.DEEP_WORK, energy_cost=9.0),
        Task(id="c2", title="UI vázlat", duration_minutes=60, load_type=CognitiveLoad.CREATIVE, energy_cost=6.0),
    ]
    pending = [
        Task(id="p1", title="Számlák", duration_minutes=30, load_type=CognitiveLoad.ADMIN, energy_cost=3.0),
    ]

    req = ShutdownSummaryRequest(
        profile=standard_profile,
        completed_tasks=completed,
        pending_tasks=pending,
        scheduled_slots=[],
        current_time="21:30",
    )

    resp = ShutdownService.create_summary(req)
    # Sleep: 23:00 -> Melatonin gate: 22:00
    assert resp.melatonin_gate_time == "22:00"
    assert resp.minutes_until_melatonin == 30
    assert resp.completed_count == 2
    assert resp.pending_count == 1
    assert resp.total_deep_work_minutes == 90
    assert resp.tomorrow_first_peak == "09:00"
    assert resp.is_shutdown_recommended_now is True
    assert len(resp.recommendations) >= 3


def test_shutdown_summary_early_day(standard_profile):
    """Verify minutes_until_melatonin and shutdown recommended flag during mid-day."""
    req = ShutdownSummaryRequest(
        profile=standard_profile,
        completed_tasks=[],
        pending_tasks=[],
        scheduled_slots=[],
        current_time="14:00",
    )

    resp = ShutdownService.create_summary(req)
    # 22:00 (1320m) - 14:00 (840m) = 480 minutes
    assert resp.melatonin_gate_time == "22:00"
    assert resp.minutes_until_melatonin == 480
    assert resp.is_shutdown_recommended_now is False


def test_shutdown_summary_overnight_sleep():
    """Verify melatonin gate calculation when sleep time crosses midnight (e.g. 00:30)."""
    night_profile = EnergyProfile(
        wake_time="08:30",
        sleep_time="00:30",
        peak_hours=[TimeInterval(start="10:00", end="12:30")],
        dip_hours=[TimeInterval(start="14:00", end="15:30")],
    )

    req = ShutdownSummaryRequest(
        profile=night_profile,
        completed_tasks=[],
        pending_tasks=[],
        scheduled_slots=[],
        current_time="23:00",
    )

    resp = ShutdownService.create_summary(req)
    # Sleep: 00:30 (30m) -> Gate: 23:30 (1410m)
    assert resp.melatonin_gate_time == "23:30"
    # Current: 23:00 (1380m) -> 30 min until gate
    assert resp.minutes_until_melatonin == 30
    assert resp.is_shutdown_recommended_now is True
