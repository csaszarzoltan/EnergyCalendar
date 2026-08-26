# API Dokumentáció: Advanced Productivity Suite (v1.2.0)

> **Kiadás státusza:** COMPLETED & Verified (76/76 teszt sikeres)  
> **Modul:** Mindful Productivity & Interoperabilitás  
> **Alap URL:** `http://localhost:8888/api/v1`

---

## 1. Új Végpontok Áttekintése

| Metódus | Útvonal | Leírás |
|---|---|---|
| `POST` | `/api/v1/energy/calendar/export-ics` | RFC 5545 `.ics` naptár export kognitív terhelési címkékkel |
| `POST` | `/api/v1/energy/calendar/import-ics` | Külső `.ics` naptár beolvasása és ütközésvédő fix feladattá konvertálása |
| `POST` | `/api/v1/energy/decompose-task` | Nagy összetett feladat ($>60\text{m}$) 3 fázisú kognitív dekompozíciója |
| `POST` | `/api/v1/energy/shutdown/summary` | Cirkadián esti lezárási riport és melatonin-kapu visszaszámláló |

---

## 2. Részletes Végpont Specifikációk

### 2.1. `POST /api/v1/energy/calendar/export-ics`
Generál egy RFC 5545 szabványos naptárfájlt.

**Kérés:**
```json
{
  "scheduled_tasks": [
    {
      "task_id": "t1",
      "title": "Backend fejlesztés",
      "start_time": "09:00",
      "end_time": "10:30",
      "duration_minutes": 90,
      "load_type": "deep_work",
      "energy_cost": 9.0,
      "average_energy_level": 9.15
    }
  ],
  "calendar_name": "Cirkadián Energia Naptár"
}
```

**Válasz (200 OK):**
`Content-Type: text/calendar`
```text
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//EnergyCalendar//Circadian Rhythm Choreographer//HU
X-WR-CALNAME:Cirkadián Energia Naptár
BEGIN:VEVENT
UID:t1-...@energycalendar.local
SUMMARY:[🧠 Deep Work] Backend fejlesztés
DTSTART:...T090000
DTEND:...T103000
END:VEVENT
END:VCALENDAR
```

---

### 2.2. `POST /api/v1/energy/decompose-task`
Felbont egy nehéz feladatot 3 fázisra: Kreatív előkészítés $\rightarrow$ Mély kivitelezés $\rightarrow$ Admin review.

**Kérés:**
```json
{
  "task": {
    "id": "t-big",
    "title": "Új mikroszolgáltatás megírása",
    "duration_minutes": 180,
    "load_type": "deep_work",
    "energy_cost": 9.0
  }
}
```

**Válasz (200 OK):**
```json
{
  "original_task_id": "t-big",
  "total_duration_minutes": 180,
  "decomposition_strategy": "3-Phase Cognitive Splitting",
  "subtasks": [
    { "title": "Új mikroszolgáltatás megírása — 1. Fázis: Koncepció & Tervezés", "duration_minutes": 45, "load_type": "creative" },
    { "title": "Új mikroszolgáltatás megírása — 2. Fázis: Mély Kivitelezés", "duration_minutes": 90, "load_type": "deep_work" },
    { "title": "Új mikroszolgáltatás megírása — 3. Fázis: Review & Dokumentálás", "duration_minutes": 45, "load_type": "admin" }
  ]
}
```

---

### 2.3. `POST /api/v1/energy/shutdown/summary`
Kiszámítja az esti melatonin-kaput ($t_{sleep} - 60\text{m}$) és a napi kognitív statisztikát.

**Válasz (200 OK):**
```json
{
  "completed_count": 5,
  "pending_count": 0,
  "total_deep_work_minutes": 150,
  "energy_debt_averted": 0.0,
  "melatonin_gate_time": "22:00",
  "minutes_until_melatonin": 199,
  "tomorrow_first_peak": "09:00",
  "recommendations": [ ... ],
  "is_shutdown_recommended_now": false
}
```
