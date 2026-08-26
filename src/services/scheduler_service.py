"""Energy-aware task scheduling and circadian choreography service."""
from __future__ import annotations
from typing import List, Optional, Tuple
from uuid import uuid4
from src.models.energy import (
    CognitiveLoad,
    EnergyDebtReport,
    EnergyProfile,
    ReflowRequest,
    ReflowResponse,
    ScheduleRequest,
    ScheduleResponse,
    ScheduledSlot,
    Task,
)
from src.services.energy_calculator import (
    EnergyCalculator,
    minutes_to_time,
    time_to_minutes,
)

class EnergyScheduler:
    """Choreographs tasks into circadian energy windows using heuristic CSP."""
    RECOVERY_DURATION_MINUTES = 20
    RECOVERY_ENERGY_COST = -3.0
    RECOVERY_TITLE = "Automatikus Kognitív Regeneráció"

    @classmethod
    def _check_fixed_task_conflicts(cls, fixed_tasks: List[Task]) -> List[Tuple[int, int]]:
        """Validate fixed tasks and ensure none have overlapping times."""
        intervals: List[Tuple[int, int]] = []
        for task in fixed_tasks:
            if not task.fixed_start:
                raise ValueError(f"Fixed task '{task.title}' must specify 'fixed_start'")
            start = time_to_minutes(task.fixed_start)
            end = start + task.duration_minutes
            if start < 0 or end > 1440:
                raise ValueError(f"Fixed task '{task.title}' exceeds 24-hour day boundary")
            for prev_start, prev_end in intervals:
                if max(start, prev_start) < min(end, prev_end):
                    raise ValueError("Fixed tasks conflict")
            intervals.append((start, end))
        return intervals

    @classmethod
    def _is_slot_free(
        cls, start: int, end: int, slots: List[ScheduledSlot], wake: int, sleep: int
    ) -> bool:
        """Check if interval [start, end] is within wake hours and free of other tasks."""
        if start < wake or end > sleep:
            return False
        return not any(
            max(start, time_to_minutes(s.start_time)) < min(end, time_to_minutes(s.end_time))
            for s in slots
        )

    @classmethod
    def _consecutive_deep_work_before(cls, start_min: int, slots: List[ScheduledSlot]) -> int:
        """Count uninterrupted consecutive deep work minutes immediately ending at start_min."""
        slot = next((s for s in slots if time_to_minutes(s.end_time) == start_min), None)
        if not slot or slot.load_type != CognitiveLoad.DEEP_WORK:
            return 0
        chain_start = time_to_minutes(slot.start_time)
        curr = slot
        while True:
            prev = next(
                (
                    s
                    for s in slots
                    if time_to_minutes(s.end_time) == time_to_minutes(curr.start_time)
                    and s.load_type == CognitiveLoad.DEEP_WORK
                ),
                None,
            )
            if prev:
                chain_start = time_to_minutes(prev.start_time)
                curr = prev
            else:
                break
        return start_min - chain_start

    @classmethod
    def _candidate_starts(
        cls, wake: int, sleep: int, limit: int, dur: int, slots: List[ScheduledSlot]
    ) -> List[int]:
        """Generate sorted candidate start minutes aligned to grid and slot endpoints."""
        max_start = min(sleep - dur, limit - dur)
        grid_points = range(wake, max_start + 1, 15)
        endpoints = [
            time_to_minutes(s.end_time)
            for s in slots
            if wake <= time_to_minutes(s.end_time) <= max_start
        ]
        return sorted(set(list(grid_points) + endpoints))

    @classmethod
    def _build_debt_report(
        cls,
        profile: EnergyProfile,
        tasks: List[Task],
        fixed_intervals: List[Tuple[int, int]],
        sleep_quality: float = 1.0,
        start_minute: Optional[int] = None,
    ) -> EnergyDebtReport:
        """Calculate total requested cognitive load, capacity, and energy debt."""
        total_capacity = EnergyCalculator.calculate_free_capacity(
            profile, fixed_intervals, sleep_quality=sleep_quality, start_minute=start_minute
        )
        total_requested = max(0.0, sum(t.energy_cost * t.duration_minutes for t in tasks))
        is_overloaded = total_requested > total_capacity
        energy_debt = max(0.0, total_requested - total_capacity)
        exhaustion_pct = (
            (total_requested / total_capacity * 100.0) if total_capacity > 0 else 0.0
        )
        if is_overloaded:
            recommendation = (
                "Kognitív túlterhelés észlelve! A tervezett terhelés meghaladja a napi "
                "energiakapacitást. Csökkentsd a mélymunka feladatok számát vagy iktass be "
                "regenerációs szüneteket."
            )
        elif exhaustion_pct > 85.0:
            recommendation = (
                "Magas mentális terhelés! Közelíted a napi energiakapacitásod határát, figyelj a regenerációra."
            )
        else:
            recommendation = (
                "Optimális energiamérleg! A feladatok kiegyensúlyozottan illeszkednek a cirkadián ritmusodhoz."
            )
        return EnergyDebtReport(
            total_capacity=round(total_capacity, 2),
            total_requested_load=round(total_requested, 2),
            energy_debt=round(energy_debt, 2),
            is_overloaded=is_overloaded,
            exhaustion_percentage=round(exhaustion_pct, 2),
            recommendation=recommendation,
        )

    @classmethod
    def _schedule_deep_work(
        cls,
        tasks: List[Task],
        profile: EnergyProfile,
        slots: List[ScheduledSlot],
        unscheduled: List[Task],
        wake: int,
        sleep: int,
        peaks: List[Tuple[int, int]],
        max_consecutive_deep: int = 120,
        rec_duration: int = 20,
        sleep_quality: float = 1.0,
    ) -> None:
        """Schedule DEEP_WORK tasks with peak priority and consecutive threshold recovery."""
        peak_thresh = 7.5 * min(1.0, sleep_quality)
        for task in tasks:
            dur = task.duration_minutes
            deadline = time_to_minutes(task.deadline) if task.deadline else sleep
            candidates = []
            for c_start in cls._candidate_starts(wake, sleep, deadline, dur, slots):
                consec = cls._consecutive_deep_work_before(c_start, slots)
                if consec > 0 and (consec + dur >= max_consecutive_deep):
                    rec_dur = rec_duration
                    if c_start + rec_dur + dur <= deadline and cls._is_slot_free(
                        c_start, c_start + rec_dur + dur, slots, wake, sleep
                    ):
                        t_start = c_start + rec_dur
                        avg_e = EnergyCalculator.calculate_average_energy(
                            profile, t_start, dur, sleep_quality=sleep_quality
                        )
                        in_peak = any(ps <= t_start < pe or ps <= c_start < pe for ps, pe in peaks)
                        tier = 0 if (in_peak and avg_e >= peak_thresh) else (1 if avg_e >= peak_thresh else 2)
                        candidates.append(
                            ((tier, -avg_e if tier > 0 else 0, c_start), c_start, rec_dur, t_start, avg_e)
                        )
                elif c_start + dur <= deadline and cls._is_slot_free(
                    c_start, c_start + dur, slots, wake, sleep
                ):
                    avg_e = EnergyCalculator.calculate_average_energy(
                        profile, c_start, dur, sleep_quality=sleep_quality
                    )
                    in_peak = any(ps <= c_start < pe for ps, pe in peaks)
                    tier = 0 if (in_peak and avg_e >= peak_thresh) else (1 if avg_e >= peak_thresh else 2)
                    candidates.append(((tier, -avg_e if tier > 0 else 0, c_start), c_start, 0, c_start, avg_e))
            if candidates:
                candidates.sort(key=lambda x: x[0])
                _, c_start, rec_dur, t_start, avg_e = candidates[0]
                if rec_dur > 0:
                    rec_avg = EnergyCalculator.calculate_average_energy(
                        profile, c_start, rec_dur, sleep_quality=sleep_quality
                    )
                    slots.append(
                        ScheduledSlot(
                            task_id=f"auto-rec-{uuid4().hex[:8]}",
                            title=cls.RECOVERY_TITLE,
                            start_time=minutes_to_time(c_start),
                            end_time=minutes_to_time(c_start + rec_dur),
                            duration_minutes=rec_dur,
                            load_type=CognitiveLoad.RECOVERY,
                            energy_cost=cls.RECOVERY_ENERGY_COST,
                            is_auto_recovery=True,
                            average_energy_level=rec_avg,
                        )
                    )
                slots.append(
                    ScheduledSlot(
                        task_id=task.id,
                        title=task.title,
                        start_time=minutes_to_time(t_start),
                        end_time=minutes_to_time(t_start + dur),
                        duration_minutes=dur,
                        load_type=CognitiveLoad.DEEP_WORK,
                        energy_cost=task.energy_cost,
                        is_auto_recovery=False,
                        average_energy_level=avg_e,
                    )
                )
            else:
                unscheduled.append(task)

    @classmethod
    def _schedule_simple_load(
        cls,
        tasks: List[Task],
        profile: EnergyProfile,
        slots: List[ScheduledSlot],
        unscheduled: List[Task],
        wake: int,
        sleep: int,
        load_type: CognitiveLoad,
        dips: List[Tuple[int, int]],
        sleep_quality: float = 1.0,
    ) -> None:
        """Schedule CREATIVE, ADMIN, or RECOVERY tasks according to energy level preference."""
        for task in tasks:
            dur = task.duration_minutes
            deadline = time_to_minutes(task.deadline) if task.deadline else sleep
            candidates = []
            for c_start in cls._candidate_starts(wake, sleep, deadline, dur, slots):
                if c_start + dur <= deadline and cls._is_slot_free(
                    c_start, c_start + dur, slots, wake, sleep
                ):
                    avg_e = EnergyCalculator.calculate_average_energy(
                        profile, c_start, dur, sleep_quality=sleep_quality
                    )
                    if load_type == CognitiveLoad.CREATIVE:
                        tier = 0 if (4.5 <= avg_e <= 7.5) else 1
                        score = (tier, abs(avg_e - 6.0), c_start)
                    elif load_type == CognitiveLoad.ADMIN:
                        in_dip = any(ds <= c_start < de for ds, de in dips)
                        tier = 0 if (in_dip and avg_e <= 4.5) else (1 if avg_e <= 4.5 else 2)
                        score = (tier, avg_e, c_start)
                    else:  # RECOVERY
                        in_dip = any(ds <= c_start < de for ds, de in dips)
                        score = (0 if in_dip else 1, avg_e, c_start)
                    candidates.append((score, c_start, avg_e))
            if candidates:
                candidates.sort(key=lambda x: x[0])
                _, c_start, avg_e = candidates[0]
                slots.append(
                    ScheduledSlot(
                        task_id=task.id,
                        title=task.title,
                        start_time=minutes_to_time(c_start),
                        end_time=minutes_to_time(c_start + dur),
                        duration_minutes=dur,
                        load_type=load_type,
                        energy_cost=task.energy_cost,
                        is_auto_recovery=False,
                        average_energy_level=avg_e,
                    )
                )
            else:
                unscheduled.append(task)

    @classmethod
    def _execute_choreography(
        cls,
        profile: EnergyProfile,
        tasks: List[Task],
        wake_min: int,
        sleep_min: int,
        sleep_quality: float = 1.0,
        max_consecutive_deep: int = 120,
        rec_duration: int = 20,
    ) -> Tuple[List[ScheduledSlot], List[Task], List[Tuple[int, int]]]:
        """Core scheduling pipeline shared across full-day and mid-day reflow."""
        fixed_tasks = [t for t in tasks if t.is_fixed]
        fixed_intervals = cls._check_fixed_task_conflicts(fixed_tasks)
        future_fixed_tasks = [
            t for t in fixed_tasks if t.fixed_start and time_to_minutes(t.fixed_start) >= wake_min
        ]
        dynamic_tasks = [t for t in tasks if not t.is_fixed]
        scheduled_slots: List[ScheduledSlot] = []
        for t in future_fixed_tasks:
            s = time_to_minutes(t.fixed_start)  # type: ignore[arg-type]
            e = s + t.duration_minutes
            avg_e = EnergyCalculator.calculate_average_energy(
                profile, s, t.duration_minutes, sleep_quality=sleep_quality
            )
            scheduled_slots.append(
                ScheduledSlot(
                    task_id=t.id,
                    title=t.title,
                    start_time=minutes_to_time(s),
                    end_time=minutes_to_time(e),
                    duration_minutes=t.duration_minutes,
                    load_type=t.load_type,
                    energy_cost=t.energy_cost,
                    is_auto_recovery=False,
                    average_energy_level=avg_e,
                )
            )
        deep_tasks = sorted([t for t in dynamic_tasks if t.load_type == CognitiveLoad.DEEP_WORK], key=lambda t: (-t.energy_cost, -t.duration_minutes))
        creative_tasks = sorted([t for t in dynamic_tasks if t.load_type == CognitiveLoad.CREATIVE], key=lambda t: (-t.energy_cost, -t.duration_minutes))
        admin_tasks = sorted([t for t in dynamic_tasks if t.load_type == CognitiveLoad.ADMIN], key=lambda t: (-t.energy_cost, -t.duration_minutes))
        recovery_tasks = sorted([t for t in dynamic_tasks if t.load_type == CognitiveLoad.RECOVERY], key=lambda t: (t.energy_cost, -t.duration_minutes))
        peaks = [(time_to_minutes(p.start), time_to_minutes(p.end)) for p in profile.peak_hours]
        dips = [(time_to_minutes(d.start), time_to_minutes(d.end)) for d in profile.dip_hours]
        unscheduled: List[Task] = []
        cls._schedule_deep_work(deep_tasks, profile, scheduled_slots, unscheduled, wake_min, sleep_min, peaks, max_consecutive_deep, rec_duration, sleep_quality)
        cls._schedule_simple_load(creative_tasks, profile, scheduled_slots, unscheduled, wake_min, sleep_min, CognitiveLoad.CREATIVE, dips, sleep_quality)
        cls._schedule_simple_load(admin_tasks, profile, scheduled_slots, unscheduled, wake_min, sleep_min, CognitiveLoad.ADMIN, dips, sleep_quality)
        cls._schedule_simple_load(recovery_tasks, profile, scheduled_slots, unscheduled, wake_min, sleep_min, CognitiveLoad.RECOVERY, dips, sleep_quality)
        scheduled_slots.sort(key=lambda s: time_to_minutes(s.start_time))
        return scheduled_slots, unscheduled, fixed_intervals

    @classmethod
    def schedule(cls, request: ScheduleRequest) -> ScheduleResponse:
        """Execute circadian choreography and produce optimal schedule response."""
        profile, tasks = request.profile, request.tasks
        wake_min, sleep_min = time_to_minutes(profile.wake_time), time_to_minutes(profile.sleep_time)
        scheduled_slots, unscheduled, fixed_intervals = cls._execute_choreography(
            profile, tasks, wake_min, sleep_min, sleep_quality=1.0, max_consecutive_deep=120, rec_duration=20
        )
        debt_report = cls._build_debt_report(profile, tasks, fixed_intervals)
        curve_points = EnergyCalculator.generate_curve(profile)
        return ScheduleResponse(
            status="warning" if debt_report.is_overloaded else "ok",
            scheduled_tasks=scheduled_slots,
            unscheduled_tasks=unscheduled,
            debt_report=debt_report,
            energy_curve=curve_points,
        )

    @classmethod
    def reflow_schedule(cls, request: ReflowRequest) -> ReflowResponse:
        """Dynamic mid-day ripple re-flow from current_time forward with sleep modulation."""
        profile = request.profile
        t_cur_min = time_to_minutes(request.current_time)
        wake_min = time_to_minutes(profile.wake_time)
        sleep_min = time_to_minutes(profile.sleep_time)
        sleep_quality = request.sleep_quality
        effective_start = max(wake_min, t_cur_min)
        max_deep = 60 if sleep_quality <= 0.65 else 120
        rec_dur = 30 if sleep_quality <= 0.65 else 20
        completed_ids = set(request.completed_task_ids)
        pending_tasks = [t for t in request.pending_tasks if t.id not in completed_ids]
        scheduled_slots, unscheduled, fixed_intervals = cls._execute_choreography(
            profile, pending_tasks, effective_start, sleep_min, sleep_quality=sleep_quality, max_consecutive_deep=max_deep, rec_duration=rec_dur
        )
        debt_report = cls._build_debt_report(
            profile, pending_tasks, fixed_intervals, sleep_quality=sleep_quality, start_minute=t_cur_min
        )
        curve_points = EnergyCalculator.generate_curve(profile, sleep_quality=sleep_quality)
        caffeine_win = EnergyCalculator.calculate_caffeine_window(profile, current_time=request.current_time)
        return ReflowResponse(
            status="warning" if debt_report.is_overloaded else "ok",
            reflow_time=request.current_time,
            scheduled_tasks=scheduled_slots,
            unscheduled_tasks=unscheduled,
            debt_report=debt_report,
            energy_curve=curve_points,
            caffeine_window=caffeine_win,
        )
