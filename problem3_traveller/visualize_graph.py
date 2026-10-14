import argparse
import csv
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def load_graph(path):
    edges = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            edges.append((int(row['u']), int(row['v']), int(row['price']),
                          row.get('on_path', ''), row.get('coupon', '')))
    return edges


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default='graph_path.csv')
    args = ap.parse_args()
    edges = load_graph(args.input)

    G = nx.DiGraph()
    for u, v, p, on, cp in edges:
        G.add_edge(u, v, price=p, on=(on == 'x'), coupon=(cp == 'x'))

    # Layout
    pos = nx.spring_layout(G, seed=42)

    fig, ax = plt.subplots(figsize=(11, 8))
    node_colors = []
    for n in G.nodes():
        if n == 1:
            node_colors.append('limegreen')
        elif n == max(G.nodes()):
            node_colors.append('red')
        else:
            node_colors.append('orange')

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=700)
    nx.draw_networkx_labels(G, pos, ax=ax, font_color='black')
    edge_labels = {(u, v): f"{d['price']}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', arrows=True,
                           connectionstyle='arc3,rad=0.05')
    nx.draw_networkx_edge_labels(G, pos, ax=ax, edge_labels=edge_labels, font_size=8)

    # animated path
    path = [(u, v) for u, v, d in G.edges(data=True) if d['on']]
    cost_text = ax.text(0.02, 0.98, "", transform=ax.transAxes, fontsize=12,
                        va='top', family='monospace')

    def update(i):
        for line in list(ax.lines):
            line.remove()
        spent = 0
        stops = 0
        txt = "Journey\n"
        for k in range(i + 1):
            u, v = path[k]
            ax.annotate("", xy=pos[v], xytext=pos[u],
                        arrowprops=dict(arrowstyle='->', color='gold', lw=3))
            p = G[u][v]['price']
            if G[u][v]['coupon']:
                spent += p // 2
                txt += f"{u}->{v}  {p} -> {p // 2} (coupon)\n"
            else:
                spent += p
                txt += f"{u}->{v}  {p}\n"
            stops += 1
        txt += f"Cost so far: {spent}   Stops: {stops - 1}"
        cost_text.set_text(txt)
        return []

    if not path:
        ax.set_title("No feasible path")
        plt.show()
        return

    ani = animation.FuncAnimation(fig, update, frames=len(path), interval=900, blit=False)
    ax.set_title("Budget traveller path (gold = chosen, couponed edges)")
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()