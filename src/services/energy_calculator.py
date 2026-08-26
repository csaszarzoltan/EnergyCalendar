"""Circadian energy rhythm calculation engine."""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

from src.models.energy import (
    CaffeineWindowResponse,
    EnergyCurvePoint,
    EnergyProfile,
    TimeInterval,
)


def time_to_minutes(hh_mm: str) -> int:
    """Convert 'HH:MM' string to total minutes from midnight."""
    parts = hh_mm.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def minutes_to_time(minutes: int) -> str:
    """Convert minute of day (0-1439) to 'HH:MM' string."""
    normalized = ((minutes % 1440) + 1440) % 1440
    return f"{normalized // 60:02d}:{normalized % 60:02d}"


class EnergyCalculator:
    """Calculates continuous circadian energy curve, capacity, and caffeine windows."""

    BASE_AWAKE_ENERGY = 5.0
    SLEEP_ENERGY = 1.0
    PEAK_AMPLITUDE = 4.5
    DIP_AMPLITUDE = 2.5

    @classmethod
    def is_sleep_time(cls, profile: EnergyProfile, minute: int) -> bool:
        """Determine if a given minute falls into the user's sleep window."""
        t_wake = time_to_minutes(profile.wake_time)
        t_sleep = time_to_minutes(profile.sleep_time)

        if t_wake < t_sleep:
            return minute < t_wake or minute >= t_sleep
        # If sleep spans over midnight (e.g. 23:00 to 07:00)
        return t_sleep <= minute < t_wake

    @classmethod
    def calculate_energy_at_minute(
        cls, profile: EnergyProfile, minute: int, sleep_quality: float = 1.0
    ) -> float:
        """Calculate the continuous circadian energy level E_cap(t) modulated by sleep_quality."""
        if cls.is_sleep_time(profile, minute):
            return cls.SLEEP_ENERGY

        # Modulate peak amplitude and dip depression based on sleep_quality
        clamped_quality = max(0.3, min(1.2, sleep_quality))
        peak_amp = cls.PEAK_AMPLITUDE * clamped_quality
        dip_amp = cls.DIP_AMPLITUDE * (1.25 if clamped_quality < 0.7 else 1.0)

        val = cls.BASE_AWAKE_ENERGY

        # Gaussian elevation for peak hours
        for peak in profile.peak_hours:
            s = time_to_minutes(peak.start)
            e = time_to_minutes(peak.end)
            mu = (s + e) / 2.0
            duration = max(1.0, float(e - s))
            sigma = max(50.0, duration / 2.0)
            diff = minute - mu
            val += peak_amp * math.exp(-(diff ** 2) / (2 * (sigma ** 2)))

        # Gaussian depression for post-prandial dips
        for dip in profile.dip_hours:
            s = time_to_minutes(dip.start)
            e = time_to_minutes(dip.end)
            mu = (s + e) / 2.0
            duration = max(1.0, float(e - s))
            sigma = max(35.0, duration / 2.2)
            diff = minute - mu
            val -= dip_amp * math.exp(-(diff ** 2) / (2 * (sigma ** 2)))

        # Bound strictly within [0.0, 10.0]
        clamped = max(0.0, min(10.0, val))
        return round(clamped, 2)

    @classmethod
    def get_zone_type(cls, profile: EnergyProfile, minute: int, energy_level: float) -> str:
        """Classify energy level and time into circadian zones."""
        if cls.is_sleep_time(profile, minute):
            return "sleep"
        if energy_level >= 7.5:
            return "peak"
        if energy_level <= 4.0:
            return "dip"
        return "moderate"

    @classmethod
    def generate_curve(
        cls, profile: EnergyProfile, sleep_quality: float = 1.0
    ) -> List[EnergyCurvePoint]:
        """Generate 96 discrete 15-minute points for the full 24-hour day."""
        points: List[EnergyCurvePoint] = []
        for minute in range(0, 1440, 15):
            energy = cls.calculate_energy_at_minute(profile, minute, sleep_quality=sleep_quality)
            zone = cls.get_zone_type(profile, minute, energy)
            points.append(
                EnergyCurvePoint(
                    time=minutes_to_time(minute),
                    minute_of_day=minute,
                    energy_level=energy,
                    zone_type=zone,
                )
            )
        return points

    @classmethod
    def calculate_average_energy(
        cls,
        profile: EnergyProfile,
        start_minute: int,
        duration_minutes: int,
        sleep_quality: float = 1.0,
    ) -> float:
        """Calculate average energy level over a continuous time interval."""
        if duration_minutes <= 0:
            return cls.calculate_energy_at_minute(profile, start_minute, sleep_quality=sleep_quality)

        total = sum(
            cls.calculate_energy_at_minute(profile, m, sleep_quality=sleep_quality)
            for m in range(start_minute, start_minute + duration_minutes)
        )
        avg = total / duration_minutes
        return round(avg, 2)

    @classmethod
    def calculate_free_capacity(
        cls,
        profile: EnergyProfile,
        fixed_intervals: List[Tuple[int, int]],
        sleep_quality: float = 1.0,
        start_minute: Optional[int] = None,
    ) -> float:
        """Calculate total integrated free cognitive energy capacity across awake hours."""
        t_wake = time_to_minutes(profile.wake_time)
        t_sleep = time_to_minutes(profile.sleep_time)

        if t_wake < t_sleep:
            awake_minutes = range(t_wake, t_sleep)
        else:
            awake_minutes = list(range(t_wake, 1440)) + list(range(0, t_sleep))

        total_cap = 0.0
        for m in awake_minutes:
            if start_minute is not None and m < start_minute:
                continue
            is_fixed_busy = any(s <= m < e for s, e in fixed_intervals)
            if not is_fixed_busy:
                total_cap += cls.calculate_energy_at_minute(
                    profile, m, sleep_quality=sleep_quality
                )

        return round(total_cap, 2)

    @classmethod
    def calculate_caffeine_window(
        cls, profile: EnergyProfile, current_time: Optional[str] = None
    ) -> CaffeineWindowResponse:
        """Calculate biologically optimal caffeine timing window and adenosine risk warning."""
        t_wake = time_to_minutes(profile.wake_time)
        t_sleep = time_to_minutes(profile.sleep_time)

        start_min = (t_wake + 90) % 1440
        cutoff_min = (t_sleep - 540) % 1440
        boost_start_min = (t_wake + 90) % 1440
        boost_end_min = (t_wake + 240) % 1440

        caffeine_start = minutes_to_time(start_min)
        caffeine_cutoff = minutes_to_time(cutoff_min)
        peak_boost_start = minutes_to_time(boost_start_min)
        peak_boost_end = minutes_to_time(boost_end_min)

        if current_time is None:
            is_safe_now = True
        else:
            cur_min = time_to_minutes(current_time)
            offset_cur = (cur_min - t_wake) % 1440
            offset_cutoff = (cutoff_min - t_wake) % 1440
            is_safe_now = offset_cur < offset_cutoff

        if not is_safe_now:
            adenosine_warning = (
                f"Figyelem: A koffein-cutoff időpont ({caffeine_cutoff}) lejárt! "
                "A késői koffeinbevitel blokkolja az adenozin receptorokat és károsítja az éjszakai mélyalvást."
            )
            recommendation = (
                "Koffein helyett igyál egy nagy pohár hideg vizet, sétálj 10 percet vagy végezz kognitív regenerációt."
            )
        else:
            cur_min = time_to_minutes(current_time) if current_time else start_min
            offset_cur = (cur_min - t_wake) % 1440
            if offset_cur < 90:
                adenosine_warning = (
                    f"Figyelem: A reggeli kortizol-csúcs (CAR) aktív. Várj {caffeine_start}-ig az első koffeinnel "
                    "az adenozin természetes lebomlásáért és a délutáni fáradtság elkerüléséért."
                )
                recommendation = (
                    f"Optimális koffein-ablak: {caffeine_start} - {caffeine_cutoff}. "
                    f"Csúcsfókusz boost: {peak_boost_start} - {peak_boost_end}."
                )
            else:
                adenosine_warning = (
                    "Optimális koffein-zóna: Nincs késői adenozin-blokkolási veszély az éjszakai alvásra nézve."
                )
                recommendation = (
                    f"Optimális koffein-ablak: {caffeine_start} - {caffeine_cutoff}. "
                    f"Csúcsfókusz boost: {peak_boost_start} - {peak_boost_end}."
                )

        return CaffeineWindowResponse(
            caffeine_start_time=caffeine_start,
            caffeine_cutoff_time=caffeine_cutoff,
            peak_boost_start=peak_boost_start,
            peak_boost_end=peak_boost_end,
            is_safe_now=is_safe_now,
            adenosine_warning=adenosine_warning,
            recommendation=recommendation,
        )

