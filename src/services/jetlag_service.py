"""Circadian timezone travel and jetlag adaptation engine."""
from __future__ import annotations

from typing import List
from src.models.market_circadian import (
    JetlagDayProtocol,
    JetlagRequest,
    JetlagResponse,
)


class JetlagChronoService:
    """Calculates phase-advance or phase-delay protocols for circadian jetlag shifts."""

    @staticmethod
    def calculate_adaptation(request: JetlagRequest) -> JetlagResponse:
        """Create day-by-day 60-90m phase shift schedule with timed phototherapy."""
        diff = request.target_utc_offset - request.origin_utc_offset
        abs_diff = abs(diff)
        # Circadian adaptation rate: ~1 hour per day
        days_needed = max(1, abs_diff)

        protocols: List[JetlagDayProtocol] = []
        is_eastward = diff > 0  # Phase advance (harder)

        base_wake = 7 * 60
        base_sleep = 23 * 60

        for d in range(1, days_needed + 1):
            shift_min = min(abs_diff * 60, d * 60)
            if is_eastward:
                cur_wake = (base_wake - shift_min) % 1440
                cur_sleep = (base_sleep - shift_min) % 1440
                light_act = "Reggel azonnal keress intenzív természetes fényt (10,000 Lux) a fázis siettetéséhez."
                mela_act = "Este 30 perccel az új lefekvési idő előtt vegyél be 0.5mg melatonint és zárd ki a fényt."
            else:
                cur_wake = (base_wake + shift_min) % 1440
                cur_sleep = (base_sleep + shift_min) % 1440
                light_act = "Késő délután tartózkodj a napfényben a cirkadián fázis késleltetéséhez."
                mela_act = "Reggeli ébredéskor viselj napszemüveget, ha túl korán ébredsz."

            protocols.append(
                JetlagDayProtocol(
                    day_number=d,
                    shifted_wake_time=f"{cur_wake // 60:02d}:{cur_wake % 60:02d}",
                    shifted_sleep_time=f"{cur_sleep // 60:02d}:{cur_sleep % 60:02d}",
                    morning_light_action=light_act,
                    evening_melatonin_action=mela_act,
                )
            )

        direction = "keleti (fázissietés)" if is_eastward else "nyugati (fáziskésleltetés)"
        guidance = f"{abs_diff} órás {direction} időzóna-ugrás. A teljes biológiai akklimatizációhoz {days_needed} nap szükséges."

        return JetlagResponse(
            hour_difference=diff,
            days_to_adapt=days_needed,
            protocols=protocols,
            guidance=guidance,
        )
