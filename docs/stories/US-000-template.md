# US-000: {Rövid cím — JTBD nyelven}

- Epic: {Place / Politics / Planning / …}
- Priority: P0 / P1 / P2
- Source: docs/research/YYYY-MM-DD-*.md + ADR-NNN
- Prototípus: {Figma link / preview URL} — státusz: draft | approved

## Story (As a … I want … So that …)
As a {szerep} I want {mit} So that {miért — JTBD}.

## Acceptance Criteria (Gherkin — given/when/then)
- AC1: given {előfeltétel} | when {akció} | then {elvárás, mérhető}
- AC2: given {edge} | when {akció} | then {elvárás}
- AC3: given {hibaállapot} | when {akció} | then {hibaüzenet, kód}
- AC4: given {gui_flow} | when {…} | then {…}

## gui_flow (UI kontraktus — a developer EZT követi, nem talál ki újat)
1. Open /{route} → látom: {heading / CTA / térkép}
2. Click {gomb — pozíció, szín, label} → {mi történik}
3. Modal/Toast: {pontos szöveg} → {következő lépés}
4. Assert: {URL / toast / canvas / lista tartalma}

## Megjegyzés
- Max 400 sor / file, type hints + docstring.
- „gui_flow lépést csak US-frissítéssel szabad változtatni.”
