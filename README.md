# Energia-Ritmus & Heti Rutin-Koreográfus (EnergyCalendar) v1.1.0

> Modern, cirkadián ritmusra és kognitív energiaszintre optimalizált feladat- és időszervező rendszer biohacking és valós idejű adaptációs modulokkal.

---

## Fő Képességek

- 🌊 **Dinamikus "Ripple Re-flow":** Egyetlen kattintással újrahullámoztatja a hátralévő napot az aktuális időponttól ($t_{now}$), ha egy meeting vagy feladat elcsúszna.
- ☕ **Koffein-Ablak & Zuhanásvédelem:** Cortisol Awakening Response (CAR) 90 perces késleltetés és 9 órás esti alvásvédő koffein-cutoff határ aranysárga zónaként az energiahullámon.
- 🛌 **Alvásminőség & Vitalitás Skálázó:** Valós idejű csúszka (30% - 120%), amely alacsony alvásminőség esetén automatikusan 60 percre szigorítja a maximális mélymunka blokkot.
- 🎧 **Zen Fókusz Mód & Web Audio Szintetizátor:** Zavarmentes fókusz-tér beépített natív **Barna Zaj (Brown noise)** és **10Hz Alfa Binaural Beats** generátorral (0 külső függőség).
- 🎯 **Kognitív Terhelés-Illesztés:** A mély fókuszú munkát (`DEEP_WORK`) a fókuszcsúcsokra, a mechanikus feladatokat (`ADMIN`) a délutáni mélypontokra helyezi.
- 🛡️ **120 perces Fókuszvédelem:** Automatikus 20-30 perces regenerációs (`RECOVERY`) szüneteket iktat be.
- ⚡ **Energy Debt Detekció:** Kognitív túlterheltségi mutató és valós idejű adósság-figyelmeztetés.
- 🧠 **NLP Gyorsbevitel:** Magyar és angol feladatleírások automatikus bontása.

---

## Gyorsindítás

### 1. Szerver futtatása
```bash
uvicorn src.main:app --host 127.0.0.1 --port 8888
```
Nyisd meg: `http://localhost:8888`  
API Dokumentáció: `http://localhost:8888/docs`

### 2. Tesztek futtatása (56 teszt)
```bash
pytest -v
```
