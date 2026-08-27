"""Dopamine friction and distraction shielding service."""
from __future__ import annotations

from src.models.market_circadian import DopamineGuardRequest, DopamineGuardResponse


class DopamineGuardService:
    """Generates friction barriers for social media and task fragmentation during peak focus."""

    @staticmethod
    def create_guard(request: DopamineGuardRequest) -> DopamineGuardResponse:
        """Define digital blocking perimeter and mindful interruption prompts."""
        cats = ["Social Media", "Video Streaming", "News Portals", "E-commerce"]
        if request.friction_level == "STRICT":
            cats.extend(["Email Notifiers", "Messaging Apps"])

        prompts = [
            "Állj meg 3 másodpercre: Valóban szükséges ez a feladatváltás a jelenlegi mélymunka blokkban?",
            "Figyelem: A dopamin-kereső impulzus 15 perces visszarázódási adósságot generál.",
            "Tarts egy lassú fiziológiás sóhajt mielőtt megnyitnád a böngésző új fülét.",
        ]

        return DopamineGuardResponse(
            active_window=f"{request.peak_start} - {request.peak_end}",
            blocked_categories=cats,
            friction_prompts=prompts,
        )
