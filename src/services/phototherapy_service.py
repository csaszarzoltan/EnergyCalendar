"""Phototherapy and circadian light exposure protocol service."""
from __future__ import annotations

from src.models.advanced_circadian import PhototherapyRequest, PhototherapyResponse


class PhototherapyService:
    """Generates lux timing to optimize morning cortisol awakening and evening melatonin."""

    @staticmethod
    def generate_plan(request: PhototherapyRequest) -> PhototherapyResponse:
        """Create timed light schedule based on wake/sleep times."""
        w_parts = [int(p) for p in request.wake_time.split(":")]
        wake_min = w_parts[0] * 60 + w_parts[1]

        s_parts = [int(p) for p in request.sleep_time.split(":")]
        sleep_min = s_parts[0] * 60 + s_parts[1]

        morn_start = f"{wake_min // 60:02d}:{wake_min % 60:02d}"
        morn_end = f"{(wake_min + 45) // 60:02d}:{(wake_min + 45) % 60:02d}"

        mid_start = f"{(wake_min + 300) // 60:02d}:{(wake_min + 300) % 60:02d}"
        mid_end = f"{(wake_min + 330) // 60:02d}:{(wake_min + 330) % 60:02d}"

        blue_min = (sleep_min - 120) % 1440
        blue_str = f"{blue_min // 60:02d}:{blue_min % 60:02d}"

        tips = [
            f"Ébredés után azonnal menj ki a természetes fényre 15-30 percre ({morn_start} - {morn_end}).",
            "Délben végezz 10 perc fénysétát a cirkadián fázis rögzítéséhez.",
            f"{blue_str}-tól kapcsold be a meleg színhőmérsékletet / kékfény szűrőt.",
        ]

        return PhototherapyResponse(
            morning_light_window=f"{morn_start} - {morn_end}",
            midday_sun_window=f"{mid_start} - {mid_end}",
            evening_blueblocker_time=blue_str,
            protocol_tips=tips,
        )
