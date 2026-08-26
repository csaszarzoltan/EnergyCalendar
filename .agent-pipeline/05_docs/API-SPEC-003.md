# API Dokumentáció: Cirkadián Power Suite (v1.1.0)

> **Kiadás státusza:** COMPLETED & Verified (56/56 teszt sikeres)  
> **Modul:** Cirkadián Adaptáció & Biohacking  
> **Alap URL:** `http://localhost:8888/api/v1`

---

## 1. Új és Bővített Végpontok

| Metódus | Útvonal | Leírás |
|---|---|---|
| `POST` | `/api/v1/energy/schedule/reflow` | Dinamikus nap-újrahangolás a jelenlegi időponttól ($t_{now}$) |
| `POST` | `/api/v1/energy/caffeine-window` | Biológiailag optimális koffein-ablak és adenozin biztonsági ellenőrzés |
| `POST` | `/api/v1/energy/profile/curve` | Bővítve `sleep_quality` ($\gamma_{recovery} \in [0.3, 1.2]$) görbe-modulációval |

---

## 2. Részletes Specifikációk

### 2.1. `POST /api/v1/energy/schedule/reflow`
A hátralévő teendőket az aktuális időponttól ($t_{now}$) kezdődően szervezi újra a cirkadián csúcsokba és mélypontokba.

**Kérés:**
```json
{
  "profile": {
    "wake_time": "07:00",
    "sleep_time": "23:00",
    "peak_hours": [{"start": "09:00", "end": "11:30"}, {"start": "16:30", "end": "18:30"}],
    "dip_hours": [{"start": "13:30", "end": "15:00"}]
  },
  "current_time": "14:15",
  "pending_tasks": [
    {
      "id": "t-deep",
      "title": "Backend kódolás",
      "duration_minutes": 60,
      "load_type": "deep_work",
      "energy_cost": 8.5
    }
  ],
  "completed_task_ids": ["t-done-1"],
  "sleep_quality": 1.0
}
```

**Válasz (200 OK):**
```json
{
  "status": "ok",
  "reflow_time": "14:15",
  "scheduled_tasks": [
    {
      "task_id": "t-deep",
      "title": "Backend kódolás",
      "start_time": "16:30",
      "end_time": "17:30",
      "duration_minutes": 60,
      "load_type": "deep_work",
      "energy_cost": 8.5,
      "average_energy_level": 8.97
    }
  ],
  "debt_report": { ... },
  "caffeine_window": {
    "caffeine_start_time": "08:30",
    "caffeine_cutoff_time": "14:00",
    "is_safe_now": false,
    "adenosine_warning": "Figyelem! A koffein-cutoff időpont (14:00) már elmúlt..."
  }
}
```

---

### 2.2. `POST /api/v1/energy/caffeine-window`
Számítja a Cortisol Awakening Response (CAR) 90 perces késleltetését és a lefekvés előtti 9 órás koffein-stop határvonalat.

**Kérés:**
```json
{
  "profile": { "wake_time": "07:00", "sleep_time": "23:00" },
  "current_time": "10:30"
}
```

**Válasz (200 OK):**
```json
{
  "caffeine_start_time": "08:30",
  "caffeine_cutoff_time": "14:00",
  "peak_boost_start": "08:30",
  "peak_boost_end": "11:00",
  "is_safe_now": true,
  "adenosine_warning": "Biztonságos koffein ablak.",
  "recommendation": "Ideális időpont kávézásra a csúcs fókusz támogatásához."
}
```
