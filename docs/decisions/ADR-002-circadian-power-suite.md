# ADR-002: Cirkadián Power Suite — Dynamic Ripple Re-flow, Koffein-Ablak és Zen Fókusz Mód

- **Dátum:** 2026-08-26
- **Státusz:** accepted
- **Szerző:** Python System Architect & E2E QA Lead
- **Kanban:** #EC-002

## Kontextus
A feladat-koreográfus alapmodellje sikeresen bizonyított. A felhasználói visszajelzések (VOC) és mély biohacking kutatások alapján a merev napirend legnagyobb ellensége a valós időcsúszás (egy elhúzódó meeting vagy feladat), a nem megfelelő koffein-időzítés (délutáni adenozin összeomlás és alvászavar), valamint a rossz alvás utáni merev terhelés. Szükség van egy dinamikus, valós idejű adaptációs rétegre.

## Döntés

1. **Dinamikus "Ripple Re-flow" Motor (`/api/v1/energy/schedule/reflow`):**
   - Bemenetként megkapja az aktuális időt ($t_{now}$, pl. "14:15"), a már befejezett feladatokat, a fix meetingeket és a hátralévő teendőket.
   - Az ütemezési horizontot $[t_{now}, t_{sleep}]$ közé szűkíti.
   - A hátralévő `DEEP_WORK` feladatokat a nap hátralévő csúcsaira (pl. 16:30-18:30 délutáni fókusz), az `ADMIN` feladatokat az alacsony energiazónákra szervezi át.
2. **Koffein-Ablak & Kognitív Zuhanás Védelem:**
   - **Koffein Kezdet (CAR védelem):** $t_{wake} + 90\text{ perc}$ (nem engedi a reggeli korai kávézást, megvédve a természetes kortizol-csúcsot).
   - **Koffein Cut-off (Mély alvás védelem):** $t_{sleep} - 9\text{ óra}$ (pl. 23:00 alvásnál 14:00 után tilos a koffein).
   - **Caffeine Window:** $[t_{wake}+90\text{m}, t_{sleep}-9\text{h}]$, vizuálisan aranysárga sávként a Canvas hullámon.
3. **Alvásminőség & Napi Regeneráció Skálázó ($\gamma_{recovery}$):**
   - $E_{cap}^{adj}(t) = E_{base} + (E_{cap}(t) - E_{base}) \times \gamma_{recovery}$ ($\gamma \in [0.3, 1.2]$).
   - Ha $\gamma \le 0.6$ (rossz alvás), a maximális folyamatos mélymunka limit **120 percről 60 percre csökken**, és a rendszer hosszabb (30m) `RECOVERY` szüneteket ír elő.
4. **Kapszula Flow-Timer & Zen Mód (0 külső függőség):**
   - Web Audio API szintetizátor: Natív **Brown Noise** (barna zaj) és **Alpha Binaural Beats** ($10\text{ Hz}$ frekvencia-különbség a két fül között) generátor a mély fókusz azonnali eléréséhez.
   - Teljes képernyős, zavarmentes fókusz modal a feladat színével pulzáló progresszióval.

## Elvetve

| Opció | Miért nem |
|---|---|
| Külső MP3 stream audio fájlok | Hálózati sávszélességet eszik, szerzői jogi/licenc problémák; a Web Audio API 0-bájtos natív szintézis azonnali és offline |
| Minden feladat merev előretolása fix percekkel | Nem veszi figyelembe a cirkadián energiaszinteket (pl. mély kódolást nem tolhatunk a 22:00-s alvás előtti órákra) |

## Következmény
- `SPEC-003` specifikálja az új végpontokat és a frontend bővítményt.
- E2E tesztkészlet (`test_e2e_003_power_suite.py`) validálja a reflow-t, a koffein-ablakot és a modulált energiaszámítást.
