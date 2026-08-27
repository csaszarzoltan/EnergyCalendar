"""Kleitman BRAC 90/20 ultradian cycle engine."""
from __future__ import annotations

from typing import List
from src.models.advanced_circadian import (
    UltradianBlock,
    UltradianSplitRequest,
    UltradianSplitResponse,
)


class UltradianEngineService:
    """Decomposes long cognitive projects into biological 90m Rest-Activity cycles."""

    @staticmethod
    def split_task(request: UltradianSplitRequest) -> UltradianSplitResponse:
        """Split duration into 90m focus blocks interleaved with 20m restorative breaks."""
        blocks: List[UltradianBlock] = []
        cycle_len = request.brac_cycle_minutes
        break_len = request.break_minutes
        remaining = request.duration_minutes
        idx = 1

        while remaining > 0:
            focus_time = min(remaining, cycle_len)
            blocks.append(
                UltradianBlock(
                    block_index=idx,
                    block_type="FOCUS",
                    title=f"{request.task_title} — {idx}. Fókusz Ciklus",
                    duration_minutes=focus_time,
                    suggested_focus_level="HIGH_ALPHA_BETA",
                )
            )
            remaining -= focus_time
            idx += 1

            if remaining > 0:
                blocks.append(
                    UltradianBlock(
                        block_index=idx,
                        block_type="BRAC_RECOVERY",
                        title=f"Ultradián BRAC Regeneráció ({break_len}m)",
                        duration_minutes=break_len,
                        suggested_focus_level="RESTORATIVE_THETA",
                    )
                )
                idx += 1

        total_cycles = max(1, len([b for b in blocks if b.block_type == "FOCUS"]))
        total_time = sum(b.duration_minutes for b in blocks)
        adv = f"A feladat sikeresen {total_cycles} ultradián fázisra lett bontva a csúcs fókusz megtartásához."

        return UltradianSplitResponse(
            blocks=blocks,
            total_cycles=total_cycles,
            total_duration=total_time,
            advice=adv,
        )
