# ADR-003: Cirkadián Napi Lezárás, .ics Naptár-Szinkron és Kognitív Feladatbontás

- **Dátum:** 2026-08-26
- **Státusz:** accepted
- **Szerző:** Python System Architect & QA Lead
- **Kanban:** #EC-003

## Kontextus
A versenytárs-elemzés (Motion, Sunsama, Goblin.tools, Rise) és a heti pásztázás (`docs/competitor/2026-W35-circadian-productivity-scan.md`) alapján a rendszernek három kulcsfontosságú hiányosságot kell áthidalnia:
1. **Munkanap Lezárási Vákuum:** A befejezetlen feladatok szorongást és alvászavart okoznak (Zeigarnik-effektus); hiányzik egy cirkadián esti lezárási rituálé.
2. **Naptár Silók:** A felhasználók meglévő Google Calendar / Outlook eseményeiket `.ics` formátumban akarják importálni, a cirkadián ütemezést pedig külső naptárakba exportálni.
3. **Kognitív Túlterhelés & Idővakság:** A túl nagy ($>120\text{m}$) feladatokat a felhasználók halogatják; szükség van intelligens kognitív feladat-dekompozícióra.

## Döntés

1. **Cirkadián Napi Lezárási Rituálé (Daily Shutdown):**
   - Végpont: `POST /api/v1/energy/shutdown/summary`
   - Kiszámítja az elvégzett mélymunka órákat, a megelőzött Energy Debt-et, az elalvás előtti Melatonin-kapu hátralévő idejét, és javaslatot ad a befejezetlen feladatok másnapi reggeli csúcsba történő átemelésére.
   - Frontend: 3-lépéses interaktív esti lezáró modal ("Shutdown Complete" rituális megerősítéssel).
2. **Kétirányú RFC 5545 `.ics` Naptármotor:**
   - Végpont: `POST /api/v1/energy/calendar/export-ics` $\rightarrow$ Standard `text/calendar` fájl letöltés kognitív címkékkel (`[🧠 Deep Work]`, `[🔋 Regeneráció]`).
   - Végpont: `POST /api/v1/energy/calendar/import-ics` $\rightarrow$ Naptár `.ics` tartalom beolvasása, események automatikus `is_fixed=True` maszkká alakítása a naptár-ütközések elkerülésére.
   - Frontend: "📥 Naptár Import (.ics)" és "📤 Naptár Export (.ics)" gombok és fájlfeltöltő dropzone.
3. **Kognitív Feladat-Dekompozíció (Subtask Chunking Engine):**
   - Végpont: `POST /api/v1/energy/decompose-task`
   - Bemenet: Egy nagy összetett feladat (pl. `title="Mobilapp újratervezés"`, `duration_minutes=240`).
   - Kimenet: Logikus, egymást követő 30-90 perces alszeletek kognitív típusokkal és leírásokkal (pl. 1. Kreatív vázlat és koncepció [60m, CREATIVE] $\rightarrow$ 2. Komponens refaktorálás [90m, DEEP_WORK] $\rightarrow$ 3. Felületi tesztek és doc [45m, ADMIN]).
   - Frontend: 1-kattintásos "⚡ Bontás" gomb a feladatkártyákon.

## Elvetve

| Opció | Miért nem |
|---|---|
| Csak manuális Google OAuth2 bejelentkezés | Függ a Google Cloud Client Secret-ektől; a szabványos `.ics` fájl kezelés univerzálisan működik Google Calendar, Apple iCal és Outlook rendszerekkel is zéró konfigurációval |
| Egyszerű egyenlő szeletelés (pl. 240m = 4x60m azonos névvel) | Nem kognitív; a valós feladatbontás különböző terhelési fázisokból áll (kreatív tervezés $\rightarrow$ mély kivitelezés $\rightarrow$ admin review) |

## Következmény
- `SPEC-004` specifikálja az új modelleket, végpontokat és UI elemeket.
- E2E tesztcsomag (`test_e2e_004.py`) validálja a Shutdown, az ICS Export/Import és a Feladatbontó működését.
