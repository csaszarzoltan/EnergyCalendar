"""Natural Language Task Parsing Service for circadian scheduling."""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

from src.models.energy import CognitiveLoad, TaskParseResponse


class TaskParser:
    """Parses free-text task inputs into structured CognitiveLoad, duration, and cost."""

    LOAD_MAPPINGS: Dict[CognitiveLoad, Tuple[List[str], float]] = {
        CognitiveLoad.DEEP_WORK: (
            [
                "kódolás",
                "kódolni",
                "tanulás",
                "tanulni",
                "architektúra",
                "fejlesztés",
                "fejleszteni",
                "írás",
                "írni",
                "tervezés",
                "tervezni",
                "coding",
                "code",
                "study",
                "deep work",
                "refactor",
                "refactoring",
                "programozás",
                "architecture",
                "development",
            ],
            8.5,
        ),
        CognitiveLoad.CREATIVE: (
            [
                "ötletelés",
                "brainstorm",
                "brainstorming",
                "design",
                "vázlat",
                "ui",
                "ux",
                "koncepció",
                "kreatív",
                "creative",
                "rajzolás",
                "wireframe",
                "prototype",
            ],
            6.0,
        ),
        CognitiveLoad.ADMIN: (
            [
                "e-mail",
                "email",
                "emails",
                "számla",
                "számlák",
                "rendszerezés",
                "hívás",
                "admin",
                "takarítás",
                "meeting",
                "egyeztetés",
                "értekezlet",
                "megbeszélés",
                "konferencia",
                "sync",
                "call",
                "standup",
                "invoice",
                "invoicing",
            ],
            3.0,
        ),
        CognitiveLoad.RECOVERY: (
            [
                "séta",
                "edzés",
                "ebéd",
                "kávé",
                "kávézás",
                "pihenő",
                "szünet",
                "meditáció",
                "walk",
                "break",
                "gym",
                "rest",
                "lunch",
                "coffee",
                "meditation",
                "workout",
            ],
            -3.0,
        ),
    }

    @classmethod
    def _extract_duration_minutes(cls, text: str) -> int:
        """Extract task duration in minutes using regex patterns."""
        text_lower = text.lower()
        hours = 0.0
        minutes = 0
        matched = False

        # Match hour expressions (e.g. '1.5 óra', '2 ó', '1h', '2 hours')
        h_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:ó|óra|h|hour|hours)\b", text_lower)
        if h_match:
            try:
                hours = float(h_match.group(1).replace(",", "."))
                matched = True
            except ValueError:
                pass

        # Match minute expressions (e.g. '90 perc', '45m', '30min', '15 mins')
        m_match = re.search(r"(\d+)\s*(?:perc|m|min|mins|minute|minutes)\b", text_lower)
        if m_match:
            try:
                minutes = int(m_match.group(1))
                matched = True
            except ValueError:
                pass

        if matched:
            total = int(hours * 60 + minutes)
            return max(5, min(720, total))

        return 45  # Default duration when unstated

    @classmethod
    def _match_keyword(cls, keyword: str, text: str) -> bool:
        """Check if a keyword matches inside text, using boundary checks for short words."""
        kw_lower = keyword.lower()
        text_lower = text.lower()

        if len(kw_lower) <= 3:
            pattern = rf"\b{re.escape(kw_lower)}\b"
            return bool(re.search(pattern, text_lower))

        return kw_lower in text_lower

    @classmethod
    def parse_task(cls, raw_text: str) -> TaskParseResponse:
        """Parse natural language task string into TaskParseResponse."""
        cleaned_text = raw_text.strip()
        duration = cls._extract_duration_minutes(cleaned_text)

        matched_load: CognitiveLoad = CognitiveLoad.DEEP_WORK
        matched_cost: float = 8.5
        confidence = 0.5

        # Check each cognitive category in order
        for load_type, (keywords, cost) in cls.LOAD_MAPPINGS.items():
            for kw in keywords:
                if cls._match_keyword(kw, cleaned_text):
                    matched_load = load_type
                    matched_cost = cost
                    confidence = 0.95
                    break
            if confidence > 0.5:
                break

        return TaskParseResponse(
            title=cleaned_text,
            duration_minutes=duration,
            load_type=matched_load,
            energy_cost=matched_cost,
            confidence=confidence,
        )
