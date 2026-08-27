from typing import List, Optional
from pydantic import BaseModel, Field
from src.models.energy import EnergyProfile, Task


class SimulationTickRequest(BaseModel):
    """Request representing current simulation clock step."""
    current_time: str = Field(..., description="Simulation clock in HH:MM format", pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    profile: EnergyProfile = Field(..., description="User circadian chronotype profile")
    tasks: List[Task] = Field(default_factory=list, description="Pending or scheduled task pool")



class SimulationTickResponse(BaseModel):
    """Response representing real-time biological telemetry at simulation tick."""
    current_time: str
    energy_level: float
    active_zone: str  # PEAK, DIP, RECOVERY, MODERATE
    active_task_title: Optional[str] = None
    caffeine_allowed: bool
    melatonin_minutes_remaining: int
    neuro_guidance: str
