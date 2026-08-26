# SPEC-001: Cirkadián Energia-Ritmus és Feladat-Koreográfus Backend

## Target Files
- `src/__init__.py` (NEW)
- `src/models/__init__.py` (NEW)
- `src/models/energy.py` (NEW)
- `src/services/__init__.py` (NEW)
- `src/services/energy_calculator.py` (NEW)
- `src/services/scheduler_service.py` (NEW)
- `src/services/nlp_parser.py` (NEW)
- `src/api/__init__.py` (NEW)
- `src/api/routes.py` (NEW)
- `src/main.py` (NEW)
- `tests/unit/test_energy_calculator.py` (NEW)
- `tests/unit/test_scheduler_service.py` (NEW)
- `tests/unit/test_nlp_parser.py` (NEW)
- `tests/unit/test_api_routes.py` (NEW)

---

## Python Interface Definitions

```python
from __future__ import annotations
from enum import Enum
from datetime import time, timedelta
from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field, field_validator
from uuid import UUID, uuid4

class CognitiveLoad(str, Enum):
    DEEP_WORK = "deep_work"       # Kognitív költség súly: 8.0 - 10.0
    CREATIVE = "creative"         # Kognitív költség súly: 5.0 - 7.0
    ADMIN = "admin"               # Kognitív költség súly: 2.0 - 4.0
    RECOVERY = "recovery"         # Negatív kognitív költség: -2.0 - -5.0 (töltődés)

class TimeInterval(BaseModel):
    start: str = Field(..., description="Időpont 'HH:MM' formátumban, pl. '09:00'")
    end: str = Field(..., description="Időpont 'HH:MM' formátumban, pl. '11:30'")

    @field_validator("start", "end")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError("Time must be in 'HH:MM' format")
        h, m = int(parts[0]), int(parts[1])
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("Hour must be 0-23 and minute must be 0-59")
        return f"{h:02d}:{m:02d}"

class EnergyProfile(BaseModel):
    wake_time: str = Field(default="07:00", description="Ébredés ideje 'HH:MM'")
    sleep_time: str = Field(default="23:00", description="Lefekvés ideje 'HH:MM'")
    peak_hours: List[TimeInterval] = Field(
        default_factory=lambda: [
            TimeInterval(start="09:00", end="11:30"),
            TimeInterval(start="16:30", end="18:30")
        ]
    )
    dip_hours: List[TimeInterval] = Field(
        default_factory=lambda: [
            TimeInterval(start="13:30", end="15:00")
        ]
    )

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., min_length=1)
    duration_minutes: int = Field(..., gt=0, le=720)
    load_type: CognitiveLoad = Field(...)
    deadline: Optional[str] = Field(default=None, description="'HH:MM' formátum ha van határidő")
    is_fixed: bool = Field(default=False, description="Fix naptári esemény ha True")
    fixed_start: Optional[str] = Field(default=None, description="Fix esemény kezdete 'HH:MM'")
    energy_cost: float = Field(default=5.0, ge=-10.0, le=10.0)

class ScheduledSlot(BaseModel):
    task_id: str
    title: str
    start_time: str # 'HH:MM'
    end_time: str   # 'HH:MM'
    duration_minutes: int
    load_type: CognitiveLoad
    energy_cost: float
    is_auto_recovery: bool = False
    average_energy_level: float

class EnergyDebtReport(BaseModel):
    total_capacity: float
    total_requested_load: float
    energy_debt: float
    is_overloaded: bool
    exhaustion_percentage: float # 0.0 - 100.0+ %
    recommendation: str

class EnergyCurvePoint(BaseModel):
    time: str # 'HH:MM'
    minute_of_day: int
    energy_level: float # 0.0 - 10.0
    zone_type: str # 'peak' | 'dip' | 'moderate' | 'sleep'

class EnergyCurveResponse(BaseModel):
    points: List[EnergyCurvePoint]
    profile: EnergyProfile

class ScheduleRequest(BaseModel):
    profile: EnergyProfile
    tasks: List[Task]

class ScheduleResponse(BaseModel):
    status: str = "ok" # "ok" | "warning"
    scheduled_tasks: List[ScheduledSlot]
    unscheduled_tasks: List[Task] = []
    debt_report: EnergyDebtReport
    energy_curve: List[EnergyCurvePoint]

class TaskParseRequest(BaseModel):
    raw_text: str

class TaskParseResponse(BaseModel):
    title: str
    duration_minutes: int
    load_type: CognitiveLoad
    energy_cost: float
    confidence: float
```

---

## Step-by-Step Implementation Details

### 1. `src/services/energy_calculator.py` (`EnergyCalculator`)
1. **Idő konverziók:** Segédfüggvények `time_to_minutes(hh_mm: str) -> int` és `minutes_to_time(m: int) -> str`.
2. **Görbe számítás (`generate_curve`):**
   - Felosztja a napot 15 perces időszeletekre ($0, 15, 30, \dots, 1425$).
   - Alapérték: Alvásidőben ($t < t_{wake}$ vagy $t \ge t_{sleep}$) $E(t) = 1.0$.
   - Ébrenléti alapérték $E_{base} = 5.0$.
   - Fókuszcsúcsok (`peak_hours`): Gauss-súlyozással emeli az energiaszintet $8.5 - 9.8$ közötti értékre.
   - Mélypontok (`dip_hours`): Csökkenti az energiaszintet $2.0 - 3.5$ közötti értékre.
   - Normalizálás: Az értékek szigorúan $[0.0, 10.0]$ tartományba szorítandók (`min(10.0, max(0.0, val))`).
3. **Zóna besorolás:**
   - $E \ge 7.5$: `'peak'`
   - $E \le 4.0$: `'dip'`
   - $4.0 < E < 7.5$: `'moderate'`
   - alvásidő: `'sleep'`
4. **Szabad kapacitás maszk:** Levonja a fix események (`is_fixed=True`) idejét a szabad intervallumokból.

### 2. `src/services/scheduler_service.py` (`EnergyScheduler`)
1. **Fix események lerakása:** Minden `is_fixed=True` és `fixed_start` meglévő feladat közvetlenül lefoglalja az időszeleteket. Ha átfedés van két fix esemény között, `ValueError("Fixed tasks conflict")` hibát dob.
2. **Dinamikus feladatok prioritási sorrendje:**
   - `DEEP_WORK` (legnagyobb kognitív súlyúak elöl).
   - `CREATIVE`.
   - `ADMIN`.
   - `RECOVERY` (felhasználó által felvett manuális pihenők).
3. **Optimális idősáv keresés:**
   - `DEEP_WORK`: Olyan összefüggő szabad idősávot keres, ahol az átlagos $E_{cap}(t)$ maximális (ideálisan $\ge 7.5$).
   - **120 perces mélymunka védelem:** Számolja az egymást követő `DEEP_WORK` perceket. Ha egy új blokkal elérné vagy meghaladná a 120 percet, automatikusan beiktat egy 20 perces `RECOVERY` feladatot (`is_auto_recovery=True`, `energy_cost=-3.0`, `title="Automatikus Kognitív Regeneráció"`), és csak utána folytatja a munkát.
   - `ADMIN`: Olyan idősávot keres, ahol az $E_{cap}(t)$ a legalacsonyabb ($E_{cap} \le 4.5$, mélypontok), hogy ne pazaroljon értékes csúcsidőt adminisztrációra.
   - `CREATIVE`: A közepes energiasávokba ($4.5 - 7.5$) illeszti.
4. **Energy Debt (Kognitív Adósság) kalkuláció:**
   - Kiszámítja az összes igényelt terhelést: $\sum (cost \times duration)$.
   - Kiszámítja a teljes rendelkezésre álló ébrenléti energiát.
   - Ha a terheltség meghaladja a kapacitást, `is_overloaded = True`, `energy_debt = requested - capacity`, és a válasz státusza `"warning"`.

### 3. `src/services/nlp_parser.py` (`TaskParser`)
1. Szabály- és mintaalapú felismerő magyar és angol kulcsszavakra:
   - Deep work kulcsszavak: `["kódolás", "tanulás", "architektúra", "fejlesztés", "írás", "tervezés", "coding", "study", "deep work", "refactor"]` -> `CognitiveLoad.DEEP_WORK`, cost: 8.5.
   - Creative kulcsszavak: `["ötletelés", "brainstorm", "design", "vázlat", "UI", "koncepció", "kreatív"]` -> `CognitiveLoad.CREATIVE`, cost: 6.0.
   - Admin kulcsszavak: `["e-mail", "számla", "rendszerezés", "hívás", "admin", "takarítás", "meeting", "egyeztetés"]` -> `CognitiveLoad.ADMIN`, cost: 3.0.
   - Recovery kulcsszavak: `["séta", "edzés", "ebéd", "kávé", "pihenő", "szünet", "meditáció", "walk", "break", "gym"]` -> `CognitiveLoad.RECOVERY`, cost: -3.0.
2. Időtartam kinyerése: Regex keresés percekre (`r'(\d+)\s*(perc|m|min|ó|óra|h|hour)'` -> percre számolva). Ha nincs megadva, alapértelmezett 45 perc.

### 4. `src/api/routes.py` és `src/main.py`
- `POST /api/v1/energy/profile/curve`: Visszaadja a 15 perces mintavételezésű görbét és zónákat.
- `POST /api/v1/energy/schedule`: Elvégzi a teljes koreográfiát és visszaadja az ütemezett kapszulákat és az Energy Debt riportot.
- `POST /api/v1/energy/parse-task`: NLP szövegbontás.
- `GET /api/v1/health`: `{"status": "ok", "service": "energy-calendar"}`.
- Global exception handler: `ValueError` -> `400 Bad Request`, egyéb -> `500`.

---

## Unit Test Acceptance Criteria (`pytest`)

* `test_calculate_energy_curve_points`: Generates exactly 96 points for a 24-hour day (15-min sampling), with peaks >8.0 and dips <4.0.
* `test_schedule_deep_work_in_peak_window`: Verifies deep work task is placed in peak hours.
* `test_schedule_admin_in_dip_window`: Verifies admin task is placed during lunch dip.
* `test_auto_recovery_insertion_after_120min_deep_work`: Verifies automatic recovery slot inserted when consecutive deep work exceeds 120 mins.
* `test_energy_debt_detection_when_overloaded`: Verifies warning status and positive energy_debt when tasks exceed capacity.
* `test_fixed_event_conflict_raises_error`: Raises `ValueError` if two fixed events overlap.
* `test_nlp_parse_hungarian_keywords`: Correctly parses "Kódolás 90 perc" into `DEEP_WORK` and duration 90.
