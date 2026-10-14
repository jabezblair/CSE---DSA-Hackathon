import argparse
import matplotlib.pyplot as plt
import networkx as nx
from timetable import (
    greedy_dsatur, exact_coloring, generate_graph, timetable_from_colors
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=12)
    ap.add_argument('--r', type=int, default=3)
    ap.add_argument('--density', type=float, default=0.25)
    ap.add_argument('--seed', type=int, default=5)
    args = ap.parse_args()

    N, R = args.n, args.r
    adj = generate_graph(N, args.density, args.seed)
    g_color, g_slots = greedy_dsatur(N, adj, R)
    e_color, e_slots, _ = exact_coloring(
        N, adj, R, greedy_color=g_color, greedy_slots=g_slots)

    palette = plt.get_cmap('tab10').colors

    # --- conflict graph, nodes coloured by slot ---
    G = nx.Graph()
    G.add_nodes_from(range(1, N + 1))
    for i in range(N):
        for j in adj[i]:
            if i < j:
                G.add_edge(i + 1, j + 1)
    pos = nx.spring_layout(G, seed=1)
    node_colors = [palette[e_color[i] % 10] for i in range(N)]

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    nx.draw_networkx(G, pos, ax=axes[0], node_color=node_colors,
                     node_size=600, with_labels=True)
    axes[0].set_title(f"Conflict graph, slots = {e_slots}")
    axes[0].axis('off')

    # --- timetable grid ---
    slots = timetable_from_colors(e_color, N)
    ax = axes[1]
    ax.set_xlim(0, R)
    ax.set_ylim(0, e_slots)
    ax.set_xticks(range(R + 1))
    ax.set_yticks(range(e_slots + 1))
    ax.invert_yaxis()
    ax.set_xlabel('Hall')
    ax.set_ylabel('Slot')
    for s in sorted(slots):
        courses = sorted(slots[s])
        colour = palette[s % 10]
        for k in range(R):
            rect = plt.Rectangle((k, s), 1, 1,
                                 facecolor='white', edgecolor='black')
            ax.add_patch(rect)
            if k < len(courses):
                ax.text(k + 0.5, s + 0.55, str(courses[k]),
                        ha='center', va='center', fontsize=11)
                rect.set_facecolor(colour)
    ax.set_title(f"Timetable ({e_slots} slots)")
    ax.set_aspect('equal')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()