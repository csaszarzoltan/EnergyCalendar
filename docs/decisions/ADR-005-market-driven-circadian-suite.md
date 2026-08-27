# ADR-005: 10 Piaci & Felhasználói Igény Alapú Cirkadián Funkció Bevezetése

- **Státusz:** Elfogadva (Accepted)
- **Dátum:** 2026-08-26
- **Döntéshozók:** Vezető Rendszertervező, Termékmenedzser
- **Kapcsolódó Kutatás:** [2026-W35-circadian-market-scan.md](../competitor/2026-W35-circadian-market-scan.md)

---

## 1. Kontextus és Piaci Megalapozás
A piackutatás igazolta, hogy a felhasználók igénylik a kontextusváltási adó számítását, az ADHD idővakság védelmet, a fejlett Web Audio hangtájakat, az időzóna-jetlag adaptációt és az értekezletek kognitív adójának kezelését.

## 2. Döntési Határozat
Bevezetünk 10 új specializált szolgáltatást az src/services/ rétegben és a hozzájuk tartozó domain modelleket a src/models/market_circadian.py fájlban:
1. ContextSwitchService
2. JetlagChronoService
3. NeuroFlowService
4. BiophilicSpaceService
5. DopamineGuardService
6. SoundscapeSynthService
7. WeatherChronoService
8. WorkoutTimingService
9. MeetingTaxService
10. InfradianRhythmService

## 3. Következmények
- Moduláris, tiszta architektúra (minden fájl szigorúan <400 sor).
- FastAPI végpontok integrálása a /api/v1/energy/* útvonalon.
- Frontend bővítés 0 külső JS könyvtárral.
