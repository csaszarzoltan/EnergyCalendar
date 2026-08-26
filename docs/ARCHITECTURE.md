# Rendszerarchitektúra: Energia-Ritmus & Heti Rutin-Koreográfus

## 1. Rendszer-Áttekintés

Az **Energia-Ritmus & Heti Rutin-Koreográfus** a merev naptári időbeosztást felváltja a biológiai cirkadián ritmusra és a feladatok kognitív terhelésére épülő, dinamikus feladat-illesztési modellel.

```
                      +-----------------------------+
                      |       Felhasználó           |
                      | (NLP feladat, Napi profil)  |
                      +-----------------------------+
                                     │
                                     ▼
                      +-----------------------------+
                      |    FastAPI REST API         |
                      | (/api/v1/energy/*)          |
                      +-----------------------------+
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
    +-------------------------+             +-------------------------+
    |    EnergyCalculator     |             |       TaskParser        |
    | - 15 perces mintavétel  |             | - Regex & Heurisztika   |
    | - Gauss csúcs/mélypont  |             | - Kognitív osztályozás  |
    | - Kapacitás integrál    |             +-------------------------+
    +-------------------------+                          │
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     ▼
                      +-----------------------------+
                      |       EnergyScheduler       |
                      | - Fix blokkok maszkolása    |
                      | - Mohó CSP idősáv-illesztés |
                      | - 120m fókuszvédelem        |
                      | - Energy Debt riasztás      |
                      +-----------------------------+
```

## 2. Kulcskomponensek

1. **Modellek (`src/models/energy.py`):**
   - `CognitiveLoad`: `DEEP_WORK`, `CREATIVE`, `ADMIN`, `RECOVERY`.
   - `EnergyProfile`: `wake_time`, `sleep_time`, `peak_hours`, `dip_hours`.
   - `Task`: `id`, `title`, `duration_minutes`, `load_type`, `is_fixed`, `energy_cost`.
2. **Kalkulátor (`src/services/energy_calculator.py`):**
   - 96 pontos cirkadián görbe $E_{cap}(t) \in [0.0, 10.0]$ Gauss-eloszlással.
3. **Ütemező (`src/services/scheduler_service.py`):**
   - Kognitív terhelés illesztés és automatikus 20 perces pihenő blokk beillesztése.
4. **Elemző (`src/services/nlp_parser.py`):**
   - Szövegből felismeri a magyar és angol feladattípusokat és perceket.
