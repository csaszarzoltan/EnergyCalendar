"""Unit tests for EnergyCalculator service."""
from __future__ import annotations

import pytest

from src.models.energy import EnergyProfile, TimeInterval
from src.services.energy_calculator import (
    EnergyCalculator,
    minutes_to_time,
    time_to_minutes,
)


@pytest.fixture
def standard_profile() -> EnergyProfile:
    """Fixture providing a standard circadian energy profile."""
    return EnergyProfile(
        wake_time="07:00",
        sleep_time="23:00",
        peak_hours=[
            TimeInterval(start="09:00", end="11:30"),
            TimeInterval(start="16:30", end="18:30"),
        ],
        dip_hours=[
            TimeInterval(start="13:30", end="15:00"),
        ],
    )


def test_time_conversions():
    """Verify time string to minute and reverse minute to string conversions."""
    assert time_to_minutes("00:00") == 0
    assert time_to_minutes("07:00") == 420
    assert time_to_minutes("12:30") == 750
    assert time_to_minutes("23:59") == 1439

    assert minutes_to_time(0) == "00:00"
    assert minutes_to_time(420) == "07:00"
    assert minutes_to_time(750) == "12:30"
    assert minutes_to_time(1439) == "23:59"
    assert minutes_to_time(1440) == "00:00"


def test_calculate_energy_curve_points(standard_profile: EnergyProfile):
    """Generates exactly 96 points for a 24-hour day (15-min sampling), with peaks >8.0 and dips <4.0."""
    points = EnergyCalculator.generate_curve(standard_profile)
    assert len(points) == 96

    # Verify timestamps are spaced by 15 minutes
    assert points[0].time == "00:00"
    assert points[1].time == "00:15"
    assert points[-1].time == "23:45"

    # Verify peaks have energy > 8.0 and zone_type 'peak'
    peak_morning = [p for p in points if "09:30" <= p.time <= "11:00"]
    assert len(peak_morning) > 0
    for p in peak_morning:
        assert p.energy_level > 8.0
        assert p.zone_type == "peak"

    # Verify dips have energy < 4.0 and zone_type 'dip'
    dip_afternoon = [p for p in points if "13:45" <= p.time <= "14:45"]
    assert len(dip_afternoon) > 0
    for p in dip_afternoon:
        assert p.energy_level < 4.0
        assert p.zone_type == "dip"


def test_sleep_time_energy_level(standard_profile: EnergyProfile):
    """Verify sleep window assigns baseline 1.0 energy and 'sleep' zone."""
    points = EnergyCalculator.generate_curve(standard_profile)

    # Before wake time (07:00)
    early_morning = [p for p in points if p.minute_of_day < 420]
    assert len(early_morning) == 28  # 00:00 to 06:45 = 28 slots
    for p in early_morning:
        assert p.energy_level == 1.0
        assert p.zone_type == "sleep"

    # After sleep time (23:00)
    late_night = [p for p in points if p.minute_of_day >= 1380]
    assert len(late_night) == 4  # 23:00, 23:15, 23:30, 23:45 = 4 slots
    for p in late_night:
        assert p.energy_level == 1.0
        assert p.zone_type == "sleep"


def test_calculate_average_energy(standard_profile: EnergyProfile):
    """Verify average energy calculation across specific time windows."""
    # Morning peak average should be high (>= 8.0)
    avg_peak = EnergyCalculator.calculate_average_energy(
        standard_profile, start_minute=540, duration_minutes=150
    )
    assert avg_peak >= 8.0

    # Afternoon dip average should be low (<= 4.0)
    avg_dip = EnergyCalculator.calculate_average_energy(
        standard_profile, start_minute=810, duration_minutes=90
    )
    assert avg_dip <= 3.5

    # Zero duration edge case
    point_val = EnergyCalculator.calculate_average_energy(
        standard_profile, start_minute=600, duration_minutes=0
    )
    assert 0.0 <= point_val <= 10.0


def test_calculate_free_capacity(standard_profile: EnergyProfile):
    """Verify total free capacity and subtraction of fixed appointments."""
    total_unconstrained = EnergyCalculator.calculate_free_capacity(
        standard_profile, fixed_intervals=[]
    )
    assert total_unconstrained > 4000.0

    # Add a fixed 2-hour meeting during peak (09:00 to 11:00 -> 540 to 660)
    fixed_intervals = [(540, 660)]
    constrained_cap = EnergyCalculator.calculate_free_capacity(
        standard_profile, fixed_intervals=fixed_intervals
    )
    assert constrained_cap < total_unconstrained
    # Difference should roughly equal the peak energy of 120 minutes (~1000+)
    diff = total_unconstrained - constrained_cap
    assert diff > 900.0


def test_zone_classification(standard_profile: EnergyProfile):
    """Verify get_zone_type classification for boundaries."""
    # Sleep
    assert EnergyCalculator.get_zone_type(standard_profile, 100, 1.0) == "sleep"

    # Peak
    assert EnergyCalculator.get_zone_type(standard_profile, 600, 8.5) == "peak"
    assert EnergyCalculator.get_zone_type(standard_profile, 600, 7.5) == "peak"

    # Dip
    assert EnergyCalculator.get_zone_type(standard_profile, 850, 3.0) == "dip"
    assert EnergyCalculator.get_zone_type(standard_profile, 850, 4.0) == "dip"

    # Moderate
    assert EnergyCalculator.get_zone_type(standard_profile, 750, 5.5) == "moderate"
    assert EnergyCalculator.get_zone_type(standard_profile, 750, 7.4) == "moderate"
    assert EnergyCalculator.get_zone_type(standard_profile, 750, 4.1) == "moderate"
