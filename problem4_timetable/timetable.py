import argparse
import csv
import random
import time
from collections import defaultdict


def greedy_dsatur(N, adj, R):
    """DSatur greedy heuristic honouring per-slot capacity R."""
    color = [-1] * N
    sat = [set() for _ in range(N)]
    slot_count = defaultdict(int)
    uncolored = set(range(N))

    while uncolored:
        u = max(uncolored, key=lambda x: (len(sat[x]), len(adj[x])))
        used = sat[u]
        c = 0
        while c in used or slot_count[c] >= R:
            c += 1
        color[u] = c
        slot_count[c] += 1
        uncolored.remove(u)
        for v in adj[u]:
            if color[v] == -1:
                sat[v].add(c)

    slots = max(color) + 1 if color else 0
    return color, slots


def exact_coloring(N, adj, R, greedy_color=None, greedy_slots=None,
                   max_nodes=5_000_000):
    """Backtracking with per-slot capacity R.

    Uses the greedy solution as the initial incumbent so that pruning
    (`used >= best_k`) only eliminates branches that cannot strictly
    improve. If greedy survives, its result is proven optimal.
    """
    if N == 0:
        return [], 0

    order = sorted(range(N), key=lambda x: -len(adj[x]))
    color = [-1] * N
    slot_count = defaultdict(int)

    if greedy_color is not None:
        best_color = [greedy_color[:]]
        best_k = [greedy_slots]
    else:
        best_color = [None]
        best_k = [N + 1]

    nodes = [0]

    def bt(pos, used):
        nodes[0] += 1
        if nodes[0] > max_nodes:
            return
        if pos == N:
            if used < best_k[0]:
                best_k[0] = used
                best_color[0] = color[:]
            return
        if used >= best_k[0]:
            return
        u = order[pos]
        forbidden = {color[v] for v in adj[u] if color[v] != -1}
        for c in range(used + 1):
            if c in forbidden:
                continue
            if slot_count[c] >= R:
                continue
            color[u] = c
            slot_count[c] += 1
            bt(pos + 1, max(used, c + 1))
            slot_count[c] -= 1
            color[u] = -1

    bt(0, 0)
    return best_color[0], best_k[0], nodes[0]


def generate_graph(N, density, seed=0):
    random.seed(seed)
    adj = [set() for _ in range(N)]
    for i in range(N):
        for j in range(i + 1, N):
            if random.random() < density:
                adj[i].add(j)
                adj[j].add(i)
    return [list(s) for s in adj]


def timetable_from_colors(color, N):
    slots = defaultdict(list)
    for i in range(N):
        slots[color[i]].append(i + 1)
    return slots


def save_conflicts(N, adj, path='conflicts.csv'):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['u', 'v'])
        for i in range(N):
            for j in adj[i]:
                if i < j:
                    w.writerow([i + 1, j + 1])


def save_timetable(slots, R, path='timetable.csv'):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Slot'] + [f'Hall{i + 1}' for i in range(R)])
        for s in sorted(slots):
            courses = sorted(slots[s])
            row = [f'Slot {s + 1}']
            for i in range(R):
                row.append(courses[i] if i < len(courses) else '')
            w.writerow(row)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=12)
    ap.add_argument('--r', type=int, default=3)
    ap.add_argument('--density', type=float, default=0.25)
    ap.add_argument('--seed', type=int, default=5)
    args = ap.parse_args()

    N, R = args.n, args.r
    adj = generate_graph(N, args.density, args.seed)
    save_conflicts(N, adj)

    t0 = time.perf_counter()
    g_color, g_slots = greedy_dsatur(N, adj, R)
    t1 = time.perf_counter()
    e_color, e_slots, nodes = exact_coloring(
        N, adj, R, greedy_color=g_color, greedy_slots=g_slots)
    t2 = time.perf_counter()

    print(f"DSatur greedy slots       : {g_slots}   ({1000 * (t1 - t0):.2f} ms)")
    print(f"Exact slots (optimal)     : {e_slots}   ({1000 * (t2 - t1):.2f} ms, "
          f"{nodes} nodes)")

    slots = timetable_from_colors(e_color, N)
    for s in sorted(slots):
        print(f"Slot {s + 1}: {sorted(slots[s])}")

    save_timetable(slots, R)
    print("Timetable -> timetable.csv")
    print("Conflicts -> conflicts.csv")


if __name__ == '__main__':
    main()