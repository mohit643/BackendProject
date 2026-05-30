def individual_score(bus):
    return bus["wait_so_far"]


def operator_score(bus, all_buses):
    same_operator_buses = []
    for b in all_buses:
        if b["operator"] == bus["operator"]:
            same_operator_buses.append(b["wait_so_far"])
    return sum(same_operator_buses)


def overall_score(all_buses):
    total = 0
    for b in all_buses:
        total = total + b["wait_so_far"]
    return total
