"""Meteorological and barometric circadian damping service."""
from __future__ import annotations

from src.models.market_circadian import WeatherImpactRequest, WeatherImpactResponse


class WeatherChronoService:
    """Adjusts circadian capacity and fatigue recovery based on atmospheric pressure and fronts."""

    @staticmethod
    def evaluate_weather(request: WeatherImpactRequest) -> WeatherImpactResponse:
        """Compute energy damping factor and extra recovery minutes needed."""
        damping = 1.0
        extra_rec = 0

        # Barometric drop (e.g. < 1008 hPa indicates storm / front)
        if request.pressure_hpa < 1005.0 or request.is_front_passing:
            damping -= 0.15
            extra_rec += 20

        if request.weather_condition.upper() in ["RAINY", "STORM"]:
            damping -= 0.10
            extra_rec += 15
        elif request.weather_condition.upper() == "CLOUDY":
            damping -= 0.05
            extra_rec += 10

        damping_clamped = max(0.5, min(1.1, round(damping, 2)))

        advice = (
            f"Légköri front és alacsony légnyomás miatt a kognitív energiaszint {int((1.0 - damping_clamped) * 100)}%-kal "
            f"visszafogottabb. Tarts +{extra_rec} perc pihenőt a nap folyamán."
        )

        return WeatherImpactResponse(
            energy_damping_factor=damping_clamped,
            extra_recovery_needed_minutes=extra_rec,
            meteorological_advice=advice,
        )
