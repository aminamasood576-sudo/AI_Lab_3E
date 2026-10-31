import heapq

graph = {
    "S": [("A", 1), ("B", 4)],
    "A": [("C", 2)],
    "B": [("G", 5)],
    "C": [("G", 3)],
    "G": []
}

h = {"S": 5, "A": 4, "B": 4, "C": 2, "G": 0}
h_zero = {"S": 0, "A": 0, "B": 0, "C": 0, "G": 0}
h_over = {"S": 5, "A": 4, "B": 4, "C": 10, "G": 0}
true_cost = {"S": 6, "A": 5, "B": 5, "C": 3, "G": 0}


def astar(graph, h, start, goal):
    pq = [(h[start], 0, start, [start])]
    best = {start: 0}
    expanded = []
    while len(pq) > 0:
        f, g, node, path = heapq.heappop(pq)
        if g > best[node]:
            continue
        print("Processed:", node, "| g =", g, "| h =", h[node], "| f =", f)
        if node == goal:
            return g, path, expanded
        expanded.append(node)
        for nxt, w in graph[node]:
            new_g = g + w
            if nxt not in best or new_g < best[nxt]:
                best[nxt] = new_g
                heapq.heappush(pq, (new_g + h[nxt], new_g, nxt, path + [nxt]))
        frontier = []
        for item in sorted(pq):
            frontier.append((item[2], item[1], item[0]))
        print("Frontier (node, g, f):", frontier)
    return None, None, expanded


def path_cost(graph, path):
    total = 0
    for i in range(len(path) - 1):
        for nxt, w in graph[path[i]]:
            if nxt == path[i + 1]:
                total = total + w
    return total


print("===== TASK 1: g, h, f VALUES AND HEURISTIC CHECK =====")
for n in h:
    print("Node", n, "| h =", h[n], "| true cost =", true_cost[n], "| admissible:", h[n] <= true_cost[n])
for u in graph:
    for v, w in graph[u]:
        print("Edge", u, "->", v, "| h(u) =", h[u], "<= cost + h(v) =", w + h[v], "|", h[u] <= w + h[v])
print()
astar(graph, h, "S", "G")

print()
print("===== TASK 2: A* =====")
cost, path, exp = astar(graph, h, "S", "G")
print("A* path:", path)
print("A* cost:", cost)
print("A* cost (checked separately):", path_cost(graph, path))
print("A* expanded nodes:", exp)
print("A* expansion count:", len(exp))

print()
print("===== TASK 2: UCS (all h = 0) =====")
ucost, upath, uexp = astar(graph, h_zero, "S", "G")
print("UCS path:", upath)
print("UCS cost:", ucost)
print("UCS cost (checked separately):", path_cost(graph, upath))
print("UCS expanded nodes:", uexp)
print("UCS expansion count:", len(uexp))

print()
print("===== TASK 3: OVERESTIMATE h(C) = 10 =====")
print("Original h(C) = 2, new h(C) = 10, true remaining cost of C = 3")
ocost, opath, oexp = astar(graph, h_over, "S", "G")
print("Path:", opath)
print("Cost:", ocost)
print("Cost (checked separately):", path_cost(graph, opath))
print("Expanded nodes:", oexp)
print("Expansion count:", len(oexp))
print("Optimal cost is", cost, "so result changed:", ocost != cost)
