import networkx as nx
import numpy as np
from graph_gen import generate_powerlaw_group_graph


def sample_random_edges(g, e_sample):
    """
    Randomly sample edges
    """

    link_counts = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
        ('b', 'a'): 0,
    }

    edge_idx_list = list(range(g.number_of_edges()))

    sampled_edges = set(
        np.random.choice(edge_idx_list, size=e_sample, replace=False)
    )

    for idx, edge in enumerate(g.edges_iter()):
        if idx in sampled_edges:
            n1, n2 = edge
            link_counts[(g.node[n1]['group'], g.node[n2]['group'])] += 1

    return link_counts

if __name__ == "__main__":
    g = generate_powerlaw_group_graph(1000, 2, [0.8, 0.8], .5)
    counts = sample_random_edges(g, 200)
    print(counts)
