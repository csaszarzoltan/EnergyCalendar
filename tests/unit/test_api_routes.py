"""Unit tests for FastAPI API route endpoints."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
def client_fixture():
    """AsyncClient fixture for testing FastAPI application routes."""
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.mark.asyncio
async def test_api_health(client_fixture: AsyncClient):
    """Test health check endpoints."""
    async with client_fixture as client:
        res1 = await client.get("/api/v1/health")
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["status"] == "ok"
        assert data1["service"] == "energy-calendar"

        res2 = await client.get("/health")
        assert res2.status_code == 200
        assert res2.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_api_energy_curve(client_fixture: AsyncClient):
    """Test POST /api/v1/energy/profile/curve."""
    payload = {
        "wake_time": "07:00",
        "sleep_time": "23:00",
        "peak_hours": [{"start": "09:00", "end": "11:30"}],
        "dip_hours": [{"start": "13:30", "end": "15:00"}],
    }
    async with client_fixture as client:
        response = await client.post("/api/v1/energy/profile/curve", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "points" in data
        assert len(data["points"]) == 96
        assert "profile" in data


@pytest.mark.asyncio
async def test_api_schedule(client_fixture: AsyncClient):
    """Test POST /api/v1/energy/schedule."""
    payload = {
        "profile": {
            "wake_time": "07:00",
            "sleep_time": "23:00",
            "peak_hours": [{"start": "09:00", "end": "11:30"}],
            "dip_hours": [{"start": "13:30", "end": "15:00"}],
        },
        "tasks": [
            {
                "id": "t1",
                "title": "Deep Work Code",
                "duration_minutes": 60,
                "load_type": "deep_work",
                "energy_cost": 9.0,
            }
        ],
    }
    async with client_fixture as client:
        response = await client.post("/api/v1/energy/schedule", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert len(data["scheduled_tasks"]) == 1
        assert "debt_report" in data
        assert "energy_curve" in data


@pytest.mark.asyncio
async def test_api_schedule_conflict_returns_400(client_fixture: AsyncClient):
    """Test POST /api/v1/energy/schedule with conflicting fixed tasks returns 400."""
    payload = {
        "profile": {
            "wake_time": "07:00",
            "sleep_time": "23:00",
            "peak_hours": [],
            "dip_hours": [],
        },
        "tasks": [
            {
                "id": "fix1",
                "title": "Meeting 1",
                "duration_minutes": 60,
                "load_type": "admin",
                "is_fixed": True,
                "fixed_start": "10:00",
            },
            {
                "id": "fix2",
                "title": "Meeting 2",
                "duration_minutes": 60,
                "load_type": "admin",
                "is_fixed": True,
                "fixed_start": "10:30",
            },
        ],
    }
    async with client_fixture as client:
        response = await client.post("/api/v1/energy/schedule", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "detail" in data


@pytest.mark.asyncio
async def test_api_parse_task(client_fixture: AsyncClient):
    """Test POST /api/v1/energy/parse-task."""
    payload = {"raw_text": "Kódolás 90 perc"}
    async with client_fixture as client:
        response = await client.post("/api/v1/energy/parse-task", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["load_type"] == "deep_work"
        assert data["duration_minutes"] == 90
        assert data["energy_cost"] == 8.5


@pytest.mark.asyncio
async def test_api_calendar_export_ics(client_fixture: AsyncClient):
    """Test POST /api/v1/energy/calendar/export-ics returns text/calendar."""
    payload = {
        "scheduled_tasks": [
            {
                "task_id": "slot-1",
                "title": "Kódolás",
                "start_time": "09:00",
                "end_time": "10:30",
                "duration_minutes": 90,
                "load_type": "deep_work",
                "energy_cost": 8.5,
                "average_energy_level": 9.0,
            }
        ],
        "calendar_name": "Cirkadián Export",
    }
    async with client_fixture as client:
        response = await client.post("/api/v1/energy/calendar/export-ics", json=payload)
        assert response.status_code == 200
        assert "text/calendar" in response.headers.get("content-type", "")
        assert "BEGIN:VCALENDAR" in response.text
        assert "Kódolás" in response.text


@pytest.mark.asyncio
async def test_api_calendar_import_ics(client_fixture: AsyncClient):
    """Test POST /api/v1/energy/calendar/import-ics parses events."""
    ics_text = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:Standup
DTSTART:20260826T093000Z
DTEND:20260826T100000Z
END:VEVENT
END:VCALENDAR"""
    async with client_fixture as client:
        response = await client.post("/api/v1/energy/calendar/import-ics", json={"ics_content": ics_text})
        assert response.status_code == 200
        data = response.json()
        assert data["imported_count"] == 1
        assert data["imported_tasks"][0]["is_fixed"] is True
        assert data["imported_tasks"][0]["fixed_start"] == "09:30"
        assert data["imported_tasks"][0]["duration_minutes"] == 30


@pytest.mark.asyncio
async def test_api_decompose_task(client_fixture: AsyncClient):
    """Test POST /api/v1/energy/decompose-task."""
    task = {
        "id": "t-big",
        "title": "Hosszú feladat",
        "duration_minutes": 120,
        "load_type": "deep_work",
        "energy_cost": 8.5,
    }
    async with client_fixture as client:
        response = await client.post("/api/v1/energy/decompose-task", json={"task": task})
        assert response.status_code == 200
        data = response.json()
        assert len(data["subtasks"]) == 3
        assert sum(s["duration_minutes"] for s in data["subtasks"]) == 120


@pytest.mark.asyncio
async def test_api_shutdown_summary(client_fixture: AsyncClient):
    """Test POST /api/v1/energy/shutdown/summary."""
    payload = {
        "profile": {
            "wake_time": "07:00",
            "sleep_time": "23:00",
            "peak_hours": [{"start": "09:00", "end": "11:30"}],
            "dip_hours": [{"start": "13:30", "end": "15:00"}],
        },
        "completed_tasks": [
            {
                "id": "c1",
                "title": "Backend munka",
                "duration_minutes": 90,
                "load_type": "deep_work",
                "energy_cost": 9.0,
            }
        ],
        "pending_tasks": [],
        "scheduled_slots": [],
        "current_time": "22:15",
    }
    async with client_fixture as client:
        response = await client.post("/api/v1/energy/shutdown/summary", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["completed_count"] == 1
        assert data["total_deep_work_minutes"] == 90
        assert data["melatonin_gate_time"] == "22:00"
        assert data["is_shutdown_recommended_now"] is True
