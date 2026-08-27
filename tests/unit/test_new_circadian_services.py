"""Unit tests for the 10 new circadian services (v1.3.0)."""
from __future__ import annotations

import pytest
from src.models.advanced_circadian import (
    AlertQueryRequest,
    BiometricSyncRequest,
    BurnoutAnalysisRequest,
    CarbLevel,
    ChronotypeProfile,
    CircadianAnalyticsRequest,
    MealImpactRequest,
    MealType,
    MicroRecoveryRequest,
    PhototherapyRequest,
    ScheduledSlotAnalytics,
    SocialSyncRequest,
    UltradianSplitRequest,
    WeeklyMatrixRequest,
    WeeklyTaskItem,
)
from src.services.alert_service import CircadianAlertService
from src.services.analytics_service import CircadianAnalyticsService
from src.services.biometric_service import BiometricSyncService
from src.services.burnout_service import BurnoutPredictionService
from src.services.micro_recovery_service import MicroRecoveryService
from src.services.nutrition_service import ChronoNutritionService
from src.services.phototherapy_service import PhototherapyService
from src.services.social_sync_service import SocialJetlagService
from src.services.ultradian_service import UltradianEngineService
from src.services.weekly_matrix_service import WeeklyMatrixService


def test_biometric_service_sync():
    req = BiometricSyncRequest(
        hrv_rmssd=70.0,
        resting_hr=50.0,
        deep_sleep_minutes=90,
        rem_sleep_minutes=90,
        wake_time="07:00",
    )
    res = BiometricSyncService.sync_biometrics(req)
    assert res.recovery_factor >= 1.0
    assert res.readiness_score >= 80


def test_weekly_matrix_service():
    req = WeeklyMatrixRequest(
        profile={"wake_time": "07:00", "sleep_time": "23:00"},
        tasks_pool=[
            WeeklyTaskItem(title="Kutatás", duration=90, cognitive_load="DEEP_WORK"),
            WeeklyTaskItem(title="Dokumentáció", duration=60, cognitive_load="ADMIN"),
        ],
        start_date="2026-08-31",
    )
    res = WeeklyMatrixService.generate_weekly_matrix(req)
    assert len(res.days_schedule) == 7
    assert "Kedd" in res.focus_days
    assert res.weekly_balance_score > 70.0


def test_alert_service():
    req = AlertQueryRequest(
        profile={"sleep_time": "23:00"},
        current_time="15:00",
        active_deep_work_minutes=135,
    )
    res = CircadianAlertService.get_alerts(req)
    assert len(res.active_alerts) >= 1
    types = [a.alert_type for a in res.active_alerts]
    assert "FATIGUE_WARNING" in types or "CAFFEINE_CUTOFF" in types


def test_ultradian_service():
    req = UltradianSplitRequest(task_title="Kódolás", duration_minutes=180)
    res = UltradianEngineService.split_task(req)
    assert res.total_cycles == 2
    assert len(res.blocks) == 3  # Focus 1, Break, Focus 2


def test_nutrition_service():
    req = MealImpactRequest(
        meal_time="12:30",
        meal_type=MealType.LUNCH,
        carb_level=CarbLevel.HIGH,
        fasting_hours=0.0,
    )
    res = ChronoNutritionService.calculate_impact(req)
    assert res.dip_severity == 1.6
    assert res.postprandial_dip_start == "13:00"


def test_phototherapy_service():
    req = PhototherapyRequest(wake_time="06:30", sleep_time="22:30")
    res = PhototherapyService.generate_plan(req)
    assert res.morning_light_window == "06:30 - 07:15"
    assert res.evening_blueblocker_time == "20:30"


def test_burnout_service():
    req = BurnoutAnalysisRequest(
        daily_debts=[10.0, 15.0, 20.0],
        daily_recoveries=[0.5, 0.6, 0.4],
        streak_days=5,
    )
    res = BurnoutPredictionService.predict_burnout(req)
    assert res.allostatic_load_index > 40.0
    assert res.risk_level in ["MODERATE", "HIGH", "CRITICAL"]


def test_social_sync_service():
    req = SocialSyncRequest(
        profiles=[
            ChronotypeProfile(name="Lark", wake_time="06:00", sleep_time="22:00"),
            ChronotypeProfile(name="Owl", wake_time="09:00", sleep_time="01:00"),
        ],
        meeting_duration_minutes=60,
    )
    res = SocialJetlagService.calculate_sync(req)
    assert len(res.golden_overlap_windows) >= 1
    assert res.alignment_quality == "HIGH"


def test_micro_recovery_service():
    req = MicroRecoveryRequest(continuous_screen_minutes=80)
    res = MicroRecoveryService.plan_recovery(req)
    assert len(res.micro_breaks) == 4
    assert any(b.name.startswith("Fiziológiás") for b in res.micro_breaks)


def test_analytics_service():
    req = CircadianAnalyticsRequest(
        scheduled_slots=[
            ScheduledSlotAnalytics(
                task_id="t1",
                title="Deep Work",
                start_time="09:00",
                end_time="11:00",
                duration=120,
                cognitive_load="DEEP_WORK",
                assigned_energy_avg=8.8,
            )
        ],
        completed_task_ids=["t1"],
    )
    res = CircadianAnalyticsService.compute_analytics(req)
    assert res.alignment_score >= 80.0
    assert res.completed_rate == 100.0
