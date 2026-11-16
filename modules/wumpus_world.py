"""
wumpus_world.py
"Campus Escape" - the Wumpus World problem solved by a logical agent.

The world is a 4x4 grid. Somewhere inside are:
    - pits      (Breeze is felt in the cells next to a pit)
    - a Wumpus  (Stench is smelt in the cells next to it)
    - gold      (Glitter is seen in the same cell)
The agent starts at (1,1), cannot see the map, and only receives percepts.
It must find the gold and climb back out to (1,1).

How the agent thinks (knowledge based agent, inference by model checking):
- Its knowledge base holds every percept it has received so far.
- To decide if a cell is safe, it enumerates all possible pit layouts (and all
  possible Wumpus positions) that agree with the knowledge base. A cell is
  provably safe only if it has no pit and no Wumpus in EVERY such model.
- If no cell is provably safe, it may shoot the Wumpus once its position is
  known, otherwise it takes the least risky guess (using the model weights,
  with each cell having a 20 percent prior chance of a pit).

Score: -1 per move, -10 for the arrow, +1000 for leaving with the gold,
       -1000 for dying.
"""

import itertools
import random
from collections import deque

SIZE = 4
PIT_P = 0.2
START = (1, 1)
CELLS = [(x, y) for y in range(1, SIZE + 1) for x in range(1, SIZE + 1)]


def neighbours(c):
    x, y = c
    return [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
            if 1 <= x + dx <= SIZE and 1 <= y + dy <= SIZE]


def fmt(c):
    return f"({c[0]},{c[1]})"


# ---------------------------------------------------------------- the world
def reachable(goal, pits):
    seen, queue = {START}, deque([START])
    while queue:
        cur = queue.popleft()
        if cur == goal:
            return True
        for n in neighbours(cur):
            if n not in seen and n not in pits:
                seen.add(n)
                queue.append(n)
    return False


def make_world(rng):
    """Random world. The start and its neighbours are always safe."""
    safe_zone = {START, *neighbours(START)}
    while True:
        pits = {c for c in CELLS if c not in safe_zone and rng.random() < PIT_P}
        free = [c for c in CELLS if c not in safe_zone and c not in pits]
        if not 1 <= len(pits) <= 4 or len(free) < 2:
            continue
        wumpus = rng.choice(free)
        gold = rng.choice([c for c in free if c != wumpus])
        if reachable(gold, pits):
            return pits, wumpus, gold


def percepts(cell, pits, wumpus, wumpus_alive):
    breeze = any(n in pits for n in neighbours(cell))
    stench = wumpus_alive and wumpus in neighbours(cell)
    return breeze, stench


# ------------------------------------------------------------ the agent's KB
class KnowledgeBase:
    def __init__(self):
        self.visited = set()
        self.breeze = {}
        self.stench = {}
        self.wumpus_alive = True

    def tell(self, cell, breeze, stench):
        self.visited.add(cell)
        self.breeze[cell] = breeze
        self.stench[cell] = stench

    def ask(self):
        """
        Model checking. Returns:
            safe      : unvisited cells that are provably safe
            pit_prob  : probability of a pit for each frontier cell
            wumpus_at : list of cells where the Wumpus could still be
        """
        unknown = [c for c in CELLS if c not in self.visited]
        frontier = [c for c in unknown if any(n in self.visited for n in neighbours(c))]

        total = 0.0
        pit_weight = {c: 0.0 for c in frontier}
        for bits in itertools.product([False, True], repeat=len(frontier)):
            pits = {c for c, b in zip(frontier, bits) if b}
            if all(any(n in pits for n in neighbours(v)) == self.breeze[v] for v in self.visited):
                w = (PIT_P ** len(pits)) * ((1 - PIT_P) ** (len(frontier) - len(pits)))
                total += w
                for c in pits:
                    pit_weight[c] += w
        pit_prob = {c: pit_weight[c] / total for c in frontier}

        if self.wumpus_alive:
            wumpus_at = [c for c in unknown
                         if all((c in neighbours(v)) == self.stench[v] for v in self.visited)]
        else:
            wumpus_at = []

        safe = {c for c in frontier if pit_prob[c] == 0 and c not in wumpus_at}
        return safe, pit_prob, wumpus_at


def find_path(start, targets, visited):
    """Shortest path that walks only through visited cells and ends in a target."""
    if start in targets:
        return [start]
    queue, seen = deque([[start]]), {start}
    while queue:
        path = queue.popleft()
        for n in neighbours(path[-1]):
            if n in seen:
                continue
            if n in targets:
                return path + [n]
            if n in visited:
                seen.add(n)
                queue.append(path + [n])
    return None


# --------------------------------------------------------------------- game
def draw_map(pits, wumpus, gold, visited, wumpus_alive):
    lines = []
    for y in range(SIZE, 0, -1):
        row = []
        for x in range(1, SIZE + 1):
            c = (x, y)
            sym = "P" if c in pits else "W" if c == wumpus else "G" if c == gold else \
                  "A" if c == START else "."
            if c == wumpus and not wumpus_alive:
                sym = "w"
            row.append(sym + ("*" if c in visited else " "))
        lines.append(" ".join(row))
    return "\n".join(lines)


def play_wumpus(command=""):
    rng = random.Random()
    pits, wumpus, gold = make_world(rng)
    kb = KnowledgeBase()
    pos, score, arrow, has_gold = START, 0, True, False
    log = ["Wumpus World (4x4). Agent starts at (1,1) and cannot see the map."]
    outcome = None

    for step in range(1, 61):
        if pos not in kb.visited:
            breeze, stench = percepts(pos, pits, wumpus, kb.wumpus_alive)
            kb.tell(pos, breeze, stench)
            felt = [n for n, f in (("Breeze", breeze), ("Stench", stench), ("Glitter", pos == gold)) if f]
            log.append(f"Step {step}: at {fmt(pos)} - percepts: {', '.join(felt) or 'none'}")

        if pos == gold and not has_gold:
            has_gold = True
            log.append("  Grabbed the gold! Now heading back to (1,1).")

        if has_gold:
            path = find_path(pos, {START}, kb.visited)
            score += -(len(path) - 1) + 1000
            pos = START
            log.append("  Climbed out of the cave with the gold.")
            outcome = "win"
            break

        safe, pit_prob, wumpus_at = kb.ask()
        path = find_path(pos, safe, kb.visited) if safe else None
        if path:
            log.append(f"  Logic: provably safe cells -> {', '.join(fmt(c) for c in sorted(safe))}")
            log.append(f"  Move: {' -> '.join(fmt(c) for c in path)}")
            score -= len(path) - 1
            pos = path[-1]
            continue

        if arrow and kb.wumpus_alive and len(wumpus_at) == 1:
            w = wumpus_at[0]
            spots = {v for v in kb.visited if v[0] == w[0] or v[1] == w[1]}
            path = find_path(pos, spots, kb.visited) if spots else None
            if path:
                log.append(f"  Logic: the Wumpus must be at {fmt(w)}. Going to {fmt(path[-1])} to shoot it.")
                score -= len(path) - 1
                pos = path[-1]
                arrow = False
                score -= 10
                if wumpus == w:
                    kb.wumpus_alive = False
                    log.append("  Shot the arrow... Scream! The Wumpus is dead, its cell is now safe.")
                else:
                    log.append("  Shot the arrow... it missed.")
                continue

        frontier = list(pit_prob)
        best = None
        for c in frontier:
            p_wumpus = 1 / len(wumpus_at) if c in wumpus_at else 0
            risk = 1 - (1 - pit_prob[c]) * (1 - p_wumpus)
            path = find_path(pos, {c}, kb.visited)
            if path and (best is None or risk < best[0]):
                best = (risk, c, path)
        if best is None:
            log.append("  No cell left to explore. The agent gives up.")
            outcome = "stuck"
            break
        risk, c, path = best
        log.append(f"  Logic: no cell is provably safe. Least risky guess: {fmt(c)} ({risk:.0%} danger).")
        score -= len(path) - 1
        pos = c
        if c in pits or (c == wumpus and kb.wumpus_alive):
            score -= 1000
            log.append(f"  Moved to {fmt(c)} and fell into a pit!" if c in pits
                       else f"  Moved to {fmt(c)} and was eaten by the Wumpus!")
            outcome = "dead"
            break
        log.append(f"  Moved to {fmt(c)} - the guess paid off.")
    else:
        outcome = "stuck"

    log.append("")
    log.append("Final map  (A=start, P=pit, W=Wumpus, w=dead Wumpus, G=gold, *=visited by agent)")
    log.append(draw_map(pits, wumpus, gold, kb.visited, kb.wumpus_alive))
    print("\n".join(log))

    cells = len(kb.visited)
    if outcome == "win":
        return f"The agent found the gold and escaped! It explored {cells} cells. Score: {score}."
    if outcome == "dead":
        return f"The agent died after exploring {cells} cells. Score: {score}. Try again for a new world."
    return f"The agent could not find a way to the gold. Score: {score}. Try again for a new world."


if __name__ == "__main__":
    print(play_wumpus())
