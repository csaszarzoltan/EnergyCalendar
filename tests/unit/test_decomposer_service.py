"""Unit tests for TaskDecomposer service."""
from __future__ import annotations

import pytest

from src.models.energy import CognitiveLoad, Task
from src.services.decomposer_service import TaskDecomposer


def test_decompose_large_task_into_3_phases():
    """Verify that a 180min task decomposes into 3 phased subtasks totalling 180min."""
    task = Task(
        id="task-big-1",
        title="Diplomamunka fejezet megírása",
        duration_minutes=180,
        load_type=CognitiveLoad.DEEP_WORK,
        energy_cost=9.0,
    )

    response = TaskDecomposer.decompose(task)
    assert response.original_task_id == "task-big-1"
    assert response.total_duration_minutes == 180
    assert response.decomposition_strategy == "3_phase_cognitive_chunking"
    assert len(response.subtasks) == 3

    # Check phase details
    p1, p2, p3 = response.subtasks
    assert p1.duration_minutes == 45
    assert p1.load_type == CognitiveLoad.CREATIVE
    assert "1. Fázis: Koncepció & Tervezés" in p1.title

    assert p2.duration_minutes == 90
    assert p2.load_type == CognitiveLoad.DEEP_WORK
    assert "2. Fázis: Mély Kivitelezés" in p2.title

    assert p3.duration_minutes == 45
    assert p3.load_type == CognitiveLoad.ADMIN
    assert "3. Fázis: Review & Dokumentálás" in p3.title

    assert sum(st.duration_minutes for st in response.subtasks) == 180


def test_decompose_small_task_returns_single():
    """Verify that tasks <= 60 minutes are not split."""
    task = Task(
        id="task-small-1",
        title="Gyors email válaszok",
        duration_minutes=45,
        load_type=CognitiveLoad.ADMIN,
        energy_cost=3.0,
    )

    response = TaskDecomposer.decompose(task)
    assert response.original_task_id == "task-small-1"
    assert len(response.subtasks) == 1
    assert response.subtasks[0].id == "task-small-1"
    assert response.decomposition_strategy == "none"


def test_decompose_exact_60_minutes():
    """Verify boundary condition for exact 60 minutes."""
    task = Task(
        id="task-exact-60",
        title="Sprint tervezés",
        duration_minutes=60,
        load_type=CognitiveLoad.CREATIVE,
        energy_cost=6.0,
    )

    response = TaskDecomposer.decompose(task)
    assert len(response.subtasks) == 1
    assert response.decomposition_strategy == "none"


def test_decompose_90_minutes_sum():
    """Verify 90 minute task decomposition duration exact sum."""
    task = Task(
        id="task-90",
        title="Komponens refaktorálás",
        duration_minutes=90,
        load_type=CognitiveLoad.DEEP_WORK,
        energy_cost=8.5,
    )

    response = TaskDecomposer.decompose(task)
    assert len(response.subtasks) == 3
    assert sum(st.duration_minutes for st in response.subtasks) == 90
    assert response.subtasks[0].load_type == CognitiveLoad.CREATIVE
    assert response.subtasks[1].load_type == CognitiveLoad.DEEP_WORK
    assert response.subtasks[2].load_type == CognitiveLoad.ADMIN
