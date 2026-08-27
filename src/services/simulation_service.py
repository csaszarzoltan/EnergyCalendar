"""Circadian time machine simulation engine and real-time state calculator."""
from __future__ import annotations

from src.models.simulation import SimulationTickRequest, SimulationTickResponse
from src.services.energy_calculator import EnergyCalculator


class SimulationService:
    """Computes exact circadian telemetry at any simulated time point."""

    @classmethod
    def evaluate_tick(cls, request: SimulationTickRequest) -> SimulationTickResponse:
        """Calculate energy, active zone, sleep gate, and neuro-guidance for a specific simulated time."""
        prof = request.profile
        t_str = request.current_time
        parts = [int(p) for p in t_str.split(":")]
        cur_min = parts[0] * 60 + parts[1]

        # 1. Calculate energy level at cur_min
        curve = EnergyCalculator.generate_curve(prof)
        pt = next((p for p in curve if p.minute_of_day == (cur_min // 15) * 15), curve[0] if curve else None)
        lvl = pt.energy_level if pt else 7.0

        # 2. Identify active zone
        def in_range(s_str: str, e_str: str) -> bool:
            sm = int(s_str.split(":")[0]) * 60 + int(s_str.split(":")[1])
            em = int(e_str.split(":")[0]) * 60 + int(e_str.split(":")[1])
            return sm <= cur_min <= em

        is_peak = any(in_range(p.start, p.end) for p in prof.peak_hours)
        is_dip = any(in_range(d.start, d.end) for d in prof.dip_hours)

        if is_peak:
            zone = "PEAK"
            guide = "🚀 Fókuszcsúcs aktív! Kapcsold be a 40Hz Gamma hangtájat és végezz mélymunkát."
        elif is_dip:
            zone = "DIP"
            guide = "🍲 Kaja-kóma mélypont! Végezz admin feladatokat, tarts 15 perces szundit vagy sétát."
        elif lvl >= 6.5:
            zone = "MODERATE"
            guide = "💡 Kiegyensúlyozott energiaszint: Ideális kreatív tervezéshez és megbeszélésekhez."
        else:
            zone = "RECOVERY"
            guide = "🔋 Regenerációs idősáv: Igyál vizet és végezz Huberman-féle fiziológiás sóhajt."

        # 3. Caffeine evaluation
        caf_win = EnergyCalculator.calculate_caffeine_window(prof, t_str)
        cut_parts = [int(p) for p in caf_win.caffeine_cutoff_time.split(":")]
        cut_min = cut_parts[0] * 60 + cut_parts[1]
        caf_ok = cur_min <= cut_min

        # 4. Melatonin calculation
        sleep_parts = [int(p) for p in prof.sleep_time.split(":")]
        sleep_min = sleep_parts[0] * 60 + sleep_parts[1]
        mela_gate = (sleep_min - 120 + 1440) % 1440
        mela_rem = (mela_gate - cur_min + 1440) % 1440

        return SimulationTickResponse(
            current_time=t_str,
            energy_level=round(lvl, 2),
            active_zone=zone,
            active_task_title=None,
            caffeine_allowed=caf_ok,
            melatonin_minutes_remaining=mela_rem,
            neuro_guidance=guide,
        )
