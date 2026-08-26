# Versenytárs Elemzés & Heti Pásztázás: 2026-W35
## Cirkadián Produktivitási és Időgazdálkodási Piac

> **Dátum:** 2026-08-26 (2026-W35)  
> **Szerző:** Python System Architect & QA Lead  
> **Cél:** A piacvezető feladatkezelő és naptár alkalmazások mély elemzése, árstruktúrájuk, erősségeik, felhasználói panaszaik és az EnergyCalendar piaci rései.

---

## 1. Versenytárs Mátrix és Árazás

| Alkalmazás | Havi Ár (B2C) | Fő Értékajánlat | Legnagyobb Előny | Felhasználói Panaszok / Piaci Rések (G2, Reddit) |
|---|---|---|---|---|
| **Motion** | **$34 / hó** (vagy $228/év) | AI naptár és automatikus átütemezés | Automatikus feladat-beszúrás naptár-résekbe | Merev, lineáris órákkal számol; nem ismeri a cirkadián ritmust; elcsúszáskor szorongást kelt; extrém drága egyéni felhasználóknak. |
| **Sunsama** | **$20 / hó** (vagy $192/év) | Tudatos, kiégés-megelőző napi tervező | Napi Lezárási Rituálé (Shutdown), terhelési limit (max 6 óra/nap) | Teljesen manuális; nincs biológiai optimalizálás; nincs automatikus idősáv-illesztés vagy koffein védelem. |
| **Rise Science** | **$60 / év** | Cirkadián energiahullám & alvásadósság | Kiváló tudományos alvás/energia modell | Tisztán passzív nézet! Nem enged feladatokat tervezni vagy végrehajtani a csúcsokon; nincs beépített naptár. |
| **Reclaim.ai** | **$10 / hó** | Okos naptár szokások és 1:1 meetingek | Google Calendar kétirányú szinkron és védelem | Mechanikus idő-számítás; hiányzik a biometria és a kognitív terhelés megkülönböztetése. |
| **Lifestack.ai** | **$12 / hó** | Cirkadián energia + naptár | Naptár és energiaszint összekapcsolása | Nincs feladat-dekompozíció; nincs beépített fókusz hangtér; hiányoznak a lezárási rituálék. |
| **Goblin.tools** | **Ingyenes / $1** | AI feladatbontó neurodivergens felhasználóknak | "Magic ToDo" komplex feladatok bontása | Egyáltalán nincs benne naptár, idővonal vagy energiamodell. |

---

## 2. A 3 Legégetőbb Piaci Rés és Felhasználói Igény (VOC)

### 1. Piaci Rés: "The Evening Shutdown Void" (Napi Lezárás és Alvásvédelem)
- **VOC:** *"A Sunsama $20/hó áráért szinte csak a Daily Shutdown funkciót fizetik a felhasználók, mert a munkanap lezárása nélkül az agy képtelen kikapcsolni (Zeigarnik-effektus)."*
- **Cirkadián Lehetőség:** Nem egyszerűen lezárjuk a napot, hanem az esti Melatonin-felszabadulási ablakhoz ($t_{sleep} - 60\text{m}$) igazítva vezetjük át a felhasználót a kognitív munkából a regenerációba.

### 2. Piaci Rés: "The Task Overwhelm Paralysis" (Túl nagy feladatok blokkolása)
- **VOC:** *"Ha beírom, hogy 'Szakdolgozat 240 perc', a naptár nem tud vele mit kezdeni, én pedig halogatok."*
- **Cirkadián Lehetőség:** Automatikus Kognitív Dekompozíció — a 120 percnél hosszabb feladatot a rendszer automatikusan felbontja egymást követő kreatív, mélymunka és admin lépésekre, amelyek pont illeszkednek a szabad csúcsokba.

### 3. Piaci Rés: "Corporate Calendar Silo" (.ics / Google Calendar interoperabilitás)
- **VOC:** *"Hiába imádom a cirkadián tervezést, ha a céges meetingjeim a Google Calendarban / Outlookban vannak és manuálisan kell átmásolnom őket."*
- **Cirkadián Lehetőség:** Szabványos RFC 5545 `.ics` export és import — a meetingek automatikusan fix sávokká válnak, az optimalizált teendők pedig egy kattintással bekerülnek a külső naptárba.
