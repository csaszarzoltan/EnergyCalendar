# ADR-001: Energia-Ritmus és Heti Rutin-Koreográfus Architektúra és Stack

- **Dátum:** 2026-08-26
- **Státusz:** accepted
- **Szerző:** Python System Architect (Antigravity / Hermes)
- **Kanban:** #EC-001

## Kontextus
A hagyományos időbeosztó alkalmazások (Google Calendar, Todoist, Notion Calendar) lineáris, statikus idősávokkal dolgoznak, figyelmen kívül hagyva az emberi cirkadián ritmust és a kognitív energiahullámokat. A cél egy modern, fiatalos, szóló fejlesztésre optimalizált alkalmazás megtervezése, amely a 24 órát egy folytonos $E_{cap}(t)$ energia-kapacitás függvényként modellezi, és korlát-kielégítési (CSP / Bin-Packing) algoritmussal szervezi a teendőket.

## Döntés

1. **Backend Stack:**
   - **Nyelv & Keretrendszer:** Python 3.11+ és **FastAPI** (aszinkron, szigorúan típusos, OpenAPI/Swagger dokumentáció).
   - **Adatmodell & Validáció:** **Pydantic v2** (`BaseModel`, `field_validator`, `Enum`).
   - **Adatbázis & Perzisztencia:** **SQLite** (WAL módban, aiosqlite / SQLAlchemy aszinkron motorral), zero-setup, hordozható, egyfájlos működés.
2. **Ütemező és Algoritmikus Motor:**
   - **Cirkadián Görbe Generátor:** Gauss- és Hermite-interpolált 15 perces időszeletes $E_{cap}(t)$ számítás.
   - **Kognitív Illesztő Algoritmus (Energy-CSP):** Fix blokkok maszkolása, `DEEP_WORK` csúcsra rendezése, automatikus 15-30 perces `RECOVERY` blokk beillesztése 120 perc fókusz után, `ADMIN` feladatok mélypontra helyezése.
   - **Energy Debt Detekció:** Kognitív túlfeszítettség számszerűsítése és figyelmeztetés.
   - **NLP / Heurisztikus Feladatbontó:** Szabály- és mintaalapú (és opcionálisan helyi LLM gateway-kompatibilis) szövegelemző a `CognitiveLoad` és időtartam kinyerésére.
3. **Frontend Stack:**
   - **Keretrendszer:** **React (Vite / Next.js) + Tailwind CSS** biolumineszcens sötét témával.
   - **Animációk & Görbék:** HTML5 Canvas / SVG spline interpoláció (`d3-shape` / Canvas API).
   - **Interakció:** `@dnd-kit` gravitációs mágneses drag-and-drop.
4. **Minőségbiztosítás:**
   - **Backend E2E & API Contract:** `pytest` + `httpx.AsyncClient` (Black-Box).
   - **Frontend UI E2E:** `Playwright` (A11y és felületi flow tesztek).

## Elvetve

| Opció | Miért nem |
|---|---|
| PostgreSQL / PostGIS | Felesleges komplexitás és függőség egy lokális/egyfelhasználós produktivitási eszközhöz |
| OR-Tools / ILP Nehézsúlyú solver | Túl bonyolult és lassú egy interaktív, azonnali visszajelzést adó drag-and-drop felülethez; a dedikált Energy-CSP heurisztika <5ms alatt lefut |
| Tisztán statikus naptár nézet | Nem adja át az energiaszintek és a kimerülés dinamikáját |

## Következmény
- **Specifikáció:** Létrejön a `SPEC-001-energy-choreographer-backend.md` a moduláris FastAPI implementációhoz.
- **Tesztek:** Előáll az E2E Black-Box tesztkészlet (`test_e2e_001.py`).
- **Fejlesztés:** A kódoló modell a `src/` alatt valósítja meg a modelleket, a kalkulátort, a schedulert és a routert.

## Kapcsolódó
- Research: `docs/research/2026-08-26-circadian-energy-calendar-deep-dive.md`
- Stories: `docs/stories/US-001-circadian-profile-and-energy-curve.md`
- Spec: `.agent-pipeline/02_specs/pending/SPEC-001-energy-choreographer-backend.md`
