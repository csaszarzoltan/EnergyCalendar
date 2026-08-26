# SPEC-004: Napi Lezárás, Naptár-Szinkron és Kognitív Feladatbontás

## Target Files
- `src/models/energy.py` (MODIFY — Add `ICSImportRequest`, `ICSImportResponse`, `ICSExportRequest`, `TaskDecomposeRequest`, `TaskDecomposeResponse`, `ShutdownSummaryRequest`, `ShutdownSummaryResponse`)
- `src/services/__init__.py` (MODIFY — Export new services)
- `src/services/calendar_sync.py` (NEW — `CalendarSyncService` for RFC 5545 `.ics` export/import)
- `src/services/decomposer_service.py` (NEW — `TaskDecomposer` for splitting large tasks into cognitive phases)
- `src/services/shutdown_service.py` (NEW — `ShutdownService` for circadian shutdown summary and melatonin gate)
- `src/api/routes.py` (MODIFY — Add 4 new REST endpoints)
- `frontend/index.html` (MODIFY — Add toolbar actions, Shutdown modal, ICS Import modal)
- `frontend/app.js` (MODIFY — Add export download, import parse, decompose handler, and shutdown ritual flow)
- `frontend/style.css` (MODIFY — Add styling for new modals and buttons)
- `tests/unit/test_calendar_sync.py` (NEW)
- `tests/unit/test_decomposer_service.py` (NEW)
- `tests/unit/test_shutdown_service.py` (NEW)

---

## Python Interface Definitions

```python
from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ICSExportRequest(BaseModel):
    scheduled_tasks: List[ScheduledSlot]
    calendar_name: str = Field(default="Cirkadián Energia Naptár")

class ICSImportRequest(BaseModel):
    ics_content: str = Field(..., min_length=10, description="Raw iCalendar RFC 5545 text")

class ICSImportResponse(BaseModel):
    imported_tasks: List[Task]
    imported_count: int
    message: str

class TaskDecomposeRequest(BaseModel):
    task: Task

class TaskDecomposeResponse(BaseModel):
    original_task_id: str
    subtasks: List[Task]
    total_duration_minutes: int
    decomposition_strategy: str

class ShutdownSummaryRequest(BaseModel):
    profile: EnergyProfile
    completed_tasks: List[Task]
    pending_tasks: List[Task]
    scheduled_slots: List[ScheduledSlot]
    current_time: Optional[str] = None

class ShutdownSummaryResponse(BaseModel):
    completed_count: int
    pending_count: int
    total_deep_work_minutes: int
    energy_debt_averted: float
    melatonin_gate_time: str      # 'HH:MM' (t_sleep - 60 min)
    minutes_until_melatonin: int
    tomorrow_first_peak: str       # 'HH:MM' (profile.peak_hours[0].start)
    recommendations: List[str]
    is_shutdown_recommended_now: bool
```

---

## Step-by-Step Implementation Details

### 1. `src/services/calendar_sync.py` (`CalendarSyncService`)
1. **`export_to_ics(slots: List[ScheduledSlot], calendar_name: str = "Cirkadián Energia Naptár") -> str`:**
   - Generál szabványos RFC 5545 `BEGIN:VCALENDAR ... END:VCALENDAR` szöveget (vagy `icalendar` / egyedi formázóval 0 függőséggel).
   - Eseményekhez: `SUMMARY:[🧠 Deep Work] Feladat neve`, `DTSTART`, `DTEND`, `DESCRIPTION`.
2. **`import_from_ics(ics_text: str) -> List[Task]`:**
   - Soronként végigpásztázza a `BEGIN:VEVENT ... END:VEVENT` blokkokat.
   - Kinyeri a `SUMMARY`, `DTSTART`, `DTEND` adatokat.
   - Minden importált eseményt `is_fixed=True`, `load_type=ADMIN` (vagy cím alapján NLP-vel felismerve), `fixed_start="HH:MM"`, és kiszámított `duration_minutes` mezőkkel ellátott `Task` objektummá alakít.

### 2. `src/services/decomposer_service.py` (`TaskDecomposer`)
1. **`decompose(task: Task) -> TaskDecomposeResponse`:**
   - Ha `task.duration_minutes <= 60`: Visszaadja az eredeti feladatot egyetlen elemként.
   - Ha `task.duration_minutes > 60`:
     - 3-fázisú kognitív dekompozíció:
       1. **Előkészítés & Koncepció:** $\approx 25\%$ időtartam $\rightarrow$ `CognitiveLoad.CREATIVE` (költség 6.0).
       2. **Mély Kivitelezés:** $\approx 50\%$ időtartam $\rightarrow$ `CognitiveLoad.DEEP_WORK` (költség 8.5–9.0, max 90m szeletekre bontva).
       3. **Befejezés, Review & Dokumentálás:** $\approx 25\%$ időtartam $\rightarrow$ `CognitiveLoad.ADMIN` (költség 3.0).
     - Minden új alfunkció egyedi UUID-t és beszédes nevet kap: `f"{task.title} — 1. Fázis: Koncepció & Tervezés"`, stb.

### 3. `src/services/shutdown_service.py` (`ShutdownService`)
1. **`create_summary(request: ShutdownSummaryRequest) -> ShutdownSummaryResponse`:**
   - Kiszámítja az összes elvégzett `deep_work` percet.
   - Melatonin-kapu ideje: $t_{sleep\_min} - 60\text{m}$.
   - Kiszámítja a hátralévő időt a melatonin-kapuig a `current_time` alapján.
   - Javaslatot generál a függőben maradt feladatok másnapi reggeli fókuszcsúcsba ($P_1$) történő áttolására.

### 4. `src/api/routes.py`
- `POST /api/v1/energy/calendar/export-ics`: Visszaadja a generált `.ics` naptárat `Response(content=..., media_type="text/calendar")` és letöltési fejléc formájában.
- `POST /api/v1/energy/calendar/import-ics`: Beolvassa a naptárat és visszaadja az importált fix feladatokat.
- `POST /api/v1/energy/decompose-task`: Dekomponálja a nagy feladatot.
- `POST /api/v1/energy/shutdown/summary`: Visszaadja az esti lezárási riportot.

---

## Unit Test Acceptance Criteria

* `test_export_to_ics_format`: Generates valid VCALENDAR/VEVENT format with DTSTART/DTEND and cognitive load prefix.
* `test_import_from_ics_parses_events`: Parses VEVENT blocks and converts them into `is_fixed=True` tasks.
* `test_decompose_large_task_into_3_phases`: Splits a 180min task into Creative, Deep Work, and Admin subtasks totaling 180min.
* `test_decompose_small_task_returns_single`: Returns 1 subtask if duration <= 60 min.
* `test_shutdown_summary_melatonin_gate`: Correctly computes melatonin gate 60 min before sleep time.
