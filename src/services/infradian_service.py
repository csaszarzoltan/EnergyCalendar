"""Infradian and seasonal macro-rhythm planner."""
from __future__ import annotations

from src.models.market_circadian import InfradianRequest, InfradianResponse


class InfradianRhythmService:
    """Calculates seasonal sleep adjustments and monthly macro focus cycles."""

    @staticmethod
    def plan_infradian(request: InfradianRequest) -> InfradianResponse:
        """Provide seasonal circadian photoperiod advice."""
        season = request.season.upper()
        if season == "WINTER":
            sleep_adj = 30  # +30 min sleep in winter
            lux_time = 45   # +45 min 10k lux exposure
            advice = "Téli szezon: +30 perc természetes alvásigény és intenzív reggeli fényterápia a SAD megelőzésére."
        elif season == "SUMMER":
            sleep_adj = -15
            lux_time = 20
            advice = "Nyári szezon: korábbi természetes ébredés, intenzív esti sötétítés."
        elif season == "AUTUMN":
            sleep_adj = 15
            lux_time = 30
            advice = "Őszi átmenet: cirkadián fázis stabilizálása rendszeres ébredési idővel."
        else:
            sleep_adj = 0
            lux_time = 25
            advice = "Tavaszi megújulás: növekvő kognitív kreatív kapacitás kihasználása."

        return InfradianResponse(
            seasonal_sleep_adjustment_minutes=sleep_adj,
            recommended_lux_exposure_minutes=lux_time,
            macro_focus_advice=advice,
        )
