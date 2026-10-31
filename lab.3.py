import heapq
from collections import deque

graph = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F"], "D": [], "E": ["G"], "F": [], "G": []}


def bfs(start, goal):
    queue = deque([(start, [start])])
    seen = {start}
    order = []
    while queue:
        node, path = queue.popleft()
        order.append(node)
        print("Processed:", node, "| Path:", path)
        if node == goal:
            return path, order
        for n in graph[node]:
            if n not in seen:
                seen.add(n)
                queue.append((n, path + [n]))
        print("Queue:", [q[0] for q in queue])
    return None, order


def dfs(start, goal):
    stack = [(start, [start])]
    seen = set()
    order = []
    while stack:
        node, path = stack.pop()
        if node in seen:
            continue
        order.append(node)
        print("Processed:", node, "| Path:", path)
        if node == goal:
            return path, order
        seen.add(node)
        for n in reversed(graph[node]):
            stack.append((n, path + [n]))
        print("Stack:", [s[0] for s in stack])
    return None, order


def dls(g, node, goal, limit, path):
    if node == goal:
        return "FOUND", path
    children = [n for n in g[node] if n not in path]
    if limit == 0:
        if children:
            return "CUTOFF", None
        return "FAILURE", None
    cutoff = False
    for n in children:
        status, result = dls(g, n, goal, limit - 1, path + [n])
        if status == "FOUND":
            return status, result
        if status == "CUTOFF":
            cutoff = True
    if cutoff:
        return "CUTOFF", None
    return "FAILURE", None


def iddfs(g, start, goal, max_depth):
    tried = []
    for limit in range(max_depth + 1):
        tried.append(limit)
        status, path = dls(g, start, goal, limit, [start])
        if status == "FOUND":
            return status, path, tried
        if status == "FAILURE":
            return status, None, tried
    return "CUTOFF", None, tried


wgraph = {
    "A": {"B": 1, "C": 5},
    "B": {"D": 2, "E": 1},
    "C": {"F": 2, "G": 7},
    "D": {},
    "E": {"G": 1},
    "F": {},
    "G": {},
}


def ucs(g, start, goal):
    heap = [(0, start, [start])]
    done = set()
    order = []
    while heap:
        cost, node, path = heapq.heappop(heap)
        if node in done:
            continue
        done.add(node)
        order.append((node, cost))
        print("Processed:", node, "| Cost:", cost, "| Path:", path)
        if node == goal:
            return path, cost, order
        for n, w in g[node].items():
            if n not in done:
                heapq.heappush(heap, (cost + w, n, path + [n]))
    return None, None, order


def bfs_weighted(g, start, goal):
    queue = deque([(start, [start])])
    seen = {start}
    while queue:
        node, path = queue.popleft()
        if node == goal:
            return path
        for n in g[node]:
            if n not in seen:
                seen.add(n)
                queue.append((n, path + [n]))
    return None


def path_cost(g, path):
    total = 0
    for i in range(len(path) - 1):
        total += g[path[i]][path[i + 1]]
    return total


print("===== TASK 1: BFS =====")
bfs_path, bfs_order = bfs("A", "G")
print("BFS final path:", bfs_path)
print("BFS visit order:", bfs_order)

print()
print("===== TASK 1: DFS =====")
dfs_path, dfs_order = dfs("A", "G")
print("DFS final path:", dfs_path)
print("DFS visit order:", dfs_order)

print()
print("===== TASK 2: DLS =====")
for limit in [1, 2, 3, 4]:
    status, path = dls(graph, "A", "G", limit, ["A"])
    print("Limit", limit, "->", status, path)

print()
print("===== TASK 2: IDDFS =====")
for m in [1, 2, 3, 4]:
    status, path, tried = iddfs(graph, "A", "G", m)
    print("Max depth", m, "->", status, path, "| Limits tried:", tried)

print()
print("===== EDGE CASES =====")
print("Start = Goal (A to A):", dls(graph, "A", "A", 0, ["A"]))
print("Unreachable goal (G to A):", iddfs(graph, "G", "A", 4))
cycle_graph = {"A": ["B"], "B": ["C"], "C": ["A", "D"], "D": []}
print("Graph with cycle (A to D):", iddfs(cycle_graph, "A", "D", 5))

print()
print("===== TASK 3: UCS =====")
print("Edge weights:")
for u in wgraph:
    for v in wgraph[u]:
        print(" ", u, "->", v, "=", wgraph[u][v])
u_path, u_cost, u_order = ucs(wgraph, "A", "G")
print("UCS path:", u_path)
print("UCS processing order:", [x[0] for x in u_order])
print("UCS total cost:", u_cost)
print("UCS cost (checked separately):", path_cost(wgraph, u_path))
print("UCS hops:", len(u_path) - 1)

b_path = bfs_weighted(wgraph, "A", "G")
print()
print("BFS path on same graph:", b_path)
print("BFS hops:", len(b_path) - 1)
print("BFS total cost:", path_cost(wgraph, b_path))
