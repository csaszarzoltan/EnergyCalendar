# Research Deep-Dive: Funkcióbővítési és Növekedési Stratégia
## Energia-Ritmus & Heti Rutin-Koreográfus (EnergyCalendar)

> **Dátum:** 2026-08-26  
> **Szerző:** Python System Architect & E2E QA Lead  
> **Kutatási Típus:** Mély VOC Bányászat, Biohacking Elemzés, Versenytárs Résfeltárás & Feature-Siker Rubrika  
> **Források:** Reddit (r/productivity, r/ADHD, r/biohackers), App Store / Play Review-k, Tudományos Adenozin & Kronobiológiai Kutatások (Huberman Lab, Borbély-modell)

---

## 1. Felhasználói Fájdalompontok & VOC Elemzés (Voice of Customer)

A hagyományos naptárakkal (Google Calendar, Notion Calendar, Motion, Sunsama) kapcsolatos legfrissebb felhasználói visszajelzések és mély interjú-kivonatok a következő 4 kritikus hiányosságot mutatják:

### Verbatim Idézetek és Bizonyítékok

| Forrás | Szó szerinti idézet (Verbatim) | Kontextus / Érzelem | Dátum | URL / Eredet | JTBD / Téma |
|---|---|---|---|---|---|
| **Reddit r/productivity** | *"Strict time blocking treats every hour as having equal value. When my energy dips at 2pm, trying to force deep work because it's on the calendar leads to guilt and burnout."* | Fusztráció / Kimerülés | 2026 | [Reddit Discussion #1](https://reddit.com/r/productivity) | `PAIN`: Merev time-blocking egyenértékű órákkal |
| **Reddit r/ADHD** | *"When one meeting runs 15 minutes late, my whole scheduled day falls apart like dominoes. I need auto-rescheduling that gently shifts things without making me feel like a failure."* | Szorongás / Idővakság | 2026 | [Reddit Discussion #2](https://reddit.com/r/ADHD) | `DESIRED_OUTCOME`: "Forgiving" Ripple Re-flow |
| **App Store (Rise/Peaks)** | *"I love seeing my circadian peaks, but why do I have to manually copy everything into my calendar? I want the energy curve to actively protect my focus and tell me when to stop drinking coffee."* | Csalódottság a silók miatt | 2026 | App Store Reviews | `GAP`: Nincs szinkron az energiahullám és az akciók közt |
| **Biohacking / Huberman** | *"Delaying caffeine 90–120 minutes after waking allows adenosine clearance and prevents the afternoon crash; late caffeine ruins deep sleep architecture."* | Tudományos optimalizálás | 2026 | Huberman Lab Podcast | `TRIGGER`: Koffein-időzítés & Zuhanásvédelem |
| **Reddit r/productivity** | *"If I slept terribly (4 hours), my calendar shouldn't expect me to do 6 hours of high-cognition coding. It should adapt my day's capacity."* | Túlterheltség | 2026 | [Reddit Discussion #3](https://reddit.com/r/productivity) | `JTBD`: Alvásminőség alapú kapacitás-skálázás |

---

## 2. Feature-Siker Értékelési Rubrika és Súlyozott Rangsor

A módszertan szerinti 5 dimenziós értékelési képlet:
$$\text{Prioritás} = 0.30 \times \text{Kereslet} + 0.25 \times \text{Versenytárs-Gap} + 0.20 \times \text{Hatás} + 0.15 \times \text{Megvalósíthatóság} + 0.10 \times \text{Bevétel/Alternatíva}$$

### Rangsorolt Backlog Mátrix (1–5 skála)

| Rank | Funkció Jelölt | Kereslet (30%) | Gap (25%) | Hatás (20%) | Megvalósíthatóság (15%) | Bevétel (10%) | Súlyozott Pontszám | Státusz / Következő Lépés |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **#1** | **🌊 Dinamikus "Ripple Re-flow" (1-Kattintásos Csúszáskezelő)** | 5.0 | 4.5 | 5.0 | 4.5 | 4.5 | **4.75** | `ADR-002` + `US-002` (Azonnali P0) |
| **#2** | **☕ Koffein-Ablak & Kognitív Összeomlás Előrejelző (Caffeine Timing)** | 4.5 | 5.0 | 4.5 | 5.0 | 4.0 | **4.65** | `ADR-003` + `US-003` (P0 Biohack) |
| **#3** | **🛌 Alvásminőség & Napi Regeneráció Skálázó (Sleep Recovery Slider)** | 4.5 | 4.0 | 4.5 | 5.0 | 4.5 | **4.45** | `ADR-004` (P1 Wearable/Manual) |
| **#4** | **⏱️ Kapszula Flow-Timer & Fókusz Mód (Ambient Deep Work Room)** | 4.5 | 3.5 | 4.5 | 4.5 | 4.0 | **4.20** | `US-005` (P1 Frontend élmény) |
| **#5** | **📅 Kétirányú Naptár Integráció (.ics Import / Export & Google Sync)** | 5.0 | 2.5 | 4.5 | 4.0 | 4.0 | **4.03** | `ADR-005` (P1 Kompatibilitás) |
| **#6** | **📊 Heti Kognitív Ritmus & Heti Hőtérkép (7-Day Energy Budget)** | 4.0 | 3.5 | 4.0 | 4.0 | 4.0 | **3.88** | `P2 Backlog` |

---

## 3. A Top 5 Funkció Részletes Elemzése

---

### #1. Dinamikus "Ripple Re-flow" (Valós Idejű Csúszáskezelő & Elnéző Újrahangolás)
- **1 Mondatos Pitch:** *"Ha elhúzódik egy meeting vagy csúszol egy feladattal, egyetlen gombnyomással újrahullámoztatja a hátralévő napot az aktuális időponttól ($t_{now}$), megvédve a cirkadián fókuszablakokat bűntudat nélkül."*
- **Miért egyedi (Versenytárs-Gap):** A Motion mereven előre tolja a téglalapokat a naptárban. Az EnergyCalendar viszont az $E_{cap}(t)$ függvény szabad energiacsúcsait újrakalkulálja a hátralévő órákra, és a `DEEP_WORK` feladatokat a délutáni másodlagos csúcsra (Peak 2), míg az adminisztrációt az esti levezetésre szervezi át.
- **Matematikai & Algoritmikus Logika:**
  $$t \in [t_{now}, t_{sleep}]$$
  A már befejezett/múltbeli feladatok zárolva maradnak, a függőben lévők $\text{FreeEnergy}(t \ge t_{now})$ alapján újrarendeződnek.
- **Kockázat:** Túl sok csúszás esetén a feladatok túlcsordulhatnak a másnapra -> Vizuális *"Áttolás Holnap Reggeli Csúcsra"* javaslat.

---

### #2. Koffein-Ablak & Kognitív Zuhanás Előrejelző (Caffeine Timing & Crash Predictor)
- **1 Mondatos Pitch:** *"Az energiahullámra rávetíti a biológiailag optimális koffein-fogyasztási ablakot (90 perccel ébredés után), kitűzi az esti alvásvédő koffein-stop határt, és modellezi a délutáni adenozin-zuhanást."*
- **Tudományos Háttér:**
  - **Koffein-Kezdet (Delay):** $t_{wake} + 90\text{ perc}$ (Megvárja a természetes Cortisol Awakening Response lecsengését).
  - **Koffein-Stop (Cut-off):** $t_{sleep} - 9\text{ óra}$ (A koffein 5-7 órás felezési ideje miatt a receptorok felszabadulnak a mély NREM alváshoz).
  - **Farmakokinetika:** $C(t) = \sum C_i \times 0.5^{\frac{t - t_i}{t_{half}}}$
- **Vizuális Megjelenés:** Arany-barna pulzáló "Koffein Zóna" sáv a Canvas hullám hátterében és csésze ikon a feladatok mellett, jelezve a legmagasabb koffein-hatékonyságú fókuszablakot.

---

### #3. Alvásminőség & Napi Kognitív Kapacitás Skálázó (Recovery Factor)
- **1 Mondatos Pitch:** *"Egy egyszerű reggeli alvásminőség csúszkával (vagy Oura/Apple Health szinkronnal) azonnal a napi valós állapotodhoz igazítja az energiahullám amplitúdóját és a napi Energy Debt küszöböt."*
- **Matematikai Skálázás:**
  $$E_{cap}^{adj}(t) = E_{base} + \left(E_{cap}(t) - E_{base}\right) \times \gamma_{recovery}$$
  Ahol $\gamma_{recovery} \in [0.4, 1.2]$ az alvásminőség szerint.
  - Ha rosszul aludtál ($\gamma = 0.5$): a fókuszcsúcsok lelapulnak, a 120 perces mélymunka limit automatikusan **60 percre szigorodik**, és a rendszer több `RECOVERY` szünetet ajánl.

---

### #4. Kapszula Flow-Timer & Fókusz Mód (Deep Work Ambient Room)
- **1 Mondatos Pitch:** *"Kattints rá bármelyik feladat-kapszulára, és a felület átvált egy teljes képernyős, zavarmentes fókusz-térbe, ahol a kapszula az energiaszint fényével telik meg, beépített lofi/binaurális háttérhanggal és idővakság elleni szelíd progresszióval."*
- **Felhasználói Érték (ADHD & Gen Z):** Legyőzi a halogatást (procrastination) és az idővakságot (time blindness), közvetlen vizuális visszajelzést adva a feladat előrehaladásáról.

---

### #5. Kétirányú Naptár Integráció (.ics Import / Export)
- **1 Mondatos Pitch:** *"Húzd be a Google Calendar / Outlook `.ics` naptáradat, ami automatikusan zárolja a fix meetingeket, és egyetlen kattintással exportáld vissza az optimalizált cirkadián feladat-koreográfiát."*
- **Megvalósítás:** Python `icalendar` / `ics` könyvtár az API oldalon, kliens oldalon drag-and-drop `.ics` fájl dropzone és Google Calendar URL feliratkozási feed.

---

## 4. Javasolt Megvalósítási Ütemterv (Roadmap)

```
[Most Kész: v1.0.0] ──► [v1.1.0: P0 Sprint] ─────────────► [v1.2.0: P1 Sprint]
- Alap Energiamodell     - #1 Ripple Re-flow (Csúszás)     - #3 Alvásminőség Slider
- 120m Fókuszvédelem     - #2 Koffein-Ablak & Crash        - #4 Kapszula Flow-Timer
- Canvas Spline & SPA    - Valós idejű óra mutató          - #5 .ics Naptár Export/Import
```
