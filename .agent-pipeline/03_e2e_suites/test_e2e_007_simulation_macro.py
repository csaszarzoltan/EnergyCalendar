"""E2E Black-Box test suite for Simulation Time Machine and Macro Orchestration (SPEC-007)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_e2e_007_simulation_tick_peak():
    payload = {
        "current_time": "09:30",
        "profile": {
            "wake_time": "07:00",
            "sleep_time": "23:00",
            "peak_hours": [{"start": "09:00", "end": "11:30"}],
            "dip_hours": [{"start": "13:30", "end": "15:00"}]
        },
        "tasks": []
    }
    res = client.post("/api/v1/energy/simulation/tick", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["active_zone"] == "PEAK"
    assert data["energy_level"] >= 7.0
    assert "neuro_guidance" in data


def test_e2e_007_simulation_tick_evening():
    payload = {
        "current_time": "22:00",
        "profile": {
            "wake_time": "07:00",
            "sleep_time": "23:00",
            "peak_hours": [{"start": "09:00", "end": "11:30"}],
            "dip_hours": [{"start": "13:30", "end": "15:00"}]
        },
        "tasks": []
    }
    res = client.post("/api/v1/energy/simulation/tick", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["caffeine_allowed"] is False
