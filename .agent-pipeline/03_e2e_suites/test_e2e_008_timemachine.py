"""E2E Black-Box test for SPEC-008 Time Machine and Ergonomics."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_e2e_008_time_machine_telemetry_flow():
    prof = {
        "wake_time": "06:30",
        "sleep_time": "22:30",
        "peak_hours": [{"start": "08:30", "end": "11:00"}],
        "dip_hours": [{"start": "13:00", "end": "14:30"}]
    }
    # Tick 1: Peak
    res = client.post("/api/v1/energy/simulation/tick", json={"current_time": "09:00", "profile": prof, "tasks": []})
    assert res.status_code == 200
    assert res.json()["active_zone"] == "PEAK"

    # Tick 2: Late
    res2 = client.post("/api/v1/energy/simulation/tick", json={"current_time": "22:00", "profile": prof, "tasks": []})
    assert res2.status_code == 200
    assert res2.json()["caffeine_allowed"] is False
