"""Unit tests for Caffeine Window calculation, adenosine warnings, and sleep quality curve modulation."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.models.energy import CaffeineQueryRequest, EnergyProfile, TimeInterval
from src.services.energy_calculator import EnergyCalculator


@pytest.fixture
def profile() -> EnergyProfile:
    """Standard circadian energy profile fixture."""
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


def test_caffeine_window_calculation(profile: EnergyProfile):
    """Verify caffeine window start (wake+90m) and cutoff (sleep-9h) calculation."""
    res = EnergyCalculator.calculate_caffeine_window(profile, current_time="10:00")

    # Wake: 07:00 -> Start: 08:30
    assert res.caffeine_start_time == "08:30"
    # Sleep: 23:00 -> Cutoff: 14:00 (23:00 - 9h)
    assert res.caffeine_cutoff_time == "14:00"
    # Peak boost window: 08:30 to 11:00 (wake + 240m)
    assert res.peak_boost_start == "08:30"
    assert res.peak_boost_end == "11:00"
    assert res.is_safe_now is True


def test_caffeine_window_late_warning(profile: EnergyProfile):
    """Verify is_safe_now is False and warning given when queried past cutoff."""
    res = EnergyCalculator.calculate_caffeine_window(profile, current_time="15:30")

    assert res.is_safe_now is False
    assert "figyelem" in res.adenosine_warning.lower() or "koffein" in res.adenosine_warning.lower()
    assert "cutoff" in res.adenosine_warning.lower() or "14:00" in res.adenosine_warning


def test_caffeine_window_early_car_warning(profile: EnergyProfile):
    """Verify early warning when queried during morning Cortisol Awakening Response (CAR)."""
    res = EnergyCalculator.calculate_caffeine_window(profile, current_time="07:30")

    assert res.is_safe_now is True
    assert "car" in res.adenosine_warning.lower() or "kortizol" in res.adenosine_warning.lower()


def test_caffeine_window_midnight_wrap():
    """Verify cutoff calculation when sleep time crosses midnight (e.g. 01:00)."""
    night_profile = EnergyProfile(
        wake_time="09:00",
        sleep_time="01:00",
        peak_hours=[TimeInterval(start="11:00", end="13:30")],
        dip_hours=[TimeInterval(start="15:00", end="16:30")],
    )
    res = EnergyCalculator.calculate_caffeine_window(night_profile, current_time="12:00")

    # Wake: 09:00 -> Start: 10:30
    assert res.caffeine_start_time == "10:30"
    # Sleep: 01:00 -> Cutoff: 16:00 (01:00 - 9h = 16:00)
    assert res.caffeine_cutoff_time == "16:00"
    assert res.is_safe_now is True

    # Check after cutoff at 17:00
    res_late = EnergyCalculator.calculate_caffeine_window(night_profile, current_time="17:00")
    assert res_late.is_safe_now is False


def test_sleep_quality_curve_modulation(profile: EnergyProfile):
    """Verify that lower sleep quality dampens energy curve peaks and deepens dips."""
    curve_normal = EnergyCalculator.generate_curve(profile, sleep_quality=1.0)
    curve_degraded = EnergyCalculator.generate_curve(profile, sleep_quality=0.5)

    # Morning peak point at 10:15 (minute 615)
    peak_pt_normal = next(p for p in curve_normal if p.time == "10:15")
    peak_pt_degraded = next(p for p in curve_degraded if p.time == "10:15")
    assert peak_pt_degraded.energy_level < peak_pt_normal.energy_level

    # Afternoon dip point at 14:15 (minute 855)
    dip_pt_normal = next(p for p in curve_normal if p.time == "14:15")
    dip_pt_degraded = next(p for p in curve_degraded if p.time == "14:15")
    assert dip_pt_degraded.energy_level < dip_pt_normal.energy_level


@pytest.mark.asyncio
async def test_api_caffeine_window_endpoint(profile: EnergyProfile):
    """Test POST /api/v1/energy/caffeine-window HTTP endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/energy/caffeine-window",
            json={"profile": profile.model_dump(), "current_time": "11:00"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["caffeine_start_time"] == "08:30"
        assert data["caffeine_cutoff_time"] == "14:00"
        assert data["is_safe_now"] is True
        assert "recommendation" in data
