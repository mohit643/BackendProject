scenario = {
    "name": "Scenario 4 — Operator-heavy",
    "description": "One operator (KPN) dominates the Bengaluru→Kochi fleet (8 of 10 buses). Tuning the operator weight up vs down should produce visibly different schedules.",
    "weights": {
        "individual": 1.0,
        "operator": 2.0,  # Heavily prioritize operator fairness
        "overall": 1.0,
    },
    "physics": {
        "battery_range_km": 240,
        "charge_time_min": 25,
        "speed_kmph": 60,
    },
    "stations": [
        {"id": "A", "chargers": 1},
        {"id": "B", "chargers": 1},
        {"id": "C", "chargers": 1},
        {"id": "D", "chargers": 1},
    ],
    "route": {
        "segments": [
            {"from": "Bengaluru", "to": "A", "distance_km": 100},
            {"from": "A", "to": "B", "distance_km": 120},
            {"from": "B", "to": "C", "distance_km": 100},
            {"from": "C", "to": "D", "distance_km": 120},
            {"from": "D", "to": "Kochi", "distance_km": 100},
        ]
    },
    "buses": [
        {"id": "bus-BK-01", "operator": "kpn", "direction": "BK", "departure": "19:00"},
        {"id": "bus-BK-02", "operator": "kpn", "direction": "BK", "departure": "19:15"},
        {"id": "bus-BK-03", "operator": "kpn", "direction": "BK", "departure": "19:30"},
        {"id": "bus-BK-04", "operator": "kpn", "direction": "BK", "departure": "19:45"},
        {"id": "bus-BK-05", "operator": "kpn", "direction": "BK", "departure": "20:00"},
        {"id": "bus-BK-06", "operator": "kpn", "direction": "BK", "departure": "20:15"},
        {"id": "bus-BK-07", "operator": "kpn", "direction": "BK", "departure": "20:30"},
        {"id": "bus-BK-08", "operator": "kpn", "direction": "BK", "departure": "20:45"},
        {
            "id": "bus-BK-09",
            "operator": "freshbus",
            "direction": "BK",
            "departure": "21:00",
        },
        {
            "id": "bus-BK-10",
            "operator": "flixbus",
            "direction": "BK",
            "departure": "21:15",
        },
        {
            "id": "bus-KB-01",
            "operator": "freshbus",
            "direction": "KB",
            "departure": "19:00",
        },
        {
            "id": "bus-KB-02",
            "operator": "flixbus",
            "direction": "KB",
            "departure": "19:15",
        },
        {"id": "bus-KB-03", "operator": "kpn", "direction": "KB", "departure": "19:30"},
        {
            "id": "bus-KB-04",
            "operator": "freshbus",
            "direction": "KB",
            "departure": "19:45",
        },
        {
            "id": "bus-KB-05",
            "operator": "flixbus",
            "direction": "KB",
            "departure": "20:00",
        },
        {"id": "bus-KB-06", "operator": "kpn", "direction": "KB", "departure": "20:15"},
        {
            "id": "bus-KB-07",
            "operator": "freshbus",
            "direction": "KB",
            "departure": "20:30",
        },
        {
            "id": "bus-KB-08",
            "operator": "flixbus",
            "direction": "KB",
            "departure": "20:45",
        },
        {"id": "bus-KB-09", "operator": "kpn", "direction": "KB", "departure": "21:00"},
        {
            "id": "bus-KB-10",
            "operator": "freshbus",
            "direction": "KB",
            "departure": "21:15",
        },
    ],
}

print(scenario["name"])
print("Total buses:", len(scenario["buses"]))
