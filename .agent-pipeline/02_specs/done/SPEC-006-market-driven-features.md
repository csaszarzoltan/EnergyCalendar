# SPEC-006: 10 Piaci & Felhasználói Igény Alapú Cirkadián Funkció Specifikációja

## 1. Szolgáltatások Specifikációja

1. ContextSwitchService (src/services/context_switch_service.py):
   - Bemenet: ContextSwitchRequest(tasks_sequence)
   - Kimenet: ContextSwitchResponse(switch_count, fragmentation_tax_minutes, batched_sequence, optimization_gain_percent)

2. JetlagChronoService (src/services/jetlag_service.py):
   - Bemenet: JetlagRequest(origin_timezone_offset, target_timezone_offset, travel_date)
   - Kimenet: JetlagResponse(shift_hours, days_needed, daily_shift_protocol, sleep_adaptation_schedule)

3. NeuroFlowService (src/services/neuro_flow_service.py):
   - Bemenet: NeuroFlowRequest(task_duration_minutes, is_hyperfocus_prone)
   - Kimenet: NeuroFlowResponse(gentle_transition_minutes, hydration_alerts, visual_pacing_cue)

4. BiophilicSpaceService (src/services/biophilic_service.py):
   - Bemenet: BiophilicAuditRequest(co2_ppm, temperature_celsius, noise_db)
   - Kimenet: BiophilicAuditResponse(cognitive_penalty_percent, air_quality_status, optimal_action)

5. DopamineGuardService (src/services/dopamine_guard_service.py):
   - Bemenet: DopamineGuardRequest(peak_start, peak_end, friction_level)
   - Kimenet: DopamineGuardResponse(blocking_window, friction_rules, dopamine_fasting_tips)

6. SoundscapeSynthService (src/services/soundscape_service.py):
   - Bemenet: SoundscapeRequest(cognitive_load, target_brainwave)
   - Kimenet: SoundscapeResponse(carrier_freq_hz, binaural_beat_hz, noise_type, filter_cutoff_hz)

7. WeatherChronoService (src/services/weather_chrono_service.py):
   - Bemenet: WeatherImpactRequest(pressure_hpa, weather_condition, is_front_passing)
   - Kimenet: WeatherImpactResponse(energy_damping_factor, additional_recovery_minutes, advice)

8. WorkoutTimingService (src/services/workout_timing_service.py):
   - Bemenet: WorkoutTimingRequest(wake_time, sleep_time, workout_type)
   - Kimenet: WorkoutTimingResponse(optimal_window_start, optimal_window_end, physiological_rationale, late_cutoff)

9. MeetingTaxService (src/services/meeting_tax_service.py):
   - Bemenet: MeetingTaxRequest(meetings_list)
   - Kimenet: MeetingTaxResponse(total_meeting_minutes, cognitive_drain_score, recommended_buffers, sanitized_schedule)

10. InfradianRhythmService (src/services/infradian_service.py):
    - Bemenet: InfradianRequest(season, cycle_day)
    - Kimenet: InfradianResponse(seasonal_sleep_adjustment_minutes, focus_intensity, light_recommendation)
