"""FastAPI API routes for energy profile, scheduling, caffeine windows, calendar sync, and shutdown."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, status

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
from src.services.calendar_sync import CalendarSyncService
from src.services.decomposer_service import TaskDecomposer
from src.services.energy_calculator import EnergyCalculator
from src.services.nlp_parser import TaskParser
from src.services.scheduler_service import EnergyScheduler
from src.services.shutdown_service import ShutdownService

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint returning system status."""
    return {"status": "ok", "service": "energy-calendar"}


@router.post(
    "/energy/profile/curve",
    response_model=EnergyCurveResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_energy_curve(profile: EnergyProfile) -> EnergyCurveResponse:
    """Generate 24-hour continuous circadian energy curve with 15-minute resolution."""
    try:
        points = EnergyCalculator.generate_curve(profile)
        return EnergyCurveResponse(points=points, profile=profile)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/energy/schedule",
    response_model=ScheduleResponse,
    status_code=status.HTTP_200_OK,
)
async def choreograph_schedule(request: ScheduleRequest) -> ScheduleResponse:
    """Choreograph tasks to align with circadian energy curve and compute debt report."""
    try:
        return EnergyScheduler.schedule(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/energy/schedule/reflow",
    response_model=ReflowResponse,
    status_code=status.HTTP_200_OK,
)
async def reflow_schedule(request: ReflowRequest) -> ReflowResponse:
    """Dynamic mid-day schedule re-flow adapting remaining tasks from current_time forward."""
    try:
        return EnergyScheduler.reflow_schedule(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/energy/caffeine-window",
    response_model=CaffeineWindowResponse,
    status_code=status.HTTP_200_OK,
)
async def calculate_caffeine_window(request: CaffeineQueryRequest) -> CaffeineWindowResponse:
    """Calculate circadian caffeine cutoff and optimal boost windows to protect deep sleep."""
    try:
        return EnergyCalculator.calculate_caffeine_window(
            profile=request.profile, current_time=request.current_time
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/energy/parse-task",
    response_model=TaskParseResponse,
    status_code=status.HTTP_200_OK,
)
async def parse_task(request: TaskParseRequest) -> TaskParseResponse:
    """Parse natural language task string into structured cognitive load and duration."""
    try:
        return TaskParser.parse_task(request.raw_text)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/energy/calendar/export-ics",
    status_code=status.HTTP_200_OK,
)
async def export_calendar_ics(request: ICSExportRequest) -> Response:
    """Export scheduled slots as an RFC 5545 iCalendar (.ics) file."""
    try:
        ics_text = CalendarSyncService.export_to_ics(
            slots=request.scheduled_tasks,
            calendar_name=request.calendar_name,
        )
        return Response(
            content=ics_text,
            media_type="text/calendar",
            headers={"Content-Disposition": 'attachment; filename="energy-calendar.ics"'},
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/energy/calendar/import-ics",
    response_model=ICSImportResponse,
    status_code=status.HTTP_200_OK,
)
async def import_calendar_ics(request: ICSImportRequest) -> ICSImportResponse:
    """Import RFC 5545 iCalendar (.ics) events and convert them to fixed circadian tasks."""
    try:
        imported_tasks = CalendarSyncService.import_from_ics(request.ics_content)
        return ICSImportResponse(
            imported_tasks=imported_tasks,
            imported_count=len(imported_tasks),
            message=f"Sikeresen importálva {len(imported_tasks)} db naptáresemény.",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/energy/decompose-task",
    response_model=TaskDecomposeResponse,
    status_code=status.HTTP_200_OK,
)
async def decompose_task(request: TaskDecomposeRequest) -> TaskDecomposeResponse:
    """Decompose large complex task (>60m) into sequenced cognitive phases."""
    try:
        return TaskDecomposer.decompose(request.task)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/energy/shutdown/summary",
    response_model=ShutdownSummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def shutdown_summary(request: ShutdownSummaryRequest) -> ShutdownSummaryResponse:
    """Generate circadian shutdown summary, statistics, and melatonin gate guidance."""
    try:
        return ShutdownService.create_summary(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
