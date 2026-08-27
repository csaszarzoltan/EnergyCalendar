"""Meeting cognitive tax and automatic decompression buffer engine."""
from __future__ import annotations

from typing import Dict, List
from src.models.market_circadian import MeetingTaxRequest, MeetingTaxResponse


class MeetingTaxService:
    """Calculates cognitive depletion from meetings and places recovery buffers."""

    @staticmethod
    def evaluate_meetings(request: MeetingTaxRequest) -> MeetingTaxResponse:
        """Compute drain score and insert 15-minute restorative buffers after meetings."""
        meetings = request.meetings
        if not meetings:
            return MeetingTaxResponse(
                total_meeting_minutes=0,
                cognitive_drain_score=0.0,
                decompression_buffers=[],
                advice="Nincsenek mai megbeszélések.",
            )

        total_min = sum(m.duration_minutes for m in meetings)
        interactive_count = sum(1 for m in meetings if m.is_interactive)

        # Drain score: 1 hour interactive meeting = ~30 points
        drain = (total_min / 60.0) * 25.0 + (interactive_count * 5.0)
        drain_score = min(100.0, round(drain, 1))

        buffers: List[Dict[str, str]] = []
        for m in meetings:
            parts = [int(p) for p in m.start_time.split(":")]
            end_m = parts[0] * 60 + parts[1] + m.duration_minutes
            buf_start = f"{end_m // 60:02d}:{end_m % 60:02d}"
            buf_end = f"{(end_m + 15) // 60:02d}:{(end_m + 15) % 60:02d}"
            buffers.append({
                "after_meeting": m.title,
                "buffer_window": f"{buf_start} - {buf_end}",
                "buffer_duration": "15 perc",
                "recommended_action": "Csendes séta vagy vízivás a kognitív feszültség feloldására.",
            })

        adv = f"Összesen {len(meetings)} megbeszélés ({total_min}m). Automatikus 15 perces levezető pufferek beszúrva."

        return MeetingTaxResponse(
            total_meeting_minutes=total_min,
            cognitive_drain_score=drain_score,
            decompression_buffers=buffers,
            advice=adv,
        )
