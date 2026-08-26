"""Unit tests for Dynamic Ripple Re-flow and sleep-modulated schedule adaptation."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.models.energy import (
    CognitiveLoad,
    EnergyProfile,
    ReflowRequest,
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


def test_reflow_schedules_only_in_future(profile: EnergyProfile):
    """Verify reflow at 14:15 schedules remaining tasks strictly at or after 14:15."""
    tasks = [
        Task(
            id="task-deep",
            title="Délutáni kódolás",
            duration_minutes=60,
            load_type=CognitiveLoad.DEEP_WORK,
            energy_cost=8.5,
        ),
        Task(
            id="task-admin",
            title="Számlák ellenőrzése",
            duration_minutes=30,
            load_type=CognitiveLoad.ADMIN,
            energy_cost=3.0,
        ),
    ]

    req = ReflowRequest(
        profile=profile,
        current_time="14:15",
        pending_tasks=tasks,
        sleep_quality=1.0,
    )
    res = EnergyScheduler.reflow_schedule(req)

    assert res.status == "ok"
    assert res.reflow_time == "14:15"
    assert len(res.scheduled_tasks) == 2
    for slot in res.scheduled_tasks:
        assert slot.start_time >= "14:15"
        assert slot.end_time <= "23:00"

    # Admin should be placed in the ongoing dip (14:15 - 14:45)
    admin_slot = next(s for s in res.scheduled_tasks if s.task_id == "task-admin")
    assert admin_slot.start_time == "14:15"

    # Deep work should be placed in afternoon peak (16:30 - 17:30)
    deep_slot = next(s for s in res.scheduled_tasks if s.task_id == "task-deep")
    assert deep_slot.start_time == "16:30"


def test_reflow_tightens_deep_work_limit_on_low_sleep(profile: EnergyProfile):
    """Verify that when sleep_quality=0.5, consecutive deep work limit tightens to 60m."""
    tasks = [
        Task(
            id="tired-1",
            title="Mély elemzés 1",
            duration_minutes=45,
            load_type=CognitiveLoad.DEEP_WORK,
            energy_cost=9.0,
        ),
        Task(
            id="tired-2",
            title="Mély elemzés 2",
            duration_minutes=45,
            load_type=CognitiveLoad.DEEP_WORK,
            energy_cost=9.0,
        ),
    ]

    req = ReflowRequest(
        profile=profile,
        current_time="08:00",
        pending_tasks=tasks,
        sleep_quality=0.5,
    )
    res = EnergyScheduler.reflow_schedule(req)

    assert res.status == "ok"
    # Should contain 2 deep work tasks + 1 auto-recovery slot
    assert len(res.scheduled_tasks) == 3

    recovery_slots = [
        s for s in res.scheduled_tasks if s.is_auto_recovery or s.load_type == CognitiveLoad.RECOVERY
    ]
    assert len(recovery_slots) == 1
    rec = recovery_slots[0]
    # Low sleep recovery duration is 30 minutes
    assert rec.duration_minutes == 30
    assert rec.is_auto_recovery is True


def test_reflow_excludes_completed_task_ids(profile: EnergyProfile):
    """Verify tasks listed in completed_task_ids are excluded from reflow scheduling."""
    tasks = [
        Task(
            id="done-1",
            title="Már kész feladat",
            duration_minutes=60,
            load_type=CognitiveLoad.DEEP_WORK,
            energy_cost=8.0,
        ),
        Task(
            id="pending-1",
            title="Még hátralévő feladat",
            duration_minutes=30,
            load_type=CognitiveLoad.ADMIN,
            energy_cost=3.0,
        ),
    ]

    req = ReflowRequest(
        profile=profile,
        current_time="11:00",
        pending_tasks=tasks,
        completed_task_ids=["done-1"],
        sleep_quality=1.0,
    )
    res = EnergyScheduler.reflow_schedule(req)

    assert len(res.scheduled_tasks) == 1
    assert res.scheduled_tasks[0].task_id == "pending-1"


def test_reflow_response_structure(profile: EnergyProfile):
    """Verify all components are present in ReflowResponse."""
    req = ReflowRequest(
        profile=profile,
        current_time="10:00",
        pending_tasks=[
            Task(
                id="t-1",
                title="Gyors feladat",
                duration_minutes=30,
                load_type=CognitiveLoad.CREATIVE,
                energy_cost=5.0,
            )
        ],
        sleep_quality=0.9,
    )
    res = EnergyScheduler.reflow_schedule(req)

    assert res.reflow_time == "10:00"
    assert len(res.energy_curve) == 96
    assert res.caffeine_window.caffeine_start_time == "08:30"
    assert res.debt_report is not None
    assert res.debt_report.total_capacity > 0


@pytest.mark.asyncio
async def test_api_reflow_endpoint(profile: EnergyProfile):
    """Test POST /api/v1/energy/schedule/reflow HTTP endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/energy/schedule/reflow",
            json={
                "profile": profile.model_dump(),
                "current_time": "14:15",
                "pending_tasks": [
                    {
                        "id": "reflow-api-1",
                        "title": "API Reflow Teszt",
                        "duration_minutes": 30,
                        "load_type": "admin",
                        "energy_cost": 3.0,
                    }
                ],
                "sleep_quality": 1.0,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["reflow_time"] == "14:15"
        assert len(data["scheduled_tasks"]) == 1
        assert data["scheduled_tasks"][0]["start_time"] >= "14:15"
        assert "caffeine_window" in data
