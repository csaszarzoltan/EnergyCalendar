"""Calendar synchronization service for RFC 5545 iCalendar (.ics) export and import."""
from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from src.models.energy import CognitiveLoad, ScheduledSlot, Task
from src.services.energy_calculator import time_to_minutes
from src.services.nlp_parser import TaskParser


class CalendarSyncService:
    """Handles RFC 5545 iCalendar (.ics) export and import with cognitive metadata."""

    LOAD_PREFIXES: Dict[CognitiveLoad, str] = {
        CognitiveLoad.DEEP_WORK: "[🧠 Deep Work]",
        CognitiveLoad.CREATIVE: "[💡 Creative]",
        CognitiveLoad.ADMIN: "[📋 Admin]",
        CognitiveLoad.RECOVERY: "[🔋 Regeneráció]",
    }

    PREFIX_TO_LOAD: Dict[str, Tuple[CognitiveLoad, float]] = {
        "deep work": (CognitiveLoad.DEEP_WORK, 8.5),
        "mélymunka": (CognitiveLoad.DEEP_WORK, 8.5),
        "creative": (CognitiveLoad.CREATIVE, 6.0),
        "kreatív": (CognitiveLoad.CREATIVE, 6.0),
        "admin": (CognitiveLoad.ADMIN, 3.0),
        "regeneráció": (CognitiveLoad.RECOVERY, -3.0),
        "recovery": (CognitiveLoad.RECOVERY, -3.0),
    }

    @classmethod
    def export_to_ics(
        cls,
        slots: List[ScheduledSlot],
        calendar_name: str = "Cirkadián Energia Naptár",
    ) -> str:
        """Generate a valid RFC 5545 VCALENDAR string from scheduled slots.

        Args:
            slots: List of scheduled task slots.
            calendar_name: Name of the exported calendar.

        Returns:
            RFC 5545 compliant text/calendar string.
        """
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//EnergyCalendar//Circadian Choreographer//HU",
            "CALSCALE:GREGORIAN",
            f"X-WR-CALNAME:{calendar_name}",
        ]

        now_dt = datetime.now(timezone.utc)
        today_str = now_dt.strftime("%Y%m%d")
        dtstamp = f"{today_str}T000000Z"

        for slot in slots:
            prefix = cls.LOAD_PREFIXES.get(slot.load_type, "[⚡ Feladat]")
            summary = slot.title if slot.title.startswith("[") else f"{prefix} {slot.title}"

            s_parts = slot.start_time.split(":")
            e_parts = slot.end_time.split(":")
            dtstart = f"{today_str}T{int(s_parts[0]):02d}{int(s_parts[1]):02d}00Z"
            dtend = f"{today_str}T{int(e_parts[0]):02d}{int(e_parts[1]):02d}00Z"
            uid = f"{slot.task_id}@{today_str}.energycalendar.app"
            desc = (
                f"Kognitív típus: {slot.load_type.value} | "
                f"Költség: {slot.energy_cost} | "
                f"Átlagos energiaszint: {slot.average_energy_level:.1f}"
            )

            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{dtstamp}",
                f"DTSTART:{dtstart}",
                f"DTEND:{dtend}",
                f"SUMMARY:{summary}",
                f"DESCRIPTION:{desc}",
                "END:VEVENT",
            ])

        lines.append("END:VCALENDAR")
        return "\r\n".join(lines) + "\r\n"

    @classmethod
    def _parse_time_str(cls, raw: str) -> Optional[Tuple[int, int]]:
        """Extract hour and minute (HH, MM) from RFC 5545 timestamp or time string."""
        clean = raw.strip()
        # Case 1: Has 'T' (e.g. 20260826T100000Z or 20260826T100000)
        if "T" in clean:
            time_part = clean.split("T")[1]
            digits = re.sub(r"\D", "", time_part)
            if len(digits) >= 4:
                h, m = int(digits[0:2]), int(digits[2:4])
                return h % 24, m % 60
        # Case 2: Colon separated (e.g. 10:00 or 10:00:00)
        if ":" in clean:
            parts = clean.split(":")
            try:
                h, m = int(re.sub(r"\D", "", parts[0])), int(re.sub(r"\D", "", parts[1]))
                return h % 24, m % 60
            except ValueError:
                pass
        # Case 3: Pure digits 4-6 chars (e.g. 1000 or 100000)
        digits = re.sub(r"\D", "", clean)
        if len(digits) >= 4:
            h, m = int(digits[0:2]), int(digits[2:4])
            return h % 24, m % 60
        return None

    @classmethod
    def _detect_cognitive_load(cls, summary: str) -> Tuple[str, CognitiveLoad, float]:
        """Detect cognitive load from bracketed prefix or NLP parsing.

        Returns:
            Tuple of (cleaned_title, CognitiveLoad, energy_cost).
        """
        # Check bracketed prefixes like [🧠 Deep Work] or [Deep Work]
        prefix_match = re.match(r"^\[(.*?)\]\s*(.*)$", summary)
        if prefix_match:
            tag_content = prefix_match.group(1).strip().lower()
            remaining_title = prefix_match.group(2).strip()
            for key, (c_load, cost) in cls.PREFIX_TO_LOAD.items():
                if key in tag_content:
                    return remaining_title or summary, c_load, cost

        # Fallback to TaskParser NLP
        parsed = TaskParser.parse_task(summary)
        if parsed.confidence > 0.6:
            return parsed.title, parsed.load_type, parsed.energy_cost

        # Default calendar import to ADMIN meetings
        return summary, CognitiveLoad.ADMIN, 3.0

    @classmethod
    def import_from_ics(cls, ics_text: str) -> List[Task]:
        """Parse raw iCalendar text and return fixed Task objects.

        Args:
            ics_text: RFC 5545 formatted iCalendar string.

        Returns:
            List of Task instances with is_fixed=True and fixed_start set.
        """
        if not ics_text or not ics_text.strip():
            return []

        # Unfold wrapped lines (RFC 5545: CRLF + single whitespace/tab)
        unfolded = re.sub(r"\r?\n[ \t]", "", ics_text)

        # Extract VEVENT blocks
        event_blocks = re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", unfolded, flags=re.DOTALL | re.IGNORECASE)
        tasks: List[Task] = []

        for block in event_blocks:
            summary = "Névtelen Naptáresemény"
            start_hh_mm = "09:00"
            end_hh_mm = "10:00"
            has_explicit_end = False

            lines = block.splitlines()
            for line in lines:
                line_str = line.strip()
                if not line_str or ":" not in line_str:
                    continue

                prop, _, val = line_str.partition(":")
                prop_key = prop.split(";")[0].strip().upper()
                val_clean = val.strip()

                if prop_key == "SUMMARY":
                    # Unescape RFC 5545 text escapes
                    summary = (
                        val_clean.replace("\\,", ",")
                        .replace("\\;", ";")
                        .replace("\\\\", "\\")
                        .replace("\\n", " ")
                    )
                elif prop_key == "DTSTART":
                    parsed_time = cls._parse_time_str(val_clean)
                    if parsed_time:
                        start_hh_mm = f"{parsed_time[0]:02d}:{parsed_time[1]:02d}"
                elif prop_key == "DTEND":
                    parsed_time = cls._parse_time_str(val_clean)
                    if parsed_time:
                        end_hh_mm = f"{parsed_time[0]:02d}:{parsed_time[1]:02d}"
                        has_explicit_end = True

            start_min = time_to_minutes(start_hh_mm)
            if has_explicit_end:
                end_min = time_to_minutes(end_hh_mm)
                duration = (end_min - start_min) % 1440
                if duration <= 0:
                    duration = 60
            else:
                duration = 60

            title, load_type, energy_cost = cls._detect_cognitive_load(summary)

            tasks.append(
                Task(
                    id=str(uuid4()),
                    title=title,
                    duration_minutes=duration,
                    load_type=load_type,
                    energy_cost=energy_cost,
                    is_fixed=True,
                    fixed_start=start_hh_mm,
                )
            )

        return tasks
