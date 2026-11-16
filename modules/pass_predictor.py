"""
pass_predictor.py
Predicts the chance of passing an exam using a Bayesian Network.

Network structure:

    Attendance     StudyHours
          \\          /
         Understanding      Assignments
                 \\             /
                       Pass

Each node is True/False. Inference is done by enumeration:
P(Pass | evidence) = sum over the unknown variables of the joint probability,
then normalised.
"""

from itertools import product

# Prior probabilities
P_ATTENDANCE = 0.7      # P(Attendance = good)
P_STUDY = 0.5           # P(StudyHours = high)
P_ASSIGN = 0.6          # P(Assignments = done)

# P(Understanding = good | Attendance, StudyHours)
P_UNDERSTAND = {
    (True, True): 0.95,
    (True, False): 0.60,
    (False, True): 0.70,
    (False, False): 0.15,
}

# P(Pass = True | Understanding, Assignments)
P_PASS = {
    (True, True): 0.97,
    (True, False): 0.85,
    (False, True): 0.55,
    (False, False): 0.20,
}

VARIABLES = ["attendance", "study", "understanding", "assignments", "passed"]


def prob(value, p_true):
    return p_true if value else 1 - p_true


def joint(a, s, u, asg, p):
    """Joint probability of one full assignment of all variables."""
    return (prob(a, P_ATTENDANCE)
            * prob(s, P_STUDY)
            * prob(u, P_UNDERSTAND[(a, s)])
            * prob(asg, P_ASSIGN)
            * prob(p, P_PASS[(u, asg)]))


def query(target, evidence):
    """Return P(target = True | evidence) by enumeration."""
    totals = {True: 0.0, False: 0.0}
    for values in product([True, False], repeat=len(VARIABLES)):
        world = dict(zip(VARIABLES, values))
        if any(world[k] != v for k, v in evidence.items()):
            continue
        totals[world[target]] += joint(*values)
    return totals[True] / (totals[True] + totals[False])


def ask_yes_no(question, take_input):
    from modules.speech import speak
    speak(question)
    ans = take_input()
    if ans.startswith("y"):
        return True
    if ans.startswith("n"):
        return False
    return None  # unknown, leave it out of the evidence


def predict_pass(take_input):
    evidence = {}
    a = ask_yes_no("Is your attendance above 75 percent? Say yes, no, or skip.", take_input)
    s = ask_yes_no("Do you study more than 2 hours a day? yes, no, or skip.", take_input)
    asg = ask_yes_no("Have you submitted all assignments? yes, no, or skip.", take_input)
    if a is not None:
        evidence["attendance"] = a
    if s is not None:
        evidence["study"] = s
    if asg is not None:
        evidence["assignments"] = asg

    p = query("passed", evidence) * 100
    u = query("understanding", evidence) * 100
    advice = "You are on track, keep going." if p >= 80 else \
        "Try to improve attendance and daily study time." if p >= 50 else \
        "Your risk is high. Start studying daily and finish the assignments."
    return (f"Based on the Bayesian network, chance of good understanding is {u:.0f} percent "
            f"and chance of passing is {p:.0f} percent. {advice}")


if __name__ == "__main__":
    print("P(Pass) with no evidence:", round(query("passed", {}), 3))
    print("P(Pass | poor attendance, low study):",
          round(query("passed", {"attendance": False, "study": False}), 3))
    print("P(Good attendance | passed):", round(query("attendance", {"passed": True}), 3))
