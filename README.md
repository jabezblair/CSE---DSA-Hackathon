\# CSE Hackathon — Data Structures and Algorithms



\*\*Department of Computer Science and Engineering\*\*

\*\*CMRIT, Bangalore — 14-OCT-2026\*\*



\## Problems Solved



| # | Problem | Algorithm | Language |

|---|---|---|---|

| 1 | Maze with Keys and Doors | BFS over `(row, col, key\_mask)` | Python |

| 2 | Closest Pair of Points | Brute force + Divide \& Conquer | Python + Java |

| 3 | Budget Traveller with Coupons | Dijkstra on `(city, hops, coupons)` | Python |

| 4 | Exam Timetable Scheduling | DSatur + backtracking | Python + Java |



\## Requirements



\- Python 3.11+

\- `pip install matplotlib networkx numpy pandas pygame`

\- Java JDK 17+ (for `ClosestPair.java`, `Timetable.java`)



\## Quick Start



```bash

\# Problem 1 — Maze

cd problem1\_maze

python maze\_solver.py --generate --n 10 --t 3

python visualize\_maze.py --input maze.csv



\# Problem 2 — Closest Pair

cd ../problem2\_closest\_pair

python closest\_pair.py --n 300 --seed 7 --float

python visualize\_closest.py --csv points.csv



\# Problem 3 — Budget Traveller

cd ../problem3\_traveller

python budget\_traveller.py --generate --n 8 --m 14 --k 3 --c 2

python visualize\_graph.py --input graph\_path.csv



\# Problem 4 — Timetable

cd ../problem4\_timetable

python timetable.py --n 12 --r 3 --density 0.25

python visualize\_timetable.py --n 12 --r 3 --density 0.25

