# US-005: Piaci & Felhasználói Igény Alapú Funkciók (v1.4.0)

## 1. Felhasználói Történet Áttekintés
**Mint** elfoglalt szakember és biohacker,  
**Akarom**, hogy az EnergyCalendar védjen a kontextusváltási fragmentációtól, az ADHD idővakságtól, a meetingek kognitív kimerülésétől és a jetlagtől,  
**Azért, hogy** tiszta fókusszal és fenntartható energiával végezhessem a napi munkámat.

---

## 2. Elfogadási Kritériumok (BDD)

### Scenario 1: Kontextusváltási Adósság Számítása
- **Given** egy feladatlista 6 váltással mélymunka és admin között
- **When** lekérem az elemzést a /api/v1/energy/context-switch/tax végponton
- **Then** a rendszer kiszámítja a fragmentációs adót (pl. 45 perc elvesztegetett figyelem) és batching javaslatot ad.

### Scenario 2: Cirkadián Jetlag Adaptáció
- **Given** egy 6 órás időzóna ugrás (pl. UTC+2 -> UTC-4)
- **When** generálom az adaptációt a /api/v1/energy/jetlag/plan végponton
- **Then** a rendszer naponkénti 60 perces eltolási fázisokat és melatonin/napfény protokollt ad vissza.

### Scenario 3: ADHD NeuroFlow Idővakság Védelem
- **Given** egy 120 perces folyamatos feladat
- **When** aktiválom a védelmet a /api/v1/energy/neuroflow/guard végponton
- **Then** a rendszer lágy kivezető szakaszt és hiperfókusz riasztást generál.

### Scenario 4: Környezeti Biophilia és CO2 Audit
- **Given** irodai adatok: CO2 = 1200 ppm, Hőmérséklet = 24.5 °C
- **When** beküldöm a környezeti auditot a /api/v1/energy/biophilic/audit végpontra
- **Then** a rendszer kiszámítja a kognitív kapacitáscsökkenést és szellőztetési riasztást ad.

### Scenario 5: Dopamin Súrlódás és Fókuszvédelem
- **Given** reggeli fókuszcsúcs 09:00 és 11:30 között
- **When** kérem a dopamin protokollt a /api/v1/energy/dopamine/guard végponton
- **Then** a rendszer szigorú digitális csendet és minimális ingerszegény zónát jelöl ki.

### Scenario 6: Web Audio Soundscapes (Gamma 40Hz, Theta, Pink)
- **Given** mély kódolási feladat
- **When** konfigurálom a hangtájat a /api/v1/energy/soundscape/config végponton
- **Then** a rendszer 40Hz Gamma és Rózsaszín Zaj szintetizátor beállításokat ad vissza.

### Scenario 7: Időjárás és Front Cirkadián Korrekció
- **Given** hidegfront és alacsony légnyomás (1002 hPa)
- **When** lekérem a korrekciót a /api/v1/energy/weather/adjust végponton
- **Then** a rendszer kiszámítja a szükséges extra regenerációs kompenzációt.

### Scenario 8: Cirkadián Edzés & Hormézis Időzítő
- **Given** felhasználói cirkadián profil
- **When** generálom az edzéstervet a /api/v1/energy/workout/timing végponton
- **Then** a rendszer 16:30-18:30 közé javasolja az intenzív izomerőt, reggelre a zsírégetést.

### Scenario 9: Értekezlet Kognitív Adó és Levezető Puffer
- **Given** 3 órányi megbeszélés
- **When** elemzem a terhelést a /api/v1/energy/meeting/tax végponton
- **Then** a rendszer automatikusan 15 perces dekompressziós sávokat ütemez.

### Scenario 10: Szezonális és Infradián Ritmus
- **Given** téli szezon rövid nappalokkal
- **When** generálom a tervet a /api/v1/energy/infradian/plan végponton
- **Then** a rendszer megnövelt reggeli lux igényt és finomított alvásablakot határoz meg.
