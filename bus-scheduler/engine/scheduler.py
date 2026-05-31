import os
import sys

# scenarios folder ka raasta jodo, taaki wahan se scenario file import kar sakein
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scenarios"))

import scenario_1
import rules

from itertools import combinations


# ==========================================================
# travel_time_minutes
# Kaam: distance (km) aur speed se nikalta hai kitne MINUTE lagenge.
# Kyun: bus kab kahan pahunchegi, wo nikalne ke liye baar-baar time chahiye.
# Dummy: travel_time_minutes(100, 60) -> 100.0  (100km, 60 speed = 100 min)
# ==========================================================
def travel_time_minutes(distance_km, speed_kmph):
    time = (
        distance_km / speed_kmph * 60
    )  # ghante nikalo (dist/speed), phir *60 = minute
    return int(time)


# ==========================================================
# time_to_minutes
# Kaam: "19:00" jaise time ko MINUTES me badalta hai (raat 12 se gini).
# Kyun: text time me jod-ghatav nahi hota; number me aasaan.
# Dummy: time_to_minutes("19:00") -> 1140   (19*60 + 0)
#        time_to_minutes("19:30") -> 1170   (19*60 + 30)
# ==========================================================
def time_to_minutes(time_str):
    hours, minutes = time_str.split(":")  # "19:00" -> "19" aur "00"
    return int(hours) * 60 + int(minutes)  # ghante ko 60 se guna + minute


# ==========================================================
# minutes_to_time
# Kaam: minutes ko 12-hour AM/PM format me badalta hai.
#       Agle din ka time (24:00+) bhi sahi (26:00 -> 2:00 AM next day).
# ==========================================================
def minutes_to_time(total_minutes):
    total_minutes = int(total_minutes)

    # agle din ka time? (1440 min = 24 ghante = 1 din)
    day = total_minutes // (24 * 60)  # kaun sa din (0 = aaj, 1 = kal)
    mins_in_day = total_minutes % (24 * 60)  # us din ke andar ke minute

    hours = mins_in_day // 60
    minutes = mins_in_day % 60

    # 24-hour ko 12-hour AM/PM me badlo
    suffix = "AM" if hours < 12 else "PM"
    hour12 = hours % 12
    if hour12 == 0:
        hour12 = 12  # 0 ko 12 dikhao (12 AM / 12 PM)

    time_str = f"{hour12}:{minutes:02d} {suffix}"

    # agar agle din ka hai to "(+1d)" lagao
    if day > 0:
        time_str = time_str + f" (+{day}d)"

    return time_str


# ==========================================================
# station_distances
# Kaam: har station Bengaluru se kitni DOORI pe hai, wo nikalta hai.
# Kyun: pata chale bus ko kis station tak kitne km chalna hai (cumulative).
# Dummy: route ke segments se ->
#        {"A":100, "B":220, "C":320, "D":440, "Kochi":540}
# ==========================================================
def station_distances(route):
    total_distance_km = 0  # ab tak ki doori jodti jayegi, shuru 0 se
    distances = {}  # yahan bharenge: station -> doori
    for segment in route["segments"]:  # har segment pe ghoomo
        total_distance_km = total_distance_km + segment["distance_km"]  # doori jodo
        distances[segment["to"]] = total_distance_km  # us station ke naam pe save karo
    return distances


# ==========================================================
# is_plan_valid
# Kaam: check karta hai ek charging-plan VALID hai ya nahi (240km rule).
# Kyun: bus do charge ke beech 240km se zyada na chale, warna beech me band.
# Dummy: is_plan_valid([100, 320], 540, 240) -> True   (A,C theek hai)
#        is_plan_valid([320], 540, 240)      -> False  (sirf C - gap bahut bada)
# ==========================================================
def is_plan_valid(charge_points, total_distance, battery_range):
    points = (
        [0] + charge_points + [total_distance]
    )  # aage 0 (start), peeche 540 (end) jodo
    for i in range(len(points) - 1):  # har do lagaatar point ka gap dekho
        gap = points[i + 1] - points[i]  # agla point - abhi wala = gap
        if gap > battery_range:  # gap 240 se zyada?
            return False  # to plan galat, turant False
    return True  # saare gap theek -> plan sahi


# ==========================================================
# make_all_combos
# Kaam: stations se saari possible JODIYAAN (combos) banata hai.
# Kyun: bus kaun-kaun se station-set pe charge kar sakti hai, sab try karne ke liye.
# Dummy: make_all_combos(["A","B","C"], 3) ->
#        [["A"],["B"],["C"],["A","B"],["A","C"],["B","C"],["A","B","C"]]
# ==========================================================
def make_all_combos(stations, max_size):
    all_combos = []
    for size in range(1, max_size + 1):  # pehle 1-station combos, phir 2, phir 3...
        for combo in combinations(stations, size):  # us size ki saari jodiyaan
            all_combos.append(list(combo))  # tuple ko list banake jodo
    return all_combos


# ==========================================================
# combo_to_distances
# Kaam: station ke NAAM ko unki DOORI me badalta hai (translator).
# Kyun: is_plan_valid ko doori-number chahiye, naam nahi.
# Dummy: combo_to_distances(["A","C"], {"A":100,"C":320}) -> [100, 320]
# ==========================================================
def combo_to_distances(combo, station_dist):
    return [station_dist[s] for s in combo]  # har station 's' ka doori-number nikalo


# ==========================================================
# find_valid_plans
# Kaam: saari jodiyaan banao, har ek ko 240km rule se check karo,
#       jo VALID hain unki list lautao.
# Kyun: ye bus ke saare "achhe raaste" hain - engine inme se best chunega.
# Dummy: 4 stations (A,B,C,D), 540, 240 ->
#        [["A","C"], ["B","C"], ["B","D"], ["A","B","C"], ...]
# ==========================================================
def find_valid_plans(station_dist, total_distance, battery_range):
    stations = list(station_dist.keys())  # sirf naam (A,B,C,D)
    # zyada se zyada kitne charge ki zaroorat (battery limit se) - bade faltu combos rokne ke liye
    max_size = min(len(stations), total_distance // battery_range + 2)
    all_combos = make_all_combos(stations, max_size)  # saari jodiyaan banwao

    valid_plans = []
    for combo in all_combos:  # har jodi ke liye
        charge_points = combo_to_distances(combo, station_dist)  # naam -> doori
        if is_plan_valid(charge_points, total_distance, battery_range):  # rule check
            valid_plans.append(combo)  # valid ho to rakho
    return valid_plans


# ==========================================================
# build_bus_timeline
# Kaam: ek bus ka pura timeline - har station pe kab pahunchi,
#       kitna wait kiya, kitna charge, kab nikli, aur end pe kab pahunchi.
# Kyun: har bus ka detailed schedule chahiye - jisse jhagda solve ho
#       aur per-station order + wait dikha sakein.
# ==========================================================
def build_bus_timeline(
    departure_min, plan, station_dist, total_distance, speed_kmph, charge_time
):
    timeline = []  # har station ka record yahan jamaa hoga
    current_time = departure_min  # ghadi departure se shuru
    last_distance = 0  # pichhle point ki doori (shuru = origin = 0)

    for station in plan:  # raaste ke har station pe
        dist = station_dist[station]  # us station ki doori (Blr se)
        gap_km = dist - last_distance  # pichhle point se kitne km chala
        travel = travel_time_minutes(gap_km, speed_kmph)  # us km ka time (minute)

        arrive = current_time + travel  # station pe pahunchne ka time
        wait = 0  # abhi 0 (akeli bus). Jhagda step me badlega.
        leave = (
            arrive + wait + charge_time
        )  # nikalne ka time = pahunchi + wait + charge

        timeline.append(
            {  # is station ka poora record
                "station": station,
                "arrive": arrive,  # kab pahunchi
                "wait": wait,  # kitna wait kiya
                "charge": charge_time,  # charge me kitna (25)
                "leave": leave,  # kab nikli
            }
        )

        current_time = leave  # agla safar yahin se (charge karke nikalne ke baad)
        last_distance = dist  # ab pichhli doori = is station ki doori

    # aakhri charge ke baad end (Kochi/Bengaluru) tak ka safar
    final_gap = total_distance - last_distance
    final_travel = travel_time_minutes(final_gap, speed_kmph)
    arrival_at_end = current_time + final_travel

    return {"stops": timeline, "final_arrival": arrival_at_end}


# ==========================================================
# make_charge_requests
# Kaam: har bus ke liye uske plan ke hisaab se "charge requests" banata hai.
#       Direction ka dhyaan: KB (Kochi->Bengaluru) wali ke liye doori
#       Kochi se napi jaati hai (ulti chal rahi hai).
# ==========================================================
def make_charge_requests(bus, plan, station_dist, speed_kmph, total_distance):
    requests = []
    departure_min = time_to_minutes(bus["departure"])
    current_time = departure_min
    last_distance = 0

    for station in plan:
        # station ki doori - direction ke hisaab se
        if bus["direction"] == "KB":
            # KB ulti chal rahi: doori Kochi se = total - (Bengaluru se doori)
            dist = total_distance - station_dist[station]
        else:
            # BK seedhi: doori Bengaluru se (jaise hai)
            dist = station_dist[station]

        gap_km = dist - last_distance
        travel = travel_time_minutes(gap_km, speed_kmph)
        arrive = current_time + travel

        requests.append(
            {
                "bus_id": bus["id"],
                "operator": bus["operator"],
                "station": station,
                "arrive": arrive,
            }
        )

        current_time = arrive
        last_distance = dist

    return requests


# ==========================================================
# collect_all_requests
# Kaam: SAARI buses ki charge-requests banata hai, time-order me.
#       Har bus ko alag-alag plan deta hai (load baant ke) aur
#       direction ka dhyaan rakhta hai (KB wali ke liye ulta order).
# ==========================================================
def collect_all_requests(buses, valid_plans, station_dist, speed_kmph, total_distance):
    all_requests = []

    # sirf 2-charge wale plans rakho (jaise A,C / B,C / B,D) - simple aur kaafi
    two_charge_plans = [p for p in valid_plans if len(p) == 2]

    for index, bus in enumerate(buses):  # har bus, uske number ke saath
        # buses ko baar-baar alag plan do (0,1,2,0,1,2...) - load baant jaye
        plan = two_charge_plans[index % len(two_charge_plans)]

        # KB direction (Kochi->Bengaluru) ulti ja rahi - stations ulte order me
        if bus["direction"] == "KB":
            plan = list(reversed(plan))

        reqs = make_charge_requests(bus, plan, station_dist, speed_kmph, total_distance)
        for r in reqs:
            all_requests.append(r)

    all_requests.sort(key=lambda r: r["arrive"])
    return all_requests


# ==========================================================
# priority_score
# Kaam: ek bus ka total weighted score nikalta hai - rules.py ke
#       teeno scores ko weights se guna karke jodta hai.
# Kyun: jhagde me kaun pehle - jiska score zyada wo pehle.
# Zyada score = zyada wait jhela / company zyada pichhe -> priority.
# ==========================================================
def priority_score(bus_state, all_bus_states, weights):
    ind = rules.individual_score(bus_state)  # is bus ka wait
    op = rules.operator_score(bus_state, all_bus_states)  # company ka total wait
    ov = rules.overall_score(all_bus_states)  # network ka total wait

    score = (
        weights["individual"] * ind + weights["operator"] * op + weights["overall"] * ov
    )
    return score


# ==========================================================
# run_scheduler
# Kaam: requests ko time-order me process karta hai. Jab ek charger
#       free ho aur kai buses wait kar rahi hon, to WEIGHTS+rules ke
#       score se decide hota hai kaun pehle (jisne zyada jhela / company
#       pichhe). Wait_so_far live update hota hai, isliye score asli kaam karta.
# Kyun: alag weight -> alag schedule, aur wait kam.
# ==========================================================
def run_scheduler(requests, stations, charge_time, weights):
    # har station ka charger kab tak busy - shuru me sab free (0)
    charger_free_at = {}
    for s in stations:
        charger_free_at[s] = 0

    # har bus ka ab tak ka wait (rules ko chahiye), shuru 0
    bus_states = {}
    for req in requests:
        bus_states[req["bus_id"]] = {
            "bus_id": req["bus_id"],
            "operator": req["operator"],
            "wait_so_far": 0,
        }

    # jo abhi process karni baaki - arrive time se sort (jo pehle aati pehle dekho)
    pending = sorted(requests, key=lambda r: r["arrive"])

    results = []

    # ek-ek karke saari requests nipta do
    while pending:
        # abhi tak ki sabse jaldi wali request ka arrive time
        next_arrive = pending[0]["arrive"]

        # is waqt tak jo buses aa chuki hain aur jinka charger abhi busy hai
        # un sab me se WEIGHTS+score se chuno kaun pehle - baaki abhi nahi
        # simple aur sahi tareeka: har request ke liye uska actual start nikalo,
        # phir jiska start sabse pehle aur (tie pe) score zyada, use process karo

        def candidate_start(req):
            free_at = charger_free_at[req["station"]]
            return max(
                req["arrive"], free_at
            )  # bus aane ke baad hi, charger free hone ke baad hi

        # sabse achhi request chuno:
        # 1. jiska start sabse pehle (kam wait)
        # 2. tie pe - jiska score zyada (weights)
        def pick_key(req):
            state = bus_states[req["bus_id"]]
            score = priority_score(state, list(bus_states.values()), weights)
            return (candidate_start(req), -score)

        # pending me se best request
        req = min(pending, key=pick_key)
        pending.remove(req)

        station = req["station"]
        arrive = req["arrive"]
        free_at = charger_free_at[station]

        if arrive >= free_at:
            wait = 0
            start = arrive
        else:
            wait = free_at - arrive
            start = free_at

        finish = start + charge_time
        charger_free_at[station] = finish

        # wait_so_far update - ab score asli kaam karega
        bus_states[req["bus_id"]]["wait_so_far"] += wait

        results.append(
            {
                "bus_id": req["bus_id"],
                "operator": req["operator"],
                "station": station,
                "arrive": arrive,
                "wait": wait,
                "start": start,
                "finish": finish,
            }
        )

    return results


# ==========================================================
# group_by_station
# Kaam: results ko station ke hisaab se baant deta hai -
#       har station pe kaun-kaun buses, kis order me charge hui.
# Kyun: UI ka "per-station view" - har station ka order dikhane ke liye.
# ==========================================================
def group_by_station(results):
    by_station = {}  # {"A": [...], "B": [...], ...}

    for r in results:  # har charge record
        station = r["station"]
        if station not in by_station:  # is station ki list pehli baar?
            by_station[station] = []  # to khaali list bana do
        by_station[station].append(r)  # is charge ko us station me daalo

    # har station ke andar charge-start time se sort (order saaf rahe)
    for station in by_station:
        by_station[station].sort(key=lambda r: r["start"])

    return by_station


# ==========================================================
# group_by_bus
# Kaam: results ko bus ke hisaab se baant deta hai -
#       har bus ne kahan-kahan charge kiya, kis time, kitna wait.
# Kyun: UI ka "per-bus timetable" - har bus ka pura schedule dikhane ke liye.
# ==========================================================
def group_by_bus(results):
    by_bus = {}  # {"bus-BK-01": [...], ...}

    for r in results:  # har charge record
        bus_id = r["bus_id"]
        if bus_id not in by_bus:  # is bus ki list pehli baar?
            by_bus[bus_id] = []  # khaali list bana do
        by_bus[bus_id].append(r)  # is charge ko us bus me daalo

    # har bus ke andar charge order time se (raaste ke order me)
    for bus_id in by_bus:
        by_bus[bus_id].sort(key=lambda r: r["start"])

    return by_bus
