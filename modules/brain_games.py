"""
brain_games.py
Puzzle breaks for students.

- Towers of Hanoi : recursive solution, needs 2^n - 1 moves
- 8 Puzzle        : solved with A* search using Manhattan distance heuristic
"""

import heapq
import random
import re

# ---------------- Towers of Hanoi ----------------

def hanoi(n, source, target, helper, moves):
    if n == 0:
        return
    hanoi(n - 1, source, helper, target, moves)
    moves.append((n, source, target))
    hanoi(n - 1, helper, target, source, moves)


def play_hanoi(command):
    numbers = re.findall(r"\d+", command)
    n = int(numbers[0]) if numbers else 3
    n = max(1, min(n, 6))
    moves = []
    hanoi(n, "A", "C", "B", moves)
    for i, (disk, s, t) in enumerate(moves, 1):
        print(f"Move {i}: disk {disk} from {s} to {t}")
    return f"Towers of Hanoi with {n} disks solved in {len(moves)} moves, which is 2 to the power {n} minus 1."


# ---------------- 8 Puzzle ----------------

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)   # 0 is the blank


def manhattan(state):
    dist = 0
    for i, tile in enumerate(state):
        if tile:
            goal_i = tile - 1
            dist += abs(i // 3 - goal_i // 3) + abs(i % 3 - goal_i % 3)
    return dist


def neighbours(state):
    i = state.index(0)
    r, c = divmod(i, 3)
    result = []
    for dr, dc, name in [(-1, 0, "Up"), (1, 0, "Down"), (0, -1, "Left"), (0, 1, "Right")]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            j = nr * 3 + nc
            s = list(state)
            s[i], s[j] = s[j], s[i]
            result.append((tuple(s), name))
    return result


def scramble(steps=60):
    """Make a random puzzle by moving the blank from the goal, so it is always solvable."""
    state = GOAL
    for _ in range(steps):
        state = random.choice(neighbours(state))[0]
    return state


def solve_8_puzzle(start):
    open_list = [(manhattan(start), 0, start, [])]
    seen = {start: 0}
    explored = 0
    while open_list:
        f, g, state, moves = heapq.heappop(open_list)
        explored += 1
        if state == GOAL:
            return moves, explored
        for nxt, move in neighbours(state):
            if g + 1 < seen.get(nxt, float("inf")):
                seen[nxt] = g + 1
                heapq.heappush(open_list, (g + 1 + manhattan(nxt), g + 1, nxt, moves + [move]))
    return None, explored


def show(state):
    for r in range(3):
        print(" ".join(str(x) if x else "_" for x in state[r * 3:r * 3 + 3]))


def play_8_puzzle(command):
    start = scramble()
    print("Start state:")
    show(start)
    moves, explored = solve_8_puzzle(start)
    print("Goal state:")
    show(GOAL)
    print("Moves of the blank:", " ".join(moves) if moves else "already solved")
    return f"8 puzzle solved using A star in {len(moves)} moves after exploring {explored} states."


if __name__ == "__main__":
    print(play_hanoi("hanoi 3"))
    print(play_8_puzzle(""))
