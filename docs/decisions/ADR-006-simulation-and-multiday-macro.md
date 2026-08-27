# ADR-006: Cirkadián Időgép Szimuláció, Heti Makro-Ritmus Tábla és Hangos Neuro-Chime Riasztások

## Státusz
Elfogadva (Accepted) — v1.5.0

## Kontextus
A felhasználóknak szükségük van arra, hogy:
1. **Előre lejátszhassák a napjukat (Circadian Time Machine):** interaktív szimulációval láthassák, mely napszakban hogyan változik az energiaszintjük, mikor jön a koffein cutoff és a kaja-kóma.
2. **Heti Makro-Ritmus Tábla:** 7 napos közvetlen vizuális nézet, ahol a mély fókusz napok és regenerációs napok szétoszthatók.
3. **Web Audio Neuro-Chime Riasztások:** Diszkrét, szintetizált hangjelzés (chime) fókuszcsúcs belépésekor vagy koffein-stopnál.

## Döntés
1. Létrehozunk egy `SimulationService` szolgáltatást (`src/services/simulation_service.py`), amely adott időpontra ($t$) kiszámítja az aktuális kognitív állapotot, hátralévő feladatokat és zónákat.
2. Frontend időgép-vezérlőt integrálunk interaktív Canvas lézerszállal és valós idejű hangjelzésekkel.
3. Unit és Black-Box E2E tesztekkel verifikáljuk a funkcionalitást.
