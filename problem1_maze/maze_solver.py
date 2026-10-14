import argparse
import csv
import random
from collections import deque


def read_grid(path):
    with open(path, newline='') as f:
        return [row for row in csv.reader(f) if row]


def write_grid(path, grid):
    with open(path, 'w', newline='') as f:
        csv.writer(f).writerows(grid)


# Door/key letters (skip 'e'/'E' because 'E' is the exit!)
DOOR_LETTERS = ['A', 'B', 'C', 'D', 'F', 'G']
KEY_LETTERS  = ['a', 'b', 'c', 'd', 'f', 'g']


def solve_maze(grid):
    n = len(grid)
    start = end = None
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 'S':
                start = (i, j)
            elif grid[i][j] == 'E':
                end = (i, j)
    if start is None or end is None:
        return -1, []

    q = deque([(start[0], start[1], 0)])
    dist = {(start[0], start[1], 0): 0}
    parent = {}
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while q:
        r, c, mask = q.popleft()
        if (r, c) == end:
            path = [(r, c)]
            st = (r, c, mask)
            while st in parent:
                st = parent[st]
                path.append((st[0], st[1]))
            path.reverse()
            return dist[(r, c, mask)], path

        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < n and 0 <= nc < n):
                continue
            ch = grid[nr][nc]
            if ch == '#':
                continue
            nmask = mask
            if ch == 'E':
                # EXIT — always passable, do NOT treat as door 'E'
                pass
            elif 'a' <= ch <= 'z':
                # any lowercase key
                if 'a' <= ch <= 'f':
                    nmask |= 1 << (ord(ch) - ord('a'))
                elif ch == 'g':
                    nmask |= 1 << 5  # treat g as the 6th key slot
            elif 'A' <= ch <= 'F' or ch == 'G':
                # it's a door (A-F, plus G for T=6)
                if ch == 'E':
                    # won't reach here because exit handled above
                    pass
                key_bit = ord(ch) - ord('A') if 'A' <= ch <= 'F' else 5
                if not (mask & (1 << key_bit)):
                    continue
            st = (nr, nc, nmask)
            if st not in dist:
                dist[st] = dist[(r, c, mask)] + 1
                parent[st] = (r, c, mask)
                q.append(st)
    return -1, []

def _carve_maze(n, seed=None):
    """Randomized DFS carving. Returns a 2D grid of '.' and '#'.

    Guarantees all '.' cells are reachable from any other '.' cell.
    Starts fully walled and carves 2-cell-wide passages.
    """
    if seed is not None:
        random.seed(seed)

    # Start with all walls
    grid = [['#' for _ in range(n)] for _ in range(n)]

    # Carve on odd coordinates (0, 2, 4, ...)
    # This ensures walls between carved cells can be broken cleanly.
    def cell_ids():
        return [(r, c) for r in range(1, n, 2) for c in range(1, n, 2)]

    ids = cell_ids()
    if not ids:
        # n < 3: fall back to simple corridor
        for r in range(n):
            for c in range(n):
                grid[r][c] = '.'
        return grid

    start = random.choice(ids)
    grid[start[0]][start[1]] = '.'
    visited = {start}
    stack = [start]
    dirs = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while stack:
        r, c = stack[-1]
        neighbors = []
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if (nr, nc) in ids and (nr, nc) not in visited:
                neighbors.append((nr, nc, dr, dc))
        if not neighbors:
            stack.pop()
            continue
        nr, nc, dr, dc = random.choice(neighbors)
        # Break the wall between (r,c) and (nr,nc)
        grid[r + dr // 2][c + dc // 2] = '.'
        grid[nr][nc] = '.'
        visited.add((nr, nc))
        stack.append((nr, nc))

    # For even n, ensure the last row / col is reachable
    for r in range(n):
        for c in range(n):
            if r == 0 or c == 0 or r == n - 1 or c == n - 1:
                if grid[r][c] == '#' and random.random() < 0.5:
                    # connect to inner cell if possible
                    if r == 0 and r + 1 < n and grid[r + 1][c] == '.':
                        grid[r][c] = '.'
                    elif r == n - 1 and grid[r - 1][c] == '.':
                        grid[r][c] = '.'
                    elif c == 0 and c + 1 < n and grid[r][c + 1] == '.':
                        grid[r][c] = '.'
                    elif c == n - 1 and grid[r][c - 1] == '.':
                        grid[r][c] = '.'
    return grid


def generate_maze(n, T, wall_p=0.20, seed=None):
    """Randomized maze with guaranteed-solvable key/door placement.

    Steps:
      1. Carve a random perfect maze.
      2. Pick S and E from open cells, far apart.
      3. BFS from S to E; if unreachable, retry.
      4. Place T keys and doors along the BFS path in order.
      5. Verify with solve_maze.
    """
    if seed is not None:
        random.seed(seed)
    if 2 * T + 2 > n * n:
        raise ValueError(f"Grid {n}x{n} too small for T={T}.")

    for _ in range(50):
        grid = _carve_maze(n, seed=None)

        opens = [(r, c) for r in range(n) for c in range(n)
                 if grid[r][c] == '.']
        if len(opens) < 2 * T + 2:
            continue

        # Pick S and E far apart
        s = random.choice(opens)
        far = [p for p in opens
               if abs(p[0] - s[0]) + abs(p[1] - s[1]) >= max(3, n)]
        if not far:
            continue
        e = random.choice(far)

        grid[s[0]][s[1]] = 'S'
        grid[e[0]][e[1]] = 'E'

        # Compute a path from S to E via BFS on open cells
        from collections import deque as _dq
        q = _dq([s])
        prev = {s: None}
        while q:
            r, c = q.popleft()
            if (r, c) == e:
                break
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n \
                        and (nr, nc) not in prev \
                        and grid[nr][nc] in '.SE':
                    prev[(nr, nc)] = (r, c)
                    q.append((nr, nc))

        if e not in prev:
            grid[s[0]][s[1]] = '.'
            grid[e[0]][e[1]] = '.'
            continue

        # Reconstruct path
        path = []
        cur = e
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()

        if len(path) < 2 * T + 2:
            grid[s[0]][s[1]] = '.'
            grid[e[0]][e[1]] = '.'
            continue

        interior = path[1:-1]
        positions = sorted(random.sample(range(len(interior)), 2 * T))
        for k in range(T):
            kr, kc = interior[positions[2 * k]]
            dr_, dc_ = interior[positions[2 * k + 1]]
            grid[kr][kc] = chr(ord('a') + k)
            grid[dr_][dc_] = chr(ord('A') + k)

        d, _ = solve_maze(grid)
        if d != -1:
            return grid

    raise RuntimeError("Could not generate a solvable maze. Try a bigger --n.")



def mark_path(grid, path):
    out = [row[:] for row in grid]
    for (r, c) in path:
        if out[r][c] == '.':
            out[r][c] = 'x'
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default=None)
    ap.add_argument('--output', default='maze_path.csv')
    ap.add_argument('--generate', action='store_true')
    ap.add_argument('--n', type=int, default=10)
    ap.add_argument('--t', type=int, default=3)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--wall-p', type=float, default=0.20)
    args = ap.parse_args()

    if args.generate or args.input is None:
        grid = generate_maze(args.n, args.t, wall_p=args.wall_p, seed=args.seed)
        write_grid('maze.csv', grid)
        print(f"Generated {args.n}x{args.n} maze with T={args.t} -> maze.csv")
    else:
        grid = read_grid(args.input)

    d, path = solve_maze(grid)
    print(f"Shortest path length: {d}")
    if d != -1:
        write_grid(args.output, mark_path(grid, path))
        print(f"Marked path saved to {args.output}")


if __name__ == '__main__':
    main()