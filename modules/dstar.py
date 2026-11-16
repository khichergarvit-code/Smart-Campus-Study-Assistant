"""
dstar.py
Live route re-planning on the campus map using D* Lite.

Idea: a student starts walking along the planned route, but some place on the
campus is blocked (construction, event, locked gate). The student only finds out
when standing next to it. A normal search (A*) would have to start again from
scratch. D* Lite keeps its old results and only repairs the part of the plan
that the blockage affected, so replanning is cheaper.

How D* Lite works (it searches backwards, from the goal to the student):
- g(s)   : the best known cost from s to the goal
- rhs(s) : one-step look ahead value = min over neighbours of cost(s, n) + g(n)
- A place is "inconsistent" when g(s) != rhs(s). Those places wait in a priority
  queue ordered by key = (min(g, rhs) + h(start, s) + km, min(g, rhs)).
- km grows when the student moves, so old keys stay correct without re-sorting.
"""

import heapq
import re

from modules.campus_navigation import GRAPH, find_places, heuristic, path_cost, a_star

INF = float("inf")


class DStarLite:
    def __init__(self, start, goal):
        self.start, self.goal = start, goal
        self.blocked = set()
        self.g = {p: INF for p in GRAPH}
        self.rhs = {p: INF for p in GRAPH}
        self.rhs[goal] = 0
        self.km = 0
        self.last = start
        self.heap = []
        self.entry = {}          # place -> key it currently has in the queue
        self.expanded = 0        # how many places were processed (work done)
        self._push(goal)

    def cost(self, a, b):
        if a in self.blocked or b in self.blocked:
            return INF
        return GRAPH[a].get(b, INF)

    def key(self, s):
        m = min(self.g[s], self.rhs[s])
        return (m + heuristic(self.start, s) + self.km, m)

    def _push(self, s):
        k = self.key(s)
        self.entry[s] = k
        heapq.heappush(self.heap, (k, s))

    def _top_key(self):
        while self.heap:
            k, s = self.heap[0]
            if self.entry.get(s) == k:
                return k
            heapq.heappop(self.heap)      # stale entry
        return (INF, INF)

    def update_vertex(self, u):
        if u != self.goal:
            self.rhs[u] = min((self.cost(u, s) + self.g[s] for s in GRAPH[u]), default=INF)
        self.entry.pop(u, None)
        if self.g[u] != self.rhs[u]:
            self._push(u)

    def compute(self):
        """Repair g-values until the route from the current position is optimal."""
        while self._top_key() < self.key(self.start) or self.rhs[self.start] != self.g[self.start]:
            k_old = self._top_key()
            if k_old == (INF, INF):
                break
            _, u = heapq.heappop(self.heap)
            self.entry.pop(u, None)
            k_new = self.key(u)
            if k_old < k_new:                       # key is out of date, re-insert
                self.entry[u] = k_new
                heapq.heappush(self.heap, (k_new, u))
            elif self.g[u] > self.rhs[u]:           # cost went down -> settle it
                self.g[u] = self.rhs[u]
                self.expanded += 1
                for p in GRAPH[u]:
                    self.update_vertex(p)
            else:                                   # cost went up -> reset and re-check
                self.g[u] = INF
                self.expanded += 1
                for p in list(GRAPH[u]) + [u]:
                    self.update_vertex(p)

    def block(self, places):
        """The student discovered that these places are blocked."""
        self.km += heuristic(self.last, self.start)
        self.last = self.start
        self.blocked.update(places)
        for n in places:
            for p in GRAPH[n]:
                self.update_vertex(p)
            self.update_vertex(n)

    def next_step(self, s):
        best, best_val = None, INF
        for n in GRAPH[s]:
            val = self.cost(s, n) + self.g[n]
            if val < best_val:
                best, best_val = n, val
        return best

    def path_from(self, s):
        path = [s]
        while path[-1] != self.goal and len(path) <= len(GRAPH):
            nxt = self.next_step(path[-1])
            if nxt is None:
                return None
            path.append(nxt)
        return path if path[-1] == self.goal else None


def astar_with_blocks(start, goal, blocked):
    """Plain A* on the map without the blocked places (used for comparison)."""
    open_list = [(heuristic(start, goal), 0, start)]
    best = {start: 0}
    expanded = 0
    while open_list:
        _, g, node = heapq.heappop(open_list)
        if g > best.get(node, INF):
            continue
        expanded += 1
        if node == goal:
            return g, expanded
        for nxt, dist in GRAPH[node].items():
            if nxt in blocked:
                continue
            if g + dist < best.get(nxt, INF):
                best[nxt] = g + dist
                heapq.heappush(open_list, (g + dist + heuristic(nxt, goal), g + dist, nxt))
    return INF, expanded


def _show(path):
    return " -> ".join(p.title() for p in path)


def _is_blocked_phrase(text, place):
    before = r"(blocked|closed|block|avoid|without|except)\s+(the\s+)?" + re.escape(place)
    after = re.escape(place) + r"\s+(is\s+|are\s+|gets\s+)?(blocked|closed)"
    return bool(re.search(before, text) or re.search(after, text))


def replan(command):
    places = find_places(command)
    blocked = [p for p in places if _is_blocked_phrase(command, p)]
    route_places = [p for p in places if p not in blocked]
    if len(route_places) < 2:
        return ("Tell me the trip and what is blocked. Example: reroute from main gate to hostel "
                "if library is blocked")
    start, goal = route_places[0], route_places[1]

    out = []
    if not blocked:
        base, _ = a_star(start, goal)
        middle = base[1:-1]
        if not middle:
            return (f"{start.title()} and {goal.title()} are directly connected, so there is "
                    "nothing in between to block. Try a longer trip.")
        blocked = [middle[len(middle) // 2]]
        out.append(f"(You did not say what is blocked, so for this demo I will block "
                   f"{blocked[0].title()}, a stop on the normal route.)")

    planner = DStarLite(start, goal)
    planner.compute()
    initial = planner.path_from(start)
    if not initial:
        return f"No route found from {start.title()} to {goal.title()}."

    out.append(f"D* Lite: {start.title()} -> {goal.title()}, hidden blockage: "
               f"{', '.join(b.title() for b in blocked)}")
    out.append(f"Initial plan : {_show(initial)} ({path_cost(initial)} m, "
               f"{planner.expanded} places processed)")

    pos, walked = start, [start]
    hidden, known = set(blocked), set()
    dstar_work, scratch_work, replans = 0, 0, 0

    while pos != goal:
        found = [n for n in GRAPH[pos] if n in hidden and n not in known]
        if found:
            known.update(found)
            planner.start = pos
            old_plan = planner.path_from(pos)
            before = planner.expanded
            planner.block(found)
            planner.compute()
            used = planner.expanded - before
            names = ", ".join(f.title() for f in found)
            new_path = planner.path_from(pos)
            if not new_path:
                out.append(f"At {pos.title()}: {names} is blocked! No other route exists from here.")
                print("\n".join(out))
                return (f"Sorry, with {names} blocked there is no way to reach {goal.title()} "
                        f"from {pos.title()}.")
            if new_path == old_plan:
                out.append(f"At {pos.title()}: {names} is blocked, but it is not on the planned "
                           "route, so the plan stays the same.")
            else:
                _, scratch = astar_with_blocks(pos, goal, known)
                dstar_work += used
                scratch_work += scratch
                replans += 1
                out.append(f"At {pos.title()}: {names} is blocked! Replanning...")
                out.append(f"New plan     : {_show(new_path)} (D* Lite repaired it by processing "
                           f"{used} places; A* from scratch would process {scratch})")
        nxt = planner.next_step(pos)
        pos = nxt
        planner.start = pos
        walked.append(pos)

    out.append(f"Route walked : {_show(walked)} ({path_cost(walked)} m)")
    print("\n".join(out))
    if replans == 0:
        return ("The blocked place was never in the way, so the original plan worked "
                f"with no replanning. Distance {path_cost(walked)} metres.")
    return (f"Reached {goal.title()} after {replans} replan(s). Distance {path_cost(walked)} metres. "
            f"D* Lite processed {dstar_work} places in total to repair the plan, while "
            f"restarting A* each time would process {scratch_work}.")


if __name__ == "__main__":
    print(replan("reroute from main gate to hostel if library is blocked"))
