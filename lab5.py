import math

count = 0


def minimax(depth, index, max_turn, scores, target, show):
    global count
    if depth == target:
        count = count + 1
        return scores[index]
    if max_turn:
        value = float("-inf")
        for i in range(2):
            child = minimax(depth + 1, index * 2 + i, False, scores, target, show)
            value = max(value, child)
        if show:
            print("Depth", depth, "| Node", index, "| MAX | value =", value)
        return value
    else:
        value = float("inf")
        for i in range(2):
            child = minimax(depth + 1, index * 2 + i, True, scores, target, show)
            value = min(value, child)
        if show:
            print("Depth", depth, "| Node", index, "| MIN | value =", value)
        return value


def alphabeta(depth, index, max_turn, scores, target, alpha, beta, show):
    global count
    if depth == target:
        count = count + 1
        return scores[index]
    if max_turn:
        value = float("-inf")
        for i in range(2):
            child = alphabeta(depth + 1, index * 2 + i, False, scores, target, alpha, beta, show)
            value = max(value, child)
            alpha = max(alpha, value)
            if alpha >= beta:
                if show and i == 0:
                    print("Pruned at depth", depth, "| Node", index, "| MAX | alpha =", alpha, "| beta =", beta)
                break
        return value
    else:
        value = float("inf")
        for i in range(2):
            child = alphabeta(depth + 1, index * 2 + i, True, scores, target, alpha, beta, show)
            value = min(value, child)
            beta = min(beta, value)
            if alpha >= beta:
                if show and i == 0:
                    print("Pruned at depth", depth, "| Node", index, "| MIN | alpha =", alpha, "| beta =", beta)
                break
        return value


def run_minimax(scores, show):
    global count
    count = 0
    target = int(math.log2(len(scores)))
    value = minimax(0, 0, True, scores, target, show)
    return value, count


def run_alphabeta(scores, show):
    global count
    count = 0
    target = int(math.log2(len(scores)))
    value = alphabeta(0, 0, True, scores, target, float("-inf"), float("inf"), show)
    return value, count


print("===== TASK 1: MINIMAX TRACE =====")
scores1 = [3, 5, 2, 9, 0, 7]
size = 2 ** math.ceil(math.log2(len(scores1)))
while len(scores1) < size:
    scores1.append(0)
print("Leaf scores:", scores1)
value, leaves = run_minimax(scores1, True)
print("Root value:", value)

print()
print("===== TASK 2: LEAF COUNT =====")
scores2 = [3, 5, 2, 9, 3, 5, 2, 9]
print("Leaf scores:", scores2)
value, leaves = run_minimax(scores2, False)
print("Minimax -> value:", value, "| leaves evaluated:", leaves)
print("Alpha-beta trace:")
value, leaves = run_alphabeta(scores2, True)
print("Alpha-beta -> value:", value, "| leaves evaluated:", leaves)

print()
print("===== TASK 3: REORDERING BRANCHES =====")
orders = [
    ("Original order", [3, 5, 2, 9, 3, 5, 2, 9]),
    ("Reversed order", [9, 2, 5, 3, 9, 2, 5, 3]),
    ("Leaf pairs swapped", [5, 3, 9, 2, 5, 3, 9, 2]),
]
for name, s in orders:
    mv, ml = run_minimax(s, False)
    av, al = run_alphabeta(s, False)
    print(name, s)
    print("  Minimax value:", mv, "| leaves:", ml)
    print("  Alpha-beta value:", av, "| leaves:", al)

print()
print("===== EDGE CASES =====")
same = [4, 4, 4, 4, 4, 4, 4, 4]
print("All leaves equal", same, "->", run_minimax(same, False), run_alphabeta(same, False))
neg = [-3, -5, -2, -9, -3, -5, -2, -9]
print("Negative leaves", neg, "->", run_minimax(neg, False), run_alphabeta(neg, False))
