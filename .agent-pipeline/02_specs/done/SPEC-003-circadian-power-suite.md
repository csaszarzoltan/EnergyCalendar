# SPEC-003: Cirkadián Power Suite — Re-flow, Koffein és Zen Fókusz

## Target Files
- `src/models/energy.py` (MODIFY — Add `CaffeineWindowResponse`, `ReflowRequest`, `ReflowResponse`, `SleepQualityOption`)
- `src/services/energy_calculator.py` (MODIFY — Support `sleep_quality` factor $\gamma_{recovery} \in [0.3, 1.2]$, and `calculate_caffeine_window()`)
- `src/services/scheduler_service.py` (MODIFY — Add `reflow_schedule()` with `current_time` constraint and sleep-tightened deep work thresholds)
- `src/api/routes.py` (MODIFY — Add `POST /api/v1/energy/schedule/reflow`, `POST /api/v1/energy/caffeine-window`)
- `frontend/index.html` (MODIFY — Add Re-flow button, sleep quality slider, caffeine overlay toggle, and Zen Focus Modal)
- `frontend/app.js` (MODIFY — Add Re-flow client handler, Caffeine gold overlay drawing, Web Audio synthetic noise generator, and Zen Timer)
- `frontend/style.css` (MODIFY — Add gold caffeine glow and Zen modal styles)
- `tests/unit/test_reflow_service.py` (NEW)
- `tests/unit/test_caffeine_service.py` (NEW)

---

## Python Interface Definitions

```python
from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CaffeineWindowResponse(BaseModel):
    caffeine_start_time: str   # 'HH:MM' (t_wake + 90 min)
    caffeine_cutoff_time: str  # 'HH:MM' (t_sleep - 9 hours)
    peak_boost_start: str      # 'HH:MM' (t_wake + 90 min)
    peak_boost_end: str        # 'HH:MM' (t_wake + 240 min)
    is_safe_now: bool          # True if current_time < caffeine_cutoff_time
    adenosine_warning: str
    recommendation: str

class ReflowRequest(BaseModel):
    profile: EnergyProfile
    current_time: str = Field(..., description="Aktuális időpont 'HH:MM', pl. '14:15'")
    pending_tasks: List[Task] = Field(..., description="Hátralévő, el nem végzett feladatok")
    completed_task_ids: List[str] = Field(default_factory=list, description="Már befejezett feladatok ID-jai")
    sleep_quality: float = Field(default=1.0, ge=0.3, le=1.2, description="Alvásminőség szorzó 0.3 - 1.2")

class ReflowResponse(BaseModel):
    status: str = "ok" # "ok" | "warning"
    reflow_time: str
    scheduled_tasks: List[ScheduledSlot]
    unscheduled_tasks: List[Task] = []
    debt_report: EnergyDebtReport
    energy_curve: List[EnergyCurvePoint]
    caffeine_window: CaffeineWindowResponse
```

---

## Step-by-Step Implementation Details

### 1. `src/services/energy_calculator.py`
1. **`calculate_caffeine_window(profile: EnergyProfile, current_time: Optional[str] = None) -> CaffeineWindowResponse`:**
   - $t_{wake}$ percekben $\rightarrow t_{start} = t_{wake} + 90\text{m}$.
   - $t_{sleep}$ percekben $\rightarrow t_{cutoff} = (t_{sleep\_min} - 540\text{m}) \pmod{1440}$.
   - $t_{boost\_end} = t_{wake} + 240\text{m}$.
   - Ha $current\_time$ meg van adva: $t_{cur} \ge t_{cutoff} \rightarrow is\_safe\_now = False$, különben $True$.
2. **`generate_curve()` bővítése `sleep_quality: float = 1.0` paraméterrel:**
   - Amplitúdók modulálása: $A_{peak} = A_{peak} \times \gamma_{recovery}$.
   - Ha $\gamma_{recovery} < 0.7$, a mélypont depresszió mélyebb: $A_{dip} = A_{dip} \times 1.25$.
   - Normalizálás $[0.0, 10.0]$ között.

### 2. `src/services/scheduler_service.py`
1. **`reflow_schedule(request: ReflowRequest) -> ScheduleResponse`:**
   - $t_{cur\_min} = \text{time\_to\_minutes}(request.current\_time)$.
   - Az ütemezési időszeletek kizárólag a $[t_{cur\_min}, t_{sleep\_min}]$ tartományban szabadok. A $t < t_{cur\_min}$ időpontok foglaltnak tekintendők.
   - **Alvásminőség szerinti korlát:** Ha $request.sleep\_quality \le 0.65$, a maximális összefüggő `DEEP_WORK` limit 60 percre szigorodik (120 helyett), és a beillesztett `RECOVERY` szünet 30 perc.
   - A hátralévő feladatokat a szabad jövőbeli sávokba illeszti.

### 3. Web Audio API & Zen Fókusz Mód (`frontend/app.js`)
1. **Brown Noise & 10Hz Alpha Binaural Beats szintézis:**
   - AudioContext, White noise buffer integrálása barna zajhoz, és sztereó szeparált oszcillátorok (pl. 210Hz bal, 220Hz jobb) az alfa agyhullámok stimulálásához.
   - Hangerőszabályzó és Start/Stop kapcsoló.
2. **Koffein Zóna Vizuális Megjelenítés:**
   - A Canvas görbén finom arany színátmenetes sáv jelenik meg a $[t_{start}, t_{cutoff}]$ tartományban egy kávé ikonnal.

---

## Unit Test Acceptance Criteria

* `test_caffeine_window_calculation`: Correctly calculates 90min delay and 9h cutoff before bedtime.
* `test_caffeine_window_late_warning`: Returns `is_safe_now=False` after cutoff time.
* `test_sleep_quality_curve_modulation`: Lower sleep quality produces lower peak energy levels.
* `test_reflow_schedules_only_in_future`: Tasks are only placed at or after `current_time`.
* `test_reflow_tightens_deep_work_limit_on_low_sleep`: When `sleep_quality=0.5`, auto-recovery is inserted after 60m of deep work.
