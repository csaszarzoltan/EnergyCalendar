"""Context switching fragmentation tax and task batching service."""
from __future__ import annotations

from typing import List
from src.models.market_circadian import (
    ContextSwitchRequest,
    ContextSwitchResponse,
    ContextTaskItem,
)


class ContextSwitchService:
    """Calculates cognitive re-focusing penalties and groups tasks by cognitive category."""

    # Gloria Mark research: ~15-23 minutes cognitive recovery per divergent switch
    TAX_PER_SWITCH_MINUTES = 15

    @classmethod
    def analyze_switches(cls, request: ContextSwitchRequest) -> ContextSwitchResponse:
        """Count divergent load type switches and produce batched schedule."""
        tasks = request.tasks
        if not tasks:
            return ContextSwitchResponse(
                switch_count=0,
                fragmentation_tax_minutes=0,
                batched_tasks=[],
                optimization_gain_percent=0.0,
                advice="Nincs elemzendő feladat.",
            )

        switches = 0
        for i in range(1, len(tasks)):
            if tasks[i].load_type.lower() != tasks[i - 1].load_type.lower():
                switches += 1

        tax_min = switches * cls.TAX_PER_SWITCH_MINUTES

        # Batch by load_type: DEEP_WORK -> CREATIVE -> ADMIN -> RECOVERY
        order = {"deep_work": 1, "creative": 2, "admin": 3, "recovery": 4}
        batched = sorted(tasks, key=lambda t: order.get(t.load_type.lower(), 99))

        batched_switches = 0
        for i in range(1, len(batched)):
            if batched[i].load_type.lower() != batched[i - 1].load_type.lower():
                batched_switches += 1

        saved_min = max(0, (switches - batched_switches) * cls.TAX_PER_SWITCH_MINUTES)
        gain_pct = round((saved_min / max(1, tax_min)) * 100, 1) if tax_min > 0 else 0.0

        adv = f"A feladatok csoportosításával (Batching) {saved_min} perc fókuszvesztést spórolsz meg a nap folyamán!"

        return ContextSwitchResponse(
            switch_count=switches,
            fragmentation_tax_minutes=tax_min,
            batched_tasks=batched,
            optimization_gain_percent=gain_pct,
            advice=adv,
        )
