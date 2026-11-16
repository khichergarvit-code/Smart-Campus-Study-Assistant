"""
focus_tracker.py
Guesses whether the student was Focused or Distracted during a study session
using a Hidden Markov Model.

Hidden states  : Focused, Distracted (we cannot see these directly)
Observations   : what the student reports doing every 15 minutes
                 -> reading, notes, phone, break

Algorithms:
- Forward algorithm : probability of the whole observation sequence
- Viterbi algorithm : most likely sequence of hidden states
"""

STATES = ["Focused", "Distracted"]
OBSERVATIONS = ["reading", "notes", "phone", "break"]

START = {"Focused": 0.6, "Distracted": 0.4}

TRANSITION = {
    "Focused": {"Focused": 0.7, "Distracted": 0.3},
    "Distracted": {"Focused": 0.4, "Distracted": 0.6},
}

EMISSION = {
    "Focused": {"reading": 0.45, "notes": 0.40, "phone": 0.05, "break": 0.10},
    "Distracted": {"reading": 0.10, "notes": 0.05, "phone": 0.60, "break": 0.25},
}


def forward(obs):
    alpha = [{s: START[s] * EMISSION[s][obs[0]] for s in STATES}]
    for t in range(1, len(obs)):
        alpha.append({
            s: sum(alpha[t - 1][p] * TRANSITION[p][s] for p in STATES) * EMISSION[s][obs[t]]
            for s in STATES
        })
    return sum(alpha[-1].values())


def viterbi(obs):
    v = [{s: START[s] * EMISSION[s][obs[0]] for s in STATES}]
    back = [{}]
    for t in range(1, len(obs)):
        v.append({})
        back.append({})
        for s in STATES:
            best_prev = max(STATES, key=lambda p: v[t - 1][p] * TRANSITION[p][s])
            v[t][s] = v[t - 1][best_prev] * TRANSITION[best_prev][s] * EMISSION[s][obs[t]]
            back[t][s] = best_prev
    last = max(STATES, key=lambda s: v[-1][s])
    path = [last]
    for t in range(len(obs) - 1, 0, -1):
        path.insert(0, back[t][path[0]])
    return path


def track_focus(take_input):
    from modules.speech import speak
    speak("Tell me what you did in each 15 minute block, separated by spaces. "
          "Use the words reading, notes, phone or break.")
    words = take_input().split()
    obs = [w for w in words if w in OBSERVATIONS]
    if not obs:
        return "I did not get any valid activities. Example: reading notes phone phone reading"

    states = viterbi(obs)
    focused = states.count("Focused")
    percent = 100 * focused / len(states)
    print("Block | Activity | Hidden state")
    for i, (o, s) in enumerate(zip(obs, states), 1):
        print(f"{i:5} | {o:8} | {s}")
    print(f"Probability of this sequence (forward algorithm): {forward(obs):.6f}")
    return f"You were focused for about {percent:.0f} percent of your session."


if __name__ == "__main__":
    sample = ["reading", "notes", "phone", "phone", "break", "reading"]
    print(viterbi(sample))
    print(forward(sample))
