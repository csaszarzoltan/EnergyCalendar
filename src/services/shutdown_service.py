"""Circadian daily shutdown and sleep protection service."""
from __future__ import annotations

from datetime import datetime
from typing import List

from src.models.energy import (
    CognitiveLoad,
    ShutdownSummaryRequest,
    ShutdownSummaryResponse,
)
from src.services.energy_calculator import minutes_to_time, time_to_minutes


class ShutdownService:
    """Computes daily shutdown metrics, melatonin countdown, and transition advice."""

    @classmethod
    def create_summary(cls, request: ShutdownSummaryRequest) -> ShutdownSummaryResponse:
        """Calculate shutdown statistics and melatonin gate guidance.

        Args:
            request: The shutdown summary request payload.

        Returns:
            ShutdownSummaryResponse with accomplishment stats and recommendations.
        """
        completed_count = len(request.completed_tasks)
        pending_count = len(request.pending_tasks)

        # Calculate completed deep work minutes
        total_deep_work_minutes = sum(
            t.duration_minutes
            for t in request.completed_tasks
            if t.load_type == CognitiveLoad.DEEP_WORK
        )

        # Calculate energy debt averted by completing demanding tasks on schedule
        debt_averted_sum = sum(
            t.energy_cost for t in request.completed_tasks if t.energy_cost > 0
        )
        energy_debt_averted = float(round(debt_averted_sum, 1))

        # Melatonin gate is 60 minutes before bedtime
        sleep_min = time_to_minutes(request.profile.sleep_time)
        melatonin_gate_min = (sleep_min - 60) % 1440
        melatonin_gate_time = minutes_to_time(melatonin_gate_min)

        # Current time resolution
        cur_time_str = request.current_time or datetime.now().strftime("%H:%M")
        cur_min = time_to_minutes(cur_time_str)

        # Distance to melatonin gate handling circular day transition
        diff = melatonin_gate_min - cur_min
        if diff < -720:
            diff += 1440
        elif diff > 720:
            diff -= 1440
        minutes_until_melatonin = diff

        tomorrow_first_peak = (
            request.profile.peak_hours[0].start
            if request.profile.peak_hours
            else "09:00"
        )

        # Shutdown recommended when within 60 minutes of melatonin gate or past it
        is_shutdown_recommended_now = minutes_until_melatonin <= 60

        recommendations: List[str] = []

        # 1. Accomplishment summary
        if total_deep_work_minutes > 0:
            recommendations.append(
                f"Kiváló munka! Ma {total_deep_work_minutes} perc mélyfókuszú (Deep Work) feladatot teljesítettél."
            )
        else:
            recommendations.append(
                f"Ma {completed_count} db feladatot zártál le sikeresen."
            )

        # 2. Melatonin gate & sleep hygiene
        if minutes_until_melatonin > 0:
            recommendations.append(
                f"Melatonin Kapu {melatonin_gate_time}-kor nyílik ({minutes_until_melatonin} perc múlva). "
                "Csökkentsd a kék fényt és válts passzív regenerációra."
            )
        else:
            recommendations.append(
                f"A Melatonin Kapu ({melatonin_gate_time}) már elérkezett! "
                "Azonnal zárd le a munkát a cirkadián ritmus és az éjszakai regeneráció védelmében."
            )

        # 3. Pending task handling for tomorrow
        if pending_count > 0:
            recommendations.append(
                f"{pending_count} db nyitott feladat maradt. Javasoljuk ezek áthelyezését "
                f"a holnapi első fókuszcsúcsra ({tomorrow_first_peak})."
            )
        else:
            recommendations.append(
                f"Minden feladat elvégezve! Holnap tiszta fejjel kezded a napot az első csúcsban ({tomorrow_first_peak})."
            )

        return ShutdownSummaryResponse(
            completed_count=completed_count,
            pending_count=pending_count,
            total_deep_work_minutes=total_deep_work_minutes,
            energy_debt_averted=energy_debt_averted,
            melatonin_gate_time=melatonin_gate_time,
            minutes_until_melatonin=minutes_until_melatonin,
            tomorrow_first_peak=tomorrow_first_peak,
            recommendations=recommendations,
            is_shutdown_recommended_now=is_shutdown_recommended_now,
        )
