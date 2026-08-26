# Research Deep-Dive: Cirkadián Energia-Ritmus és Kognitív Terhelés Alapú Feladat-Koreográfus
## Swiss P Map / EnergyCalendar — Kutatás és Rendszertervezés

> **Dátum:** 2026-08-26  
> **Szerző:** Python System Architect (Hermes / Antigravity)  
> **Téma:** Nem-lineáris időgazdálkodás, cirkadián bioritmus modellezés, kognitív terhelés optimalizálás és dinamikus feladat-koreográfia  
> **Cél:** A merev, rekeszes naptárak (time-blocking) meghaladása folyamatos kognitív energia-kapacitás függvény ($E_{cap}(t)$) és intelligens illesztő algoritmus segítségével.

---

## 1. Vezetői Összefoglaló és Piaci Helyzetkép (VOC & Benchmark)

A modern tudásmunkások és fiatal szakemberek (Gen Z / Millennial) körében a klasszikus naptárak és todo listák (Google Calendar, Outlook, Todoist) alapvető elégtelenséggel küzdenek:
1. **Lineáris illúzió:** A hagyományos naptár minden órát egyenértékűnek tekint (09:00 reggel = 14:00 ebéd után), holott az emberi agy kognitív kapacitása nem egyenletes.
2. **Kognitív kimerülés (Burnout & Energy Debt):** A felhasználók hajlamosak a naptárukat 100%-ra tölteni mély fókuszú munkával, ami délutánra agyi ködöt és produktivitási zuhanást eredményez.
3. **Merev blokkosítás kontra rugalmas ritmus:** Ha egy meeting 15 perccel elcsúszik, a merev time-block naptár összeomlik, és bűntudatot generál.

### Piaci Körkép és Versenytárs Mátrix

| Megoldás | Cirkadián Modellezés | Kognitív Terhelés Kezelés ($C$) | Regenerációs Szünetek | Gravitációs / Vizuális UI | NLP Automatikus Besorolás |
|---|---|---|---|---|---|
| **Google Calendar / Outlook** | ❌ Nincs | ❌ Nincs | ❌ Nincs | ❌ Merev rácsos | ❌ Nincs |
| **Motion / Reclaim.ai** | ❌ Naptár-rés alapú | ⚠️ Statikus prioritás | ⚠️ Opcionális buffer | ❌ Standard naptár | ⚠️ Részleges |
| **RISE Science** | ✅ Alvás/Cirkadián | ❌ Nincs feladatkezelés | ❌ Nincs | ⚠️ Statikus grafikon | ❌ Nincs |
| **Lifestack.ai** | ⚠️ Alapvető hullámok | ⚠️ Részleges | ❌ Nincs auto-pihenő | ⚠️ Hagyományos sávok | ❌ Nincs |
| **Energia-Koreográfus (Tervünk)** | **✅ Folyamatos $E_{cap}(t)$** | **✅ 4-szintű kognitív skála** | **✅ Automatikus 120m rest** | **✅ Dinamikus spline + kapszulák** | **✅ Helyi intelligens parser** |

---

## 2. Kronobiológiai és Kognitív Tudományos Alapok

A rendszer a kronobiológia és az alvásszabályozás elismert **Borbély-féle Két-Folyamat Modelljére (Two-Process Model of Sleep Regulation)**, valamint az ultradián ritmusokra épül:

1. **Process C (Cirkadián oszcilláció):**
   - A tobozmirigy és a suprachiasmatic nucleus (SCN) által vezérelt belső 24 órás óra.
   - Jellemzője a reggeli ébredés után 1.5–3 órával jelentkező **Kognitív Csúcs (Peak 1)**, a 7-8 órával ébredés utáni **Post-prandial Dip (Kaja-kóma mélypont)**, valamint a kora esti **Másodlagos Csúcs (Peak 2)**.
2. **Process S (Homeosztatikus kognitív nyomás):**
   - Az ébrenlét alatt az agyban felhalmozódó adenozin és mentális fáradtság.
   - A mély fókuszú munka (`DEEP_WORK`) gyorsítja a Process S meredekségét.
3. **Ultradián Ritmus (90-120 perces fókuszablakok):**
   - Ernest Rossi és Nathaniel Kleitman kutatásai szerint az emberi fókusz ~90-120 perc után kognitív platóra ér, ami után legalább 15-30 perc regeneráció (`RECOVERY`) szükséges az idegi kapacitás helyreállításához.

---

## 3. Matematikai Energiamodell

### 3.1. Az Energia-Kapacitás Függvény: $E_{cap}(t) \in [0.0, 10.0]$
Legyen $t$ a nap egy adott időpontja percekben ($t \in [0, 1440]$).
A felhasználó kronotípusa alapján:
- $t_{wake}$ és $t_{sleep}$: ébredési és elalvási időpontok.
- $P_1 = [t_{p1\_start}, t_{p1\_end}]$: Elsődleges fókuszcsúcs ($E \approx 8.5 - 10.0$).
- $D_1 = [t_{d1\_start}, t_{d1\_end}]$: Post-lunch energiamélypont ($E \approx 2.0 - 4.0$).
- $P_2 = [t_{p2\_start}, t_{p2\_end}]$: Másodlagos fellendülés ($E \approx 6.0 - 7.5$).

A folytonos $E_{cap}(t)$ görbét egy darabonként simított hermite-spline vagy többcsúcsú Gauss-görbe szuperpozíciójaként modellezzük:

$$E_{cap}(t) = E_{base} + A_1 e^{-\frac{(t - \mu_1)^2}{2\sigma_1^2}} - A_d e^{-\frac{(t - \mu_d)^2}{2\sigma_d^2}} + A_2 e^{-\frac{(t - \mu_2)^2}{2\sigma_2^2}} - \lambda_{decay}(t - t_{wake})$$

Ahol:
- $E_{base} \approx 4.0$ az alap ébrenléti energiaszint.
- $A_1, A_2$ a fókuszcsúcsok amplitúdói, $A_d$ a mélypont depressziója.
- $\lambda_{decay}$ a Process S lassú lineáris fáradási koefficiense.

### 3.2. Feladat Kognitív Terhelési Kategóriák

| Kategória (`CognitiveLoad`) | Kognitív Súly ($W$) | Optimális $E_{cap}(t)$ Tartomány | Jellemző Tevékenység |
|---|---|---|---|
| `DEEP_WORK` | $8.0 - 10.0$ | $\ge 7.5$ | Kódolás, tanulás, stratégiai írás, architektúra |
| `CREATIVE` | $5.0 - 7.0$ | $5.0 - 7.4$ | Brainstorming, vázlatok, design, asszociatív munka |
| `ADMIN` | $2.0 - 4.0$ | $1.0 - 4.9$ | Számlázás, rutin e-mailek, adminisztráció, rendszerezés |
| `RECOVERY` | $-2.0 - -5.0$ | Bármikor (Dipekben ajánlott) | Séta, meditáció, edzés, ebéd, szünet |

### 3.3. Szabad Energia és Túlcsordulási Egyenleg (Energy Debt)

A fix események (pl. 10:00 meeting, orvos) lefoglalják az adott idősávokat:
$$\text{FreeEnergy}(t) = \begin{cases} 0, & \text{ha } t \in \text{FixEsemény} \\ E_{cap}(t), & \text{egyébként} \end{cases}$$

A napi kognitív adósság (**Energy Debt**, $E_{debt}$):
$$E_{debt} = \max\left(0, \sum_{i \in \text{Tasks}} (\text{energy\_cost}_i \times \text{duration}_i) - \int_{t_{wake}}^{t_{sleep}} \text{FreeEnergy}(t) \, dt\right)$$

Ha $E_{debt} > 0$, a rendszer nem blokkol, hanem **vizuális túlterhelési figyelmeztetést** (hőtérkép vörös zóna, energiahitel index) ad a felhasználónak.

---

## 4. Az Ütemező Algoritmus (Energy-Constrained Bin-Packing / CSP)

Az algoritmus 5 determinisztikus lépésben fut le:

1. **Rács-felosztás:** A nap felosztása 15 perces diszkrét időszeletekre ($S_k$).
2. **Fix blokkok maszkolása:** A merev naptári események lefoglalják a szeleteket.
3. **Feladatok osztályozása és rendezése:**
   - A `DEEP_WORK` feladatok a legnagyobb kognitív költség szerint csökkenő sorrendbe rendezve.
   - A `CREATIVE`, majd `ADMIN` feladatok sorba állítása.
4. **Mohó / Korlát-Kielégítési Illesztés:**
   - Minden `DEEP_WORK` feladat a legmagasabb átlagos $\text{FreeEnergy}$ ablakba kerül.
   - **Kényszer:** Ha az egymást követő `DEEP_WORK` blokkok összege $> 120$ perc, a rendszer kötelezően beékel egy $15-30$ perces `RECOVERY` blokkot.
   - Az `ADMIN` feladatok a dip (mélypont) időszakokba kerülnek ($E_{cap} \le 4.5$).
5. **Konzisztencia és Túlcsordulás számítás:**
   - Megszámolja a be nem férő feladatokat és kiszámítja a napi $E_{debt}$ értéket.

---

## 5. Modern Frontend Koncepció: "Vivid Bioluminescence"

A felhasználói élmény szakít a hideg, unalmas téglalap-naptárakkal:
- **Dinamikus Hullámvonal (Canvas / SVG Spline):** A nap hátterében folyamatosan pulzáló biolumineszcens görbe:
  - Zöldeskék / Cyan: Csúcsenergia zónák.
  - Ibolya / Mályva: Kreatív zónák.
  - Sárgás narancs: Admin / Mélypont zónák.
  - Vörös: Energy Debt / Kognitív túlterhelés.
- **Úszó Feladat-Kapszulák:** Lekerekített kapszula kártyák, amelyek hossza arányos az időtartammal, fényük és szegélyük a terhelési típust tükrözi.
- **Gravitációs Drag-and-Drop:** Amikor a felhasználó mozgat egy kapszulát, az energiahullám mágneses vonzással ráugrik a kompatibilis energiasávra.
- **Kognitív Hőtérkép Sáv:** Fejlécben lévő 0-100%-os mentális telítettségi indikátor.
