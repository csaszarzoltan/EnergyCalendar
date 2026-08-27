"""Unit tests for Time Machine HUD and Multi-Lane Layout Engine (SPEC-008)."""
from __future__ import annotations

import pytest
from src.models.energy import EnergyProfile, TimeInterval, Task, CognitiveLoad
from src.models.simulation import SimulationTickRequest
from src.services.simulation_service import SimulationService


def test_time_machine_progression():
    prof = EnergyProfile(
        wake_time="07:00",
        sleep_time="23:00",
        peak_hours=[TimeInterval(start="09:00", end="11:30")],
        dip_hours=[TimeInterval(start="13:30", end="15:00")],
    )
    # Morning tick
    req_m = SimulationTickRequest(current_time="09:15", profile=prof)
    res_m = SimulationService.evaluate_tick(req_m)
    assert res_m.active_zone == "PEAK"

    # Afternoon dip tick
    req_d = SimulationTickRequest(current_time="14:15", profile=prof)
    res_d = SimulationService.evaluate_tick(req_d)
    assert res_d.active_zone == "DIP"


def test_time_machine_evening_winddown():
    prof = EnergyProfile(wake_time="07:00", sleep_time="23:00")
    req = SimulationTickRequest(current_time="22:30", profile=prof)
    res = SimulationService.evaluate_tick(req)
    assert res.caffeine_allowed is False
