# Cirkadián & Kognitív Architektúra Bővítés — Mélyreható Kutatás (v1.3.0)

> **Dátum:** 2026-08-26  
> **Szerző:** AI Architekt & Biohacking Kutatócsoport  
> **Cél:** 10 élvonalbeli cirkadián, biometrikus és kognitív funkció tudományos megalapozása az EnergyCalendar platformhoz.

---

## 1. Tudományos Háttér & Motiváció

Az EnergyCalendar v1.2.0 sikeresen bevezette az alapvető 96 pontos cirkadián görbét, a koffein ablakot, a Ripple Re-flow algoritmust és az RFC 5545 naptárszinkronizációt. A v1.3.0 célja a biológiai pontosság és a kognitív ergonómia elmélyítése 10 új dimenzióval.

### Összehasonlító Elemzés & Értékelési Mátrix

| Funkció Modul | Tudományos Alap (Irodalom) | Bemeneti Változók | Kimeneti Mutató / Hatás | Komplexitás |
|---|---|---|---|:---:|
| **1. BiometricSync** | Shaffer & Ginsberg (2017), Oura/Whoop HRV modellek | HRV RMSSD, RHR, mély/REM alváspercek | Dinamikus $\\gamma_{recovery} \\in [0.3, 1.2]$, fáziseltolódás | Közepes |
| **2. WeeklyMatrix** | Circadian Macro-Rhythm, Csíkszentmihályi Flow | 7 napos feladatlista, heti meeting-terhelés | 7 napos kiegyenlített naptár, Deep Work napok | Magas |
| **3. CircadianAlert** | Huberman Lab (2021), CAR & Adenozin kinetika | Aktuális idő, ébredés/alvás időpontok | Valós idejű eseményértesítések | Alacsony |
| **4. UltradianEngine** | Kleitman (1963) Basic Rest-Activity Cycle (BRAC) | 90 perces kognitív ciklusok | 90m fókusz + 20m szünet idősávok | Közepes |
| **5. ChronoNutrition** | Satchin Panda (2018) Circadian Fasting, Postprandial Dip | Makrotápanyag (CH/Fehérje), étkezési idő | Dip mélység moduláció ($\\Delta E_{dip}$), IF ablak | Közepes |
| **6. Phototherapy** | Czeisler et al. (1986), Melatonin szuppresszió | Napkelte/napnyugta, lux érték | 10,000 Lux ablak, kékfény-stop időpont | Alacsony |
| **7. BurnoutPrediction** | McEwen (1998) Allostatic Load Index | 7 napos kumulatív Debt, alváshiány | Kiégési kockázati pontszám, dekompresszió | Közepes |
| **8. SocialJetlag** | Roenneberg (2012) Social Jetlag Index | Csapat kronotípusok (Pacsirta/Bagoly) | Közös aranyablak (Golden Window), Jetlag pont | Közepes |
| **9. MicroRecovery** | Huberman & Spiegel (2023) Physiological Sigh, 20-20-20 | Folyamatos képernyőidő | Szomatikus mikroszünetek, légzésgyakorlatok | Alacsony |
| **10. CircadianAnalytics** | Fókusz ROI, Energy Alignment Index | Tervezett vs tényleges teljesítés | Circadian Alignment Score (0-100%), statisztika | Közepes |

---

## 2. Matematikai & Algoritmikus Részletek

### 2.1. Biometrikus Recovery Számítás
\\gamma_{recovery} = \\text{clamp}\\left( 0.4 \\times \\frac{\\text{HRV}_{rmssd}}{50.0} + 0.3 \\times \\frac{60.0}{\\text{RHR}} + 0.3 \\times \\frac{\\text{DeepSleepMin} + \\text{REMSleepMin}}{120.0}, 0.3, 1.2 \\right)

### 2.2. Allosztatikus Terhelés (Burnout Index)
\\text{BurnoutIndex} = \\min\\left(100, \\sum_{d=1}^{N} w_d \\cdot \\text{Debt}_d \\times (1.3 - \\gamma_{recovery, d})\\right)

### 2.3. Krono-Táplálkozási Kaja-Kóma Depresszió
A_{dip}^{eff} = A_{dip} \\times \\left(1.0 + 0.5 \\times \\text{CarbRatio} - 0.2 \\times \\text{FastingBonus}\\right)