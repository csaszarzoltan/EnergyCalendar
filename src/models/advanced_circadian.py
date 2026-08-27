"""Advanced circadian domain models for biometrics, weekly macro-rhythm, and analytics."""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class BiometricSyncRequest(BaseModel):
    """Biometric wearable sensor input payload."""
    hrv_rmssd: float = Field(..., ge=10.0, le=250.0, description="HRV RMSSD in milliseconds")
    resting_hr: float = Field(..., ge=30.0, le=120.0, description="Resting heart rate in bpm")
    deep_sleep_minutes: int = Field(..., ge=0, le=360, description="Deep sleep minutes")
    rem_sleep_minutes: int = Field(..., ge=0, le=360, description="REM sleep minutes")
    wake_time: str = Field(default="07:00", description="Wake-up time in HH:MM")


class BiometricSyncResponse(BaseModel):
    """Biometric sync calculated readiness and circadian modulation."""
    recovery_factor: float = Field(..., ge=0.3, le=1.2)
    readiness_score: int = Field(..., ge=0, le=100)
    recommended_peak_offset_minutes: int = Field(...)
    message: str = Field(...)


class WeeklyTaskItem(BaseModel):
    """Task item for weekly scheduling pool."""
    title: str = Field(..., min_length=1)
    duration: int = Field(..., gt=0, le=720)
    cognitive_load: str = Field(default="DEEP_WORK")


class WeeklyMatrixRequest(BaseModel):
    """Request for weekly 7-day circadian load distribution."""
    profile: Dict[str, Any] = Field(...)
    tasks_pool: List[WeeklyTaskItem] = Field(default_factory=list)
    start_date: str = Field(default="2026-08-31")


class DayScheduleSummary(BaseModel):
    """Summary of scheduled cognitive load for a single day."""
    day_index: int = Field(...)
    day_name: str = Field(...)
    date_str: str = Field(...)
    is_focus_day: bool = Field(default=False)
    is_recovery_day: bool = Field(default=False)
    total_deep_work_minutes: int = Field(default=0)
    total_admin_minutes: int = Field(default=0)
    tasks: List[Dict[str, Any]] = Field(default_factory=list)


class WeeklyMatrixResponse(BaseModel):
    """7-day scheduled macro rhythm and balance score."""
    days_schedule: List[DayScheduleSummary] = Field(...)
    focus_days: List[str] = Field(...)
    recovery_days: List[str] = Field(...)
    weekly_balance_score: float = Field(...)
    recommendation: str = Field(...)


class AlertQueryRequest(BaseModel):
    """Query for real-time circadian and cognitive alerts."""
    profile: Dict[str, Any] = Field(...)
    current_time: str = Field(..., description="Current time in HH:MM")
    active_deep_work_minutes: int = Field(default=0, ge=0)


class CircadianAlert(BaseModel):
    """A single real-time circadian or fatigue alert."""
    alert_type: str = Field(..., description="CAFFEINE_CUTOFF, MELATONIN_GATE, FATIGUE_WARNING, BLUE_LIGHT")
    severity: str = Field(..., description="INFO, WARNING, CRITICAL")
    message: str = Field(...)
    action_prompt: str = Field(...)


class AlertQueryResponse(BaseModel):
    """Active circadian alerts and countdown to next biological milestone."""
    active_alerts: List[CircadianAlert] = Field(default_factory=list)
    next_milestone: str = Field(...)
    countdown_minutes: int = Field(...)


class UltradianSplitRequest(BaseModel):
    """Request to split complex task according to 90/20 BRAC ultradian cycles."""
    task_title: str = Field(..., min_length=1)
    duration_minutes: int = Field(..., gt=0, le=720)
    brac_cycle_minutes: int = Field(default=90, ge=30, le=120)
    break_minutes: int = Field(default=20, ge=5, le=45)


class UltradianBlock(BaseModel):
    """A single ultradian focus or recovery block."""
    block_index: int = Field(...)
    block_type: str = Field(...)  # FOCUS or BRAC_RECOVERY
    title: str = Field(...)
    duration_minutes: int = Field(...)
    suggested_focus_level: str = Field(...)


class UltradianSplitResponse(BaseModel):
    """Decomposed ultradian cycle schedule."""
    blocks: List[UltradianBlock] = Field(...)
    total_cycles: int = Field(...)
    total_duration: int = Field(...)
    advice: str = Field(...)


class MealType(str, Enum):
    """Meal categories."""
    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"
    SNACK = "SNACK"


class CarbLevel(str, Enum):
    """Carbohydrate intensity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class MealImpactRequest(BaseModel):
    """Chrono-nutrition postprandial dip request."""
    meal_time: str = Field(..., description="Meal time in HH:MM")
    meal_type: MealType = Field(default=MealType.LUNCH)
    carb_level: CarbLevel = Field(default=CarbLevel.HIGH)
    fasting_hours: float = Field(default=0.0, ge=0.0)


class MealImpactResponse(BaseModel):
    """Calculated postprandial dip and walking window."""
    postprandial_dip_start: str = Field(...)
    postprandial_dip_end: str = Field(...)
    dip_severity: float = Field(...)
    optimal_walk_window: str = Field(...)
    recommendation: str = Field(...)


class PhototherapyRequest(BaseModel):
    """Circadian phototherapy and lux exposure request."""
    wake_time: str = Field(default="06:30")
    sleep_time: str = Field(default="22:30")
    target_lux: int = Field(default=10000, ge=500, le=50000)


class PhototherapyResponse(BaseModel):
    """Recommended light exposure and blue light filter windows."""
    morning_light_window: str = Field(...)
    midday_sun_window: str = Field(...)
    evening_blueblocker_time: str = Field(...)
    protocol_tips: List[str] = Field(...)


class BurnoutAnalysisRequest(BaseModel):
    """Allostatic load and burnout risk analysis input."""
    daily_debts: List[float] = Field(...)
    daily_recoveries: List[float] = Field(...)
    streak_days: int = Field(default=5, ge=1)


class BurnoutAnalysisResponse(BaseModel):
    """Burnout risk and allostatic load evaluation."""
    allostatic_load_index: float = Field(..., ge=0.0, le=100.0)
    risk_level: str = Field(..., description="LOW, MODERATE, HIGH, CRITICAL")
    decompression_days_needed: int = Field(...)
    recommendation: str = Field(...)


class ChronotypeProfile(BaseModel):
    """Chronotype profile for social sync."""
    name: str = Field(...)
    wake_time: str = Field(...)
    sleep_time: str = Field(...)
    peak_hours: List[str] = Field(default_factory=list)
    dip_hours: List[str] = Field(default_factory=list)


class SocialSyncRequest(BaseModel):
    """Request to find circadian overlap and calculate social jetlag."""
    profiles: List[ChronotypeProfile] = Field(..., min_length=2)
    meeting_duration_minutes: int = Field(default=45, ge=15, le=180)


class GoldenOverlapWindow(BaseModel):
    """Optimal shared peak focus window for collaboration."""
    start_time: str = Field(...)
    end_time: str = Field(...)
    overlap_quality: str = Field(...)
    suitability_score: float = Field(...)


class SocialSyncResponse(BaseModel):
    """Calculated social overlap windows and social jetlag score."""
    golden_overlap_windows: List[GoldenOverlapWindow] = Field(...)
    social_jetlag_score: float = Field(...)
    alignment_quality: str = Field(...)
    summary: str = Field(...)


class MicroRecoveryRequest(BaseModel):
    """Continuous work micro-recovery trigger."""
    continuous_screen_minutes: int = Field(..., ge=10, le=480)


class MicroBreak(BaseModel):
    """Single micro-recovery prompt."""
    name: str = Field(...)
    trigger_at_minute: int = Field(...)
    duration_seconds: int = Field(...)
    action: str = Field(...)


class MicroRecoveryResponse(BaseModel):
    """Somatic and ocular recovery protocol."""
    micro_breaks: List[MicroBreak] = Field(...)
    physiological_sigh_instructions: str = Field(...)
    eye_reset_202020: str = Field(...)


class ScheduledSlotAnalytics(BaseModel):
    """Scheduled task slot for analytics evaluation."""
    task_id: str = Field(...)
    title: str = Field(...)
    start_time: str = Field(...)
    end_time: str = Field(...)
    duration: int = Field(...)
    cognitive_load: str = Field(...)
    assigned_energy_avg: float = Field(...)


class CircadianAnalyticsRequest(BaseModel):
    """Performance and alignment reporting input."""
    scheduled_slots: List[ScheduledSlotAnalytics] = Field(default_factory=list)
    completed_task_ids: List[str] = Field(default_factory=list)


class CircadianAnalyticsResponse(BaseModel):
    """Circadian alignment score and cognitive ROI metrics."""
    alignment_score: float = Field(..., ge=0.0, le=100.0)
    deep_work_ratio: float = Field(...)
    energy_roi_factor: float = Field(...)
    completed_rate: float = Field(...)
    summary: str = Field(...)
