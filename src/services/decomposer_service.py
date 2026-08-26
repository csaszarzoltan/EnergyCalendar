"""Cognitive Task Decomposition Service for circadian load balancing."""
from __future__ import annotations

from uuid import uuid4

from src.models.energy import CognitiveLoad, Task, TaskDecomposeResponse


class TaskDecomposer:
    """Decomposes large tasks into sequenced cognitive subtasks."""

    @classmethod
    def decompose(cls, task: Task) -> TaskDecomposeResponse:
        """Decompose a task based on its duration and cognitive load requirements.

        If the task duration is 60 minutes or less, it is returned as a single task.
        If the task duration is greater than 60 minutes, it is split into 3 phases:
          1. Concept & Planning (~25%, CREATIVE)
          2. Deep Execution (~50%, DEEP_WORK)
          3. Review & Documentation (~25%, ADMIN)

        Args:
            task: The original task to decompose.

        Returns:
            TaskDecomposeResponse with structured subtasks.
        """
        if task.duration_minutes <= 60:
            return TaskDecomposeResponse(
                original_task_id=task.id,
                subtasks=[task],
                total_duration_minutes=task.duration_minutes,
                decomposition_strategy="none",
            )

        total = task.duration_minutes

        # Calculate phase durations: ~25%, ~50%, ~25%
        p1 = max(5, round(total * 0.25))
        p3 = max(5, round(total * 0.25))
        p2 = total - p1 - p3

        # Safety adjustment if rounding edge case occurs
        if p2 <= 0:
            p1 = max(1, total // 4)
            p3 = max(1, total // 4)
            p2 = total - p1 - p3

        deep_work_cost = max(8.5, task.energy_cost) if task.load_type == CognitiveLoad.DEEP_WORK else 8.5

        subtasks = [
            Task(
                id=str(uuid4()),
                title=f"{task.title} — 1. Fázis: Koncepció & Tervezés",
                duration_minutes=p1,
                load_type=CognitiveLoad.CREATIVE,
                energy_cost=6.0,
                is_fixed=False,
                deadline=task.deadline,
            ),
            Task(
                id=str(uuid4()),
                title=f"{task.title} — 2. Fázis: Mély Kivitelezés",
                duration_minutes=p2,
                load_type=CognitiveLoad.DEEP_WORK,
                energy_cost=deep_work_cost,
                is_fixed=False,
                deadline=task.deadline,
            ),
            Task(
                id=str(uuid4()),
                title=f"{task.title} — 3. Fázis: Review & Dokumentálás",
                duration_minutes=p3,
                load_type=CognitiveLoad.ADMIN,
                energy_cost=3.0,
                is_fixed=False,
                deadline=task.deadline,
            ),
        ]

        return TaskDecomposeResponse(
            original_task_id=task.id,
            subtasks=subtasks,
            total_duration_minutes=total,
            decomposition_strategy="3_phase_cognitive_chunking",
        )
