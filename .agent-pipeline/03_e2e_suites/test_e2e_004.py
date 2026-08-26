"""E2E Test Suite for SPEC-004: Advanced Productivity Suite.

Black-box verification of Daily Shutdown, iCalendar .ics Export/Import, and Task Decomposition.
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
async def test_e2e_ics_export_content():
    """Verify that export-ics returns valid RFC 5545 VCALENDAR text with cognitive markers."""
    scheduled = [
        {
            "task_id": "t1",
            "title": "Backend architektúra tervezés",
            "start_time": "09:00",
            "end_time": "10:30",
            "duration_minutes": 90,
            "load_type": "deep_work",
            "energy_cost": 9.0,
            "average_energy_level": 9.2
        },
        {
            "task_id": "t2",
            "title": "Regenerációs séta",
            "start_time": "10:30",
            "end_time": "10:50",
            "duration_minutes": 20,
            "load_type": "recovery",
            "energy_cost": -3.0,
            "average_energy_level": 8.0
        }
    ]
    
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        response = await client.post("/api/v1/energy/calendar/export-ics", json={
            "scheduled_tasks": scheduled,
            "calendar_name": "Cirkadián Energia Naptár"
        })
        assert response.status_code == 200
        content = response.text
        assert "BEGIN:VCALENDAR" in content
        assert "END:VCALENDAR" in content
        assert "BEGIN:VEVENT" in content
        assert "END:VEVENT" in content
        assert "Backend architektúra tervezés" in content
        assert "090000" in content or "09:00" in content


@pytest.mark.asyncio
async def test_e2e_ics_import_and_fixed_mask():
    """Verify that import-ics parses external calendar events and sets is_fixed=True."""
    sample_ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Google Inc//Google Calendar 70.9054//EN
BEGIN:VEVENT
UID:meeting-123@google.com
SUMMARY:Heti Vezetői Értekezlet
DTSTART:20260826T100000Z
DTEND:20260826T110000Z
DESCRIPTION:Projekt áttekintés
END:VEVENT
END:VCALENDAR"""
    
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        response = await client.post("/api/v1/energy/calendar/import-ics", json={
            "ics_content": sample_ics
        })
        assert response.status_code == 200
        data = response.json()
        assert data["imported_count"] >= 1
        tasks = data["imported_tasks"]
        meeting = tasks[0]
        assert "Heti Vezetői Értekezlet" in meeting["title"]
        assert meeting["is_fixed"] is True
        assert meeting["duration_minutes"] == 60


@pytest.mark.asyncio
async def test_e2e_task_decomposition():
    """Verify that large tasks (>60m) are decomposed into creative, deep work, and admin subtasks."""
    big_task = {
        "id": "big-task-1",
        "title": "Diplomamunka fejezet megírása",
        "duration_minutes": 180,
        "load_type": "deep_work",
        "energy_cost": 9.0
    }
    
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        response = await client.post("/api/v1/energy/decompose-task", json={
            "task": big_task
        })
        assert response.status_code == 200
        data = response.json()
        subtasks = data["subtasks"]
        assert len(subtasks) == 3
        # Total sum of durations must equal 180 min
        total_m = sum(st["duration_minutes"] for st in subtasks)
        assert total_m == 180
        # Check cognitive loads in order (creative -> deep_work -> admin)
        assert subtasks[0]["load_type"] == "creative"
        assert subtasks[1]["load_type"] == "deep_work"
        assert subtasks[2]["load_type"] == "admin"


@pytest.mark.asyncio
async def test_e2e_shutdown_summary(test_profile):
    """Verify daily shutdown summary with melatonin gate (sleep - 60m) and statistics."""
    completed = [
        {
            "id": "t1",
            "title": "Kódolás",
            "duration_minutes": 90,
            "load_type": "deep_work",
            "energy_cost": 9.0
        }
    ]
    pending = [
        {
            "id": "t2",
            "title": "Számlák",
            "duration_minutes": 30,
            "load_type": "admin",
            "energy_cost": 3.0
        }
    ]
    
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_API_URL)
    async with client_ctx as client:
        response = await client.post("/api/v1/energy/shutdown/summary", json={
            "profile": test_profile,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "scheduled_slots": [],
            "current_time": "21:30"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["completed_count"] == 1
        assert data["pending_count"] == 1
        assert data["total_deep_work_minutes"] == 90
        # sleep is 23:00 -> melatonin gate is 22:00 (23:00 - 60 min)
        assert data["melatonin_gate_time"] == "22:00"
        assert data["tomorrow_first_peak"] == "09:00"


@pytest.mark.asyncio
async def test_e2e_gui_v120_dom_controls():
    """Verify the new buttons and modals for Shutdown, Export, and Import exist in HTML."""
    client_ctx = AsyncClient(transport=ASGITransport(app=app), base_url="http://test") if app else AsyncClient(base_url=BASE_WEB_URL)
    async with client_ctx as client:
        response = await client.get("/")
        content = response.text
        assert 'id="btn-open-shutdown"' in content
        assert 'id="btn-export-ics"' in content
        assert 'id="btn-import-ics"' in content
        assert 'id="shutdown-ritual-modal"' in content
        assert 'id="ics-import-modal"' in content
