import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from maze_solver import read_grid, solve_maze

KEY_COLORS = ['#FF6B6B', '#4ECDC4', '#FFD93D', '#C77DFF', '#F79D65', '#6BCB77']


def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def build_frame(grid, mask, path_so_far, n):
    img = np.ones((n, n, 3))
    for i in range(n):
        for j in range(n):
            ch = grid[i][j]
            if ch == '#':
                img[i, j] = (0, 0, 0)
            elif ch == 'S':
                img[i, j] = (0, 0.8, 0)
            elif ch == 'E':
                img[i, j] = (0.9, 0, 0)
            elif 'a' <= ch <= 'f':
                k = ord(ch) - ord('a')
                img[i, j] = (1, 1, 1) if (mask & (1 << k)) else hex_to_rgb(KEY_COLORS[k])
            elif 'A' <= ch <= 'F':
                k = ord(ch) - ord('A')
                img[i, j] = (0.85, 0.85, 0.85) if (mask & (1 << k)) else hex_to_rgb(KEY_COLORS[k])
    for (r, c) in path_so_far:
        img[r, c] = (0.15, 0.4, 1.0)
    for (r, c) in path_so_far:
        if grid[r][c] == 'S':
            img[r, c] = (0, 0.8, 0)
        elif grid[r][c] == 'E':
            img[r, c] = (0.9, 0, 0)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default='maze.csv')
    ap.add_argument('--save', default=None)
    ap.add_argument('--interval', type=int, default=300)
    args = ap.parse_args()

    grid = read_grid(args.input)
    n = len(grid)
    d, path = solve_maze(grid)
    print(f"Shortest path length: {d}")
    if d == -1:
        return

    frames = []
    mask = 0
    for idx in range(len(path)):
        r, c = path[idx]
        ch = grid[r][c]
        if 'a' <= ch <= 'f':
            mask |= 1 << (ord(ch) - ord('a'))
        frames.append(build_frame(grid, mask, path[:idx + 1], n))

    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(frames[0], interpolation='nearest')
    title = ax.set_title("")
    ax.set_xticks([]); ax.set_yticks([])

    inv_text = ax.text(0, -1.5, "", fontsize=11, family='monospace')

    def update(i):
        im.set_data(frames[i])
        title.set_text(f"Step {i}/{len(frames) - 1}")
        # Compute inventory at step i by replaying
        m = 0
        for k in range(i + 1):
            r, c = path[k]
            ch = grid[r][c]
            if 'a' <= ch <= 'f':
                m |= 1 << (ord(ch) - ord('a'))
        inv = "Keys: " + " ".join(
            chr(ord('a') + k) if (m & (1 << k)) else "_" for k in range(6))
        inv_text.set_text(inv)
        return im, title, inv_text

    ani = animation.FuncAnimation(fig, update, frames=len(frames),
                                  interval=args.interval, blit=False)
    if args.save:
        ani.save(args.save, writer='pillow', fps=5)
    plt.show()


if __name__ == '__main__':
    main()