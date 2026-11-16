"""
em_clustering.py
"Which type of student am I?" - the EM algorithm on a Gaussian Mixture Model.

Data: study hours per day and attendance percent of 60 students (generated with
a fixed random seed so the result is repeatable). Nobody told the algorithm
which student belongs to which group, the group is a HIDDEN variable.

EM (Expectation Maximisation) learns the hidden groups by repeating:
    E-step : for every student, compute the probability that the student
             belongs to each group, using the current group parameters
             (these are called responsibilities).
    M-step : re-estimate each group's weight, mean and variance, using the
             responsibilities as soft counts.
The log-likelihood of the data never decreases, so the loop stops when it
stops improving.

Each group is a Gaussian with independent hours and attendance
(diagonal covariance), written in plain Python (no numpy).
"""

import math
import random
import re

K = 3
VAR_FLOOR = 0.05          # keeps a group from collapsing onto one point
LABELS = ["Consistent achiever", "Average learner", "Needs support"]
ADVICE = {
    "Consistent achiever": "Great habits, keep it up and help your friends.",
    "Average learner": "You are doing okay. A little more daily study and attendance will lift you.",
    "Needs support": "Try to attend more classes and study a bit every day. Make a timetable with me.",
}


def make_students(seed=42):
    """Synthetic data: 20 students from each of 3 hidden groups."""
    rng = random.Random(seed)
    groups = [(5.0, 0.8, 90, 4), (3.0, 0.7, 75, 5), (1.0, 0.5, 55, 6)]
    data = []
    for mh, sh, ma, sa in groups:
        for _ in range(20):
            hours = max(0.0, rng.gauss(mh, sh))
            attend = min(100.0, max(0.0, rng.gauss(ma, sa)))
            data.append((round(hours, 2), round(attend, 1)))
    rng.shuffle(data)
    return data


def gauss(x, mean, var):
    return math.exp(-((x - mean) ** 2) / (2 * var)) / math.sqrt(2 * math.pi * var)


def density(point, mean, var):
    return gauss(point[0], mean[0], var[0]) * gauss(point[1], mean[1], var[1])


def e_step(data, weights, means, variances):
    """Return responsibilities and the log-likelihood of the data."""
    resp, loglik = [], 0.0
    for p in data:
        parts = [weights[j] * density(p, means[j], variances[j]) for j in range(K)]
        total = sum(parts)
        resp.append([x / total for x in parts])
        loglik += math.log(total)
    return resp, loglik


def m_step(data, resp):
    n = len(data)
    weights, means, variances = [], [], []
    for j in range(K):
        nj = sum(r[j] for r in resp)
        mean = tuple(sum(r[j] * p[d] for r, p in zip(resp, data)) / nj for d in range(2))
        var = tuple(max(VAR_FLOOR, sum(r[j] * (p[d] - mean[d]) ** 2 for r, p in zip(resp, data)) / nj)
                    for d in range(2))
        weights.append(nj / n)
        means.append(mean)
        variances.append(var)
    return weights, means, variances


def fit(data, max_iter=60, tol=1e-4, seed=0):
    rng = random.Random(seed)
    # start the means far apart: one random point, then the points farthest from the chosen ones
    means = [data[rng.randrange(len(data))]]
    while len(means) < K:
        means.append(max(data, key=lambda p: min((p[0] - m[0]) ** 2 + (p[1] - m[1]) ** 2 for m in means)))
    overall = tuple(sum((p[d] - sum(q[d] for q in data) / len(data)) ** 2 for p in data) / len(data)
                    for d in range(2))
    weights = [1 / K] * K
    variances = [overall] * K

    history, prev = [], -float("inf")
    for _ in range(max_iter):
        resp, loglik = e_step(data, weights, means, variances)       # E-step
        history.append(loglik)
        weights, means, variances = m_step(data, resp)               # M-step
        if abs(loglik - prev) < tol:
            break
        prev = loglik
    return weights, means, variances, history


def name_groups(means):
    """Rank groups: more study hours and attendance means a better group."""
    score = [m[0] / 5 + m[1] / 100 for m in means]
    order = sorted(range(K), key=lambda j: -score[j])
    return {j: LABELS[rank] for rank, j in enumerate(order)}


def first_number(text):
    match = re.search(r"\d+(\.\d+)?", text)
    return float(match.group()) if match else None


def find_my_group(take_input):
    from modules.speech import speak

    data = make_students()
    weights, means, variances, history = fit(data)
    names = name_groups(means)

    lines = [f"EM on {len(data)} students, {K} hidden groups",
             "Iter | Log-likelihood (must keep increasing)"]
    shown = list(range(min(5, len(history)))) + ([len(history) - 1] if len(history) > 5 else [])
    for i in shown:
        lines.append(f"{i + 1:4} | {history[i]:10.2f}")
    if len(history) > 6:
        lines.insert(len(lines) - 1, " ...")
    lines.append(f"Converged after {len(history)} iterations.")
    lines.append("")
    lines.append("Group                | Share | Avg study hrs | Avg attendance")
    for j in sorted(range(K), key=lambda j: LABELS.index(names[j])):
        lines.append(f"{names[j]:20} | {weights[j] * 100:4.0f}% | {means[j][0]:13.1f} | {means[j][1]:13.0f}%")
    print("\n".join(lines))

    speak("Now tell me about yourself. How many hours do you study per day?")
    hours = first_number(take_input())
    speak("What is your attendance percent?")
    attend = first_number(take_input())
    if hours is None or attend is None:
        return "I need two numbers, for example 3 hours and 80 percent. Say 'which group am I' to try again."
    attend = min(attend, 100.0)

    parts = [weights[j] * density((hours, attend), means[j], variances[j]) for j in range(K)]
    total = sum(parts)
    post = [x / total for x in parts]
    best = max(range(K), key=lambda j: post[j])
    print("Your group probabilities (E-step on your numbers):\n" +
          "\n".join(f"  {names[j]:20} {post[j] * 100:5.1f}%"
                    for j in sorted(range(K), key=lambda j: LABELS.index(names[j]))))
    article = "an" if names[best][0] in "AEIOU" else "a"
    return (f"With {hours:g} hours of study and {attend:g} percent attendance, you are most likely "
            f"{article} {names[best]} ({post[best] * 100:.0f} percent sure). {ADVICE[names[best]]}")


if __name__ == "__main__":
    answers = iter(["3.5", "80"])
    print(find_my_group(lambda: next(answers)))
