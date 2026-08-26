# Rendszerarchitektúra: Energia-Ritmus & Heti Rutin-Koreográfus (v1.2.0)

## 1. Rendszer-Áttekintés

Az **Energia-Ritmus & Heti Rutin-Koreográfus** a merev naptári időbeosztást felváltja a biológiai cirkadián ritmusra és a feladatok kognitív terhelésére épülő dinamikus optimalizálási modellel.

```
                      +---------------------------------------+
                      |             Felhasználó               |
                      | (NLP feladat, Napi profil, .ics file) |
                      +---------------------------------------+
                                          │
                                          ▼
                      +---------------------------------------+
                      |         FastAPI REST API              |
                      |        (/api/v1/energy/*)             |
                      +---------------------------------------+
                                          │
    ┌─────────────────┬───────────────────┼───────────────────┬─────────────────┐
    ▼                 ▼                   ▼                   ▼                 ▼
+--------------+ +-----------------+ +-------------+ +-----------------+ +---------------+
|EnergyCalc    | |EnergyScheduler  | |TaskParser   | |CalendarSync     | |TaskDecomposer |
|- 15m minták  | |- CSP illesztés  | |- Magyar/    | |- RFC 5545 .ics  | |- 3 fázisú     |
|- Gauss csúcs | |- Ripple Re-flow | |  angol NLP  | |  export/import  | |  feladatbontás|
|- Koffein CAR |- Sleep szigorítás | |- Kifejezés  | |- Fix maszkolás  | |  (Creative,   |
|- Alvás modul.| |- 120m fókuszvéd.| |  kinyerés   | |  ütközés ellen  | |   Deep, Admin)|
+--------------+ +-----------------+ +-------------+ +-----------------+ +---------------+
        │                 │                                                      │
        └─────────────────┼──────────────────────────────────────────────────────┤
                          ▼                                                      ▼
              +-----------------------+                              +-----------------------+
              |    Ütemezett Naptár   |                              |    ShutdownService    |
              | - Idősávok & Pihenők  |                              | - Melatonin-kapu      |
              | - Energy Debt Riport  |                              | - Napi Siker & Zárás  |
              +-----------------------+                              +-----------------------+
```

---

## 2. Kulcskomponensek és Szolgáltatások

### 2.1. Adatmodellek (`src/models/energy.py`)
- **`CognitiveLoad` (Enum):**
  - `DEEP_WORK`: Komplex kódolás, tanulás, stratégiai tervezés ($E \ge 7.5$).
  - `CREATIVE`: Ötletelés, UI/UX vázlat, írás ($5.0 \le E < 7.5$).
  - `ADMIN`: Email, számlák, mechanikus rutin ($E \le 4.5$).
  - `RECOVERY`: Kávészünet, séta, légzésgyakorlat (negatív energiaköltség: regenerál).
- **`EnergyProfile`:** Ébredési és alvási idő, egyéni fókuszcsúcsok (`peak_hours`) és délutáni mélypontok (`dip_hours`).
- **`Task`:** Egyedi azonosító, cím, időtartam percekben, kognitív terhelés, energiaköltség, `is_fixed` jelző fix naptári eseményekhez.
- **`ReflowRequest` & `ReflowResponse`:** Az aktuális időponttól ($t_{now}$) történő nap-újrahangolás adatmodelljei.
- **`ICSExportRequest`, `ICSImportRequest`, `ICSImportResponse`:** Naptár-interoperabilitási modellek.
- **`TaskDecomposeRequest`, `TaskDecomposeResponse`:** Kognitív feladatbontási modellek.
- **`ShutdownSummaryRequest`, `ShutdownSummaryResponse`:** Napi lezárási modellek.

### 2.2. Cirkadián Kalkulátor (`src/services/energy_calculator.py`)
- Kiszámítja a 96 mintavételi pontból álló $E_{cap}(t)$ folytonos függvényt a 24 órás skálán.
- **Koffein-Ablak:**
  - Cortisol Awakening Response (CAR) delay: $t_{wake} + 90\text{m}$.
  - Alvásvédő koffein-cutoff: $t_{sleep} - 9\text{h}$.
- **Alvásminőség Skálázás:** $\gamma_{recovery} \in [0.3, 1.2]$ szorzóval modulálja az energiaszint amplitúdóját.

### 2.3. Ütemező & Ripple Re-flow Motor (`src/services/scheduler_service.py`)
- **Mohó Korlát-Kielégítés (Greedy CSP):** A teendőket kognitív típusuk szerint a legmegfelelőbb szabad kapacitási résekbe illeszti.
- **Fókuszvédelem:** 120 perc folyamatos `DEEP_WORK` után automatikusan 20 perces `RECOVERY` blokkot szúr be.
- **Alvás-Függő Szigorítás:** Ha $\gamma_{recovery} \le 0.65$, a maximális mélymunka limit automatikusan **60 percre csökken**, a pihenő pedig **30 percre nő**.
- **Ripple Re-flow:** Az aktuális időpont ($t_{now}$) előtti perceket letiltja, a befejezett feladatokat megőrzi, és a fennmaradó teendőket jövőbeli szabad résekbe szervezi.

### 2.4. Naptár-Szinkronizáló (`src/services/calendar_sync.py`)
- **RFC 5545 `.ics` Export:** Kognitív emoji címkékkel (`[🧠 Deep Work]`, `[🔋 Regeneráció]`) formázott szabványos naptárfájlt generál.
- **RFC 5545 `.ics` Import:** Beolvassa a külső naptárakat, és a meglévő eseményeket fix feladatokká (`is_fixed=True`) alakítja, amelyek lemászkolják az idősávokat.

### 2.5. Kognitív Feladat-Dekompozíció (`src/services/decomposer_service.py`)
- A 60 percnél hosszabb, halogatásra hajlamosító feladatokat 3 fázisra bontja:
  1. Koncepció & Tervezés (`CREATIVE`, ~25% idő)
  2. Mély Kivitelezés (`DEEP_WORK`, ~50% idő)
  3. Review & Dokumentálás (`ADMIN`, ~25% idő)

### 2.6. Napi Lezárási Rituálé (`src/services/shutdown_service.py`)
- Összegzi a nap során elvégzett mélymunka órákat és az elkerült Energy Debt-et.
- Kiszámítja az esti Melatonin-Kaput ($t_{sleep} - 60\text{m}$) és a visszaszámlálót.
- Előkészíti a nyitott feladatokat a másnapi reggeli első fókuszcsúcsra.

---

## 3. Frontend Felépítés (`frontend/`)

- **Biolumineszcens Dark UI:** Sötét kékesszürke háttér, neon cián fókuszcsúcsok, aranysárga mélypontok és koffein zóna, lila kreatív sávok, smaragdzöld regenerációs kártyák.
- **HTML5 Canvas:** Spline Bezier görbével rajzolja ki a folytonos $E_{cap}(t)$ energiahullámot valós időben.
- **Web Audio API szintetizátor (0 Külső JS könyvtár):**
  - Aluláteresztő szűrővel formázott Barna Zaj (Brownian Noise).
  - Sztereó panneléssel elválasztott 210 Hz és 220 Hz szinuszhullám 10 Hz Alfa frekvenciás agyhullám stimulációhoz.
