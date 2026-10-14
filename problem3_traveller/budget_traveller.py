import argparse
import csv
import heapq
import random


def solve(N, edges, K, C):
    """Dijkstra on state (city, hops_used, coupons_used). At most K stops -> hops <= K+1."""
    max_hops = K + 1
    adj = [[] for _ in range(N + 1)]
    for u, v, p in edges:
        adj[u].append((v, p))

    INF = float('inf')
    dist = [[[INF] * (C + 1) for _ in range(max_hops + 1)] for _ in range(N + 1)]
    dist[1][0][0] = 0
    parent = {}
    pq = [(0, 1, 0, 0)]
    best = None

    while pq:
        cost, u, hops, coupons = heapq.heappop(pq)
        if cost > dist[u][hops][coupons]:
            continue
        if u == N:
            best = (cost, hops, coupons)
            break
        if hops == max_hops:
            continue
        for v, p in adj[u]:
            nh = hops + 1
            if cost + p < dist[v][nh][coupons]:
                dist[v][nh][coupons] = cost + p
                parent[(v, nh, coupons)] = (u, hops, coupons, 0)
                heapq.heappush(pq, (cost + p, v, nh, coupons))
            if coupons + 1 <= C:
                disc = p // 2
                if cost + disc < dist[v][nh][coupons + 1]:
                    dist[v][nh][coupons + 1] = cost + disc
                    parent[(v, nh, coupons + 1)] = (u, hops, coupons, 1)
                    heapq.heappush(pq, (cost + disc, v, nh, coupons + 1))

    if best is None:
        return -1, []

    cost, hops, coupons = best
    state = (N, hops, coupons)
    path = []
    while state in parent:
        pu, ph, pc, used = parent[state]
        path.append((pu, state[0], used))
        state = (pu, ph, pc)
    path.reverse()
    return cost, path


def read_graph_csv(path):
    edges = []
    N = 0
    with open(path, newline='') as f:
        for row in csv.reader(f):
            if len(row) < 3:
                continue
            u, v, p = int(row[0]), int(row[1]), int(row[2])
            edges.append((u, v, p))
            N = max(N, u, v)
    return N, edges

def generate_graph(N, M, K, C, seed=0):
    random.seed(seed)
    edges = set()
    # ensure a chain from 1 to N with K+1 edges (forces intermediate stops)
    chain = [1] + sorted(random.sample(range(2, N), min(K, N - 2))) + [N]
    for i in range(len(chain) - 1):
        edges.add((chain[i], chain[i + 1], random.randint(10, 100)))
    # add random extra edges, but NEVER a direct 1 -> N
    while len(edges) < M:
        u = random.randint(1, N)
        v = random.randint(1, N)
        if u == v:
            continue
        if u == 1 and v == N:
            continue          # <-- forbids the direct edge
        edges.add((u, v, random.randint(10, 100)))
    return N, list(edges)

def write_graph_csv(path, N, edges, path_edges=None):
    """path_edges = list of (from, to, coupon_used)."""
    used = {}
    if path_edges:
        for u, v, c in path_edges:
            used[(u, v)] = c
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['u', 'v', 'price', 'on_path', 'coupon'])
        for (u, v, p) in edges:
            on = 'x' if (u, v) in used else ''
            cp = 'x' if used.get((u, v), 0) == 1 else ''
            w.writerow([u, v, p, on, cp])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default=None)
    ap.add_argument('--generate', action='store_true')
    ap.add_argument('--n', type=int, default=8)
    ap.add_argument('--m', type=int, default=14)
    ap.add_argument('--k', type=int, default=3)
    ap.add_argument('--c', type=int, default=2)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--output', default='graph_path.csv')
    args = ap.parse_args()

    if args.generate or args.input is None:
        N, edges = generate_graph(args.n, args.m, args.k, args.c, args.seed)
        K, C = args.k, args.c
    else:
        # assume format: first line K C, then u,v,p rows
        with open(args.input, newline='') as f:
            rows = [r for r in csv.reader(f) if r]
        K, C = int(rows[0][0]), int(rows[0][1])
        N = 0
        edges = []
        for r in rows[1:]:
            if len(r) < 3:
                continue
            u, v, p = int(r[0]), int(r[1]), int(r[2])
            edges.append((u, v, p))
            N = max(N, u, v)

    cost, path = solve(N, edges, K, C)
    print(f"Minimum cost: {cost}")
    for u, v, c in path:
        print(f"  {u} -> {v}  coupon={'YES' if c else 'no'}")
    write_graph_csv(args.output, N, edges, path)
    print(f"Graph with path marked -> {args.output}")


if __name__ == '__main__':
    main()