# ADR-004: 10 Új Cirkadián, Biometrikus és Kognitív Funkció Integrációja

- **Státusz:** Elfogadva (Accepted)
- **Dátum:** 2026-08-26
- **Döntéshozók:** Vezető Architekt, Cirkadián Rendszertervező
- **Kapcsolódó Kutatás:** [2026-08-26-ten-circadian-advancements.md](../research/2026-08-26-ten-circadian-advancements.md)

---

## 1. Kontextus és Problémafelvetés
Az EnergyCalendar v1.2.0 robusztus alapokat biztosít a cirkadián napi ütemezéshez. A felhasználók azonban komplexebb életviteli támogatást igényelnek: valódi biometrikus szenzoradatok kezelését, többnapos heti tervezést, valós idejű biológiai riasztásokat, BRAC ultradián ciklusokat és társas cirkadián egyensúlyt.

## 2. Megfontolt Alternatívák
- **A Opció (Monolitikus bővítés):** Az összes új kalkulációt a meglévő EnergyCalculator és EnergyScheduler osztályokba zsúfoljuk.
  - *Elvetve:* Megsértené a 400 sor/fájl szabályt és a Single Responsibility elvet.
- **B Opció (Mikroszolgáltatásos felbontás különálló modulokkal):** Minden funkció külön dedikált service fájlt (src/services/<funkció>_service.py) kap, önálló Pydantic domain típusokkal.
  - *Elfogadva:* Magas kohézió, alacsony csatolás, kiváló tesztelhetőség.

## 3. Döntési Határozat
Bevezetünk 10 új szolgáltatási modult:
1. BiometricSyncService (HRV, RHR és alvásfázis feldolgozás)
2. WeeklyMatrixService (7 napos naptár és heti terheléssimítás)
3. CircadianAlertService (Cirkadián határidők és állapotriasztások)
4. UltradianEngineService (90/20 perces Kleitman BRAC ciklusok)
5. ChronoNutritionService (Étkezési idősávok és kaja-kóma csillapítás)
6. PhototherapyService (10k Lux és kékfény protokoll)
7. BurnoutPredictionService (Allosztatikus terhelés és kumulatív kiégés modell)
8. SocialJetlagService (Többprofilos cirkadián metszet és social jetlag)
9. MicroRecoveryService (20-20-20 és szomatikus sóhaj mikroszünetek)
10. CircadianAnalyticsService (Alignment Score és kognitív ROI)

## 4. Következmények
- Pozitív: Moduláris, tiszta architektúra, átfogó tesztlefedettség.
- Megkötés: Minden új modul szigorúan típusozott és max 400 sor.