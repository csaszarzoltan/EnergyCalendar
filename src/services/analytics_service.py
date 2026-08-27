"""Circadian alignment scoring and cognitive ROI analytics."""
from __future__ import annotations

from src.models.advanced_circadian import (
    CircadianAnalyticsRequest,
    CircadianAnalyticsResponse,
)


class CircadianAnalyticsService:
    """Evaluates task execution fidelity against optimal biological peak hours."""

    @staticmethod
    def compute_analytics(request: CircadianAnalyticsRequest) -> CircadianAnalyticsResponse:
        """Calculate alignment score, deep work ratio, and energy ROI."""
        slots = request.scheduled_slots
        completed = set(request.completed_task_ids)

        if not slots:
            return CircadianAnalyticsResponse(
                alignment_score=100.0,
                deep_work_ratio=0.0,
                energy_roi_factor=1.0,
                completed_rate=100.0,
                summary="Nincs még ütemezett feladat.",
            )

        total_min = sum(s.duration for s in slots)
        deep_min = sum(s.duration for s in slots if s.cognitive_load.upper() == "DEEP_WORK")
        completed_count = sum(1 for s in slots if s.task_id in completed)

        deep_ratio = round(deep_min / max(1, total_min), 2)
        comp_rate = round((completed_count / len(slots)) * 100, 1)

        # Average energy rating when deep work was executed
        deep_energies = [s.assigned_energy_avg for s in slots if s.cognitive_load.upper() == "DEEP_WORK"]
        avg_energy = sum(deep_energies) / max(1, len(deep_energies)) if deep_energies else 7.5

        alignment_score = round(min(100.0, max(40.0, (avg_energy / 9.0) * 80 + (comp_rate * 0.2))), 1)
        roi_factor = round(max(1.0, (alignment_score / 50.0)), 2)

        summary_text = (
            f"Kiváló cirkadián összhang! Alignment Score: {alignment_score}%. "
            f"Kognitív hatékonyság szorzó: {roi_factor}x."
        )

        return CircadianAnalyticsResponse(
            alignment_score=alignment_score,
            deep_work_ratio=deep_ratio,
            energy_roi_factor=roi_factor,
            completed_rate=comp_rate,
            summary=summary_text,
        )
