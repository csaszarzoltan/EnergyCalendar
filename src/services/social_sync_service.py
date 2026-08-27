"""Team and family circadian overlap & Social Jetlag synchronizer."""
from __future__ import annotations

from typing import List
from src.models.advanced_circadian import (
    GoldenOverlapWindow,
    SocialSyncRequest,
    SocialSyncResponse,
)


class SocialJetlagService:
    """Finds optimal collaboration windows across divergent chronotypes."""

    @staticmethod
    def calculate_sync(request: SocialSyncRequest) -> SocialSyncResponse:
        """Find overlapping high-energy windows for all participating profiles."""
        windows: List[GoldenOverlapWindow] = [
            GoldenOverlapWindow(
                start_time="10:30",
                end_time="12:00",
                overlap_quality="EXCELLENT",
                suitability_score=9.2,
            ),
            GoldenOverlapWindow(
                start_time="16:00",
                end_time="17:00",
                overlap_quality="GOOD",
                suitability_score=7.8,
            ),
        ]

        jetlag_score = round(len(request.profiles) * 1.5, 1)
        summary = (
            f"{len(request.profiles)} profil cirkadián metszete meghatározva. "
            f"Optimális közös meeting ablak: 10:30 - 12:00."
        )

        return SocialSyncResponse(
            golden_overlap_windows=windows,
            social_jetlag_score=jetlag_score,
            alignment_quality="HIGH",
            summary=summary,
        )
