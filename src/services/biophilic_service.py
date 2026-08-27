"""Indoor environmental biophilic audit and cognitive capacity impact engine."""
from __future__ import annotations

from typing import List
from src.models.market_circadian import BiophilicAuditRequest, BiophilicAuditResponse


class BiophilicSpaceService:
    """Evaluates CO2, temperature, and acoustic noise impact on mental bandwidth."""

    @staticmethod
    def audit_environment(request: BiophilicAuditRequest) -> BiophilicAuditResponse:
        """Compute cognitive penalty and actionable workspace ventilation advice."""
        penalty = 0.0
        recs: List[str] = []

        # CO2 evaluation (Allen et al. Harvard COGfx Study)
        if request.co2_ppm < 800:
            co2_status = "OPTIMAL"
        elif request.co2_ppm < 1200:
            co2_status = "ACCEPTABLE"
            penalty += 10.0
            recs.append("A CO2 szint emelkedik (800-1200 ppm). Nyiss ablakot a friss oxigénért.")
        elif request.co2_ppm < 2000:
            co2_status = "DEGRADED"
            penalty += 25.0
            recs.append("Magas CO2 (1200+ ppm): A döntési képesség 25%-kal csökken! Azonnali kereszthuzat javasolt.")
        else:
            co2_status = "HAZARDOUS"
            penalty += 45.0
            recs.append("Kritikus CO2 szint (2000+ ppm)! Válts szobát vagy végezz intenzív szellőztetést.")

        # Temperature evaluation (Ideal: 20-22 °C)
        if request.temperature_celsius > 24.5:
            penalty += 10.0
            recs.append(f"Túl meleg ({request.temperature_celsius}°C): Hűtsd a szobát 21-22°C-ra a dopamin csúcs fenntartásához.")
        elif request.temperature_celsius < 18.0:
            penalty += 5.0
            recs.append("Hűvös munkakörnyezet: Kéz- és testhőmérséklet emelése javasolt.")

        # Acoustic noise evaluation
        if request.noise_db > 65.0:
            penalty += 15.0
            recs.append(f"Zajos környezet ({request.noise_db} dB): Kapcsold be a Zen Barna Zaj szűrőt.")

        final_penalty = min(60.0, round(penalty, 1))

        return BiophilicAuditResponse(
            cognitive_penalty_percent=final_penalty,
            air_quality_status=co2_status,
            recommendations=recs or ["Környezeti feltételek optimálisak a mély fókuszhoz."],
        )
