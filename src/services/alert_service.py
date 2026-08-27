"""Real-time circadian and fatigue alert management service."""
from __future__ import annotations

from typing import List
from src.models.advanced_circadian import AlertQueryRequest, AlertQueryResponse, CircadianAlert


class CircadianAlertService:
    """Evaluates time thresholds for caffeine cutoff, melatonin gate, and continuous strain."""

    @staticmethod
    def get_alerts(request: AlertQueryRequest) -> AlertQueryResponse:
        """Check active circadian conditions and return warning list."""
        alerts: List[CircadianAlert] = []
        cur_parts = [int(p) for p in request.current_time.split(":")]
        cur_min = cur_parts[0] * 60 + cur_parts[1]

        # Check continuous deep work strain
        if request.active_deep_work_minutes >= 120:
            alerts.append(
                CircadianAlert(
                    alert_type="FATIGUE_WARNING",
                    severity="WARNING",
                    message=f"Folyamatos mélymunka elérte a {request.active_deep_work_minutes} percet!",
                    action_prompt="Tarts 20 perc aktív regenerációs szünetet (séta vagy légzés).",
                )
            )

        # Parse sleep time for caffeine cutoff (sleep - 9h)
        sleep_str = request.profile.get("sleep_time", "23:00")
        sleep_parts = [int(p) for p in sleep_str.split(":")]
        sleep_min = sleep_parts[0] * 60 + sleep_parts[1]
        caff_cutoff_min = (sleep_min - 540) % 1440

        if cur_min >= caff_cutoff_min and cur_min < sleep_min:
            alerts.append(
                CircadianAlert(
                    alert_type="CAFFEINE_CUTOFF",
                    severity="WARNING",
                    message="A koffein cutoff időablak lezárult! További koffein rontja a mélyalvást.",
                    action_prompt="Válts vízre vagy koffeinmentes teára.",
                )
            )

        # Melatonin gate (sleep - 1h)
        melatonin_min = (sleep_min - 60) % 1440
        if cur_min >= melatonin_min and cur_min < sleep_min:
            alerts.append(
                CircadianAlert(
                    alert_type="MELATONIN_GATE",
                    severity="INFO",
                    message="Közeledik a Melatonin Kapu! Kapcsold be a kékfény szűrőt.",
                    action_prompt="Csökkentsd a képernyőfényt és kezd el a lezárási rituálét.",
                )
            )

        countdown = max(0, melatonin_min - cur_min) if cur_min < melatonin_min else 0
        milestone = "Melatonin Kapu nyitás" if countdown > 0 else "Alvási fázis"

        return AlertQueryResponse(
            active_alerts=alerts,
            next_milestone=milestone,
            countdown_minutes=countdown,
        )
