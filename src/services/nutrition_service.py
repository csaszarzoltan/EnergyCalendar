"""Circadian chrono-nutrition and postprandial dip calculator."""
from __future__ import annotations

from src.models.advanced_circadian import CarbLevel, MealImpactRequest, MealImpactResponse


class ChronoNutritionService:
    """Evaluates meal timing and macronutrient load on cognitive depression."""

    @staticmethod
    def calculate_impact(request: MealImpactRequest) -> MealImpactResponse:
        """Calculate postprandial dip window and light physical activity recommendation."""
        parts = [int(p) for p in request.meal_time.split(":")]
        meal_min = parts[0] * 60 + parts[1]

        # Postprandial dip starts ~30 min after meal and lasts 60-90 min
        dip_start_min = (meal_min + 30) % 1440
        dip_duration = 90 if request.carb_level == CarbLevel.HIGH else 60
        dip_end_min = (dip_start_min + dip_duration) % 1440

        severity_map = {CarbLevel.HIGH: 1.6, CarbLevel.MEDIUM: 1.2, CarbLevel.LOW: 0.8}
        severity = severity_map.get(request.carb_level, 1.0)
        if request.fasting_hours >= 14.0:
            severity = round(severity * 0.85, 2)

        walk_start = f"{(meal_min + 15) // 60:02d}:{(meal_min + 15) % 60:02d}"
        walk_end = f"{(meal_min + 30) // 60:02d}:{(meal_min + 30) % 60:02d}"

        return MealImpactResponse(
            postprandial_dip_start=f"{dip_start_min // 60:02d}:{dip_start_min % 60:02d}",
            postprandial_dip_end=f"{dip_end_min // 60:02d}:{dip_end_min % 60:02d}",
            dip_severity=severity,
            optimal_walk_window=f"{walk_start} - {walk_end}",
            recommendation="Egy 15 perces könnyű séta közvetlenül ebéd után 40%-kal csökkenti a kaja-kóma mélységét.",
        )
