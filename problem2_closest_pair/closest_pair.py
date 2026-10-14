import argparse
import math
import random
import time


def dist2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def brute_force(points):
    """Returns (min_distance, (p1, p2))."""
    n = len(points)
    best = float('inf')
    bp = (None, None)
    for i in range(n):
        for j in range(i + 1, n):
            d = dist2(points[i], points[j])
            if d < best:
                best = d
                bp = (points[i], points[j])
    if best == float('inf'):
        return float('inf'), (None, None)
    return math.sqrt(best), bp


def closest_pair(points):
    """Divide-and-conquer O(N log^2 N). Returns (distance, (p1, p2))."""
    n = len(points)
    if n < 2:
        return float('inf'), (None, None)

    idx = list(range(n))
    px = sorted(idx, key=lambda i: (points[i][0], points[i][1]))

    def rec(ix):
        m = len(ix)
        if m <= 3:
            best = float('inf')
            bp = (None, None)
            for a in range(m):
                for b in range(a + 1, m):
                    i, j = ix[a], ix[b]
                    d = dist2(points[i], points[j])
                    if d < best:
                        best = d
                        bp = (points[i], points[j])
            return (math.sqrt(best) if best < float('inf') else float('inf')), bp

        mid = m // 2
        mid_x = points[ix[mid]][0]
        dl, pl = rec(ix[:mid])
        dr, pr = rec(ix[mid:])
        d, bp = (dl, pl) if dl <= dr else (dr, pr)

        strip = [i for i in ix if abs(points[i][0] - mid_x) < d]
        strip.sort(key=lambda i: points[i][1])
        for a in range(len(strip)):
            for b in range(a + 1, min(a + 8, len(strip))):
                i, j = strip[a], strip[b]
                dd = math.sqrt(dist2(points[i], points[j]))
                if dd < d:
                    d = dd
                    bp = (points[i], points[j])
        return d, bp

    return rec(px)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=200)
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--float', action='store_true')
    ap.add_argument('--csv', default='points.csv')
    args = ap.parse_args()

    random.seed(args.seed)
    if args.float:
        pts = [(random.uniform(0, 1000), random.uniform(0, 1000))
               for _ in range(args.n)]
    else:
        pts = [(random.randint(0, 1000), random.randint(0, 1000))
               for _ in range(args.n)]

    with open(args.csv, 'w') as f:
        for x, y in pts:
            f.write(f"{x},{y}\n")

    if len(pts) < 2:
        print("Brute-Force : inf (N<2)")
        print("Divide&Conq : inf (N<2)")
        return

    t0 = time.perf_counter()
    bd, (b1, b2) = brute_force(pts)
    t1 = time.perf_counter()
    dd, (d1, d2) = closest_pair(pts)
    t2 = time.perf_counter()

    print(f"Brute-Force : {bd:.6f}  {b1}  {b2}  time={1000 * (t1 - t0):.3f} ms")
    print(f"Divide&Conq : {dd:.6f}  {d1}  {d2}  time={1000 * (t2 - t1):.3f} ms")
    print(f"Agree: {abs(bd - dd) < 1e-9}")


if __name__ == '__main__':
    main()