import streamlit as st  # ← ye sabse pehle (st isi se aata hai)
import pandas as pd
import sys
import os

# scenarios folder ka raasta jodo
sys.path.append(os.path.join(os.path.dirname(__file__), "scenarios"))
sys.path.append(os.path.join(os.path.dirname(__file__), "engine"))
import scheduler

import scenario_1
import scenario_2
import scenario_3
import scenario_4
import scenario_5


# saare scenarios ek dictionary me - naam -> uska data

SCENARIOS = {
    scenario_1.scenario["name"]: scenario_1.scenario,
    scenario_2.scenario["name"]: scenario_2.scenario,
    scenario_3.scenario["name"]: scenario_3.scenario,
    scenario_4.scenario["name"]: scenario_4.scenario,
    scenario_5.scenario["name"]: scenario_5.scenario,
}


# dropdown - user scenario chune
choice = st.selectbox("Scenario chuno:", list(SCENARIOS.keys()))

# chune hue scenario ka data
selected = SCENARIOS[choice]
st.info(selected["description"])

st.write("Tumne chuna:", choice)
st.write("Total buses:", len(selected["buses"]))

# ---- Scenario ka input data dikhao ----
st.header("Scenario Input")

# weights dikhao
st.write("Weights:", selected["weights"])

# buses ki list ko table me dikhao
st.subheader("Buses")
buses_table = pd.DataFrame(selected["buses"])  # list of dicts -> table
st.dataframe(buses_table)


# ---- Scheduler chalao ----
st.header("Schedule Result")

# scenario se zaroori cheezein nikalo
route = selected["route"]
physics = selected["physics"]
total_distance = sum(seg["distance_km"] for seg in route["segments"])

# station distances (endpoint hata ke - sirf charging stations)
dist = scheduler.station_distances(route)
# endpoints (Bengaluru/Kochi) hatao - sirf A,B,C,D charging stations chahiye
charging_stations = [s["id"] for s in selected["stations"]]
dist = {k: v for k, v in dist.items() if k in charging_stations}
# valid plans nikalo
valid_plans = scheduler.find_valid_plans(
    dist, total_distance, physics["battery_range_km"]
)


# saari requests banao + scheduler chalao
requests = scheduler.collect_all_requests(
    selected["buses"], valid_plans, dist, physics["speed_kmph"], total_distance
)


results = scheduler.run_scheduler(
    requests, charging_stations, physics["charge_time_min"], selected["weights"]
)

st.write("Total charges scheduled:", len(results))


# ---- Per-bus timetable ----
st.subheader("Per-Bus Timetable")

by_bus = scheduler.group_by_bus(results)

# har bus ka schedule ek table me
bus_rows = []
for bus_id in by_bus:
    for r in by_bus[bus_id]:
        bus_rows.append(
            {
                "Bus": r["bus_id"],
                "Operator": r["operator"],
                "Station": r["station"],
                "Pahunchi": scheduler.minutes_to_time(r["arrive"]),
                "Wait (min)": f"{r['wait'] // 60:02d}:{r['wait'] % 60:02d}",
                "Charge Start": scheduler.minutes_to_time(r["start"]),
                "Charge End": scheduler.minutes_to_time(r["finish"]),
            }
        )

st.dataframe(pd.DataFrame(bus_rows))


# ---- Per-station order ----
st.subheader("Per-Station Charging Order")

by_station = scheduler.group_by_station(results)

# har station alag dikhao
for station in by_station:
    st.write("Station", station)
    station_rows = []
    for r in by_station[station]:
        station_rows.append(
            {
                "Order Time": scheduler.minutes_to_time(r["start"]),
                "Bus": r["bus_id"],
                "Operator": r["operator"],
                "Wait (min)": f"{r['wait'] // 60:02d}:{r['wait'] % 60:02d}",
                "Charge": scheduler.minutes_to_time(r["start"])
                + " - "
                + scheduler.minutes_to_time(r["finish"]),
            }
        )
    st.dataframe(pd.DataFrame(station_rows))
