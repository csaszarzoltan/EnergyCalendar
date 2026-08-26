# US-001: Cirkadián Energia-Ritmus és Feladat-Koreográfus

- **Epic:** Cirkadián Tervező & Rutin Koreográfus
- **Prioritás:** P0
- **Forrás:** `docs/research/2026-08-26-circadian-energy-calendar-deep-dive.md` + `docs/decisions/ADR-001-energy-calendar-architecture.md`
- **Prototípus:** `http://localhost:3000/app` — Státusz: `draft`

---

## Story (As a … I want … So that …)
**As a** modern tudásmunkás / egyetemista  
**I want** a napi feladataimat a cirkadián energiaszintemhez és a kognitív terhelési típusukhoz illesztve megtervezni  
**So that** elkerüljem a délutáni kognitív kimerülést (burnout), a mély fókuszú munkát a biológiai csúcsaimra időzítsem, és automatikus regenerációs szüneteket kapjak.

---

## Acceptance Criteria (Gherkin BDD)

### AC1 (Happy path — Cirkadián Profil és Optimális Illesztés):
- **given** egy konfigurált energiamodell (pl. ébredés 07:00, fókuszcsúcs 09:00–11:30 és 16:30–18:00, kaja-kóma mélypont 13:30–15:00, alvás 23:00)
- **when** benyújtok 1 db 90 perces `DEEP_WORK` és 1 db 45 perces `ADMIN` feladatot
- **then** a rendszer a `DEEP_WORK` feladatot a délelőtti csúcsidőszakra ($E_{cap} \ge 8.0$), az `ADMIN` feladatot pedig a délutáni mélypontra ($E_{cap} \le 4.5$) ütemezi.

### AC2 (Edge case — 120 perces Fókuszkorlát és Automatikus Pihenő):
- **given** 2 db egymást követő 75 perces `DEEP_WORK` feladat (összesen 150 perc mély fókusz)
- **when** a koreográfus futtatásra kerül
- **then** a rendszer az első feladat után kötelező jelleggel beiktat egy 15–30 perces `RECOVERY` blokkot (negatív kognitív költséggel), megvédve a felhasználót a kimerüléstől.

### AC3 (Error / Overload state — Energy Debt és Figyelmeztetés):
- **given** egy olyan feladatkészlet, amelynek összesített kognitív igénye meghaladja a nap szabad energiakapacitását ($\sum (cost \times duration) > \int FreeEnergy(t) dt$)
- **when** az ütemezés lefut
- **then** a rendszer nem dob 500-as hibát, és nem tiltja le a feladatokat, hanem `status: "warning"` mellett kiszámítja a pontos `energy_debt` értéket, és túlterhelési figyelmeztetést ad vissza.

### AC4 (GUI Flow Contract — Hullámgörbe és Gravitációs Drag-and-Drop):
- **given** a felhasználó megnyitja a `/` kezdőoldalt
- **when** a felület betöltődik
- **then** a háttérben kirajzolódik a dinamikus, színkódolt energiahullám (Canvas/SVG), a fejlécben megjelenik a Kognitív Hőtérkép Sáv (0–100%), a feladatok úszó kapszulaként jelennek meg, és mozgatáskor az energiazónák mágnesként vonzzák őket a megfelelő idősávba.

---

## gui_flow (Kötelező Érvényű Felületi Szerződés)

1. **Navigate to:** `/` -> Vizuális ellenőrzés:
   - Címsor látható: `role=heading[name="Energia-Ritmus & Heti Rutin-Koreográfus"]`
   - Kognitív hőtérkép sáv: `data-testid="cognitive-debt-meter"`
   - Dinamikus hullámvonal: `canvas[data-testid="energy-wave-canvas"]` vagy `svg[data-testid="energy-wave-svg"]`
2. **Interact:** Új feladat hozzáadása gyorsmezővel:
   - Fill `input[name="quick_task_input"]` értékkel: `"Kódolás: új auth modul 90 perc"`
   - Click `button[name="btn_add_task"]` -> NLP elemzés lefut, kapszula megjelenik `DEEP_WORK` címkével
3. **Interact:** Drag-and-Drop áthelyezés:
   - Húzd a feladatkapszulát a 14:00 idősávra (mélypont zóna) -> A kapszula narancs pulzálással figyelmeztet, majd mágnesesen a 09:30-as optimális zónába pattan.
4. **Assert:** Mentális telítettségi mutató frissül, az ütemezett idősávok listája konzisztens.

---

## Megjegyzések & Minőségi Szabályok
- Típusbiztos API szerződés FastAPI és Pydantic v2 használatával.
- Max 400 sor fájlonként; kódolási stílus a [METHODOLOGY.md](file:///c:/Projects/EnergyCalendar/METHODOLOGY.md) szerint.
