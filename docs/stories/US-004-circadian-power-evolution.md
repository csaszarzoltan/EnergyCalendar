# US-004: Cirkadián Evolúció — 10 Új Funkció

## 1. Felhasználói Történet Áttekintés
**Mint** tudatos biohacker és tudásmunkás,  
**Akarom**, hogy az EnergyCalendar kezelje a biometrikus adataimat, a heti makro-ritmusomat, az étkezési és fényterápiás hatásokat, valamint a mikroszüneteket és a társas szinkront,  
**Azért, hogy** maximalizáljam a kognitív teljesítményemet és megelőzzem a kiégést.

---

## 2. Elfogadási Kritériumok (BDD)

### Scenario 1: Biometrikus HRV és Alvásadatok Feldolgozása
- **Given** egy éjszakai alvásadat: HRV = 65 ms, RHR = 52 bpm, Deep+REM = 140 perc
- **When** beküldöm a biometrikus adatokat a /api/v1/energy/biometrics/sync végpontra
- **Then** a rendszer kiszámítja a $\\gamma_{recovery} \\approx 1.15$ értéket és frissíti a cirkadián fázist.

### Scenario 2: Heti Makro-Ritmus és Kognitív Simítás
- **Given** 7 napra elosztandó feladatok listája
- **When** lekérem a heti mátrixot a /api/v1/energy/weekly/matrix végponton
- **Then** a rendszer kiegyenlíti a napi terhelést, és kijelöli a Deep Work fókusz napokat.

### Scenario 3: Valós Idejű Cirkadián Riasztások
- **Given** aktuális időpont {now} = 14:15$, és a koffein cutoff $ volt
- **When** lekérem a cirkadián riasztásokat a /api/v1/energy/alerts végponton
- **Then** a válasz tartalmaz egy aktív figyelmeztetést a koffein tilalomról.

### Scenario 4: Ultradián 90/20 Ciklus Bontás
- **Given** egy 180 perces komplex projekt
- **When** átadom az ultradián motornak a /api/v1/energy/ultradian/split végponton
- **Then** a rendszer 2 x 90 perces blokkra bontja 20 perces pihenőkkel.

### Scenario 5: Krono-Táplálkozási Kaja-Kóma Elemzés
- **Given** magas szénhidráttartalmú ebéd 12:30-kor
- **When** beküldöm az étkezést a /api/v1/energy/nutrition/impact végpontra
- **Then** a rendszer kiszámítja a megnövekedett mélyponti depressziót és az optimális regenerációs sávot.

### Scenario 6: Fényterápia & Kékfény Protokoll
- **Given** ébredés 06:30-kor és lefekvés 22:30-kor
- **When** lekérem a fényprotokollt a /api/v1/energy/phototherapy/plan végponton
- **Then** a reggeli napfény 06:30–07:15, a kékfény blokkolás pedig 20:30-tól javasolt.

### Scenario 7: Allosztatikus Terhelés & Kiégés-Előrejelzés
- **Given** az elmúlt 5 nap kumulatív kognitív adósság adatai
- **When** lekérem a kiégési indexet a /api/v1/energy/burnout/prediction végponton
- **Then** a rendszer visszaadja az Allostatic Load Indexet (0-100) és regenerációs ajánlást.

### Scenario 8: Csapat Cirkadián Metszet (Social Jetlag)
- **Given** egy Pacsirta és egy Éjjeli Bagoly profil
- **When** összehasonlítom őket a /api/v1/energy/social/sync végponton
- **Then** a rendszer kijelöli az optimális közös aranyablakot (10:30–12:00) és a Social Jetlag mértékét.

### Scenario 9: Szomatikus Mikroszünetek (20-20-20 & Physiological Sigh)
- **Given** 60 perc folyamatos képernyőmunka
- **When** lekérem a mikroszüneteket a /api/v1/energy/micro-recovery/plan végponton
- **Then** a rendszer ütemezi a 20-20-20 szemtornát és a 3x fiziológiás sóhajt.

### Scenario 10: Cirkadián Teljesítmény és Alignment Riport
- **Given** elvégzett feladatok és az elért cirkadián egyezés
- **When** generálom az analitikát a /api/v1/energy/analytics/alignment végponton
- **Then** a rendszer kiszámítja a Circadian Alignment Score-t (pl. 88%).