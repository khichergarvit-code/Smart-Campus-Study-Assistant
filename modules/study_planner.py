"""
study_planner.py
Makes a weekly study timetable.

Problem: place every study hour of every subject into time slots
(6 days x 4 slots) so that the timetable is "good".

Cost of a timetable (lower is better):
- same subject in two back to back slots on the same day  -> +3
- a hard subject in the last slot of the day (tired)      -> +2
- same subject more than twice in one day                  -> +4 per extra
- days with too many or too few study hours (unbalanced)   -> +1 per hour of difference

Algorithms used:
- Hill Climbing       : keeps swapping slots only if cost goes down (can get stuck)
- Simulated Annealing : sometimes accepts a worse swap so it can escape local minima
"""

import math
import random

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
SLOTS = ["9-10 AM", "11-12 PM", "3-4 PM", "7-8 PM"]

# subject -> (hours needed per week, is it hard?)
SUBJECTS = {
    "Artificial Intelligence": (5, True),
    "DBMS": (4, True),
    "Computer Networks": (4, False),
    "Operating Systems": (4, True),
    "Maths": (3, False),
}


def make_random_timetable():
    items = []
    for subject, (hours, _) in SUBJECTS.items():
        items += [subject] * hours
    total_slots = len(DAYS) * len(SLOTS)
    items += ["Free"] * (total_slots - len(items))
    random.shuffle(items)
    return items


def cost(tt):
    total = 0
    n = len(SLOTS)
    target = sum(h for h, _ in SUBJECTS.values()) / len(DAYS)
    for d in range(len(DAYS)):
        day = tt[d * n:(d + 1) * n]
        for i in range(n - 1):
            if day[i] != "Free" and day[i] == day[i + 1]:
                total += 3
        if day[-1] != "Free" and SUBJECTS[day[-1]][1]:
            total += 2
        for subject in SUBJECTS:
            if day.count(subject) > 2:
                total += 4 * (day.count(subject) - 2)
        busy = sum(1 for s in day if s != "Free")
        total += abs(busy - target)
    return total


def random_swap(tt):
    new = tt[:]
    i, j = random.sample(range(len(new)), 2)
    new[i], new[j] = new[j], new[i]
    return new


def hill_climbing(max_steps=5000):
    current = make_random_timetable()
    current_cost = cost(current)
    for _ in range(max_steps):
        neighbour = random_swap(current)
        c = cost(neighbour)
        if c < current_cost:
            current, current_cost = neighbour, c
    return current, current_cost


def simulated_annealing(start_temp=10.0, cooling=0.995, min_temp=0.01):
    current = make_random_timetable()
    current_cost = cost(current)
    best, best_cost = current, current_cost
    temp = start_temp
    while temp > min_temp:
        neighbour = random_swap(current)
        c = cost(neighbour)
        delta = c - current_cost
        # always accept better, accept worse with probability e^(-delta/T)
        if delta < 0 or random.random() < math.exp(-delta / temp):
            current, current_cost = neighbour, c
            if c < best_cost:
                best, best_cost = neighbour, c
        temp *= cooling
    return best, best_cost


def format_timetable(tt):
    n = len(SLOTS)
    width = 24
    lines = ["Day  | " + " | ".join(s.ljust(width) for s in SLOTS)]
    lines.append("-" * len(lines[0]))
    for d, day in enumerate(DAYS):
        row = tt[d * n:(d + 1) * n]
        lines.append(f"{day}  | " + " | ".join(s.ljust(width) for s in row))
    return "\n".join(lines)


def make_plan(command):
    if "hill" in command:
        tt, c = hill_climbing()
        method = "Hill Climbing"
    else:
        tt, c = simulated_annealing()
        method = "Simulated Annealing"
    print(format_timetable(tt))
    return f"Here is your weekly study timetable made using {method}. Final cost is {c:.1f}, lower is better."


def compare():
    hc = [hill_climbing()[1] for _ in range(5)]
    sa = [simulated_annealing()[1] for _ in range(5)]
    return sum(hc) / 5, sum(sa) / 5


if __name__ == "__main__":
    print(make_plan("timetable"))
    hc, sa = compare()
    print(f"Average cost over 5 runs -> Hill Climbing: {hc:.2f}, Simulated Annealing: {sa:.2f}")
