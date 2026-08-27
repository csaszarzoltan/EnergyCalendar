# EnergyCalendar — Agent Context & Quickstart

> Ezt olvassa minden AI Agent belépéskor (Hermes, Gemini CLI, Claude, Codex, Antigravity, GPT...). Rövid eligazítás — 30 sor.

## Mi ez
**EnergyCalendar (Energia-Ritmus & Heti Rutin-Koreográfus)** — Biológiai cirkadián ritmusra és kognitív terhelésre optimalizált feladat- és időszervező rendszer (v1.6.0). 
- **Stack:** Python 3.11+ (FastAPI, Pydantic v2, Uvicorn), Modern Vanilla JS + Canvas + Web Audio API SPA (0 külső JS függőség), Pytest + Playwright.

## Jelenlegi Állapot (v1.6.0)
- **123/123 teszt zöld (100% PASS):** 43 Black-Box E2E teszt + 80 Unit teszt.
- **Élő szerver:** `http://127.0.0.1:8888` (Swagger: `/docs`).
- **Pipeline:** `.agent-pipeline/` (SPEC-001..008 lezárva a `manifest.json`-ban).

## Hol mi van
- `docs/HANDOVER.md` — **Teljes átadási dokumentáció, modulok leírása és következő feladatok (Start here!)**
- `docs/ARCHITECTURE.md` — Rendszerarchitektúra és komponens gráf
- `docs/decisions/ADR-*.md` — Döntési naplók (ADR-001..003)
- `docs/stories/US-*.md` — Felhasználói történetek és BDD elfogadási kritériumok
- `src/` — Backend alkalmazás (`models`, `services`, `api`)
- `frontend/` — Egyoldalas biolumineszcens webalkalmazás (`index.html`, `app.js`, `style.css`)
- `tests/` & `.agent-pipeline/03_e2e_suites/` — Tesztcsomagok

## Alapszabályok (Kötelező)
1. **Döntés nélkül ne kódolj:** Kutatás $\rightarrow$ ADR $\rightarrow$ Story $\rightarrow$ Spec $\rightarrow$ RED E2E teszt $\rightarrow$ Kód $\rightarrow$ GREEN teszt $\rightarrow$ Manifest frissítés.
2. **Kódszabályok:** Max 400 sor/fájl; szigorú típusjelölések (`type hints`) és docstringek.
3. **Tesztelés:** Minden új végponthoz és logikához írj Black-Box E2E tesztet (`pytest -v`).
4. **Git konvenció:** `<scope>: <leírás>` commit formátum.

## Következő Sprint Ötletek (Roadmap)
Lásd: `docs/HANDOVER.md` (6. Fejezet) — Wearable HRV/Oura szinkron, Heti makro-ritmus nézet, Hangos/WebPush értesítések.
