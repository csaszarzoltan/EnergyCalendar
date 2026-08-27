"""FastAPI API routes for energy profile, scheduling, caffeine windows, calendar sync, and advanced circadian suite (v1.5.0)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, status

from src.models.simulation import SimulationTickRequest, SimulationTickResponse
from src.services.simulation_service import SimulationService

from src.models.energy import (
    CaffeineQueryRequest,
    CaffeineWindowResponse,
    EnergyCurveResponse,
    EnergyProfile,
    ICSExportRequest,
    ICSImportRequest,
    ICSImportResponse,
    ReflowRequest,
    ReflowResponse,
    ScheduleRequest,
    ScheduleResponse,
    ShutdownSummaryRequest,
    ShutdownSummaryResponse,
    TaskDecomposeRequest,
    TaskDecomposeResponse,
    TaskParseRequest,
    TaskParseResponse,
)
from src.models.advanced_circadian import (
    AlertQueryRequest,
    AlertQueryResponse,
    BiometricSyncRequest,
    BiometricSyncResponse,
    BurnoutAnalysisRequest,
    BurnoutAnalysisResponse,
    CircadianAnalyticsRequest,
    CircadianAnalyticsResponse,
    MealImpactRequest,
    MealImpactResponse,
    MicroRecoveryRequest,
    MicroRecoveryResponse,
    PhototherapyRequest,
    PhototherapyResponse,
    SocialSyncRequest,
    SocialSyncResponse,
    UltradianSplitRequest,
    UltradianSplitResponse,
    WeeklyMatrixRequest,
    WeeklyMatrixResponse,
)
from src.models.market_circadian import (
    BiophilicAuditRequest,
    BiophilicAuditResponse,
    ContextSwitchRequest,
    ContextSwitchResponse,
    DopamineGuardRequest,
    DopamineGuardResponse,
    InfradianRequest,
    InfradianResponse,
    JetlagRequest,
    JetlagResponse,
    MeetingTaxRequest,
    MeetingTaxResponse,
    NeuroFlowRequest,
    NeuroFlowResponse,
    SoundscapeRequest,
    SoundscapeResponse,
    WeatherImpactRequest,
    WeatherImpactResponse,
    WorkoutTimingRequest,
    WorkoutTimingResponse,
)
from src.services.alert_service import CircadianAlertService
from src.services.analytics_service import CircadianAnalyticsService
from src.services.biometric_service import BiometricSyncService
from src.services.biophilic_service import BiophilicSpaceService
from src.services.burnout_service import BurnoutPredictionService
from src.services.calendar_sync import CalendarSyncService
from src.services.context_switch_service import ContextSwitchService
from src.services.decomposer_service import TaskDecomposer
from src.services.dopamine_guard_service import DopamineGuardService
from src.services.energy_calculator import EnergyCalculator
from src.services.infradian_service import InfradianRhythmService
from src.services.jetlag_service import JetlagChronoService
from src.services.meeting_tax_service import MeetingTaxService
from src.services.micro_recovery_service import MicroRecoveryService
from src.services.neuro_flow_service import NeuroFlowService
from src.services.nlp_parser import TaskParser
from src.services.nutrition_service import ChronoNutritionService
from src.services.phototherapy_service import PhototherapyService
from src.services.scheduler_service import EnergyScheduler
from src.services.shutdown_service import ShutdownService
from src.services.social_sync_service import SocialJetlagService
from src.services.soundscape_service import SoundscapeSynthService
from src.services.ultradian_service import UltradianEngineService
from src.services.weather_chrono_service import WeatherChronoService
from src.services.weekly_matrix_service import WeeklyMatrixService
from src.services.workout_timing_service import WorkoutTimingService

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint returning system status."""
    return {"status": "ok", "service": "energy-calendar"}


@router.post("/energy/profile/curve", response_model=EnergyCurveResponse, status_code=status.HTTP_200_OK)
async def generate_energy_curve(profile: EnergyProfile) -> EnergyCurveResponse:
    """Generate 24-hour continuous circadian energy curve with 15-minute resolution."""
    try:
        points = EnergyCalculator.generate_curve(profile)
        return EnergyCurveResponse(points=points, profile=profile)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/energy/schedule", response_model=ScheduleResponse, status_code=status.HTTP_200_OK)
async def choreograph_schedule(request: ScheduleRequest) -> ScheduleResponse:
    """Choreograph tasks to align with circadian energy curve and compute debt report."""
    try:
        return EnergyScheduler.schedule(request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/energy/schedule/reflow", response_model=ReflowResponse, status_code=status.HTTP_200_OK)
async def reflow_schedule(request: ReflowRequest) -> ReflowResponse:
    """Dynamic mid-day schedule re-flow adapting remaining tasks from current_time forward."""
    try:
        return EnergyScheduler.reflow_schedule(request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/energy/caffeine-window", response_model=CaffeineWindowResponse, status_code=status.HTTP_200_OK)
async def calculate_caffeine_window(request: CaffeineQueryRequest) -> CaffeineWindowResponse:
    """Calculate circadian caffeine cutoff and optimal boost windows to protect deep sleep."""
    try:
        return EnergyCalculator.calculate_caffeine_window(profile=request.profile, current_time=request.current_time)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/energy/parse-task", response_model=TaskParseResponse, status_code=status.HTTP_200_OK)
async def parse_task(request: TaskParseRequest) -> TaskParseResponse:
    """Parse natural language task string into structured cognitive load and duration."""
    try:
        return TaskParser.parse_task(request.raw_text)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/energy/calendar/export-ics", status_code=status.HTTP_200_OK)
async def export_calendar_ics(request: ICSExportRequest) -> Response:
    """Export scheduled slots as an RFC 5545 iCalendar (.ics) file."""
    try:
        ics_text = CalendarSyncService.export_to_ics(slots=request.scheduled_tasks, calendar_name=request.calendar_name)
        return Response(content=ics_text, media_type="text/calendar", headers={"Content-Disposition": 'attachment; filename="energy-calendar.ics"'})
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/energy/calendar/import-ics", response_model=ICSImportResponse, status_code=status.HTTP_200_OK)
async def import_calendar_ics(request: ICSImportRequest) -> ICSImportResponse:
    """Import RFC 5545 iCalendar (.ics) events and convert them to fixed circadian tasks."""
    try:
        imported_tasks = CalendarSyncService.import_from_ics(request.ics_content)
        return ICSImportResponse(imported_tasks=imported_tasks, imported_count=len(imported_tasks), message=f"Sikeresen importálva {len(imported_tasks)} db naptáresemény.")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/energy/decompose-task", response_model=TaskDecomposeResponse, status_code=status.HTTP_200_OK)
async def decompose_task(request: TaskDecomposeRequest) -> TaskDecomposeResponse:
    """Decompose large complex task (>60m) into sequenced cognitive phases."""
    try:
        return TaskDecomposer.decompose(request.task)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/energy/shutdown/summary", response_model=ShutdownSummaryResponse, status_code=status.HTTP_200_OK)
async def shutdown_summary(request: ShutdownSummaryRequest) -> ShutdownSummaryResponse:
    """Generate circadian shutdown summary, statistics, and melatonin gate guidance."""
    try:
        return ShutdownService.create_summary(request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


# === SPEC-005 VÉGPONTOK ===
@router.post("/energy/biometrics/sync", response_model=BiometricSyncResponse, status_code=status.HTTP_200_OK)
async def sync_biometrics(request: BiometricSyncRequest) -> BiometricSyncResponse:
    return BiometricSyncService.sync_biometrics(request)

@router.post("/energy/weekly/matrix", response_model=WeeklyMatrixResponse, status_code=status.HTTP_200_OK)
async def generate_weekly_matrix(request: WeeklyMatrixRequest) -> WeeklyMatrixResponse:
    return WeeklyMatrixService.generate_weekly_matrix(request)

@router.post("/energy/alerts", response_model=AlertQueryResponse, status_code=status.HTTP_200_OK)
async def query_circadian_alerts(request: AlertQueryRequest) -> AlertQueryResponse:
    return CircadianAlertService.get_alerts(request)

@router.post("/energy/ultradian/split", response_model=UltradianSplitResponse, status_code=status.HTTP_200_OK)
async def split_ultradian_task(request: UltradianSplitRequest) -> UltradianSplitResponse:
    return UltradianEngineService.split_task(request)

@router.post("/energy/nutrition/impact", response_model=MealImpactResponse, status_code=status.HTTP_200_OK)
async def calculate_nutrition_impact(request: MealImpactRequest) -> MealImpactResponse:
    return ChronoNutritionService.calculate_impact(request)

@router.post("/energy/phototherapy/plan", response_model=PhototherapyResponse, status_code=status.HTTP_200_OK)
async def phototherapy_plan(request: PhototherapyRequest) -> PhototherapyResponse:
    return PhototherapyService.generate_plan(request)

@router.post("/energy/burnout/prediction", response_model=BurnoutAnalysisResponse, status_code=status.HTTP_200_OK)
async def predict_burnout(request: BurnoutAnalysisRequest) -> BurnoutAnalysisResponse:
    return BurnoutPredictionService.predict_burnout(request)

@router.post("/energy/social/sync", response_model=SocialSyncResponse, status_code=status.HTTP_200_OK)
async def calculate_social_sync(request: SocialSyncRequest) -> SocialSyncResponse:
    return SocialJetlagService.calculate_sync(request)

@router.post("/energy/micro-recovery/plan", response_model=MicroRecoveryResponse, status_code=status.HTTP_200_OK)
async def plan_micro_recovery(request: MicroRecoveryRequest) -> MicroRecoveryResponse:
    return MicroRecoveryService.plan_recovery(request)

@router.post("/energy/analytics/alignment", response_model=CircadianAnalyticsResponse, status_code=status.HTTP_200_OK)
async def compute_circadian_analytics(request: CircadianAnalyticsRequest) -> CircadianAnalyticsResponse:
    return CircadianAnalyticsService.compute_analytics(request)


# === 10 ÚJ PIACI & FELHASZNÁLÓI VÉGPONT (SPEC-006 / v1.4.0) ===

@router.post("/energy/context-switch/tax", response_model=ContextSwitchResponse, status_code=status.HTTP_200_OK)
async def analyze_context_switch_tax(request: ContextSwitchRequest) -> ContextSwitchResponse:
    """Calculate cognitive fragmentation tax and provide task batching suggestions."""
    return ContextSwitchService.analyze_switches(request)

@router.post("/energy/jetlag/plan", response_model=JetlagResponse, status_code=status.HTTP_200_OK)
async def calculate_jetlag_plan(request: JetlagRequest) -> JetlagResponse:
    """Generate multi-day circadian phase adaptation protocol for timezone travel."""
    return JetlagChronoService.calculate_adaptation(request)

@router.post("/energy/neuroflow/guard", response_model=NeuroFlowResponse, status_code=status.HTTP_200_OK)
async def generate_neuroflow_guard(request: NeuroFlowRequest) -> NeuroFlowResponse:
    """Create gentle transition and anti-hyperfocus crash pacing for ADHD and deep flow."""
    return NeuroFlowService.create_pacing(request)

@router.post("/energy/biophilic/audit", response_model=BiophilicAuditResponse, status_code=status.HTTP_200_OK)
async def audit_biophilic_space(request: BiophilicAuditRequest) -> BiophilicAuditResponse:
    """Evaluate indoor CO2, temperature, and noise impact on cognitive capacity."""
    return BiophilicSpaceService.audit_environment(request)

@router.post("/energy/dopamine/guard", response_model=DopamineGuardResponse, status_code=status.HTTP_200_OK)
async def configure_dopamine_guard(request: DopamineGuardRequest) -> DopamineGuardResponse:
    """Establish high-friction focus barriers and digital distraction shielding."""
    return DopamineGuardService.create_guard(request)

@router.post("/energy/soundscape/config", response_model=SoundscapeResponse, status_code=status.HTTP_200_OK)
async def get_soundscape_config(request: SoundscapeRequest) -> SoundscapeResponse:
    """Generate Web Audio parameters for 40Hz Gamma, Theta, Delta, and colored noise."""
    return SoundscapeSynthService.generate_config(request)

@router.post("/energy/weather/adjust", response_model=WeatherImpactResponse, status_code=status.HTTP_200_OK)
async def adjust_for_weather(request: WeatherImpactRequest) -> WeatherImpactResponse:
    """Modulate energy damping and fatigue recovery based on barometric pressure and fronts."""
    return WeatherChronoService.evaluate_weather(request)

@router.post("/energy/workout/timing", response_model=WorkoutTimingResponse, status_code=status.HTTP_200_OK)
async def get_workout_timing(request: WorkoutTimingRequest) -> WorkoutTimingResponse:
    """Calculate optimal circadian biological window for physical training and sleep safety."""
    return WorkoutTimingService.calculate_window(request)

@router.post("/energy/meeting/tax", response_model=MeetingTaxResponse, status_code=status.HTTP_200_OK)
async def calculate_meeting_tax(request: MeetingTaxRequest) -> MeetingTaxResponse:
    """Calculate cognitive meeting drain score and insert automatic decompression buffers."""
    return MeetingTaxService.evaluate_meetings(request)

@router.post("/energy/infradian/plan", response_model=InfradianResponse, status_code=status.HTTP_200_OK)
async def plan_infradian_rhythm(request: InfradianRequest) -> InfradianResponse:
    """Calculate seasonal sleep adjustments, light exposure, and monthly macro focus cycles."""
    return InfradianRhythmService.plan_infradian(request)

# === SPEC-007: SZIMULÁCIÓS IDŐGÉP VÉGPONTOK (v1.5.0) ===
@router.post("/energy/simulation/tick", response_model=SimulationTickResponse, status_code=status.HTTP_200_OK)
async def evaluate_simulation_tick(request: SimulationTickRequest) -> SimulationTickResponse:
    """Calculate exact real-time circadian telemetry, active phase, and neuro-guidance for a simulated clock tick."""
    return SimulationService.evaluate_tick(request)
