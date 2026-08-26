# US-003: Napi Lezárás, Naptár-Szinkron és Kognitív Feladatbontás

- **Epic:** Mindful Productivity & Interoperabilitás
- **Prioritás:** P0
- **Forrás:** `docs/competitor/2026-W35-circadian-productivity-scan.md` + `docs/decisions/ADR-003-shutdown-calendar-deconstruction.md`
- **Prototípus:** `http://localhost:8888` — Státusz: `approved`

---

## Story
**As a** sokat dolgozó szakember / egyetemista  
**I want** a napom végén egy tudatos cirkadián lezárási rituálét végezni, a céges naptáramat `.ics` formátumban importálni/exportálni, a túl nagy feladataimat pedig automatikusan kognitív alszeletekre bontani  
**So that** megelőzzem a kiégést, megvédjem az éjszakai melatonin-ciklusomat, szinkronban maradjak a Google Naptárammal, és legyőzzem a halogatást.

---

## Acceptance Criteria (Gherkin BDD)

### AC1 (Happy path — .ics Naptár Export & Import):
- **given** egy aktív, feladatokkal feltöltött cirkadián nap
- **when** a felhasználó meghívja a `/api/v1/energy/calendar/export-ics` végpontot
- **then** a rendszer egy érvényes `BEGIN:VCALENDAR ... END:VCALENDAR` RFC 5545 naptárfájlt ad vissza, amely tartalmazza az összes idősávot és kognitív címkét.
- **and when** egy külső `.ics` tartalmat küld a `/api/v1/energy/calendar/import-ics` végpontra
- **then** az importált események `is_fixed=True` maszkként automatikusan beépülnek a napba, megelőzve az ütközéseket.

### AC2 (Edge case — Kognitív Feladatbontás):
- **given** egy 180 perces komplex feladat (`title="Diplomamunka fejezet megírása"`)
- **when** a felhasználó meghívja a `/api/v1/energy/decompose-task` végpontot
- **then** a rendszer 3 logikus, egymásra épülő alszeletre bontja a feladatot (1. Kutatás & vázlat [CREATIVE, 45m] $\rightarrow$ 2. Mély írás [DEEP_WORK, 90m] $\rightarrow$ 3. Formázás és referenciák [ADMIN, 45m]), mindegyik önállóan ütemezhető feladatként.

### AC3 (State check — Cirkadián Napi Lezárás & Alvásvédelem):
- **given** a munkanap vége közeledik a lefekvés előtt
- **when** a felhasználó lefuttatja a `/api/v1/energy/shutdown/summary` hívást
- **then** a rendszer összegzi az elvégzett mélymunka perceket, kiszámítja a Melatonin Kapu idejét ($t_{sleep} - 60\text{m}$), és javaslatot ad a nyitott feladatok másnapi reggeli csúcsra való átütemezésére.

### AC4 (GUI Flow Contract — Vezérlők és Modalok):
- **given** a felhasználó a főoldalon tartózkodik
- **when** a felület betöltődik
- **then** elérhető a "🌙 Napi Lezárás (Shutdown)" gomb (`id="btn-open-shutdown"`), a "📤 Naptár Export" gomb (`id="btn-export-ics"`), a "📥 Naptár Import" gomb (`id="btn-import-ics"`), a feladatkártyákon pedig a "⚡ Bontás" gomb (`class="btn-decompose-task"`).

---

## gui_flow (UI Kontraktus)

1. **Toolbar:**
   - Click `#btn-export-ics` $\rightarrow$ Böngésző letölti az `energy-calendar.ics` fájlt.
   - Click `#btn-import-ics` $\rightarrow$ Megnyílik az import modal `#ics-import-modal`, fájl vagy szöveg bemásolható.
2. **Shutdown Ritual Modal:**
   - Click `#btn-open-shutdown` $\rightarrow$ Megnyílik `#shutdown-ritual-modal`.
   - Lépés 1: Befejezetlen feladatok áttekintése.
   - Lépés 2: Kognitív siker és Melatonin visszaszámláló megtekintése.
   - Lépés 3: Click `#btn-complete-shutdown` $\rightarrow$ "Munkanap lezárva! Jó pihenést!" üzenet.
3. **Decompose Button:**
   - Click `.btn-decompose-task` a 90 percnél hosszabb feladatoknál $\rightarrow$ A feladat átalakul 2-3 kisebb kapszulává a backlogban.
