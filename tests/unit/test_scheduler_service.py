"""Unit tests for EnergyScheduler service."""
from __future__ import annotations

import pytest

from src.models.energy import (
    CognitiveLoad,
    EnergyProfile,
    ScheduleRequest,
    Task,
    TimeInterval,
)
from src.services.scheduler_service import EnergyScheduler


@pytest.fixture
def profile() -> EnergyProfile:
    """Standard circadian energy profile fixture."""
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


def test_schedule_deep_work_in_peak_window(profile: EnergyProfile):
    """Verifies deep work task is placed in peak hours."""
    tasks = [
        Task(
            id="dw-1",
            title="Architektúra tervezés",
            duration_minutes=90,
            load_type=CognitiveLoad.DEEP_WORK,
            energy_cost=9.0,
        )
    ]
    request = ScheduleRequest(profile=profile, tasks=tasks)
    response = EnergyScheduler.schedule(request)

    assert response.status == "ok"
    assert len(response.scheduled_tasks) == 1
    slot = response.scheduled_tasks[0]
    assert slot.task_id == "dw-1"
    assert "09:00" <= slot.start_time < "11:30"
    assert slot.average_energy_level >= 7.5


def test_schedule_admin_in_dip_window(profile: EnergyProfile):
    """Verifies admin task is placed during lunch dip."""
    tasks = [
        Task(
            id="adm-1",
            title="Számlák rendezése",
            duration_minutes=45,
            load_type=CognitiveLoad.ADMIN,
            energy_cost=3.0,
        )
    ]
    request = ScheduleRequest(profile=profile, tasks=tasks)
    response = EnergyScheduler.schedule(request)

    assert response.status == "ok"
    assert len(response.scheduled_tasks) == 1
    slot = response.scheduled_tasks[0]
    assert slot.task_id == "adm-1"
    assert "13:30" <= slot.start_time < "15:00"
    assert slot.average_energy_level <= 4.5


def test_auto_recovery_insertion_after_120min_deep_work(profile: EnergyProfile):
    """Verifies automatic recovery slot inserted when consecutive deep work exceeds 120 mins."""
    tasks = [
        Task(
            id="dw-part-1",
            title="Kódolás 1. rész",
            duration_minutes=75,
            load_type=CognitiveLoad.DEEP_WORK,
            energy_cost=9.0,
        ),
        Task(
            id="dw-part-2",
            title="Kódolás 2. rész",
            duration_minutes=75,
            load_type=CognitiveLoad.DEEP_WORK,
            energy_cost=9.0,
        ),
    ]
    request = ScheduleRequest(profile=profile, tasks=tasks)
    response = EnergyScheduler.schedule(request)

    assert response.status == "ok"
    # Should contain 2 deep work tasks + 1 auto-recovery slot = 3 total slots
    assert len(response.scheduled_tasks) == 3

    recovery_slots = [
        s for s in response.scheduled_tasks if s.is_auto_recovery or s.load_type == CognitiveLoad.RECOVERY
    ]
    assert len(recovery_slots) == 1
    rec = recovery_slots[0]
    assert rec.duration_minutes == 20
    assert rec.energy_cost < 0.0
    assert rec.title == "Automatikus Kognitív Regeneráció"


def test_energy_debt_detection_when_overloaded(profile: EnergyProfile):
    """Verifies warning status and positive energy_debt when tasks exceed capacity."""
    heavy_tasks = [
        Task(
            id=f"heavy-{i}",
            title=f"Maraton feladat {i}",
            duration_minutes=120,
            load_type=CognitiveLoad.DEEP_WORK,
            energy_cost=10.0,
        )
        for i in range(6)
    ]
    request = ScheduleRequest(profile=profile, tasks=heavy_tasks)
    response = EnergyScheduler.schedule(request)

    assert response.status == "warning"
    debt = response.debt_report
    assert debt.is_overloaded is True
    assert debt.energy_debt > 0.0
    assert debt.exhaustion_percentage > 100.0
    assert "túlterhelés" in debt.recommendation.lower()


def test_fixed_event_conflict_raises_error(profile: EnergyProfile):
    """Raises ValueError if two fixed events overlap."""
    conflicting_tasks = [
        Task(
            id="f-1",
            title="Meeting 1",
            duration_minutes=60,
            load_type=CognitiveLoad.ADMIN,
            is_fixed=True,
            fixed_start="10:00",
        ),
        Task(
            id="f-2",
            title="Meeting 2",
            duration_minutes=60,
            load_type=CognitiveLoad.ADMIN,
            is_fixed=True,
            fixed_start="10:30",
        ),
    ]
    request = ScheduleRequest(profile=profile, tasks=conflicting_tasks)
    with pytest.raises(ValueError, match="Fixed tasks conflict"):
        EnergyScheduler.schedule(request)


def test_schedule_creative_in_moderate_window(profile: EnergyProfile):
    """Verifies creative task is placed in moderate energy window (4.5 - 7.5)."""
    tasks = [
        Task(
            id="cr-1",
            title="UI Wireframe Brainstorming",
            duration_minutes=60,
            load_type=CognitiveLoad.CREATIVE,
            energy_cost=6.0,
        )
    ]
    request = ScheduleRequest(profile=profile, tasks=tasks)
    response = EnergyScheduler.schedule(request)

    assert response.status == "ok"
    assert len(response.scheduled_tasks) == 1
    slot = response.scheduled_tasks[0]
    assert slot.task_id == "cr-1"
    assert 4.5 <= slot.average_energy_level <= 7.5


def test_schedule_with_deadline_constraint(profile: EnergyProfile):
    """Verifies that tasks respect deadline constraint."""
    tasks = [
        Task(
            id="dl-1",
            title="Sürgős riport",
            duration_minutes=60,
            load_type=CognitiveLoad.ADMIN,
            deadline="12:00",
            energy_cost=3.0,
        )
    ]
    request = ScheduleRequest(profile=profile, tasks=tasks)
    response = EnergyScheduler.schedule(request)

    assert response.status == "ok"
    assert len(response.scheduled_tasks) == 1
    slot = response.scheduled_tasks[0]
    assert slot.end_time <= "12:00"


def test_fixed_task_missing_start_raises_error(profile: EnergyProfile):
    """Verifies fixed task with no fixed_start raises ValueError."""
    tasks = [
        Task(
            id="f-invalid",
            title="Invalid Fixed Task",
            duration_minutes=30,
            load_type=CognitiveLoad.ADMIN,
            is_fixed=True,
            fixed_start=None,
        )
    ]
    request = ScheduleRequest(profile=profile, tasks=tasks)
    with pytest.raises(ValueError, match="fixed_start"):
        EnergyScheduler.schedule(request)
