import argparse
import random
import time
import matplotlib.pyplot as plt
from closest_pair import brute_force, closest_pair


def load_points(path):
    pts = []
    with open(path) as f:
        for line in f:
            a, b = line.strip().split(',')
            pts.append((float(a), float(b)))
    return pts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='points.csv')
    args = ap.parse_args()

    pts = load_points(args.csv)
    bd, (b1, b2) = brute_force(pts)
    dd, (d1, d2) = closest_pair(pts)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    ax = axes[0]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.scatter(xs, ys, s=15, c='steelblue', label='points')
    if b1 and b2:
        ax.plot([b1[0], b2[0]], [b1[1], b2[1]], 'r-', linewidth=2,
                label=f'Brute Force d={bd:.3f}')
    if d1 and d2:
        ax.plot([d1[0], d2[0]], [d1[1], d2[1]], 'g--', linewidth=2,
                label=f'D&C d={dd:.3f}')
    if pts:
        sorted_x = sorted(pts, key=lambda p: p[0])
        mid_x = sorted_x[len(pts) // 2][0]
        ax.axvline(mid_x, color='purple', linestyle=':', linewidth=1)
        ax.axvspan(mid_x - dd, mid_x + dd, alpha=0.08, color='purple',
                   label='strip (2d)')
    ax.legend()
    ax.set_title("Closest pair & dividing strip")
    ax.grid(True, linestyle='--', alpha=0.4)

    # runtime comparison
    ax2 = axes[1]
    sizes = [50, 100, 200, 400, 800]
    bt, dt = [], []
    random.seed(123)
    for n in sizes:
        test = [(random.random() * 1000, random.random() * 1000) for _ in range(n)]
        t0 = time.perf_counter()
        brute_force(test)
        t1 = time.perf_counter()
        closest_pair(test)
        t2 = time.perf_counter()
        bt.append((t1 - t0) * 1000)
        dt.append((t2 - t1) * 1000)
    ax2.plot(sizes, bt, 'ro-', label='Brute Force')
    ax2.plot(sizes, dt, 'gs-', label='Divide & Conquer')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel('N')
    ax2.set_ylabel('time (ms)')
    ax2.set_title("Runtime vs N")
    ax2.grid(True, which='both', linestyle='--', alpha=0.4)
    ax2.legend()

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()