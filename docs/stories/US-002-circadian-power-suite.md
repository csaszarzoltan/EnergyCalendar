# US-002: Cirkadián Power Suite — Re-flow, Koffein és Zen Fókusz

- **Epic:** Cirkadián Adaptáció & Biohacking
- **Prioritás:** P0
- **Forrás:** `docs/research/2026-08-26-circadian-feature-expansion-deep-dive.md` + `docs/decisions/ADR-002-circadian-power-suite.md`
- **Prototípus:** `http://localhost:8888` — Státusz: `approved`

---

## Story
**As a** modern tudásmunkás / egyetemista  
**I want** ha elcsúszik a napom, egyetlen kattintással újrahangolni a hátralévő teendőimet, látni a biológiailag optimális koffein-ablakomat, és zavartalan fókusz-módban dolgozni natív hangtérrel  
**So that** bűntudat nélkül adaptálódjak a valósághoz, megvédjem az éjszakai mélyalvásomat, és azonnal mély fókuszba kerüljek.

---

## Acceptance Criteria (Gherkin BDD)

### AC1 (Happy path — Dinamikus Ripple Re-flow):
- **given** a felhasználó 14:15-kor csúszásban van 1 db függőben lévő `DEEP_WORK` és 1 db `ADMIN` feladattal
- **when** meghívja a `/api/v1/energy/schedule/reflow` végpontot `current_time="14:15"` értékkel
- **then** a rendszer a már elmúlt időszakot levédi, az `ADMIN` feladatot a még tartó 14:15-15:00 mélypontra teszi, a `DEEP_WORK` feladatot pedig a 16:30-18:30 délutáni fókuszcsúcsra ütemezi át.

### AC2 (Edge case — Alvásminőség és Korlátozás-Szigorítás):
- **given** a felhasználó alvásminősége alacsony (`sleep_quality = 0.5` / 50%)
- **when** az energiamodell kiszámításra kerül
- **then** az $E_{cap}(t)$ görbe amplitúdója lecsökken, a folyamatos mélymunka limit automatikusan 60 percre szigorodik, és 30 perces regeneráció kerül beillesztésre.

### AC3 (Error / Warning state — Késői Koffein Figyelmeztetés):
- **given** egy 23:00 lefekvési idővel rendelkező profil
- **when** a koffein-ablak lekérdezésre kerül
- **then** a rendszer a `caffeine_cutoff` időt pontosan 14:00-ra határozza meg ($t_{sleep} - 9\text{h}$), és 14:00 után `is_safe_for_caffeine = False` figyelmeztetést ad.

### AC4 (GUI Flow Contract — Zen Fókusz Mód és Valós Idejű Vezérlők):
- **given** a felhasználó rákattint egy feladatkapszula "Fókusz" gombjára
- **when** a Zen Modal megnyílik (`id="zen-focus-modal"`)
- **then** elindul a vizuális fókusz-időzítő, a bekapcsolható natív Web Audio szintetizátor (Brown Noise / Binaural Beats), és a feladat befejezésekor a "Befejezve & Újrahangolás" gomb automatikusan lefrissíti a hátralévő napot.

---

## gui_flow (UI Kontraktus)

1. **Header Controls:**
   - Alvásminőség csúszka: `input[id="sleep-quality-slider"]` (tartomány: 30% - 100%).
   - Koffein Zóna gomb: `button[id="btn-toggle-caffeine"]` -> arany zóna be/ki kapcsolása a Canvas hullámon.
   - Re-flow gomb: `button[id="btn-reflow-now"]` -> aktuális időponttól áthullámoztatja a feladatokat.
2. **Interactive Zen Mode:**
   - Kapszula kattintás -> Megjelenik a `#zen-focus-modal`.
   - Audio kapcsoló: `#btn-toggle-zen-audio` -> Web Audio szintetizálás indul (barna zaj / 10Hz binaural beat).
   - "Kész & Következő": `#btn-zen-complete` -> feladat készre állítva, azonnali Re-flow.
