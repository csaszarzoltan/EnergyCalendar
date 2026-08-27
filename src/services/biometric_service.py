"""Biometric and wearable sensor data sync service for circadian recovery scoring."""
from __future__ import annotations

from src.models.advanced_circadian import BiometricSyncRequest, BiometricSyncResponse


class BiometricSyncService:
    """Calculates biological readiness and circadian recovery modifier from wearable telemetry."""

    @staticmethod
    def sync_biometrics(request: BiometricSyncRequest) -> BiometricSyncResponse:
        """Process HRV, resting heart rate, and sleep staging to yield recovery factor."""
        # Baseline: HRV 50ms = 1.0, RHR 60bpm = 1.0, 120m restorative sleep = 1.0
        hrv_score = request.hrv_rmssd / 50.0
        rhr_score = 60.0 / max(30.0, request.resting_hr)
        sleep_stage_score = (request.deep_sleep_minutes + request.rem_sleep_minutes) / 120.0

        raw_recovery = (0.4 * hrv_score) + (0.3 * rhr_score) + (0.3 * sleep_stage_score)
        clamped_recovery = max(0.3, min(1.2, round(raw_recovery, 2)))
        readiness_score = int(max(0, min(100, round(raw_recovery * 85))))

        # Offset peak hours slightly if wake time is earlier/later
        peak_offset = 0
        wake_parts = [int(p) for p in request.wake_time.split(":")]
        wake_minutes = wake_parts[0] * 60 + wake_parts[1]
        std_wake_minutes = 7 * 60
        peak_offset = wake_minutes - std_wake_minutes

        msg = (
            f"Biometrikus szinkron sikeres! Készültségi pontszám: {readiness_score}/100. "
            f"Alvási regeneráció: {int(clamped_recovery * 100)}%."
        )

        return BiometricSyncResponse(
            recovery_factor=clamped_recovery,
            readiness_score=readiness_score,
            recommended_peak_offset_minutes=peak_offset,
            message=msg,
        )
