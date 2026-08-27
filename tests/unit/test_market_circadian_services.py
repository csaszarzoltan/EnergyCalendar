"""Unit tests for the 10 market-driven circadian services (SPEC-006 / v1.4.0)."""
from __future__ import annotations

import pytest
from src.models.market_circadian import (
    BiophilicAuditRequest,
    BrainwaveType,
    ContextSwitchRequest,
    ContextTaskItem,
    DopamineGuardRequest,
    InfradianRequest,
    JetlagRequest,
    MeetingItem,
    MeetingTaxRequest,
    NeuroFlowRequest,
    SoundscapeRequest,
    WeatherImpactRequest,
    WorkoutTimingRequest,
    WorkoutType,
)
from src.services.biophilic_service import BiophilicSpaceService
from src.services.context_switch_service import ContextSwitchService
from src.services.dopamine_guard_service import DopamineGuardService
from src.services.infradian_service import InfradianRhythmService
from src.services.jetlag_service import JetlagChronoService
from src.services.meeting_tax_service import MeetingTaxService
from src.services.neuro_flow_service import NeuroFlowService
from src.services.soundscape_service import SoundscapeSynthService
from src.services.weather_chrono_service import WeatherChronoService
from src.services.workout_timing_service import WorkoutTimingService


def test_context_switch_service():
    req = ContextSwitchRequest(
        tasks=[
            ContextTaskItem(title="Kódolás 1", load_type="deep_work", duration_minutes=60),
            ContextTaskItem(title="Email", load_type="admin", duration_minutes=20),
            ContextTaskItem(title="Kódolás 2", load_type="deep_work", duration_minutes=45),
            ContextTaskItem(title="Számlák", load_type="admin", duration_minutes=15),
        ]
    )
    res = ContextSwitchService.analyze_switches(req)
    assert res.switch_count == 3
    assert res.fragmentation_tax_minutes == 45
    assert res.optimization_gain_percent > 0.0


def test_jetlag_chrono_service():
    req = JetlagRequest(origin_utc_offset=2, target_utc_offset=-4)  # 6h west
    res = JetlagChronoService.calculate_adaptation(req)
    assert res.hour_difference == -6
    assert res.days_to_adapt == 6
    assert len(res.protocols) == 6


def test_neuro_flow_service():
    req = NeuroFlowRequest(task_title="Komplex kód refaktor", duration_minutes=120)
    res = NeuroFlowService.create_pacing(req)
    assert res.gentle_transition_minutes == 10
    assert len(res.pacing_checkpoints) >= 2


def test_biophilic_space_service():
    req = BiophilicAuditRequest(co2_ppm=1400, temperature_celsius=25.0, noise_db=50.0)
    res = BiophilicSpaceService.audit_environment(req)
    assert res.air_quality_status == "DEGRADED"
    assert res.cognitive_penalty_percent >= 25.0


def test_dopamine_guard_service():
    req = DopamineGuardRequest(peak_start="09:00", peak_end="11:30", friction_level="STRICT")
    res = DopamineGuardService.create_guard(req)
    assert "Social Media" in res.blocked_categories
    assert len(res.friction_prompts) >= 2


def test_soundscape_service():
    req = SoundscapeRequest(cognitive_load="DEEP_WORK", target_brainwave=BrainwaveType.GAMMA)
    res = SoundscapeSynthService.generate_config(req)
    assert res.binaural_beat_hz == 40.0
    assert res.noise_color == "PINK"


def test_weather_chrono_service():
    req = WeatherImpactRequest(pressure_hpa=998.0, weather_condition="STORM", is_front_passing=True)
    res = WeatherChronoService.evaluate_weather(req)
    assert res.energy_damping_factor < 1.0
    assert res.extra_recovery_needed_minutes >= 20


def test_workout_timing_service():
    req = WorkoutTimingRequest(wake_time="07:00", sleep_time="23:00", workout_type=WorkoutType.STRENGTH_HYPERTROPHY)
    res = WorkoutTimingService.calculate_window(req)
    assert res.optimal_window_start == "16:00"
    assert res.sleep_protection_cutoff == "20:00"


def test_meeting_tax_service():
    req = MeetingTaxRequest(
        meetings=[
            MeetingItem(title="Standup", start_time="09:30", duration_minutes=30),
            MeetingItem(title="Architektúra review", start_time="14:00", duration_minutes=60),
        ]
    )
    res = MeetingTaxService.evaluate_meetings(req)
    assert res.total_meeting_minutes == 90
    assert len(res.decompression_buffers) == 2


def test_infradian_service():
    req = InfradianRequest(season="WINTER")
    res = InfradianRhythmService.plan_infradian(req)
    assert res.seasonal_sleep_adjustment_minutes == 30
    assert res.recommended_lux_exposure_minutes == 45
