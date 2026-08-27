"""Domain models for market-driven circadian productivity suite (v1.4.0)."""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ContextTaskItem(BaseModel):
    """A task in an execution sequence for context switch analysis."""
    title: str = Field(...)
    load_type: str = Field(..., description="deep_work, creative, admin, recovery")
    duration_minutes: int = Field(default=30, gt=0)


class ContextSwitchRequest(BaseModel):
    """Request to compute context switching fragmentation tax."""
    tasks: List[ContextTaskItem] = Field(..., min_length=1)


class ContextSwitchResponse(BaseModel):
    """Context switching tax calculation and batched suggestion."""
    switch_count: int = Field(...)
    fragmentation_tax_minutes: int = Field(...)
    batched_tasks: List[ContextTaskItem] = Field(...)
    optimization_gain_percent: float = Field(...)
    advice: str = Field(...)


class JetlagRequest(BaseModel):
    """Circadian timezone shift and jetlag adaptation input."""
    origin_utc_offset: int = Field(..., ge=-12, le=14)
    target_utc_offset: int = Field(..., ge=-12, le=14)
    travel_date: str = Field(default="2026-09-01")


class JetlagDayProtocol(BaseModel):
    """Daily phase adaptation protocol for timezone travel."""
    day_number: int = Field(...)
    shifted_wake_time: str = Field(...)
    shifted_sleep_time: str = Field(...)
    morning_light_action: str = Field(...)
    evening_melatonin_action: str = Field(...)


class JetlagResponse(BaseModel):
    """Complete multi-day jetlag adaptation plan."""
    hour_difference: int = Field(...)
    days_to_adapt: int = Field(...)
    protocols: List[JetlagDayProtocol] = Field(...)
    guidance: str = Field(...)


class NeuroFlowRequest(BaseModel):
    """ADHD time-blindness and hyperfocus pacing input."""
    task_title: str = Field(...)
    duration_minutes: int = Field(..., gt=0, le=480)
    is_hyperfocus_prone: bool = Field(default=True)


class NeuroFlowResponse(BaseModel):
    """Gentle transition, visual pacing and hyperfocus checkpoints."""
    gentle_transition_minutes: int = Field(...)
    pacing_checkpoints: List[str] = Field(...)
    hydration_breaks: int = Field(...)
    flow_strategy: str = Field(...)


class BiophilicAuditRequest(BaseModel):
    """Indoor environmental telemetry audit."""
    co2_ppm: int = Field(..., ge=300, le=5000)
    temperature_celsius: float = Field(..., ge=10.0, le=40.0)
    noise_db: float = Field(..., ge=20.0, le=120.0)


class BiophilicAuditResponse(BaseModel):
    """Cognitive penalty evaluation from environmental stressors."""
    cognitive_penalty_percent: float = Field(..., ge=0.0, le=60.0)
    air_quality_status: str = Field(..., description="OPTIMAL, ACCEPTABLE, DEGRADED, HAZARDOUS")
    recommendations: List[str] = Field(...)


class DopamineGuardRequest(BaseModel):
    """High-friction focus zone configuration."""
    peak_start: str = Field(default="09:00")
    peak_end: str = Field(default="11:30")
    friction_level: str = Field(default="STRICT", description="MILD, MODERATE, STRICT")


class DopamineGuardResponse(BaseModel):
    """Digital friction rules and distraction blocking schedule."""
    active_window: str = Field(...)
    blocked_categories: List[str] = Field(...)
    friction_prompts: List[str] = Field(...)


class BrainwaveType(str, Enum):
    """Binaural brainwave frequencies."""
    DELTA = "DELTA"      # 1-4 Hz
    THETA = "THETA"      # 4-8 Hz
    ALPHA = "ALPHA"      # 8-12 Hz
    BETA = "BETA"        # 13-30 Hz
    GAMMA = "GAMMA"      # 30-50 Hz


class SoundscapeRequest(BaseModel):
    """Adaptive neural soundscape request."""
    cognitive_load: str = Field(default="DEEP_WORK")
    target_brainwave: Optional[BrainwaveType] = None


class SoundscapeResponse(BaseModel):
    """Web Audio synthesizer configuration parameters."""
    carrier_freq_hz: float = Field(...)
    binaural_beat_hz: float = Field(...)
    noise_color: str = Field(..., description="BROWN, PINK, WHITE")
    filter_cutoff_hz: int = Field(...)
    brainwave_target: str = Field(...)
    usage_guidance: str = Field(...)


class WeatherImpactRequest(BaseModel):
    """Meteorological and barometric cognitive impact query."""
    pressure_hpa: float = Field(default=1013.25, ge=900.0, le=1100.0)
    weather_condition: str = Field(default="RAINY", description="SUNNY, CLOUDY, RAINY, STORM")
    is_front_passing: bool = Field(default=False)


class WeatherImpactResponse(BaseModel):
    """Weather-modulated energy damping and recovery adjustment."""
    energy_damping_factor: float = Field(..., ge=0.5, le=1.1)
    extra_recovery_needed_minutes: int = Field(...)
    meteorological_advice: str = Field(...)


class WorkoutType(str, Enum):
    """Workout modality."""
    CARDIO_FAT_BURN = "CARDIO_FAT_BURN"
    STRENGTH_HYPERTROPHY = "STRENGTH_HYPERTROPHY"
    HIIT_ANAEROBIC = "HIIT_ANAEROBIC"
    YOGA_MOBILITY = "YOGA_MOBILITY"


class WorkoutTimingRequest(BaseModel):
    """Circadian workout optimization request."""
    wake_time: str = Field(default="07:00")
    sleep_time: str = Field(default="23:00")
    workout_type: WorkoutType = Field(default=WorkoutType.STRENGTH_HYPERTROPHY)


class WorkoutTimingResponse(BaseModel):
    """Optimal circadian biological window for physical training."""
    optimal_window_start: str = Field(...)
    optimal_window_end: str = Field(...)
    biological_rationale: str = Field(...)
    sleep_protection_cutoff: str = Field(...)


class MeetingItem(BaseModel):
    """A calendar meeting item."""
    title: str = Field(...)
    start_time: str = Field(...)
    duration_minutes: int = Field(..., gt=0)
    is_interactive: bool = Field(default=True)


class MeetingTaxRequest(BaseModel):
    """Meeting drain and decompression buffer query."""
    meetings: List[MeetingItem] = Field(default_factory=list)


class MeetingTaxResponse(BaseModel):
    """Meeting cognitive tax and automatic decompression buffers."""
    total_meeting_minutes: int = Field(...)
    cognitive_drain_score: float = Field(...)
    decompression_buffers: List[Dict[str, str]] = Field(...)
    advice: str = Field(...)


class InfradianRequest(BaseModel):
    """Infradian and seasonal rhythm request."""
    season: str = Field(default="WINTER", description="SPRING, SUMMER, AUTUMN, WINTER")
    cycle_day: Optional[int] = Field(default=None, ge=1, le=35)


class InfradianResponse(BaseModel):
    """Seasonal and monthly macro adjustment recommendations."""
    seasonal_sleep_adjustment_minutes: int = Field(...)
    recommended_lux_exposure_minutes: int = Field(...)
    macro_focus_advice: str = Field(...)
