"""
DAA ASSIGNMENT 4B – ALGORITHM ENGINEERING
Tasks 1–6: Word Wrap, Knapsack, Routing, Assembly Line,
MST (Kruskal/Prim/Boruvka), and TSP Dynamic Programming.

Run:
    python DAA_Assignment_4B.py

The program runs reproducible demonstrations for every task.
All datasets are defined below and can be edited.
"""

from itertools import permutations
from math import inf
from time import perf_counter


# ============================================================
# TASK 1 – WORD WRAP USING DYNAMIC PROGRAMMING
# ============================================================

def word_wrap(words, width, show_dp=True):
    """
    DP[i] = minimum penalty for arranging words[i:] into lines.
    penalty of a non-final line = (width - used_characters)^2.
    The final line has penalty zero.
    """
    n = len(words)
    dp = [inf] * (n + 1)
    next_break = [-1] * (n + 1)
    dp[n] = 0

    for i in range(n - 1, -1, -1):
        used = 0
        for j in range(i, n):
            needed = len(words[j]) if j == i else len(words[j]) + 1
            used += needed
            if used > width:
                break

            line_penalty = 0 if j == n - 1 else (width - used) ** 2
            candidate = line_penalty + dp[j + 1]

            if candidate < dp[i]:
                dp[i] = candidate
                next_break[i] = j + 1

    if next_break[0] == -1:
        raise ValueError("At least one word is wider than the line width.")

    lines = []
    line_details = []
    i = 0
    while i < n:
        j = next_break[i]
        selected = words[i:j]
        used = sum(map(len, selected)) + len(selected) - 1
        unused = width - used
        penalty = 0 if j == n else unused ** 2
        lines.append(" ".join(selected))
        line_details.append((selected, unused, penalty))
        i = j

    if show_dp:
        print("DP suffix states (DP[i] = minimum penalty for words i..end):")
        for i, value in enumerate(dp):
            print(f"  DP[{i}] = {value}")

    print(f"Line width = {width}")
    print(f"Minimum total penalty = {dp[0]}")
    for number, (line, (selected, unused, penalty)) in enumerate(zip(lines, line_details), 1):
        print(f"  Line {number}: {' '.join(selected)}")
        print(f"    Unused spaces = {unused}; line penalty = {penalty}")
    return dp[0], lines, dp, line_details


def task1():
    print("\n" + "=" * 72)
    print("TASK 1 – WORD WRAP")
    print("=" * 72)
    words = "Dynamic programming creates balanced lines for clear document layout".split()
    print("Words:", " ".join(words))
    print("\nBase case: width 18")
    word_wrap(words, 18)
    cases = [12, 18, 24]
    print("\nRequirement-change experiments:")
    for width in cases:
        print(f"\n--- Width {width} ---")
        word_wrap(words, width, show_dp=False)

    print("\nBoundary test: one word exactly equal to the line width.")
    word_wrap(["ALGORITHM", "DESIGN"], 9, show_dp=True)


# ============================================================
# TASK 2 – FRACTIONAL GREEDY AND 0/1 DP KNAPSACK
# ============================================================

def fractional_knapsack(items, capacity):
    # items: (ID, weight, value)
    ordered = sorted(items, key=lambda x: x[2] / x[1], reverse=True)
    remaining = capacity
    total = 0.0
    selected = []
    operations = 0

    print("Fractional Knapsack decisions (descending value/weight):")
    for item_id, weight, value in ordered:
        operations += 1
        ratio = value / weight
        if remaining <= 0:
            break
        fraction = min(1.0, remaining / weight)
        taken_weight = fraction * weight
        earned = fraction * value
        remaining -= taken_weight
        total += earned
        selected.append((item_id, fraction, taken_weight, earned))
        print(f"  {item_id}: ratio={ratio:.2f}, fraction={fraction:.2f}, "
              f"weight taken={taken_weight:.2f}, value gained={earned:.2f}")
    print(f"Fractional total value = {total:.2f}; weight used = {capacity-remaining:.2f}")
    return total, selected, operations


def zero_one_knapsack(items, capacity):
    n = len(items)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    decisions = 0

    for i in range(1, n + 1):
        item_id, weight, value = items[i - 1]
        for cap in range(capacity + 1):
            decisions += 1
            dp[i][cap] = dp[i - 1][cap]
            if weight <= cap:
                dp[i][cap] = max(
                    dp[i][cap],
                    value + dp[i - 1][cap - weight]
                )

    chosen = []
    cap = capacity
    for i in range(n, 0, -1):
        if dp[i][cap] != dp[i - 1][cap]:
            item_id, weight, value = items[i - 1]
            chosen.append((item_id, weight, value))
            cap -= weight
    chosen.reverse()

    print("0/1 DP final row:", dp[n])
    print("0/1 selected items:", chosen)
    print(f"0/1 maximum value = {dp[n][capacity]}; "
          f"weight used = {sum(x[1] for x in chosen)}")
    return dp[n][capacity], chosen, decisions, len(dp) * len(dp[0])


def task2():
    print("\n" + "=" * 72)
    print("TASK 2 – GREEDY VS DYNAMIC PROGRAMMING KNAPSACK")
    print("=" * 72)

    normal = [("A", 2, 40), ("B", 3, 50), ("C", 5, 60)]
    capacity = 5
    print("\nNormal case – capacity 5:", normal)
    fractional_knapsack(normal, capacity)
    zero_one_knapsack(normal, capacity)

    adversarial = [("A", 10, 60), ("B", 20, 100), ("C", 30, 120)]
    capacity = 50
    print("\nAdversarial 0/1 case – capacity 50:", adversarial)
    print("Greedy ratio order commits to A first (ratio 6), then B (ratio 5).")
    greedy_total = 0
    used = 0
    for item_id, weight, value in sorted(adversarial, key=lambda x: x[2]/x[1], reverse=True):
        if used + weight <= capacity:
            used += weight
            greedy_total += value
            print(f"  Greedy accepts {item_id}; used={used}; value={greedy_total}")
        else:
            print(f"  Greedy rejects {item_id}; it does not fit.")
    print("Greedy 0/1 value =", greedy_total)
    optimum, chosen, work, cells = zero_one_knapsack(adversarial, capacity)
    print("First harmful commitment: accepting A prevents selecting B + C.")
    print("B + C has weight 50 and value 220, which is the optimum.")
    print("\nEngineering comparison:")
    print("  Fractional greedy: O(n log n) time including sort, O(n) storage; optimal for divisible items.")
    print("  0/1 DP: O(nW) time and O(nW) table storage; exact for integer capacity.")
    print(f"  This 0/1 run evaluated {work} DP cells and stored {cells} table cells.")
    print("  If a fast near-optimal answer is acceptable, use ratio-greedy as an approximation/heuristic,")
    print("  but disclose that it has no general optimality guarantee for indivisible items.")


# ============================================================
# TASK 3 – DIJKSTRA, BELLMAN-FORD, FLOYD, WARSHALL
# ============================================================

VERTICES = list("ABCDEFGH")
BASE_EDGES = [
    ("A", "B", 4), ("A", "C", 10), ("B", "C", 2), ("B", "D", 7),
    ("C", "D", 3), ("C", "E", 8), ("D", "E", 2), ("D", "F", 6),
    ("E", "F", 1), ("E", "G", 5), ("F", "G", 2), ("G", "H", 3),
    ("F", "H", 8), ("B", "E", 9)
]


def dijkstra(vertices, edges, source):
    adj = {v: [] for v in vertices}
    for u, v, w in edges:
        if w < 0:
            raise ValueError("Dijkstra requires non-negative edge weights.")
        adj[u].append((v, w))

    dist = {v: inf for v in vertices}
    pred = {v: None for v in vertices}
    done = set()
    dist[source] = 0
    final_order = []

    while len(done) < len(vertices):
        candidates = [v for v in vertices if v not in done]
        u = min(candidates, key=lambda x: dist[x])
        if dist[u] == inf:
            break
        done.add(u)
        final_order.append(u)

        for v, w in adj[u]:
            if v not in done and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u

    return dist, pred, final_order


def reconstruct_path(pred, target):
    if target not in pred:
        return []
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = pred[cur]
    return list(reversed(path))


def bellman_ford(vertices, edges, source):
    dist = {v: inf for v in vertices}
    pred = {v: None for v in vertices}
    dist[source] = 0

    for _ in range(len(vertices) - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != inf and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                changed = True
        if not changed:
            break

    negative_cycle = False
    for u, v, w in edges:
        if dist[u] != inf and dist[u] + w < dist[v]:
            negative_cycle = True
            break

    return dist, pred, negative_cycle


def floyd_warshall(vertices, edges):
    n = len(vertices)
    idx = {v: i for i, v in enumerate(vertices)}
    d = [[inf] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for u, v, w in edges:
        d[idx[u]][idx[v]] = min(d[idx[u]][idx[v]], w)

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] != inf and d[k][j] != inf:
                    d[i][j] = min(d[i][j], d[i][k] + d[k][j])
    return d


def warshall(vertices, edges):
    n = len(vertices)
    idx = {v: i for i, v in enumerate(vertices)}
    reach = [[False] * n for _ in range(n)]
    for i in range(n):
        reach[i][i] = True
    for u, v, _ in edges:
        reach[idx[u]][idx[v]] = True

    for k in range(n):
        for i in range(n):
            for j in range(n):
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])
    return reach


def print_matrix(vertices, matrix, boolean=False):
    print("     " + " ".join(f"{v:>5}" for v in vertices))
    for v, row in zip(vertices, matrix):
        vals = []
        for x in row:
            if x == inf:
                vals.append("INF")
            elif boolean:
                vals.append("1" if x else "0")
            else:
                vals.append(str(int(x)))
        print(f"{v:>3}  " + " ".join(f"{x:>5}" for x in vals))


def task3():
    print("\n" + "=" * 72)
    print("TASK 3 – ROUTING ENGINE")
    print("=" * 72)
    print("Vertices:", VERTICES)
    print("Directed edges:", BASE_EDGES)
    dist, pred, order = dijkstra(VERTICES, BASE_EDGES, "A")
    print("\nStage A – Dijkstra from A")
    print("Finalisation order:", order)
    for v in VERTICES:
        print(f"  {v}: distance={dist[v]}, predecessor={pred[v]}, path={reconstruct_path(pred, v)}")

    # Negative edge B -> F changes best route to F and H.
    negative_edges = BASE_EDGES + [("B", "F", -5)]
    print("\nStage B – Add negative edge B -> F with weight -5.")
    print("Prediction: Dijkstra's non-negative-edge assumption is broken; paths through B->F may improve.")
    try:
        dijkstra(VERTICES, negative_edges, "A")
    except ValueError as exc:
        print("Dijkstra correctly refuses modified graph:", exc)
    bf_dist, bf_pred, neg_cycle = bellman_ford(VERTICES, negative_edges, "A")
    print("Bellman-Ford distances:")
    for v in VERTICES:
        print(f"  {v}: {bf_dist[v]}, path={reconstruct_path(bf_pred, v)}")

    print("\nStage C – Add reachable negative cycle F -> G (-4), G -> F (1).")
    cycle_edges = negative_edges + [("F", "G", -4), ("G", "F", 1)]
    _, _, cycle = bellman_ford(VERTICES, cycle_edges, "A")
    print("Reachable negative-weight cycle detected =", cycle)

    print("\nStage D – Floyd distance matrix (base non-negative graph):")
    print_matrix(VERTICES, floyd_warshall(VERTICES, BASE_EDGES))
    print("\nWarshall reachability matrix (1 = reachable):")
    print_matrix(VERTICES, warshall(VERTICES, BASE_EDGES), boolean=True)


# ============================================================
# TASK 4 – TWO-LINE ASSEMBLY LINE SCHEDULING
# ============================================================

def assembly_line(a1, a2, t1, t2, entry, exit_times, verbose=True):
    n = len(a1)
    f1 = [0] * n
    f2 = [0] * n
    p1 = [None] * n
    p2 = [None] * n

    f1[0] = entry[0] + a1[0]
    f2[0] = entry[1] + a2[0]

    for j in range(1, n):
        stay1 = f1[j-1] + a1[j]
        transfer1 = f2[j-1] + t2[j-1] + a1[j]
        if stay1 <= transfer1:
            f1[j], p1[j] = stay1, 1
        else:
            f1[j], p1[j] = transfer1, 2

        stay2 = f2[j-1] + a2[j]
        transfer2 = f1[j-1] + t1[j-1] + a2[j]
        if stay2 <= transfer2:
            f2[j], p2[j] = stay2, 2
        else:
            f2[j], p2[j] = transfer2, 1

        if verbose:
            print(f"Station {j+1}:")
            print(f"  Line 1: stay={stay1}, transfer={transfer1}, choose={p1[j]}")
            print(f"  Line 2: stay={stay2}, transfer={transfer2}, choose={p2[j]}")

    finish1 = f1[-1] + exit_times[0]
    finish2 = f2[-1] + exit_times[1]
    if finish1 <= finish2:
        total, line = finish1, 1
    else:
        total, line = finish2, 2

    route = [0] * n
    route[-1] = line
    for j in range(n-1, 0, -1):
        route[j-1] = p1[j] if route[j] == 1 else p2[j]

    print("Minimum production time =", total)
    print("Optimal line route =", " -> ".join(f"Line {x}, Station {i+1}" for i, x in enumerate(route)))
    transfers = [i+1 for i in range(1, n) if route[i] != route[i-1]]
    print("Transfer before station(s) =", transfers if transfers else "None")
    return total, route


def task4():
    print("\n" + "=" * 72)
    print("TASK 4 – ASSEMBLY LINE SCHEDULING")
    print("=" * 72)
    a1 = [7, 9, 3, 4, 8, 4]
    a2 = [8, 5, 6, 4, 5, 7]
    t1 = [2, 3, 1, 3, 4]
    t2 = [2, 1, 2, 2, 1]
    entry = [2, 4]
    exits = [3, 2]

    print("Base case:")
    base_total, base_route = assembly_line(a1, a2, t1, t2, entry, exits)

    print("\nPrediction before experiment: increase transfer time t1[0] from 2 to 20.")
    print("Prediction: transferring from Line 1 to Line 2 before station 2 becomes less attractive;")
    print("the route should stay on Line 1 at station 2, and total time should increase.")
    changed_t1 = t1[:]
    changed_t1[0] = 20
    print("Modified transfer-time run:")
    assembly_line(a1, a2, changed_t1, t2, entry, exits)

    print("\nProduction disruption: increase Line 1 station 3 processing time from 3 to 25.")
    changed_a1 = a1[:]
    changed_a1[2] = 25
    assembly_line(changed_a1, a2, t1, t2, entry, exits)

    print("\nThree-line extension:")
    print("State becomes F[line][station], with one minimum cost for each of 3 lines at each station.")
    print("For each destination line l, compare staying on l with transfers from every other line k.")
    print("Store predecessorLine[l][station] to reconstruct the chosen line at every station.")
    print("This generalises the transition from 2 alternatives to 3 possible predecessor lines.")


# ============================================================
# TASK 5 – MINIMUM SPANNING TREE: KRUSKAL, PRIM, BORUVKA
# ============================================================

MST_VERTICES = list("ABCDEFGH")
MST_EDGES = [
    ("A", "B", 4), ("A", "C", 3), ("B", "C", 2), ("B", "D", 5),
    ("C", "D", 3), ("C", "E", 6), ("D", "E", 1), ("D", "F", 7),
    ("E", "F", 4), ("E", "G", 5), ("F", "G", 2), ("F", "H", 6),
    ("G", "H", 3), ("B", "E", 8), ("C", "F", 9)
]


def kruskal(vertices, edges):
    parent = {v: v for v in vertices}
    rank = {v: 0 for v in vertices}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1
        return True

    chosen = []
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if union(u, v):
            chosen.append((u, v, w))
            print(f"  Kruskal accepts {u}-{v} ({w})")
        else:
            print(f"  Kruskal rejects cycle edge {u}-{v} ({w})")
        if len(chosen) == len(vertices) - 1:
            break
    return chosen


def prim(vertices, edges, start="A"):
    adj = {v: [] for v in vertices}
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    visited = {start}
    chosen = []
    while len(visited) < len(vertices):
        candidates = [
            (w, u, v)
            for u in visited
            for v, w in adj[u]
            if v not in visited
        ]
        if not candidates:
            raise ValueError("Graph is disconnected.")
        w, u, v = min(candidates)
        chosen.append((u, v, w))
        visited.add(v)
        print(f"  Prim adds {u}-{v} ({w}); visited={sorted(visited)}")
    return chosen


def boruvka(vertices, edges):
    parent = {v: v for v in vertices}

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    chosen = []
    while len({find(v) for v in vertices}) > 1:
        cheapest = {}
        for u, v, w in edges:
            ru, rv = find(u), find(v)
            if ru != rv:
                if ru not in cheapest or w < cheapest[ru][2]:
                    cheapest[ru] = (u, v, w)
                if rv not in cheapest or w < cheapest[rv][2]:
                    cheapest[rv] = (u, v, w)

        added = False
        for edge in cheapest.values():
            u, v, w = edge
            ru, rv = find(u), find(v)
            if ru != rv:
                parent[ru] = rv
                chosen.append(edge)
                added = True
                print(f"  Boruvka adds {u}-{v} ({w})")
        if not added:
            raise ValueError("Graph is disconnected.")
    return chosen


def mst_cost(edges):
    return sum(w for _, _, w in edges)


def task5():
    print("\n" + "=" * 72)
    print("TASK 5 – KRUSKAL, PRIM AND BORUVKA")
    print("=" * 72)
    print("Same connected undirected graph:", MST_EDGES)

    print("\nKruskal trace:")
    k = kruskal(MST_VERTICES, MST_EDGES)
    print("Kruskal MST:", k, "cost =", mst_cost(k))

    print("\nPrim trace:")
    p = prim(MST_VERTICES, MST_EDGES)
    print("Prim MST:", p, "cost =", mst_cost(p))

    print("\nBoruvka trace:")
    b = boruvka(MST_VERTICES, MST_EDGES)
    print("Boruvka MST:", b, "cost =", mst_cost(b))

    print("\nMultiple-MST experiment:")
    # A four-cycle with equal weights has multiple valid MST edge sets.
    tie_edges = [("A","B",1), ("B","C",1), ("C","D",1), ("D","A",1), ("A","C",2)]
    print("Equal-weight cycle edges:", tie_edges)
    tie_k = kruskal(list("ABCD"), tie_edges)
    tie_p = prim(list("ABCD"), tie_edges)
    print("Kruskal tied-graph tree:", tie_k, "cost =", mst_cost(tie_k))
    print("Prim tied-graph tree:", tie_p, "cost =", mst_cost(tie_p))
    print("Different edge sets can both be correct when equal-weight alternatives exist.")

    print("\nDeployment interpretation:")
    print("  Sparse graph: Kruskal or Boruvka can be attractive; sorting or component-edge scans are manageable.")
    print("  Dense graph: Prim with an adjacency matrix / suitable priority structure can be competitive.")
    print("  Distributed graph: Boruvka is naturally parallel because each component chooses its cheapest outgoing edge per phase.")


# ============================================================
# TASK 6 – TRAVELLING SALESPERSON: HELD-KARP DP
# ============================================================

def tsp_held_karp(cost):
    """
    Vertex 0 is the hub. DP[mask][j] is minimum cost to start at 0,
    visit exactly the non-hub vertices in mask, and finish at j.
    """
    n = len(cost)
    m = n - 1
    full = (1 << m) - 1
    dp = {}
    parent = {}
    evaluated = 0

    for j in range(1, n):
        mask = 1 << (j - 1)
        dp[(mask, j)] = cost[0][j]
        parent[(mask, j)] = 0
        evaluated += 1

    for size in range(2, m + 1):
        for mask in range(1, full + 1):
            if mask.bit_count() != size:
                continue
            for j in range(1, n):
                bitj = 1 << (j - 1)
                if not (mask & bitj):
                    continue
                prev_mask = mask ^ bitj
                best = inf
                best_prev = None
                for k in range(1, n):
                    if prev_mask & (1 << (k - 1)):
                        candidate = dp[(prev_mask, k)] + cost[k][j]
                        if candidate < best:
                            best = candidate
                            best_prev = k
                dp[(mask, j)] = best
                parent[(mask, j)] = best_prev
                evaluated += 1

    best_cost = inf
    last = None
    for j in range(1, n):
        candidate = dp[(full, j)] + cost[j][0]
        if candidate < best_cost:
            best_cost = candidate
            last = j

    route_rev = [last]
    mask = full
    current = last
    while current != 0:
        previous = parent[(mask, current)]
        mask ^= 1 << (current - 1)
        current = previous
        if current != 0:
            route_rev.append(current)

    route = [0] + list(reversed(route_rev)) + [0]
    return best_cost, route, evaluated, len(dp)


def exhaustive_tsp(cost):
    n = len(cost)
    best = inf
    best_route = None
    for order in permutations(range(1, n)):
        route = (0,) + order + (0,)
        total = sum(cost[route[i]][route[i+1]] for i in range(n))
        if total < best:
            best = total
            best_route = route
    return best, best_route


def task6():
    print("\n" + "=" * 72)
    print("TASK 6 – TSP USING DYNAMIC PROGRAMMING")
    print("=" * 72)
    cost = [
        [0, 10, 15, 20, 18, 12, 25],
        [10, 0, 35, 25, 17, 28, 30],
        [15, 35, 0, 30, 20, 22, 18],
        [20, 25, 30, 0, 11, 16, 24],
        [18, 17, 20, 11, 0, 14, 19],
        [12, 28, 22, 16, 14, 0, 13],
        [25, 30, 18, 24, 19, 13, 0],
    ]
    names = ["Hub", "A", "B", "C", "D", "E", "F"]
    print("Cost matrix:")
    for row in cost:
        print(row)

    best, route, evaluated, stored = tsp_held_karp(cost)
    print("Optimal route:", " -> ".join(names[i] for i in route))
    print("Minimum travel cost =", best)
    print("DP states evaluated =", evaluated)
    print("DP states stored =", stored)

    print("\nValidation with hub + 4 locations:")
    small = [row[:5] for row in cost[:5]]
    dp_cost, dp_route, dp_states, _ = tsp_held_karp(small)
    brute_cost, brute_route = exhaustive_tsp(small)
    print("DP cost =", dp_cost, "route =", dp_route)
    print("Exhaustive cost =", brute_cost, "route =", brute_route)
    print("Validation passed =", dp_cost == brute_cost)

    print("\nState-space experiment (number of delivery locations excludes hub):")
    print("Locations | DP states evaluated | Stored states (memory proxy) | Runtime (ms)")
    for locations in range(4, 9):
        n = locations + 1
        # symmetric complete graph with deterministic positive weights
        matrix = [[0 if i == j else ((i*7 + j*11) % 29) + 1 for j in range(n)] for i in range(n)]
        started = perf_counter()
        _, _, count, stored_count = tsp_held_karp(matrix)
        elapsed_ms = (perf_counter() - started) * 1000
        print(f"{locations:9d} | {count:19d} | {stored_count:26d} | {elapsed_ms:11.3f}")

    print("\nFor 200 locations, exact Held-Karp DP is impractical because its state space")
    print("grows on the order of n * 2^n. A heuristic/metaheuristic (nearest neighbour,")
    print("2-opt, simulated annealing or genetic search) can return a strong route quickly,")
    print("but the company gives up a guarantee of mathematical optimality.")
    print("Reflection: DP removes repeated subproblems, but it still has exponentially many subsets.")


def main():
    task1()
    task2()
    task3()
    task4()
    task5()
    task6()
    print("\n" + "=" * 72)
    print("ALL SIX ASSIGNMENT TASK DEMONSTRATIONS COMPLETED")
    print("=" * 72)


if __name__ == "__main__":
    main()
