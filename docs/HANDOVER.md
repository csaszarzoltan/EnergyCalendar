# EnergyCalendar — Teljes Ügynök Átadási Dokumentáció (Agent Handover Guide)

> **Verzió:** v1.2.0 (2026-08-26)  
> **Állapot:** 100% Zöld (76/76 teszt PASSED), Üzemkész, GitHubra feltöltve  
> **Cél:** Teljes kontextusátadás bármely bejövő AI kódoló/architekt ügynöknek (Hermes, Claude, GPT, Codex, Gemini, Antigravity).

---

## 1. Rendszer-Áttekintés & Termékvízió

Az **Energia-Ritmus & Heti Rutin-Koreográfus (EnergyCalendar)** egy olyan intelligens időszervező és naptárplatform, amely a naptári napot nem üres, merev óradobozokként, hanem a felhasználó **biológiai cirkadián energiaszintjeként ($E_{cap}(t)$)** kezeli.

### Fő Értékajánlatok:
1. **Biológiai Illesztés:** A nehéz, mély fókuszú munkát (`DEEP_WORK`) a természetes dopamin- és fókuszcsúcsokra (pl. 09:00–11:30 és 16:30–18:30) szervezi, a mechanikus feladatokat (`ADMIN`) a délutáni "kaja-kóma" mélypontra (13:30–15:00) helyezi.
2. **Kognitív Zuhanás & Kiégés Védelem:** Automatikus 20–30 perces regenerációs (`RECOVERY`) szüneteket iktat be 120 perc folyamatos mélymunka után, valamint valós idejű `Energy Debt` figyelmeztetést ad túlterhelés esetén.
3. **Koffein Zóna & Alvásvédelem (Biohacking):** 90 perces Cortisol Awakening Response (CAR) késleltetés reggel és 9 órás lefekvés előtti koffein-stop határvonal.
4. **Dinamikus Ripple Re-flow:** 1-kattintásos elcsúszás-kezelő: a pillanatnyi időponttól ($t_{now}$) kezdve újraszervezi a hátralévő napot bűntudat nélkül.
5. **Kétirányú Naptár-Interoperabilitás:** RFC 5545 szabványos `.ics` naptár export és import, amely a külső meetingeket automatikusan fix sávokként maszkolja a naptár-ütközések megelőzésére.
6. **AI Feladat-Dekompozíció:** A 60 percnél hosszabb feladatokat automatikusan 3 logikus fázisra (Kreatív előkészítés $\rightarrow$ Mély kivitelezés $\rightarrow$ Admin review) bontja.
7. **Napi Lezárási Rituálé (Daily Shutdown):** Feloldja a Zeigarnik-effektust, összegzi a napi sikereket, és visszaszámol az esti Melatonin Kapuig ($t_{sleep} - 60\text{m}$).
8. **Zavarmentes Zen Fókusz Szoba:** Natív Web Audio szintetizátorral előállított Barna Zaj (Brownian noise) és 10Hz Alfa Binaural Beats azonnali fókuszjavításhoz (0 külső függőség).

---

## 2. Architektúra & Komponens Térkép

```
                              ┌───────────────────────────┐
                              │  Frontend SPA (HTML/CSS)  │
                              │  - Canvas Bezier Görbe    │
                              │  - Web Audio Synthesizer  │
                              │  - Napi Lezárás & Modals  │
                              └─────────────┬─────────────┘
                                            │ HTTP / JSON
                                            ▼
                              ┌───────────────────────────┐
                              │     FastAPI Router        │
                              │     (src/api/routes.py)   │
                              └─────────────┬─────────────┘
                                            │
         ┌──────────────────┬───────────────┼───────────────┬──────────────────┐
         ▼                  ▼               ▼               ▼                  ▼
┌─────────────────┐┌─────────────────┐┌───────────┐┌─────────────────┐┌─────────────────┐
│ EnergyCalculator││ EnergyScheduler ││TaskParser ││CalendarSync     ││ TaskDecomposer  │
│ - 96 pontos     ││ - CSP bin-pack  ││- Magyar/  ││- RFC 5545 .ics  ││ - 3-fázisú      │
│   görbe         ││ - Ripple Re-flow││  Angol NLP││  export/import  ││   kognitív      │
│ - Koffein ablak ││ - Sleep szigor  ││  szabályok││- Fix maszkolás  ││   szeletelés    │
│ - Alvás skálázás││ - 120m/60m limit│└───────────┘└─────────────────┘└─────────────────┘
└─────────────────┘└─────────────────┘                                         │
                                                                               ▼
                                                                     ┌─────────────────┐
                                                                     │ ShutdownService │
                                                                     │ - Melatonin kapu│
                                                                     │ - Zeigarnik fix │
                                                                     └─────────────────┘
```

---

## 3. Matematikai & Algoritmikus Modellek

### 3.1. Cirkadián Kapacitás Görbe $E_{cap}(t)$
- A napot 96 darab 15 perces idősávra osztjuk ($t \in [0, 95]$).
- Alapértelmezett ébrenléti alapszint: $E_{base} = 5.0$, alvási szint: $E_{sleep} = 1.0$.
- A csúcsidőszakokban Gauss-függvény növeli a szintet:
  $$E_{peak}(t) = A_{peak} \cdot \exp\left(-\frac{(t - \mu_{peak})^2}{2\sigma^2}\right)$$
- A délutáni kaja-kóma mélypontban depresszió lép fel ($A_{dip} \approx 2.5$).
- **Alvásminőség moduláció ($\gamma_{recovery} \in [0.3, 1.2]$):**
  $$E_{cap}^{adj}(t) = E_{base} + (E_{cap}(t) - E_{base}) \times \gamma_{recovery}$$

### 3.2. Koffein Ablak & Kognitív Zuhanás Modell
- $t_{caff\_start} = (t_{wake} + 90\text{ perc}) \pmod{1440}$ (Cortisol Awakening Response védelem).
- $t_{caff\_cutoff} = (t_{sleep} - 540\text{ perc}) \pmod{1440}$ (9 órás lefekvés előtti alvásvédelem).
- Ha $t_{now} \ge t_{caff\_cutoff} \implies \text{is\_safe\_now} = \text{False}$, figyelmeztetés jelenik meg.

### 3.3. Dinamikus Ripple Re-flow Algoritmus
1. A korábbi időintervallumokat ($t < t_{current}$) a rendszer elérhetetlenként maszkolja le.
2. A befejezett feladatokat (`completed_task_ids`) kizárja.
3. Ha $\gamma_{recovery} \le 0.65$, a megengedett folyamatos mélymunka limit 120 percről **60 percre szigorodik**, és a szünet 30 percre nő.
4. A hátralévő feladatokat prioritás szerint (Mélymunka $\rightarrow$ Csúcsidő, Admin $\rightarrow$ Mélypont, Kreatív $\rightarrow$ Átlagos) helyezi el a jövőbeli szabad résekbe.

### 3.4. 3-Fázisú Kognitív Dekompozíció
- Ha a feladat hossza $T > 60\text{ perc}$:
  - **1. Fázis: Koncepció & Tervezés:** $T_1 = \text{round}(T \times 0.25) \implies \text{CREATIVE}$
  - **2. Fázis: Mély Kivitelezés:** $T_2 = \text{round}(T \times 0.50) \implies \text{DEEP\_WORK}$
  - **3. Fázis: Review & Dokumentálás:** $T_3 = T - T_1 - T_2 \implies \text{ADMIN}$

---

## 4. Fájltérkép & Könyvtárszerkezet

Minden fájl szigorúan a **max 400 sor/fájl** szabály alatt van tartva.

| Fájl | Sorok száma | Feladatkör |
|---|:---:|---|
| `src/models/energy.py` | 305 | Pydantic v2 domain modellek és enumnok |
| `src/services/energy_calculator.py` | 215 | 96 pontos cirkadián görbe és koffein matematika |
| `src/services/scheduler_service.py` | 280 | Mohó CSP ütemező és Ripple Re-flow motor |
| `src/services/calendar_sync.py` | 217 | RFC 5545 `.ics` Export és Import parszoló |
| `src/services/decomposer_service.py` | 86 | Kognitív feladatbontó algoritmus |
| `src/services/shutdown_service.py` | 115 | Napi lezárási rituálé és melatonin-kapu |
| `src/services/nlp_parser.py` | 175 | Természetes nyelvű szabály/regex parszoló |
| `src/api/routes.py` | 190 | FastAPI REST végpontok (`/api/v1/energy/*`) |
| `src/main.py` | 55 | FastAPI alkalmazásgyár és statikus fájl mount |
| `frontend/index.html` | 313 | Biolumineszcens sötét témájú UI, modalok és vezérlők |
| `frontend/app.js` | 380 | Canvas görbe, Web Audio szintetizátor, REST kliens |
| `frontend/style.css` | 390 | Neon stílusok, animációk, pulzáló idősávok |

---

## 5. Fejlesztői & Ügynök Parancsok

### Alkalmazás futtatása
```bash
python -m uvicorn src.main:app --host 127.0.0.1 --port 8888
```
- Web felület: `http://localhost:8888`
- Interaktív Swagger API dokumentáció: `http://localhost:8888/docs`

### Teljes Tesztcsomag Futtatása (76 Teszt)
```bash
pytest -v
```

### Csak E2E Tesztek Futtatása
```bash
pytest .agent-pipeline/03_e2e_suites/ -v
```

### Szintaxis & Típus Ellenőrzés
```bash
python -m compileall -q src tests
```

---

## 6. Folyamatban Lévő Pipeline Státusz (`.agent-pipeline/`)

A feladatok a `manifest.json` alapján állapotkövetettek:
- **`SPEC-001` (Backend Core):** `COMPLETED` (`.agent-pipeline/02_specs/done/SPEC-001-...md`)
- **`SPEC-002` (Frontend SPA):** `COMPLETED` (`.agent-pipeline/02_specs/done/SPEC-002-...md`)
- **`SPEC-003` (Circadian Power Suite):** `COMPLETED` (`.agent-pipeline/02_specs/done/SPEC-003-...md`)
- **`SPEC-004` (Advanced Suite):** `COMPLETED` (`.agent-pipeline/02_specs/done/SPEC-004-...md`)

---

## 7. Következő Sprint Javaslatok (Roadmap v1.3.0 & v2.0.0)

Ha folytatni szeretnéd a projekt fejlesztését, az alábbi kiemelt modulok következnek:

1. **Sprint v1.3.0: Biometrikus & Wearable Integráció (HRV & Alvásadat Sync):**
   - Integráció Oura Ring, Apple HealthKit vagy Whoop API-kkal.
   - Az alvásminőség (`sleep_quality`) automatikus beolvasása az ébredési pulzus és HRV alapján (a manuális csúszka helyett).
2. **Sprint v1.4.0: Heti Makro-Koreográfus (Weekly Rhythm Matrix):**
   - 7 napos nézet: a hétfői fókuszterhelés kiegyenlítése a pénteki alacsonyabb kognitív kapacitással.
   - Heti meeting-mentes "Deep Work Csütörtök" automatikus kijelölése.
3. **Sprint v2.0.0: Valós Idejű WebPush / Hangos Átmeneti Figyelmeztetések:**
   - Hangos vagy rendszerértesítés, amikor a felhasználó átlép a Koffein Cutoff zónába vagy amikor kezdődik a Melatonin Kapu.
