# API Dokumentáció: Energia-Ritmus & Heti Rutin-Koreográfus (v1.0.0)

> **Kiadás státusza:** COMPLETED & Verified  
> **Backend:** FastAPI (Python 3.11+)  
> **Alap URL:** `http://localhost:8000/api/v1`

---

## 1. Végpontok Áttekintése

| Metódus | Útvonal | Leírás |
|---|---|---|
| `GET` | `/api/v1/health` | Rendszer állapotellenőrzés (Health check) |
| `POST` | `/api/v1/energy/profile/curve` | 24 órás folytonos $E_{cap}(t)$ görbe generálása 15 perces mintavételezéssel |
| `POST` | `/api/v1/energy/schedule` | Feladat-koreográfia futtatása, idősáv-illesztés, fókuszvédelem és Energy Debt |
| `POST` | `/api/v1/energy/parse-task` | Természetes nyelvű feladatbontó (időtartam és kognitív terhelés kinyerése) |

---

## 2. Részletes Végpont Specifikációk

### 2.1. `GET /api/v1/health`
Ellenőrzi a webszolgáltatás elérhetőségét.

**Válasz (200 OK):**
```json
{
  "status": "ok",
  "service": "energy-calendar",
  "version": "1.0.0"
}
```

---

### 2.2. `POST /api/v1/energy/profile/curve`
Kiszámítja és visszaadja a nap 96 darab 15 perces időszeletéhez tartozó energiaszinteket és cirkadián zónákat (`peak`, `dip`, `moderate`, `sleep`).

**Kérés törzs:**
```json
{
  "wake_time": "07:00",
  "sleep_time": "23:00",
  "peak_hours": [
    {"start": "09:00", "end": "11:30"},
    {"start": "16:30", "end": "18:30"}
  ],
  "dip_hours": [
    {"start": "13:30", "end": "15:00"}
  ]
}
```

**Válasz (200 OK):**
```json
{
  "points": [
    {
      "time": "09:00",
      "minute_of_day": 540,
      "energy_level": 8.52,
      "zone_type": "peak"
    },
    {
      "time": "14:00",
      "minute_of_day": 840,
      "energy_level": 2.85,
      "zone_type": "dip"
    }
  ],
  "profile": { ... }
}
```

---

### 2.3. `POST /api/v1/energy/schedule`
Optimalizált idősáv-kiosztást végez a megadott feladatokra az $E_{cap}(t)$ görbéhez illesztve.

**Kiemelt Üzleti Szabályok:**
1. **Mély munka (`DEEP_WORK`):** A legmagasabb átlagos energiaszintű csúcsidőszakokba kerül.
2. **120 perces Fókuszkorlát:** Egymást követő $\ge 120$ perc mélymunka esetén automatikusan beilleszt egy 20 perces `RECOVERY` blokkot.
3. **Admin feladatok (`ADMIN`):** Az energiamélypontokra (post-lunch dip) szerveződnek.
4. **Kognitív Adósság (`EnergyDebtReport`):** Ha a kért terhelés meghaladja a napi kapacitást, a válasz státusza `"warning"`, részletes adósságmutatókkal.

**Kérés törzs:**
```json
{
  "profile": {
    "wake_time": "07:00",
    "sleep_time": "23:00",
    "peak_hours": [{"start": "09:00", "end": "11:30"}],
    "dip_hours": [{"start": "13:30", "end": "15:00"}]
  },
  "tasks": [
    {
      "id": "t1",
      "title": "Backend architektúra tervezés",
      "duration_minutes": 90,
      "load_type": "deep_work",
      "energy_cost": 9.0
    },
    {
      "id": "t2",
      "title": "E-mailek és számlák",
      "duration_minutes": 45,
      "load_type": "admin",
      "energy_cost": 3.0
    }
  ]
}
```

**Válasz (200 OK):**
```json
{
  "status": "ok",
  "scheduled_tasks": [
    {
      "task_id": "t1",
      "title": "Backend architektúra tervezés",
      "start_time": "09:00",
      "end_time": "10:30",
      "duration_minutes": 90,
      "load_type": "deep_work",
      "energy_cost": 9.0,
      "is_auto_recovery": false,
      "average_energy_level": 9.15
    },
    {
      "task_id": "t2",
      "title": "E-mailek és számlák",
      "start_time": "13:30",
      "end_time": "14:15",
      "duration_minutes": 45,
      "load_type": "admin",
      "energy_cost": 3.0,
      "is_auto_recovery": false,
      "average_energy_level": 2.75
    }
  ],
  "unscheduled_tasks": [],
  "debt_report": {
    "total_capacity": 4850.0,
    "total_requested_load": 945.0,
    "energy_debt": 0.0,
    "is_overloaded": false,
    "exhaustion_percentage": 19.48,
    "recommendation": "Fenntartható terhelés. Jóváhagyva."
  },
  "energy_curve": [ ... ]
}
```

---

### 2.4. `POST /api/v1/energy/parse-task`
Szöveges bemenetből azonosítja a címet, időtartamot és a terhelési kategóriát.

**Kérés:**
```json
{
  "raw_text": "Kódolás: új auth modul 90 perc"
}
```

**Válasz (200 OK):**
```json
{
  "title": "új auth modul",
  "duration_minutes": 90,
  "load_type": "deep_work",
  "energy_cost": 8.5,
  "confidence": 0.9
}
```
