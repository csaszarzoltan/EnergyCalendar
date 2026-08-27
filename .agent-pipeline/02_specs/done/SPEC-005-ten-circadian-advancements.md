# SPEC-005: 10 Új Cirkadián, Biometrikus és Kognitív Funkció Specifikációja

## 1. Modulok és Szolgáltatások Specifikációja

1. **BiometricSyncService (src/services/biometric_service.py):**
   - Bemenet: BiometricSyncRequest(hrv_rmssd, resting_hr, deep_sleep_minutes, rem_sleep_minutes, wake_time)
   - Kimenet: BiometricSyncResponse(recovery_factor, readiness_score, recommended_peak_offset_minutes, message)

2. **WeeklyMatrixService (src/services/weekly_matrix_service.py):**
   - Bemenet: WeeklyMatrixRequest(profile, tasks_pool, start_date)
   - Kimenet: WeeklyMatrixResponse(days_schedule, focus_days, recovery_days, weekly_balance_score)

3. **CircadianAlertService (src/services/alert_service.py):**
   - Bemenet: AlertQueryRequest(profile, current_time, active_deep_work_minutes)
   - Kimenet: AlertQueryResponse(active_alerts, next_event_countdown)

4. **UltradianEngineService (src/services/ultradian_service.py):**
   - Bemenet: UltradianSplitRequest(task_title, duration_minutes, brac_cycle_minutes=90, break_minutes=20)
   - Kimenet: UltradianSplitResponse(blocks, total_cycles, total_duration)

5. **ChronoNutritionService (src/services/nutrition_service.py):**
   - Bemenet: MealImpactRequest(meal_time, meal_type, carb_level, fasting_hours)
   - Kimenet: MealImpactResponse(postprandial_dip_start, postprandial_dip_end, dip_severity, optimal_walk_window)

6. **PhototherapyService (src/services/phototherapy_service.py):**
   - Bemenet: PhototherapyRequest(wake_time, sleep_time, target_lux)
   - Kimenet: PhototherapyResponse(morning_light_window, midday_sun_window, evening_blueblocker_time, protocol_tips)

7. **BurnoutPredictionService (src/services/burnout_service.py):**
   - Bemenet: BurnoutAnalysisRequest(daily_debts, daily_recoveries, streak_days)
   - Kimenet: BurnoutAnalysisResponse(allostatic_load_index, risk_level, decompression_days_needed, recommendation)

8. **SocialJetlagService (src/services/social_sync_service.py):**
   - Bemenet: SocialSyncRequest(profiles, meeting_duration_minutes)
   - Kimenet: SocialSyncResponse(golden_overlap_windows, social_jetlag_score, alignment_quality)

9. **MicroRecoveryService (src/services/micro_recovery_service.py):**
   - Bemenet: MicroRecoveryRequest(continuous_screen_minutes)
   - Kimenet: MicroRecoveryResponse(micro_breaks, physiological_sigh_instructions, eye_reset_202020)

10. **CircadianAnalyticsService (src/services/analytics_service.py):**
    - Bemenet: CircadianAnalyticsRequest(scheduled_slots, completed_task_ids, energy_curve)
    - Kimenet: CircadianAnalyticsResponse(alignment_score, deep_work_ratio, energy_roi_factor, summary)