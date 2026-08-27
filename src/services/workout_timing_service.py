"""Circadian exercise timing and physical hormesis optimizer."""
from __future__ import annotations

from src.models.market_circadian import (
    WorkoutTimingRequest,
    WorkoutTimingResponse,
    WorkoutType,
)


class WorkoutTimingService:
    """Identifies optimal biological windows for strength, endurance, and sleep safety."""

    @staticmethod
    def calculate_window(request: WorkoutTimingRequest) -> WorkoutTimingResponse:
        """Determine training window based on core body temperature and circadian hormones."""
        w_parts = [int(p) for p in request.wake_time.split(":")]
        wake_min = w_parts[0] * 60 + w_parts[1]
        s_parts = [int(p) for p in request.sleep_time.split(":")]
        sleep_min = s_parts[0] * 60 + s_parts[1]

        # Sleep protection cutoff: 3 hours before bed
        cutoff_min = (sleep_min - 180) % 1440
        cutoff_str = f"{cutoff_min // 60:02d}:{cutoff_min % 60:02d}"

        w_type = request.workout_type
        if w_type == WorkoutType.CARDIO_FAT_BURN:
            start_min = (wake_min + 30) % 1440
            end_min = (wake_min + 120) % 1440
            rationale = "Reggeli éhgyomri kardió: optimális kortizol zsírmobilizáció és fázissietetés."
        elif w_type == WorkoutType.STRENGTH_HYPERTROPHY:
            start_min = (wake_min + 540) % 1440  # +9h (e.g. 16:30)
            end_min = (wake_min + 690) % 1440   # +11.5h (e.g. 18:30)
            rationale = "Késő délutáni erőedzés: testhőmérséklet csúcs, maximális izomerő és ízületi rugalmasság."
        elif w_type == WorkoutType.HIIT_ANAEROBIC:
            start_min = (wake_min + 360) % 1440  # +6h
            end_min = (wake_min + 480) % 1440
            rationale = "Kora délutáni anaerob terhelés a kaja-kóma lezárása után."
        else:
            start_min = (sleep_min - 240) % 1440
            end_min = (sleep_min - 180) % 1440
            rationale = "Esti nyújtás és mobilitás: paraszimpatikus aktiválás a melatonin termeléshez."

        start_str = f"{start_min // 60:02d}:{start_min % 60:02d}"
        end_str = f"{end_min // 60:02d}:{end_min % 60:02d}"

        return WorkoutTimingResponse(
            optimal_window_start=start_str,
            optimal_window_end=end_str,
            biological_rationale=rationale,
            sleep_protection_cutoff=cutoff_str,
        )
