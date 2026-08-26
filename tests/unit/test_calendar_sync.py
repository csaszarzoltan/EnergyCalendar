"""Unit tests for CalendarSyncService (RFC 5545 iCalendar Export and Import)."""
from __future__ import annotations

import pytest

from src.models.energy import CognitiveLoad, ScheduledSlot, Task
from src.services.calendar_sync import CalendarSyncService


def test_export_to_ics_format():
    """Verify that export_to_ics produces valid RFC 5545 calendar with proper VEVENTs and cognitive tags."""
    slots = [
        ScheduledSlot(
            task_id="task-1",
            title="Architektúra tervezés",
            start_time="09:00",
            end_time="10:30",
            duration_minutes=90,
            load_type=CognitiveLoad.DEEP_WORK,
            energy_cost=9.0,
            average_energy_level=8.8,
        ),
        ScheduledSlot(
            task_id="task-2",
            title="Regenerációs pihenő",
            start_time="10:30",
            end_time="11:00",
            duration_minutes=30,
            load_type=CognitiveLoad.RECOVERY,
            energy_cost=-3.0,
            average_energy_level=7.5,
        ),
    ]

    ics_result = CalendarSyncService.export_to_ics(slots, calendar_name="Teszt Naptár")
    assert "BEGIN:VCALENDAR" in ics_result
    assert "END:VCALENDAR" in ics_result
    assert "X-WR-CALNAME:Teszt Naptár" in ics_result
    assert "BEGIN:VEVENT" in ics_result
    assert "END:VEVENT" in ics_result
    assert "SUMMARY:[🧠 Deep Work] Architektúra tervezés" in ics_result
    assert "SUMMARY:[🔋 Regeneráció] Regenerációs pihenő" in ics_result
    assert "090000Z" in ics_result
    assert "103000Z" in ics_result
    assert "UID:task-1@" in ics_result


def test_import_from_ics_parses_events():
    """Verify that import_from_ics parses VEVENT blocks and converts them into fixed Tasks."""
    sample_ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Google Inc//Google Calendar 70.9054//EN
BEGIN:VEVENT
UID:event-101@google.com
SUMMARY:Heti Sprint Értekezlet
DTSTART:20260826T140000Z
DTEND:20260826T153000Z
DESCRIPTION:Heti státusz megbeszélés
END:VEVENT
BEGIN:VEVENT
UID:event-102@google.com
SUMMARY:[🧠 Deep Work] Algoritmus optimalizáció
DTSTART:20260826T160000Z
DTEND:20260826T170000Z
END:VEVENT
END:VCALENDAR"""

    tasks = CalendarSyncService.import_from_ics(sample_ics)
    assert len(tasks) == 2

    # Task 1
    t1 = tasks[0]
    assert "Heti Sprint Értekezlet" in t1.title
    assert t1.is_fixed is True
    assert t1.fixed_start == "14:00"
    assert t1.duration_minutes == 90
    assert t1.load_type == CognitiveLoad.ADMIN

    # Task 2 with prefix recognition
    t2 = tasks[1]
    assert t2.title == "Algoritmus optimalizáció"
    assert t2.is_fixed is True
    assert t2.fixed_start == "16:00"
    assert t2.duration_minutes == 60
    assert t2.load_type == CognitiveLoad.DEEP_WORK


def test_import_from_ics_empty_or_malformed():
    """Verify safe fallback for empty or eventless ICS text."""
    assert CalendarSyncService.import_from_ics("") == []
    assert CalendarSyncService.import_from_ics("   ") == []
    assert CalendarSyncService.import_from_ics("BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR") == []


def test_import_from_ics_with_escaped_characters():
    """Verify unescaping of commas, semicolons, and newlines."""
    ics_text = """BEGIN:VCALENDAR
BEGIN:VEVENT
SUMMARY:Projekt egyeztetés\\, Q3 roadmap és tervek
DTSTART:20260826T110000Z
DTEND:20260826T120000Z
END:VEVENT
END:VCALENDAR"""
    tasks = CalendarSyncService.import_from_ics(ics_text)
    assert len(tasks) == 1
    assert "Projekt egyeztetés, Q3 roadmap és tervek" in tasks[0].title
