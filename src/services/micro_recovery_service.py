"""Ocular and somatic micro-recovery generator (20-20-20 & Physiological Sigh)."""
from __future__ import annotations

from typing import List
from src.models.advanced_circadian import (
    MicroBreak,
    MicroRecoveryRequest,
    MicroRecoveryResponse,
)


class MicroRecoveryService:
    """Generates structured micro-breaks to reset parasympathetic nervous system."""

    @staticmethod
    def plan_recovery(request: MicroRecoveryRequest) -> MicroRecoveryResponse:
        """Generate micro-break schedule based on screen minutes."""
        breaks: List[MicroBreak] = []
        minutes = request.continuous_screen_minutes

        for t in range(20, minutes + 1, 20):
            if t % 60 == 0:
                breaks.append(
                    MicroBreak(
                        name="Fiziológiás Sóhaj & Nyújtás",
                        trigger_at_minute=t,
                        duration_seconds=60,
                        action="Végezz 3 mély dupla belégzést orron át, majd hosszú lassú kilégzést szájon át.",
                    )
                )
            else:
                breaks.append(
                    MicroBreak(
                        name="20-20-20 Szemtorna",
                        trigger_at_minute=t,
                        duration_seconds=20,
                        action="Nézz el legalább 6 méter (20 láb) távolságba 20 másodpercig.",
                    )
                )

        sigh_info = "Fiziológiás sóhaj (Huberman Lab): 2 gyors belégzés orron át (második a tüdőcsúcs kitágítására) + 1 hosszú sóhaj kilégzés."
        eye_info = "20-20-20 szabály: 20 percenként nézz 20 láb (6m) távolra 20 másodpercig a szemizmok ellazítására."

        return MicroRecoveryResponse(
            micro_breaks=breaks,
            physiological_sigh_instructions=sigh_info,
            eye_reset_202020=eye_info,
        )
