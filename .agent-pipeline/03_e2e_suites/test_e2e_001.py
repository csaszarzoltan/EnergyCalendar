"""E2E Test Suite for SPEC-001: Circadian Energy Rhythm and Task Choreographer.

Black-box verification of the FastAPI backend and Playwright GUI flow.
"""
from __future__ import annotations
import pytest
from httpx import AsyncClient, ASGITransport

# We attempt to import app dynamically if available; fallback to standard test transport
try:
    from src.main import app
except ImportError:
    app = None

BASE_API_URL = "http://localhost:8000/api/v1"
BASE_WEB_URL = "http://localhost:3000"


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
async def test_e2e_health_check():
    """Verify backend health check endpoint."""
    if app is not None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
    else:
        async with AsyncClient(base_url=BASE_API_URL) as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_e2e_energy_curve_generation(test_profile):
    """Verify 24h continuous energy curve generation with 15-minute resolution."""
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        response = await client.post("/api/v1/energy/profile/curve", json=test_profile)
        assert response.status_code == 200
        data = response.json()
        assert "points" in data
        points = data["points"]
        # Exactly 96 points in 24 hours (24 * 4)
        assert len(points) == 96
        
        # Verify peak window has energy_level >= 8.0
        peak_points = [p for p in points if "09:15" <= p["time"] <= "11:00"]
        assert len(peak_points) > 0
        for p in peak_points:
            assert p["energy_level"] >= 8.0
            assert p["zone_type"] == "peak"
            
        # Verify dip window has energy_level <= 4.0
        dip_points = [p for p in points if "13:45" <= p["time"] <= "14:45"]
        assert len(dip_points) > 0
        for p in dip_points:
            assert p["energy_level"] <= 4.0
            assert p["zone_type"] == "dip"


@pytest.mark.asyncio
async def test_e2e_nlp_task_parsing():
    """Verify natural language task parsing into duration and CognitiveLoad."""
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        payload = {"raw_text": "Kódolás: új auth modul megírása 90 perc"}
        response = await client.post("/api/v1/energy/parse-task", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["load_type"] == "deep_work"
        assert data["duration_minutes"] == 90
        assert data["energy_cost"] >= 8.0


@pytest.mark.asyncio
async def test_e2e_choreograph_happy_path(test_profile):
    """Verify smart matching: Deep work in peak hours, Admin in dip hours."""
    tasks = [
        {
            "id": "task-deep-1",
            "title": "Architektúra tervezés",
            "duration_minutes": 90,
            "load_type": "deep_work",
            "energy_cost": 9.0
        },
        {
            "id": "task-admin-1",
            "title": "Számlák rendezése",
            "duration_minutes": 45,
            "load_type": "admin",
            "energy_cost": 3.0
        }
    ]
    
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        response = await client.post("/api/v1/energy/schedule", json={
            "profile": test_profile,
            "tasks": tasks
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        scheduled = data["scheduled_tasks"]
        assert len(scheduled) == 2
        
        deep_slot = next(s for s in scheduled if s["task_id"] == "task-deep-1")
        admin_slot = next(s for s in scheduled if s["task_id"] == "task-admin-1")
        
        # Deep work scheduled in peak morning window (09:00 - 11:30)
        assert "09:00" <= deep_slot["start_time"] < "11:30"
        assert deep_slot["average_energy_level"] >= 7.5
        
        # Admin scheduled in dip afternoon window (13:30 - 15:00)
        assert "13:30" <= admin_slot["start_time"] < "15:00"
        assert admin_slot["average_energy_level"] <= 4.5


@pytest.mark.asyncio
async def test_e2e_consecutive_deep_work_auto_recovery(test_profile):
    """Verify automatic recovery block insertion when consecutive deep work >= 120 mins."""
    tasks = [
        {
            "id": "deep-1",
            "title": "Backend refaktor 1",
            "duration_minutes": 75,
            "load_type": "deep_work",
            "energy_cost": 9.0
        },
        {
            "id": "deep-2",
            "title": "Backend refaktor 2",
            "duration_minutes": 75,
            "load_type": "deep_work",
            "energy_cost": 9.0
        }
    ]
    
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        response = await client.post("/api/v1/energy/schedule", json={
            "profile": test_profile,
            "tasks": tasks
        })
        assert response.status_code == 200
        data = response.json()
        scheduled = data["scheduled_tasks"]
        
        # Total slots should be 3 (deep-1, auto-recovery, deep-2)
        assert len(scheduled) == 3
        recovery_slots = [s for s in scheduled if s.get("is_auto_recovery") is True or s["load_type"] == "recovery"]
        assert len(recovery_slots) >= 1
        recovery = recovery_slots[0]
        assert recovery["duration_minutes"] >= 15
        assert recovery["energy_cost"] < 0  # Negative load for restorative recharging


@pytest.mark.asyncio
async def test_e2e_cognitive_overload_energy_debt(test_profile):
    """Verify warning and Energy Debt calculation when total load exceeds capacity."""
    # 6 massive 120min deep work sessions with max cost (12 hours of deep work)
    heavy_tasks = [
        {
            "id": f"heavy-deep-{i}",
            "title": f"Maraton feladat {i}",
            "duration_minutes": 120,
            "load_type": "deep_work",
            "energy_cost": 10.0
        } for i in range(6)
    ]
    
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        response = await client.post("/api/v1/energy/schedule", json={
            "profile": test_profile,
            "tasks": heavy_tasks
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "warning"
        debt = data["debt_report"]
        assert debt["is_overloaded"] is True
        assert debt["energy_debt"] > 0
        assert debt["exhaustion_percentage"] > 100.0


@pytest.mark.asyncio
async def test_e2e_fixed_event_conflict_handling(test_profile):
    """Verify 400 Bad Request if fixed calendar events overlap."""
    conflicting_tasks = [
        {
            "id": "fixed-1",
            "title": "Meeting A",
            "duration_minutes": 60,
            "load_type": "admin",
            "is_fixed": True,
            "fixed_start": "10:00",
            "energy_cost": 4.0
        },
        {
            "id": "fixed-2",
            "title": "Meeting B",
            "duration_minutes": 60,
            "load_type": "admin",
            "is_fixed": True,
            "fixed_start": "10:30",
            "energy_cost": 4.0
        }
    ]
    
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        response = await client.post("/api/v1/energy/schedule", json={
            "profile": test_profile,
            "tasks": conflicting_tasks
        })
        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "detail" in data
