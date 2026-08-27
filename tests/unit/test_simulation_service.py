"""Unit tests for the Circadian Simulation Engine (SPEC-007 / v1.5.0)."""
from __future__ import annotations

import pytest
from src.models.energy import EnergyProfile, TimeInterval
from src.models.simulation import SimulationTickRequest
from src.services.simulation_service import SimulationService



def test_simulation_service_peak_tick():
    prof = EnergyProfile(
        wake_time="07:00",
        sleep_time="23:00",
        peak_hours=[TimeInterval(start="09:00", end="11:30")],
        dip_hours=[TimeInterval(start="13:30", end="15:00")],
    )
    req = SimulationTickRequest(current_time="10:00", profile=prof)
    res = SimulationService.evaluate_tick(req)

    assert res.current_time == "10:00"
    assert res.active_zone == "PEAK"
    assert res.energy_level >= 7.5
    assert res.caffeine_allowed is True
    assert res.melatonin_minutes_remaining > 0


def test_simulation_service_dip_tick():
    prof = EnergyProfile(
        wake_time="07:00",
        sleep_time="23:00",
        peak_hours=[TimeInterval(start="09:00", end="11:30")],
        dip_hours=[TimeInterval(start="13:30", end="15:00")],
    )
    req = SimulationTickRequest(current_time="14:00", profile=prof)
    res = SimulationService.evaluate_tick(req)

    assert res.active_zone == "DIP"
    assert res.energy_level <= 5.5
