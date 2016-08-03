from matplotlib import pyplot as plt
import networkx as nx

from svggen.api.ports import all_ports

if __name__ == '__main__':

    G = nx.DiGraph()

    labels = {idx: port.__name__ for idx, port in enumerate(all_ports)}

    for idx1, port1 in enumerate(all_ports):
        for idx2, port2 in enumerate(all_ports):
            if port1(None).canMate(port2(None)):
                G.add_edge(idx1, idx2)

    nx.draw(
        G,
        pos=nx.spring_layout(G, k=0.5),
        with_labels=True,
        labels=labels,
        font_color='orange',
        font_weight='bold',
    )

    plt.show()

