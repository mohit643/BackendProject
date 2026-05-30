# Architecture

Ye document batata hai: kaun sa approach chuna aur kyun, data structure ka design, kaun se future changes anticipate kiye aur unhe design bina code-change ke kaise handle karta hai, weight/rule kaise badle, aur kya assumptions liye.

---

## 1. Approach / framework — aur kyun

**Approach: pluggable cost-function ke saath time-ordered greedy event simulation.**

Soch ye hai ki ye problem CRUD (store/show) ya forecast (predict) nahi hai — ye ek **decision-making** problem hai, bilkul Google Maps jaisa: situation do, system soch ke best plan banake de.

Kaam do hisson mein bata gaya:

- **Engine** — buses ko time ke order mein process karta hai. Har charge "request" par dekhta hai charger free hai ya busy; free to turant charge, busy to wait. Jab kai buses ek charger par kareeb same time aati hain (jhagda), to faisla ek **score** se hota hai.
- **Rules** — har soft-rule (individual, operator, overall) ek alag chhota function hai jo ek number (score) lautata hai. Engine in scores ko weights se mila kar priority nikalta hai.

**Kyun ye fit hai:**

- **Simple aur defensible** — har charge ka faisla saaf logic se hota hai, samjhana aasaan.
- **Scale ke liye sahi** — engine (kaise schedule kare) aur rules (kis cheez ko importance) alag hain. Naya rule = naya function, engine touch nahi. Weight = data ki value.
- **Aage badhne ki gunjaish** — agar kal greedy ki jagah proper optimizer (jaise OR-Tools) chahiye, to rules same rahenge — sirf engine swap hoga. Cost-function abstraction wahi rehta.

Is scale (20 buses, 4 stations) ke liye full optimization (ILP/search) over-engineering hota — spec bhi "don't over-engineer" kehta hai. Greedy + weighted scoring is problem ke liye sahi balance hai.

---

## 2. Data structure design

Ek scenario = ek Python dictionary jo **puri duniya** describe karta hai. Code is dictionary ko padhta hai; kuch hardcode nahi.

```python
scenario = {
    "name": "...",                 # dropdown label
    "description": "...",          # UI explanation
    "route": {
        "segments": [              # har segment alag — distance change easy
            {"from": "Bengaluru", "to": "A", "distance_km": 100},
            ...
        ]
    },
    "stations": [                  # har station ka apna charger-count
        {"id": "A", "chargers": 1},
        ...
    ],
    "physics": {                   # duniya ke constants — ek jagah
        "battery_range_km": 240,
        "charge_time_min": 25,
        "speed_kmph": 60,
    },
    "weights": {                   # tunable — ek jagah, hardcode nahi
        "individual": 1.0,
        "operator": 1.0,
        "overall": 1.0,
    },
    "buses": [                     # list — ginti chahe jitni ho
        {"id": "bus-BK-01", "operator": "kpn", "direction": "BK", "departure": "19:00"},
        ...
    ],
}
```

**Design choices aur kyun:**

- **Route ko segments ki list rakha** (ek total number nahi) — taaki station add karna ya kisi segment ki doori badalna ek-line ka kaam ho. `station_distances` cumulative doori khud nikal leta hai.
- **`chargers` ko har station par alag field** rakha — taaki "B par 2 charger" sirf data badalne se ho.
- **`physics` alag block** — battery/charge-time/speed ek jagah; nayi battery aaye to ek number badlo.
- **`weights` ek hi jagah** — spec ka core requirement (one obvious value, one obvious place).
- **`buses` ek list** — 14, 20, ya 100 — code ko parwah nahi.
- **`direction` field** ("BK"/"KB") — engine isi se decide karta hai ki doori Bengaluru se napni hai ya Kochi se.

**Output data** (har charge ka record) bhi saaf rakha: `bus_id, operator, station, arrive, wait, start, finish` — taaki UI ise per-bus aur per-station dono tarah group kar sake.

---

## 3. Anticipated future changes (aur design unhe kaise handle karta hai)

Sabse zaroori section. Ye wo changes hain jo maine design karte waqt soche, aur har ek **bina code-change** ke handle hota hai (sirf data ya chhota add):

| Future change                                                     | Kaise handle hota hai (code-change nahi)                                                                                                                              |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Naya charging station (E)**                                     | `stations` mein `{"id": "E", "chargers": 1}` aur `route.segments` mein ek segment add. `station_distances`, `find_valid_plans` sab list se chalte hain — khud adjust. |
| **Kisi station par zyada chargers (B par 2)**                     | `stations` mein `chargers: 2`. (Engine ka charger-tracking ek list of free-times ban jaye — chhota extend, niche note.)                                               |
| **Naya operator (RedBus)**                                        | Bus ke `operator` field mein likho. Engine kabhi operators ki ginti hardcode nahi karta — `operator_score` dynamic hai.                                               |
| **Segment ki distance badalna**                                   | `segments` mein number badlo. Saari cumulative distances khud recompute.                                                                                              |
| **Battery/charge-time/speed badalna**                             | `physics` mein value badlo. Engine wahi value padhta hai.                                                                                                             |
| **Weight badalna**                                                | `weights` mein value badlo — ek jagah.                                                                                                                                |
| **Naya soft-rule (priority bus, time-of-day cost, driver shift)** | `rules.py` mein naya function + `priority_score` mein ek line. Scheduling engine same.                                                                                |
| **Buses ki ginti badalna**                                        | `buses` list chhoti/badi karo — koi rewrite nahi.                                                                                                                     |
| **Naya scenario**                                                 | Ek nayi `scenario_N.py` file, app.py mein register. Same structure.                                                                                                   |
| **Multiple routes / route badalna**                               | Route data-driven hai; ek aur route ka data add ho sakta hai (multi-route ke liye thoda orchestration extend).                                                        |

Iska saar: **agar kal kuch badle, code tutne ka chance lagbhag zero hai** kisi bhi reasonable change ke liye — kyunki engine kuch maanta nahi, sab data se padhta hai.

---

## 4. Weight kaise badle (code example)

`scenarios/scenario_4.py`:

```python
"weights": {
    "individual": 1.0,
    "operator": 2.0,   # <-- ek value, ek jagah
    "overall": 1.0,
},
```

Engine (`run_scheduler` → `priority_score`) ise padh kar har bus ka weighted score nikalta hai:

```python
score = (
    weights["individual"] * individual_score(bus)
    + weights["operator"]  * operator_score(bus, all_buses)
    + weights["overall"]   * overall_score(all_buses)
)
```

Weight badla → score badla → jhagde mein "kaun pehle" badla → alag schedule. Code touch nahi.

---

## 5. Naya rule kaise add kare (code example)

**Step 1 — `engine/rules.py` mein naya score function:**

```python
def priority_bus_score(bus):
    return 1000 if bus.get("priority") else 0
```

**Step 2 — `engine/scheduler.py` ke `priority_score` mein jodo:**

```python
def priority_score(bus_state, all_bus_states, weights):
    ind = rules.individual_score(bus_state)
    op  = rules.operator_score(bus_state, all_bus_states)
    ov  = rules.overall_score(all_bus_states)
    pr  = rules.priority_bus_score(bus_state)            # naya rule

    return (
        weights["individual"] * ind
        + weights["operator"]  * op
        + weights["overall"]   * ov
        + weights.get("priority", 1.0) * pr              # naya weight (data se)
    )
```

Engine ka scheduling loop, charger-tracking, sab same. Rule aur uska weight pluggable hain.

---

## 6. Assumptions

- **Speed 60 km/h fixed** (1 km = 1 min) — spec ke example ke mutabik.
- **Har bus 2-charge plan leti hai** — 540 km route par 240 km battery ke saath 2 charge kaafi hain; 3+ charge ke valid combos bhi nikalte hain par default 2 use karte hain.
- **Load round-robin se baanta** — har bus ko baari-baari alag valid plan (A,C / B,C / B,D) diya jata hai, taaki saari buses ek hi station par na ghuse. Ye ek simple, fair starting strategy hai; iske upar weighted scoring lagti hai.
- **KB direction** — Kochi→Bengaluru buses ke liye doori Kochi se napi jati hai (total − Bengaluru-doori) aur plan reverse hota hai.
- **1 charger per station** abhi assume hai. `chargers` field data mein hai; multi-charger ke liye engine ka `charger_free_at` ek single time ke bajaye N free-times ki list ban jayega — chhota, localized change.
- **Jhagde mein tie** — agar score barabar ho to jo bus pehle pahunchi wo pehle (arrive time primary sort key, score secondary).

---

## 7. Kya done, kya next

**Done:** data structure (5 scenarios), valid-plan generation (240 km rule + max-charges cap), time/distance + direction handling, weighted greedy scheduler, Streamlit UI (input + per-bus + per-station).

**Next:** multi-charger support, best-plan selection ko aur optimize karna (abhi round-robin), aur (zaroorat pade to) greedy se proper optimizer par move.
