"""7-day weekly circadian macro-rhythm and cognitive load smoothing."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List
from src.models.advanced_circadian import DayScheduleSummary, WeeklyMatrixRequest, WeeklyMatrixResponse


class WeeklyMatrixService:
    """Schedules cognitive tasks across a 7-day week respecting circadian capacity."""

    DAY_NAMES = ["Hétfő", "Kedd", "Szerda", "Csütörtök", "Péntek", "Szombat", "Vasárnap"]

    @classmethod
    def generate_weekly_matrix(cls, request: WeeklyMatrixRequest) -> WeeklyMatrixResponse:
        """Distribute task pool across the week, designating Focus and Recovery days."""
        days_schedule: List[DayScheduleSummary] = []
        try:
            start_dt = datetime.strptime(request.start_date, "%Y-%m-%d")
        except ValueError:
            start_dt = datetime(2026, 8, 31)

        tasks = list(request.tasks_pool)
        focus_days: List[str] = ["Kedd", "Csütörtök"]
        recovery_days: List[str] = ["Péntek", "Vasárnap"]

        for i in range(7):
            cur_dt = start_dt + timedelta(days=i)
            day_name = cls.DAY_NAMES[cur_dt.weekday()]
            is_focus = day_name in focus_days
            is_rec = day_name in recovery_days

            assigned_tasks = []
            deep_min = 0
            admin_min = 0

            # Greedy assign tasks for focus or balance days
            if tasks and (is_focus or not is_rec):
                t = tasks.pop(0)
                assigned_tasks.append({"title": t.title, "duration": t.duration, "load": t.cognitive_load})
                if t.cognitive_load.upper() == "DEEP_WORK":
                    deep_min += t.duration
                else:
                    admin_min += t.duration

            days_schedule.append(
                DayScheduleSummary(
                    day_index=i,
                    day_name=day_name,
                    date_str=cur_dt.strftime("%Y-%m-%d"),
                    is_focus_day=is_focus,
                    is_recovery_day=is_rec,
                    total_deep_work_minutes=deep_min,
                    total_admin_minutes=admin_min,
                    tasks=assigned_tasks,
                )
            )

        balance_score = round(max(50.0, min(100.0, 90.0 - (len(tasks) * 5.0))), 1)
        rec = "Heti makro-ritmus kiegyensúlyozva: Kedd/Csütörtök mélymunka fókusszal."

        return WeeklyMatrixResponse(
            days_schedule=days_schedule,
            focus_days=focus_days,
            recovery_days=recovery_days,
            weekly_balance_score=balance_score,
            recommendation=rec,
        )
