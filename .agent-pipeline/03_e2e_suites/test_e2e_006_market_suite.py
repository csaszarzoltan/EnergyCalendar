"""E2E Test suite for the 10 market-driven Circadian & Cognitive services (SPEC-006)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_e2e_006_context_switch_tax():
    payload = {
        "tasks": [
            {"title": "Kódolás", "load_type": "deep_work", "duration_minutes": 60},
            {"title": "Email", "load_type": "admin", "duration_minutes": 20},
            {"title": "Tervezés", "load_type": "creative", "duration_minutes": 45},
            {"title": "Számlák", "load_type": "admin", "duration_minutes": 15},
        ]
    }
    response = client.post("/api/v1/energy/context-switch/tax", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "fragmentation_tax_minutes" in data
    assert len(data["batched_tasks"]) == 4


def test_e2e_006_jetlag_plan():
    payload = {
        "origin_utc_offset": 1,
        "target_utc_offset": -5,
        "travel_date": "2026-09-01",
    }
    response = client.post("/api/v1/energy/jetlag/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["hour_difference"] == -6
    assert len(data["protocols"]) == 6


def test_e2e_006_neuroflow_guard():
    payload = {
        "task_title": "Nagy refaktorálás",
        "duration_minutes": 90,
        "is_hyperfocus_prone": True,
    }
    response = client.post("/api/v1/energy/neuroflow/guard", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "gentle_transition_minutes" in data


def test_e2e_006_biophilic_audit():
    payload = {
        "co2_ppm": 1100,
        "temperature_celsius": 23.0,
        "noise_db": 55.0,
    }
    response = client.post("/api/v1/energy/biophilic/audit", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "cognitive_penalty_percent" in data


def test_e2e_006_dopamine_guard():
    payload = {
        "peak_start": "09:00",
        "peak_end": "11:30",
        "friction_level": "STRICT",
    }
    response = client.post("/api/v1/energy/dopamine/guard", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["blocked_categories"]) >= 4


def test_e2e_006_soundscape_config():
    payload = {
        "cognitive_load": "DEEP_WORK",
        "target_brainwave": "GAMMA",
    }
    response = client.post("/api/v1/energy/soundscape/config", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["binaural_beat_hz"] == 40.0


def test_e2e_006_weather_adjust():
    payload = {
        "pressure_hpa": 1002.0,
        "weather_condition": "RAINY",
        "is_front_passing": True,
    }
    response = client.post("/api/v1/energy/weather/adjust", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["energy_damping_factor"] < 1.0


def test_e2e_006_workout_timing():
    payload = {
        "wake_time": "07:00",
        "sleep_time": "23:00",
        "workout_type": "STRENGTH_HYPERTROPHY",
    }
    response = client.post("/api/v1/energy/workout/timing", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "optimal_window_start" in data


def test_e2e_006_meeting_tax():
    payload = {
        "meetings": [
            {"title": "Heti tervező", "start_time": "10:00", "duration_minutes": 60, "is_interactive": True}
        ]
    }
    response = client.post("/api/v1/energy/meeting/tax", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["decompression_buffers"]) == 1


def test_e2e_006_infradian_plan():
    payload = {
        "season": "WINTER",
    }
    response = client.post("/api/v1/energy/infradian/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["seasonal_sleep_adjustment_minutes"] == 30
