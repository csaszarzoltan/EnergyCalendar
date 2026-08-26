# SPEC-002: Energia-Ritmus & Heti Rutin-Koreográfus Frontend és Web Alkalmazás

## Target Files
- `frontend/index.html` (NEW)
- `frontend/app.js` (NEW)
- `frontend/style.css` (NEW)
- `src/main.py` (MODIFY — Mount static files directory at `/static` and serve `frontend/index.html` at `/`)
- `tests/unit/test_frontend_mount.py` (NEW)

---

## Architecture & Visual Concept

1. **Stílusvilág (Bioluminescent Dark Theme):**
   - Sötét háttér (`#0a0e17`, `#111827`).
   - Színkódok:
     - `DEEP_WORK`: Neon Cyan (`#06b6d4`, `#22d3ee`), intenzív ragyogás.
     - `CREATIVE`: Electric Purple / Violet (`#a855f7`, `#c084fc`).
     - `ADMIN`: Amber / Warm Gold (`#f59e0b`, `#fbbf24`).
     - `RECOVERY`: Emerald / Mint Green (`#10b981`, `#34d399`).
     - `ENERGY_DEBT`: Coral Red / Crimson (`#ef4444`, `#f87171`), pulzáló vészjelzés.
2. **Interaktív Főelemek:**
   - **Kognitív Hőtérkép Sáv (Header):** 0-100% mentális telítettség vizuális mutató, Energy Debt jelvény.
   - **Dinamikus Hullámvonal (Canvas):** 24 órás folytonos spline görbe a háttérben, az $E_{cap}(t)$ értékek alapján, zónahatárokkal (Peak zónák kék fénnyel, Dip zónák narancs sávval).
   - **Úszó Feladat-Kapszulák & Idővonal:** 06:00 - 23:00 idősáv, ahová a feladatok beilleszkednek.
   - **Gravitációs Drag-and-Drop:** Egérrel/érintéssel mozgatható kapszulák, amelyek a legközelebbi 15 perces idősávra és a kompatibilis energiazónára ugranak (snapping).
   - **NLP Gyorsbeviteli Mező:** Gépelés: *"Kódolás: új auth modul 90 perc"* -> Azonnali automatikus felismerés és kapszula-generálás.
   - **Cirkadián Profil Vezérlőpult & Presetek:**
     - Presetek: Pacsirta (06:00-22:00), Standard (07:00-23:00), Éjjeli bagoly (09:00-01:00).
     - Manuális idősáv állítás (ébredés, alvás, csúcsok, mélypontok).
   - **Auto-Koreográfia Gomb:** Egy kattintásra meghívja a `/api/v1/energy/schedule` végpontot, animálja a feladatok átrendezését és beszúrja a 120m fókusz utáni automatikus `RECOVERY` blokkokat.

---

## Step-by-Step Implementation Details

1. **`frontend/index.html`:**
   - Modern HTML5, Tailwind CSS CDN + FontAwesome / Lucide ikonok + Canvas API.
   - Reszponzív, fiatalos layout: Fejléc (Hőtérkép + Profil gomb), Fő terület (NLP beviteli sáv + Idővonal a hullámvászonnal + Feladat gyűjtő dokk / Backlog), Oldalsáv (Energia Debt és Statisztikák).
2. **`frontend/app.js`:**
   - Aszinkron REST kliens a backendhez (`/api/v1/energy/*`).
   - Canvas $E_{cap}(t)$ renderelő: sima Bezier / Hermite spline görbét rajzol neon gradienssel és zóna kiemelésekkel.
   - Feladatkezelés: helyi állapotban (`state.tasks`, `state.scheduled`, `state.profile`).
   - NLP gyors hozzáadás: meghívja a `POST /api/v1/energy/parse-task` végpontot.
   - Drag-and-Drop eseménykezelők: `dragstart`, `dragover`, `drop` vagy Pointer Events a kapszulák idővonalra húzásához.
   - Ütemezés: meghívja a `POST /api/v1/energy/schedule` végpontot, frissíti az idővonalat és az Energy Debt riportot.
3. **`src/main.py` Módosítás:**
   - `StaticFiles(directory="frontend", html=True)` felcsatolása a gyökér `/` útvonalra és `/static` alá.
   - A meglévő `/api/v1/*` végpontok és tesztek érintetlenek maradnak.

---

## Unit & Integration Test Acceptance Criteria

* `test_frontend_root_serves_html`: `GET /` 200 OK választ ad `text/html` tartalommal.
* `test_static_assets_available`: `GET /app.js` és `GET /style.css` 200 OK státusszal elérhető.
* `test_api_endpoints_still_pass`: Az összes korábbi unit és E2E teszt változatlanul 100%-ban zöld marad.
