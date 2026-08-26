"""Domain models for circadian energy management and task scheduling."""
from __future__ import annotations

from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class CognitiveLoad(str, Enum):
    """Cognitive load category representing mental effort and energy impact."""
    DEEP_WORK = "deep_work"       # High cognitive demand (weight: 8.0 - 10.0)
    CREATIVE = "creative"         # Associative / ideation demand (weight: 5.0 - 7.0)
    ADMIN = "admin"               # Low cognitive demand / routine (weight: 2.0 - 4.0)
    RECOVERY = "recovery"         # Restorative recharging (negative cost: -2.0 - -5.0)


class TimeInterval(BaseModel):
    """Represents a time interval between two 24-hour HH:MM timestamps."""
    start: str = Field(..., description="Time in 'HH:MM' format, e.g. '09:00'")
    end: str = Field(..., description="Time in 'HH:MM' format, e.g. '11:30'")

    @field_validator("start", "end")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """Validate and normalize HH:MM time format."""
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError("Time must be in 'HH:MM' format")
        try:
            h, m = int(parts[0]), int(parts[1])
        except ValueError as exc:
            raise ValueError("Time components must be integers") from exc
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("Hour must be 0-23 and minute must be 0-59")
        return f"{h:02d}:{m:02d}"


class EnergyProfile(BaseModel):
    """User circadian rhythm profile configuration."""
    wake_time: str = Field(default="07:00", description="Wake-up time in 'HH:MM'")
    sleep_time: str = Field(default="23:00", description="Bedtime in 'HH:MM'")
    peak_hours: List[TimeInterval] = Field(
        default_factory=lambda: [
            TimeInterval(start="09:00", end="11:30"),
            TimeInterval(start="16:30", end="18:30"),
        ]
    )
    dip_hours: List[TimeInterval] = Field(
        default_factory=lambda: [
            TimeInterval(start="13:30", end="15:00"),
        ]
    )

    @field_validator("wake_time", "sleep_time")
    @classmethod
    def validate_profile_times(cls, v: str) -> str:
        """Validate and normalize wake_time and sleep_time formats."""
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError("Time must be in 'HH:MM' format")
        try:
            h, m = int(parts[0]), int(parts[1])
        except ValueError as exc:
            raise ValueError("Time components must be integers") from exc
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("Hour must be 0-23 and minute must be 0-59")
        return f"{h:02d}:{m:02d}"


class Task(BaseModel):
    """Input task specification for scheduling."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., min_length=1)
    duration_minutes: int = Field(..., gt=0, le=720)
    load_type: CognitiveLoad = Field(...)
    deadline: Optional[str] = Field(default=None, description="Deadline in 'HH:MM' format")
    is_fixed: bool = Field(default=False, description="True for fixed calendar appointments")
    fixed_start: Optional[str] = Field(default=None, description="Fixed start time in 'HH:MM'")
    energy_cost: float = Field(default=5.0, ge=-10.0, le=10.0)

    @field_validator("deadline", "fixed_start")
    @classmethod
    def validate_optional_time(cls, v: Optional[str]) -> Optional[str]:
        """Validate optional time fields if provided."""
        if v is None:
            return None
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError("Time must be in 'HH:MM' format")
        try:
            h, m = int(parts[0]), int(parts[1])
        except ValueError as exc:
            raise ValueError("Time components must be integers") from exc
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("Hour must be 0-23 and minute must be 0-59")
        return f"{h:02d}:{m:02d}"


class ScheduledSlot(BaseModel):
    """Scheduled task time slot."""
    task_id: str
    title: str
    start_time: str
    end_time: str
    duration_minutes: int
    load_type: CognitiveLoad
    energy_cost: float
    is_auto_recovery: bool = False
    average_energy_level: float


class EnergyDebtReport(BaseModel):
    """Cognitive load and energy debt calculation report."""
    total_capacity: float
    total_requested_load: float
    energy_debt: float
    is_overloaded: bool
    exhaustion_percentage: float
    recommendation: str


class EnergyCurvePoint(BaseModel):
    """15-minute resolution point on the circadian energy curve."""
    time: str
    minute_of_day: int
    energy_level: float
    zone_type: str


class EnergyCurveResponse(BaseModel):
    """API response model for 24h energy curve."""
    points: List[EnergyCurvePoint]
    profile: EnergyProfile


class ScheduleRequest(BaseModel):
    """Request payload for choreographing tasks."""
    profile: EnergyProfile
    tasks: List[Task]


class ScheduleResponse(BaseModel):
    """Response payload containing choreographed schedule and debt analysis."""
    status: str = "ok"
    scheduled_tasks: List[ScheduledSlot]
    unscheduled_tasks: List[Task] = []
    debt_report: EnergyDebtReport
    energy_curve: List[EnergyCurvePoint]


class TaskParseRequest(BaseModel):
    """Request payload for natural language task parsing."""
    raw_text: str


class TaskParseResponse(BaseModel):
    """Response payload for natural language task parsing."""
    title: str
    duration_minutes: int
    load_type: CognitiveLoad
    energy_cost: float
    confidence: float


class CaffeineWindowResponse(BaseModel):
    """Circadian caffeine timing and adenosine risk analysis."""
    caffeine_start_time: str = Field(..., description="Caffeine window start 'HH:MM' (wake + 90 min)")
    caffeine_cutoff_time: str = Field(..., description="Caffeine cutoff 'HH:MM' (sleep - 9 hours)")
    peak_boost_start: str = Field(..., description="Peak boost window start 'HH:MM' (wake + 90 min)")
    peak_boost_end: str = Field(..., description="Peak boost window end 'HH:MM' (wake + 240 min)")
    is_safe_now: bool = Field(..., description="True if current_time < caffeine_cutoff_time")
    adenosine_warning: str = Field(..., description="Adenosine receptor and sleep impact warning")
    recommendation: str = Field(..., description="Actionable caffeine recommendation")


class ReflowRequest(BaseModel):
    """Request payload for dynamic mid-day schedule re-flow."""
    profile: EnergyProfile
    current_time: str = Field(..., description="Aktuális időpont 'HH:MM', pl. '14:15'")
    pending_tasks: List[Task] = Field(..., description="Hátralévő, el nem végzett feladatok")
    completed_task_ids: List[str] = Field(default_factory=list, description="Már befejezett feladatok ID-jai")
    sleep_quality: float = Field(default=1.0, ge=0.3, le=1.2, description="Alvásminőség szorzó 0.3 - 1.2")

    @field_validator("current_time")
    @classmethod
    def validate_current_time(cls, v: str) -> str:
        """Validate HH:MM time format."""
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError("Time must be in 'HH:MM' format")
        try:
            h, m = int(parts[0]), int(parts[1])
        except ValueError as exc:
            raise ValueError("Time components must be integers") from exc
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("Hour must be 0-23 and minute must be 0-59")
        return f"{h:02d}:{m:02d}"


class ReflowResponse(BaseModel):
    """Response payload for mid-day schedule re-flow."""
    status: str = "ok"
    reflow_time: str
    scheduled_tasks: List[ScheduledSlot]
    unscheduled_tasks: List[Task] = []
    debt_report: EnergyDebtReport
    energy_curve: List[EnergyCurvePoint]
    caffeine_window: CaffeineWindowResponse


class CaffeineQueryRequest(BaseModel):
    """Request payload for caffeine window calculation."""
    profile: EnergyProfile
    current_time: Optional[str] = Field(default=None, description="Aktuális időpont 'HH:MM'")

    @field_validator("current_time")
    @classmethod
    def validate_current_time(cls, v: Optional[str]) -> Optional[str]:
        """Validate optional HH:MM time format."""
        if v is None:
            return None
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError("Time must be in 'HH:MM' format")
        try:
            h, m = int(parts[0]), int(parts[1])
        except ValueError as exc:
            raise ValueError("Time components must be integers") from exc
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("Hour must be 0-23 and minute must be 0-59")
        return f"{h:02d}:{m:02d}"


class ICSExportRequest(BaseModel):
    """Request payload for exporting scheduled slots to iCalendar format."""
    scheduled_tasks: List[ScheduledSlot]
    calendar_name: str = Field(default="Cirkadián Energia Naptár")


class ICSImportRequest(BaseModel):
    """Request payload for importing external iCalendar RFC 5545 text."""
    ics_content: str = Field(..., min_length=10, description="Raw iCalendar RFC 5545 text")


class ICSImportResponse(BaseModel):
    """Response payload containing tasks imported from iCalendar."""
    imported_tasks: List[Task]
    imported_count: int
    message: str


class TaskDecomposeRequest(BaseModel):
    """Request payload for breaking down a large task into cognitive subtasks."""
    task: Task


class TaskDecomposeResponse(BaseModel):
    """Response payload containing decomposed cognitive subtasks."""
    original_task_id: str
    subtasks: List[Task]
    total_duration_minutes: int
    decomposition_strategy: str


class ShutdownSummaryRequest(BaseModel):
    """Request payload for circadian shutdown summary report."""
    profile: EnergyProfile
    completed_tasks: List[Task]
    pending_tasks: List[Task]
    scheduled_slots: List[ScheduledSlot]
    current_time: Optional[str] = Field(default=None, description="Current time 'HH:MM'")

    @field_validator("current_time")
    @classmethod
    def validate_current_time(cls, v: Optional[str]) -> Optional[str]:
        """Validate optional HH:MM format."""
        if v is None:
            return None
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError("Time must be in 'HH:MM' format")
        try:
            h, m = int(parts[0]), int(parts[1])
        except ValueError as exc:
            raise ValueError("Time components must be integers") from exc
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("Hour must be 0-23 and minute must be 0-59")
        return f"{h:02d}:{m:02d}"


class ShutdownSummaryResponse(BaseModel):
    """Response payload for end-of-day circadian shutdown ritual."""
    completed_count: int
    pending_count: int
    total_deep_work_minutes: int
    energy_debt_averted: float
    melatonin_gate_time: str      # 'HH:MM' (t_sleep - 60 min)
    minutes_until_melatonin: int
    tomorrow_first_peak: str       # 'HH:MM' (profile.peak_hours[0].start)
    recommendations: List[str]
    is_shutdown_recommended_now: bool


