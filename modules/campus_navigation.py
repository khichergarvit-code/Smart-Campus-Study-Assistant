"""
campus_navigation.py
Finds a route between two places on the college campus.

Algorithms used:
- BFS  : route with the fewest stops
- DFS  : any route (not always the shortest)
- IDS  : Iterative Deepening Search, fewest stops with low memory
- A*   : shortest route by distance, using straight line distance as heuristic
"""

import heapq
import math
from collections import deque

# (x, y) position of each place on the campus map, in metres
LOCATIONS = {
    "main gate": (0, 0),
    "parking": (60, -40),
    "admin block": (100, 30),
    "library": (200, 60),
    "cse block": (260, 140),
    "cafeteria": (180, 160),
    "auditorium": (90, 150),
    "medical center": (30, 120),
    "sports ground": (320, 20),
    "hostel": (360, 200),
}

# Walking paths between places: (place1, place2) -> distance in metres
PATHS = [
    ("main gate", "parking", 75),
    ("main gate", "admin block", 110),
    ("main gate", "medical center", 125),
    ("parking", "admin block", 81),
    ("admin block", "library", 105),
    ("admin block", "auditorium", 121),
    ("medical center", "auditorium", 68),
    ("auditorium", "cafeteria", 91),
    ("library", "cafeteria", 103),
    ("library", "cse block", 100),
    ("library", "sports ground", 127),
    ("cafeteria", "cse block", 85),
    ("cse block", "hostel", 120),
    ("sports ground", "hostel", 185),
]


def build_graph():
    graph = {place: {} for place in LOCATIONS}
    for a, b, dist in PATHS:
        graph[a][b] = dist
        graph[b][a] = dist
    return graph


GRAPH = build_graph()


def heuristic(a, b):
    """Straight line (Euclidean) distance between two places."""
    (x1, y1), (x2, y2) = LOCATIONS[a], LOCATIONS[b]
    return math.hypot(x1 - x2, y1 - y2)


def path_cost(path):
    return sum(GRAPH[path[i]][path[i + 1]] for i in range(len(path) - 1))


def bfs(start, goal):
    queue = deque([[start]])
    visited = {start}
    explored = 0
    while queue:
        path = queue.popleft()
        node = path[-1]
        explored += 1
        if node == goal:
            return path, explored
        for nxt in GRAPH[node]:
            if nxt not in visited:
                visited.add(nxt)
                queue.append(path + [nxt])
    return None, explored


def dfs(start, goal):
    stack = [[start]]
    visited = set()
    explored = 0
    while stack:
        path = stack.pop()
        node = path[-1]
        if node in visited:
            continue
        visited.add(node)
        explored += 1
        if node == goal:
            return path, explored
        for nxt in GRAPH[node]:
            if nxt not in visited:
                stack.append(path + [nxt])
    return None, explored


def depth_limited(node, goal, limit, path, counter):
    counter[0] += 1
    if node == goal:
        return path
    if limit == 0:
        return None
    for nxt in GRAPH[node]:
        if nxt not in path:
            result = depth_limited(nxt, goal, limit - 1, path + [nxt], counter)
            if result:
                return result
    return None


def ids(start, goal):
    counter = [0]
    for depth in range(len(GRAPH)):
        result = depth_limited(start, goal, depth, [start], counter)
        if result:
            return result, counter[0]
    return None, counter[0]


def a_star(start, goal):
    open_list = [(heuristic(start, goal), 0, start, [start])]
    best_g = {start: 0}
    explored = 0
    while open_list:
        f, g, node, path = heapq.heappop(open_list)
        explored += 1
        if node == goal:
            return path, explored
        for nxt, dist in GRAPH[node].items():
            new_g = g + dist
            if new_g < best_g.get(nxt, float("inf")):
                best_g[nxt] = new_g
                heapq.heappush(open_list, (new_g + heuristic(nxt, goal), new_g, nxt, path + [nxt]))
    return None, explored


ALGORITHMS = {"bfs": bfs, "dfs": dfs, "ids": ids, "a*": a_star}


def find_places(text):
    """Return place names in the order they appear in the sentence."""
    found = []
    for place in LOCATIONS:
        pos = text.find(place)
        if pos != -1:
            found.append((pos, place))
    found.sort()
    return [place for _, place in found]


def navigate(command):
    places = find_places(command)
    if len(places) < 2:
        return ("Please tell me two places. Example: route from main gate to hostel. "
                "Places I know: " + ", ".join(LOCATIONS))

    start, goal = places[0], places[1]

    algo = "a*"
    for name in ("bfs", "dfs", "ids"):
        if name in command.split():
            algo = name

    path, explored = ALGORITHMS[algo](start, goal)
    if not path:
        return f"No route found from {start} to {goal}."

    route = " -> ".join(p.title() for p in path)
    return (f"Using {algo.upper()}: {route}. "
            f"Distance {path_cost(path)} metres, {len(path) - 1} stops, {explored} nodes explored.")


def compare_all(start, goal):
    """Run all four algorithms on the same route, used for the comparison table."""
    rows = []
    for name, func in ALGORITHMS.items():
        path, explored = func(start, goal)
        rows.append((name.upper(), " -> ".join(path), path_cost(path), explored))
    return rows


if __name__ == "__main__":
    for row in compare_all("main gate", "hostel"):
        print(row)
