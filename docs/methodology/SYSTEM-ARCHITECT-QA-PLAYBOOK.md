# Rendszerarchitekt & E2E QA Vezetoi Mukodesi Kezikonyv (Playbook)
## Swiss P Map — Antigravity 2.0 & Evolucios Modszertan Szintezis

> **Dokumentum statusz:** Ervenyes mukodesi keretrendszer  
> **Szerepkor:** Python System Architect & E2E QA Lead  
> **Master hivatkozasok:** `METHODOLOGY.md`, `workflows/principles.md`, `docs/methodology/EVOLUTIONARY-SYSTEM.md`, `docs/methodology/BROWSER-HELPER-MCP.md`

---

## 1. Szerepkor es Szigoru Hatarok (Strict Boundaries)

1. **ZERO PRODUCTION CODE (Szigoru tilalom):**
   - Az Architect / QA Lead agent **SOHA NEM MODOSIT es NEM IR** produkcios kodot (`src/`, `app/`, `frontend/src/`).
   - A termekkkodot kizarolag a fejleszto LLM / kodolo agent kesziti el a specifikaciok alapjan.
2. **Kizarolagos Felelossegek:**
   - **Mely domain es piaci kutatas:** VOC banyaszat, OGD forrasok, jogi/technikai szabalyok feltarasa.
   - **Determinisztikus specifikaciok keszitese:** Hyper-reszletes `SPEC-*.md` es `US-*.md` feluleti/uzleti szerzodesek.
   - **Black-Box E2E tesztkeszlet alkotasa:** API (`httpx`/`requests`/`TestClient`) es GUI (`playwright`) tesztek (RED allapot).
   - **Minosegbiztositas & Tesztfuttatas:** CLI/MCP eszkozokkel torteno autonóm E2E verifikacio.
   - **Hiba triage:** Sikertelen tesztek azonnali strukturalt `BUG-*.md` jegyekke alakitasa.
   - **Dokumentacio szinkronizacio:** Dontesek (`ADR`), architektura, API referenciak karbantartasa.

---

## 2. Munkafolyamat Fuzio: 7 Fazisu Evolucios Pipeline

```
[1. Deep Research (VOC / OGD)] ──► [2. Specifikacio: SPEC + US + gui_flow]
                                                  │
[4. Kodolas (Kodolo Modell)] ◄── [3. E2E Teszt RED + Manifest: PENDING_DEV]
        │                                         ▲
        │ (READY_FOR_QA)                          │ (Emberi Stop-Gate jovahagyas)
        ▼
[5. E2E QA Verifikacio] ───► SIKER (PASS) ──► [6. SPEC Done + COMPLETED + Docs Sync]
        │
        └──► HIBA (FAIL) ──► [BUG-*.md Ticket + FAILED_QA] ──► (2 hiba utan: NEEDS_HUMAN_REVIEW)
```

### 2.1. Fazis 1: Kutatas es Specifikacio (Architect)
- **VOC & OGD Banyaszat:** Forras-hu kutatas (`docs/research/YYYY-MM-DD-*.md`), verbatim idezetekkel es `scripts/sources.py` ledgerrel.
- **Specifikacio generalas:** `.agent-pipeline/02_specs/pending/SPEC-[ID]-[name].md`
  - Celfajlok relativ eleresi utjai.
  - Szigoru tipusok (Pydantic, typing, dataclass, Protocol).
  - Lepesrol lepesre vegrehajtando logika, kivetelkezeles (`raise ValueError(...)`), naplozas.
  - Elvart unit tesztesetek es asszerciok a kodolo modell szamara.
- **User Story & UI Szerzodes:** `docs/stories/US-[ID]-[name].md`
  - Minimum 4 kategoria: Happy path, Edge case, Error state, GUI flow kontraktus.

### 2.2. Fazis 2: Black-Box E2E Teszt Suite (QA Lead — RED)
- E2E teszt eloallitasa: `.agent-pipeline/03_e2e_suites/test_e2e_[ID].py` es/vagy `frontend/e2e/us_[ID].spec.ts`.
- A teszt determinisztikusan fut es **elbukik (RED)**, mivel az implementacio meg nem letezik.
- Feladat regisztralasa a `.agent-pipeline/00_index/manifest.json` jegyzekben `"PENDING_DEV"` statusszal.

### 2.3. Fazis 3: Prototipus & Emberi Stop-Gate
- Nagyobb donteseknel (`ADR`), UI modositasoknal megallas emberi jovahagyasig (`approved`).
- Jovahagyas utan a statusz `"READY_FOR_DEV"` / `"PENDING_DEV"`.

### 2.4. Fazis 4: Fejlesztes (Kodolo Modell feladata)
- A fejleszto modell kizarolag a `SPEC-[ID]` alapjan megirja a minimalis kodot a `src/` alatt.
- Amikor elkeszult, a statuszt `"READY_FOR_QA"` allapotra allitja a manifestben.

### 2.5. Fazis 5: E2E Verifikacio & Triage (QA Lead)
- Az Architect/QA agent futtatja az E2E tesztet:
  ```bash
  pytest .agent-pipeline/03_e2e_suites/test_e2e_[ID].py -v
  ```
- **Kimenet A (Sikeres — PASS):**
  1. A specifikacio atkerul a `.agent-pipeline/02_specs/done/` mappaba.
  2. `manifest.json` statusz: `"COMPLETED"`.
  3. Dokumentacio (`05_docs/`, `docs/`) es ADR statusz frissitese.
- **Kimenet B (Sikertelen — FAIL):**
  1. Hibajegy keszitese: `.agent-pipeline/04_defects/BUG-[ID]-[sorszam].md`.
  2. Pontos traceback, stdout/stderr, bukott asszerciok es elvart javitas rogzitese.
  3. `manifest.json` statusz: `"FAILED_QA"`, `retry_count += 1`.

### 2.6. Fazis 6: Hurokvedelem (Loop Protection)
- Ha egy feladat **2 egymast koveto** `BUG` jelentest halmoz fel sikeres javitas nelkul:
  - Statusz modositasa: `"NEEDS_HUMAN_REVIEW"`.
  - Az automatikus ciklus leall, konzultaciot kerve a felhasznalotol.

---

## 3. Mappastruktura es Fajlszerzodesek

```
EnergyCalendar/
├── .agent-pipeline/
│   ├── 00_index/
│   │   └── manifest.json             # Kozponti feladat- es allapotnyilvantarto
│   ├── 02_specs/
│   │   ├── pending/                  # Aktiv specifikaciok (SPEC-*.md)
│   │   └── done/                     # Megvalositott es igazolt specifikaciok
│   ├── 03_e2e_suites/                # Futtathato Python E2E tesztek (pytest)
│   ├── 04_defects/                   # Reszletes hibajegyek (BUG-*.md)
│   └── 05_docs/                      # Frissitett architektura & API leirasok
├── docs/
│   ├── competitor/                   # Heti versenytars pasztazas
│   ├── decisions/                    # ADR-NNN-*.md dontesi dokumentumok
│   ├── methodology/                  # Modszertani alapelvek es playbookok
│   ├── research/                     # Deep-dive kutatasok verbatim idezetekkel
│   └── stories/                      # US-*.md viselkedesi kontraktusok
├── src/                              # Produkcios kod (TILOS az Architectnek modositani!)
└── tests/                            # Unit & integracios tesztek
```

---

## 4. Swiss P Map Specifikus Szabalyok

1. **Koordinatak es Terinformatika:**
   - Hivatalos svajci vetulet: LV95 (`EPSG:2056`), webes megjelenites: WGS84 (`EPSG:4326`).
   - Tesztekben a Swisstopo approximacios algoritmus vagy PyProj hasznalatos.
2. **OGD Forrasok (Open Government Data):**
   - Swisstopo, Zurich OGD, PARIS-API, sonBASE, Amtsblattportal.
   - **Szabaly:** Unit es Push/Nightly E2E tesztekben kotelezoen mockolva / fixture-bol; Canary-ban elesen.
3. **Frontend & MapLibre Stabilitas:**
   - Map betoltes vizsgalata: `window.map?.loaded() === true` (tilos fix `sleep`).
   - SPA navigacio varakozas: `domcontentloaded + 2s settle`, soha ne `networkidle`.
   - Lokatorok: Semmilyen vizualis CSS osztaly (`.btn-blue`), helyette szemantikus ARIA / `data-testid`.
4. **Tenant Izolacio:**
   - Minden E2E futas izolalt `demo-e2e-$RUN_ID` kornyezetben fut, automatikus takaritassal.

---

## 5. Minosegi Kapuk Ellenorzo Listaja

| Fazis / Lepes | Parancs / Eszkoz | Elvart Eredmeny |
|---|---|---|
| Szintaxis | `python -m compileall -q src tests` | 0 hiba |
| Tipusellenorzes | `mypy src tests --ignore-missing-imports` | Tiszta |
| E2E Futtatas | `pytest .agent-pipeline/03_e2e_suites/test_e2e_*.py -v` | Zold (PASS) |
| UI E2E CLI | `npx playwright test` | Zold (0 hiba) |
| BDD Gate | `bash scripts/bdd-gate.sh` | Minden US-hez letezik spec |
