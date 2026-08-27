"""E2E Test suite for the 10 new Circadian and Cognitive services (SPEC-005)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_e2e_005_biometric_sync():
    payload = {
        "hrv_rmssd": 68.0,
        "resting_hr": 52.0,
        "deep_sleep_minutes": 80,
        "rem_sleep_minutes": 90,
        "wake_time": "06:45",
    }
    response = client.post("/api/v1/energy/biometrics/sync", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recovery_factor" in data
    assert "readiness_score" in data
    assert 0.3 <= data["recovery_factor"] <= 1.2
    assert 0 <= data["readiness_score"] <= 100


def test_e2e_005_weekly_matrix():
    payload = {
        "profile": {
            "wake_time": "07:00",
            "sleep_time": "23:00",
            "peak_hours": ["09:00-11:30"],
            "dip_hours": ["13:30-15:00"],
            "sleep_quality": 1.0,
        },
        "tasks_pool": [
            {"title": "Stratégia", "duration": 120, "cognitive_load": "DEEP_WORK"},
            {"title": "Email", "duration": 45, "cognitive_load": "ADMIN"},
        ],
        "start_date": "2026-08-31",
    }
    response = client.post("/api/v1/energy/weekly/matrix", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["days_schedule"]) == 7
    assert "weekly_balance_score" in data


def test_e2e_005_circadian_alerts():
    payload = {
        "profile": {
            "wake_time": "07:00",
            "sleep_time": "23:00",
            "peak_hours": ["09:00-11:30"],
            "dip_hours": ["13:30-15:00"],
            "sleep_quality": 1.0,
        },
        "current_time": "14:30",
        "active_deep_work_minutes": 130,
    }
    response = client.post("/api/v1/energy/alerts", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["active_alerts"]) >= 1


def test_e2e_005_ultradian_split():
    payload = {
        "task_title": "Architektúra tervezés",
        "duration_minutes": 180,
        "brac_cycle_minutes": 90,
        "break_minutes": 20,
    }
    response = client.post("/api/v1/energy/ultradian/split", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["blocks"]) >= 2
    assert data["total_cycles"] == 2


def test_e2e_005_nutrition_impact():
    payload = {
        "meal_time": "12:30",
        "meal_type": "LUNCH",
        "carb_level": "HIGH",
        "fasting_hours": 0.0,
    }
    response = client.post("/api/v1/energy/nutrition/impact", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["dip_severity"] > 1.0
    assert "optimal_walk_window" in data


def test_e2e_005_phototherapy_plan():
    payload = {
        "wake_time": "06:30",
        "sleep_time": "22:30",
        "target_lux": 10000,
    }
    response = client.post("/api/v1/energy/phototherapy/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "morning_light_window" in data
    assert "evening_blueblocker_time" in data


def test_e2e_005_burnout_prediction():
    payload = {
        "daily_debts": [5.0, 12.0, 8.0, 15.0, 4.0],
        "daily_recoveries": [0.9, 0.7, 0.6, 0.5, 0.8],
        "streak_days": 5,
    }
    response = client.post("/api/v1/energy/burnout/prediction", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["allostatic_load_index"] <= 100
    assert data["risk_level"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]


def test_e2e_005_social_sync():
    payload = {
        "profiles": [
            {
                "name": "Alice (Lark)",
                "wake_time": "06:00",
                "sleep_time": "22:00",
                "peak_hours": ["08:30-11:00"],
                "dip_hours": ["13:00-14:30"],
            },
            {
                "name": "Bob (Owl)",
                "wake_time": "09:00",
                "sleep_time": "01:00",
                "peak_hours": ["11:00-13:30"],
                "dip_hours": ["15:00-16:30"],
            },
        ],
        "meeting_duration_minutes": 45,
    }
    response = client.post("/api/v1/energy/social/sync", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "golden_overlap_windows" in data
    assert "social_jetlag_score" in data


def test_e2e_005_micro_recovery():
    payload = {
        "continuous_screen_minutes": 90,
    }
    response = client.post("/api/v1/energy/micro-recovery/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["micro_breaks"]) >= 2
    assert "physiological_sigh_instructions" in data


def test_e2e_005_analytics_alignment():
    payload = {
        "scheduled_slots": [
            {
                "task_id": "t1",
                "title": "Mély munka",
                "start_time": "09:00",
                "end_time": "11:00",
                "duration": 120,
                "cognitive_load": "DEEP_WORK",
                "assigned_energy_avg": 8.5,
            }
        ],
        "completed_task_ids": ["t1"],
    }
    response = client.post("/api/v1/energy/analytics/alignment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["alignment_score"] <= 100
