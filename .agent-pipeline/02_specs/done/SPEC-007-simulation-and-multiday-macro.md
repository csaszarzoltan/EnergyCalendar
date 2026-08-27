# SPEC-007: Cirkadián Időgép Szimulációs Motor és Heti Makro Ütemezés (v1.5.0)

## 1. Célkitűzés
Valós idejű időgép állapotgép (Simulation State Engine) megvalósítása a cirkadián fázisok dinamikus lekövetésére és a heti 7 napos makro-terhelés optimalizálására.

## 2. API Szerződések
- `POST /api/v1/energy/simulation/tick`
  - Input: `{ "current_time": "10:30", "profile": EnergyProfile, "tasks": List[TaskItem] }`
  - Output: `{ "current_time": "10:30", "energy_level": 8.7, "active_zone": "PEAK", "active_task": Optional[str], "caffeine_allowed": true, "melatonin_minutes_remaining": 660, "neuro_guidance": "Csúcsidőszak: Ne engedd a kontextusváltást!" }`
