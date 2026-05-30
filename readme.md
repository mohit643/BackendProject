# Bus Charging Scheduler

Electric buses ek fixed route (Bengaluru → A → B → C → D → Kochi, 540 km) par chalti hain. Beech mein 4 charging stations hain (A, B, C, D), har ek par 1 charger. Har bus full charge par sirf 240 km chal sakti hai, isliye har bus ko beech mein kam se kam 2 baar charge karna padta hai. Ye app ek scheduler hai jo decide karta hai: har bus kaun se stations par charge karegi, kis order mein charger use hoga, aur kitna wait karegi.

Built with **Python + Streamlit**. Ek repo, ek process.

- **Hosted app:** `<your-streamlit-link-here>`
- **GitHub repo:** `<your-github-link-here>`

---

## How to run locally

Requirements: Python 3.10+ (3.11 / 3.12 recommended), pip.

```bash
# 1. Repo clone karo
git clone <your-github-link-here>
cd bus-scheduler

# 2. (Optional but recommended) virtual environment
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

# 3. Dependencies install karo
pip install -r requirements.txt

# 4. App chalao
streamlit run app.py
```

App browser mein khul jayega (`http://localhost:8501`). Upar dropdown se scenario chuno, neeche input data aur schedule dikhega.

---

## Project structure

```
bus-scheduler/
├── scenarios/          # DATA — 5 scenario files (puri duniya describe karti hain)
│   ├── scenario_1.py   # Even spacing
│   ├── scenario_2.py   # Bunched start
│   ├── scenario_3.py   # Asymmetric load
│   ├── scenario_4.py   # Operator-heavy
│   └── scenario_5.py   # Worst case convergence
├── engine/             # LOGIC
│   ├── rules.py        # 3 soft-rule score functions
│   └── scheduler.py    # saara scheduling logic
├── app.py              # Streamlit UI
└── requirements.txt
```

Design idea: **DATA (scenarios) ko CODE (engine) se alag rakha gaya hai.** Engine kuch hardcode nahi maanta — sab kuch data file se padhta hai. Isliye station / charger / operator / route badalna sirf data ka kaam hai, code rewrite nahi.

---

## How to change a weight

Weights teen soft-rules ki importance batate hain: `individual`, `operator`, `overall`. Ye har scenario file mein ek hi jagah hain — code mein kahin hardcode nahi.

`scenarios/scenario_4.py` mein:

```python
"weights": {
    "individual": 1.0,
    "operator": 2.0,   # <-- yahan badlo. Zyada value = us rule ki zyada importance
    "overall": 1.0,
},
```

Bas value badlo. Engine ise `run_scheduler` mein padh kar score nikalta hai — code chhuna nahi padta. Weight badalne se jhagde mein "kaun pehle charge kare" ka faisla badal jata hai, isliye alag weight → alag schedule.

---

## How to add a new rule

Naya soft-rule jodna do chhote steps ka kaam hai — engine rewrite nahi.

**Step 1 — `engine/rules.py` mein naya score function likho.** Ye ek number lautata hai (zyada = zyada priority):

```python
# Example: priority buses ko aage rakhne wala rule
def priority_bus_score(bus):
    # maan lo bus dict mein "priority" field hai
    return 1000 if bus.get("priority") else 0
```

**Step 2 — `engine/scheduler.py` ke `priority_score` mein use jodo:**

```python
def priority_score(bus_state, all_bus_states, weights):
    ind = rules.individual_score(bus_state)
    op = rules.operator_score(bus_state, all_bus_states)
    ov = rules.overall_score(all_bus_states)
    pr = rules.priority_bus_score(bus_state)          # <-- naya rule

    score = (
        weights["individual"] * ind
        + weights["operator"] * op
        + weights["overall"] * ov
        + weights.get("priority", 1.0) * pr           # <-- naya weight (data se)
    )
    return score
```

Naye rule ka weight bhi scenario file ke `weights` mein add kar sakte ho. Engine ka baaki hissa (charger free/busy, scheduling loop) bilkul same rehta hai.

---

## What the app shows

1. **Scenario dropdown** — 5 scenarios.
2. **Scenario input** — buses ki table (id, operator, direction, departure) + weights.
3. **Per-Bus Timetable** — har bus: kahan charge, kab pahunchi, kitna wait, charge time.
4. **Per-Station Charging Order** — A/B/C/D par buses kis order mein charge hui.

---

## Notes

- Speed 60 km/h fixed (1 km = 1 min) — spec ke example ke mutabik.
- Har bus 2-charge plan leti hai (is route par zyada ki zaroorat nahi).
- KB (Kochi→Bengaluru) buses ke liye doori Kochi se napi jati hai (ulti direction).
- 240 km battery rule har plan par enforce hota hai — koi invalid plan nahi chunta.

Aur detail ke liye **ARCHITECTURE.md** dekhein.
