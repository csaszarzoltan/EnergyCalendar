"""Burnout prediction and allostatic load evaluation service."""
from __future__ import annotations

from src.models.advanced_circadian import BurnoutAnalysisRequest, BurnoutAnalysisResponse


class BurnoutPredictionService:
    """Evaluates multi-day cognitive strain, sleep debt, and allostatic load."""

    @staticmethod
    def predict_burnout(request: BurnoutAnalysisRequest) -> BurnoutAnalysisResponse:
        """Compute allostatic load index and recommend decompression periods."""
        debts = request.daily_debts or [0.0]
        recoveries = request.daily_recoveries or [1.0]

        total_debt = sum(debts)
        avg_rec = sum(recoveries) / max(1, len(recoveries))

        # Allostatic formula: higher debt + poor recovery = higher load
        raw_load = (total_debt * 1.5) * (1.4 - avg_rec) * (request.streak_days / 5.0)
        allostatic_index = max(0.0, min(100.0, round(raw_load, 1)))

        if allostatic_index < 25.0:
            risk = "LOW"
            decom = 0
            rec_text = "Optimális kognitív terhelés és regeneráció. Folytasd a jelenlegi ritmust!"
        elif allostatic_index < 55.0:
            risk = "MODERATE"
            decom = 1
            rec_text = "Enyhe kognitív adósság felhalmozódás. Tervezz be egy könnyített napot."
        elif allostatic_index < 80.0:
            risk = "HIGH"
            decom = 2
            rec_text = "Magas allosztatikus terhelés! Csökkentsd a mélymunka órákat a hétvégén."
        else:
            risk = "CRITICAL"
            decom = 3
            rec_text = "Kritikus kiégési kockázat! Azonnali kötelező dekompresszió javasolt."

        return BurnoutAnalysisResponse(
            allostatic_load_index=allostatic_index,
            risk_level=risk,
            decompression_days_needed=decom,
            recommendation=rec_text,
        )
