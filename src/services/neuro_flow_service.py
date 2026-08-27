"""ADHD time-blindness protection and neurodivergent pacing service."""
from __future__ import annotations

from typing import List
from src.models.market_circadian import NeuroFlowRequest, NeuroFlowResponse


class NeuroFlowService:
    """Provides gentle decompression and anti-hyperfocus crash protocols."""

    @staticmethod
    def create_pacing(request: NeuroFlowRequest) -> NeuroFlowResponse:
        """Calculate transition padding and checkpoints to avoid cognitive burnout."""
        dur = request.duration_minutes
        # Gentle transition: 5-15 min depending on duration
        transition_min = 10 if dur >= 60 else 5
        checkpoints: List[str] = []

        interval = 30 if dur <= 90 else 45
        for t in range(interval, dur, interval):
            checkpoints.append(f"{t}. perc: Vizuális állapotellenőrzés & testtartás korrekció")

        hydration_count = max(1, dur // 45)

        strat = (
            f"Lágy levezető szakasz ({transition_min}m) beállítva a feladat végére, "
            "hogy megelőzzük a hirtelen kognitív kimerülést és az ADHD hiperfókusz összeomlást."
        )

        return NeuroFlowResponse(
            gentle_transition_minutes=transition_min,
            pacing_checkpoints=checkpoints,
            hydration_breaks=hydration_count,
            flow_strategy=strat,
        )
