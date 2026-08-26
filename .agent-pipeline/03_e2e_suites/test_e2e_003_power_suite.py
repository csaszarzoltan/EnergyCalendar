"""E2E Test Suite for SPEC-003: Circadian Power Suite.

Black-box verification of Ripple Re-flow, Caffeine timing, and Sleep Quality scaling.
"""
from __future__ import annotations
import pytest
from httpx import AsyncClient, ASGITransport

try:
    from src.main import app
except ImportError:
    app = None

BASE_API_URL = "http://localhost:8000/api/v1"
BASE_WEB_URL = "http://localhost:8000"


@pytest.fixture
def test_profile():
    return {
        "wake_time": "07:00",
        "sleep_time": "23:00",
        "peak_hours": [
            {"start": "09:00", "end": "11:30"},
            {"start": "16:30", "end": "18:30"}
        ],
        "dip_hours": [
            {"start": "13:30", "end": "15:00"}
        ]
    }


@pytest.mark.asyncio
async def test_e2e_caffeine_window_calculation(test_profile):
    """Verify caffeine window calculation (wake+90m start, sleep-9h cutoff)."""
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        response = await client.post("/api/v1/energy/caffeine-window", json={
            "profile": test_profile,
            "current_time": "10:00"
        })
        assert response.status_code == 200
        data = response.json()
        # wake_time = 07:00 -> start = 08:30
        assert data["caffeine_start_time"] == "08:30"
        # sleep_time = 23:00 -> cutoff = 14:00 (23:00 - 9h)
        assert data["caffeine_cutoff_time"] == "14:00"
        # At 10:00 it is safe
        assert data["is_safe_now"] is True


@pytest.mark.asyncio
async def test_e2e_caffeine_late_cutoff_warning(test_profile):
    """Verify warning when querying caffeine window past cutoff time."""
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        response = await client.post("/api/v1/energy/caffeine-window", json={
            "profile": test_profile,
            "current_time": "15:30"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_safe_now"] is False
        assert "figyelem" in data["adenosine_warning"].lower() or "koffein" in data["adenosine_warning"].lower() or "cutoff" in data["adenosine_warning"].lower()


@pytest.mark.asyncio
async def test_e2e_reflow_future_only(test_profile):
    """Verify that re-flow at 14:15 only schedules tasks in the future (>= 14:15)."""
    tasks = [
        {
            "id": "reflow-task-deep",
            "title": "Délutáni kódolás",
            "duration_minutes": 60,
            "load_type": "deep_work",
            "energy_cost": 8.5
        },
        {
            "id": "reflow-task-admin",
            "title": "Levelezés",
            "duration_minutes": 30,
            "load_type": "admin",
            "energy_cost": 3.0
        }
    ]
    
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        response = await client.post("/api/v1/energy/schedule/reflow", json={
            "profile": test_profile,
            "current_time": "14:15",
            "pending_tasks": tasks,
            "sleep_quality": 1.0
        })
        assert response.status_code == 200
        data = response.json()
        scheduled = data["scheduled_tasks"]
        assert len(scheduled) == 2
        for s in scheduled:
            assert s["start_time"] >= "14:15"


@pytest.mark.asyncio
async def test_e2e_reflow_low_sleep_quality_tightening(test_profile):
    """Verify that low sleep quality (0.5) tightens deep work threshold to 60 min."""
    # 2x 45 min deep work = 90 min deep work (exceeds 60 min low sleep limit)
    tasks = [
        {
            "id": "tired-deep-1",
            "title": "Nehéz matek 1",
            "duration_minutes": 45,
            "load_type": "deep_work",
            "energy_cost": 9.0
        },
        {
            "id": "tired-deep-2",
            "title": "Nehéz matek 2",
            "duration_minutes": 45,
            "load_type": "deep_work",
            "energy_cost": 9.0
        }
    ]
    
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        response = await client.post("/api/v1/energy/schedule/reflow", json={
            "profile": test_profile,
            "current_time": "08:00",
            "pending_tasks": tasks,
            "sleep_quality": 0.5
        })
        assert response.status_code == 200
        data = response.json()
        scheduled = data["scheduled_tasks"]
        # Should have auto-recovery inserted because 90m > 60m limit
        recovery_slots = [s for s in scheduled if s.get("is_auto_recovery") is True or s["load_type"] == "recovery"]
        assert len(recovery_slots) >= 1


@pytest.mark.asyncio
async def test_e2e_gui_power_suite_dom_controls():
    """Verify the new interactive Power Suite controls exist in HTML."""
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_WEB_URL)
    async with client_ctx as client:
        response = await client.get("/")
        content = response.text
        assert 'id="btn-reflow-now"' in content
        assert 'id="btn-toggle-caffeine"' in content
        assert 'id="sleep-quality-slider"' in content
        assert 'id="zen-focus-modal"' in content
        assert 'id="btn-toggle-zen-audio"' in content
