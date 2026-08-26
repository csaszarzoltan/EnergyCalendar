"""Unit tests for NLP task parser service."""
from __future__ import annotations

import pytest

from src.models.energy import CognitiveLoad
from src.services.nlp_parser import TaskParser


def test_nlp_parse_hungarian_keywords():
    """Correctly parses 'Kódolás 90 perc' into DEEP_WORK and duration 90."""
    result = TaskParser.parse_task("Kódolás 90 perc")
    assert result.load_type == CognitiveLoad.DEEP_WORK
    assert result.duration_minutes == 90
    assert result.energy_cost == 8.5
    assert result.confidence >= 0.9


def test_nlp_parse_creative_keywords():
    """Parses creative tasks in Hungarian and English."""
    res1 = TaskParser.parse_task("UI design és vázlat készítés 60 perc")
    assert res1.load_type == CognitiveLoad.CREATIVE
    assert res1.duration_minutes == 60
    assert res1.energy_cost == 6.0

    res2 = TaskParser.parse_task("Brainstorming session 1.5 óra")
    assert res2.load_type == CognitiveLoad.CREATIVE
    assert res2.duration_minutes == 90
    assert res2.energy_cost == 6.0


def test_nlp_parse_admin_keywords():
    """Parses administrative and routine tasks."""
    res1 = TaskParser.parse_task("Számlák rendezése és e-mail válaszok 45m")
    assert res1.load_type == CognitiveLoad.ADMIN
    assert res1.duration_minutes == 45
    assert res1.energy_cost == 3.0

    res2 = TaskParser.parse_task("Sprint standup meeting 15 min")
    assert res2.load_type == CognitiveLoad.ADMIN
    assert res2.duration_minutes == 15
    assert res2.energy_cost == 3.0


def test_nlp_parse_recovery_keywords():
    """Parses recovery and wellness tasks with negative cognitive cost."""
    res1 = TaskParser.parse_task("Séta a természetben 30 perc")
    assert res1.load_type == CognitiveLoad.RECOVERY
    assert res1.duration_minutes == 30
    assert res1.energy_cost == -3.0

    res2 = TaskParser.parse_task("Kávé szünet és meditáció 20 min")
    assert res2.load_type == CognitiveLoad.RECOVERY
    assert res2.duration_minutes == 20
    assert res2.energy_cost == -3.0


def test_nlp_parse_english_keywords():
    """Parses English keywords accurately."""
    res = TaskParser.parse_task("Refactor authentication module 2 hours")
    assert res.load_type == CognitiveLoad.DEEP_WORK
    assert res.duration_minutes == 120
    assert res.energy_cost == 8.5


def test_nlp_parse_default_duration():
    """Defaults to 45 minutes when no duration is specified in raw text."""
    res = TaskParser.parse_task("Tanulás vizsgára")
    assert res.load_type == CognitiveLoad.DEEP_WORK
    assert res.duration_minutes == 45


def test_nlp_parse_fractional_durations():
    """Handles fractional hours formatted with comma or dot."""
    res_dot = TaskParser.parse_task("Kódolás 1.5 hour")
    assert res_dot.duration_minutes == 90

    res_comma = TaskParser.parse_task("Kódolás 2,5 óra")
    assert res_comma.duration_minutes == 150
