import networkx as nx
import numpy as np
from graph_gen import generate_powerlaw_group_graph


def sample_random_edges(g, e_sample):
    """
    Randomly sample edges
    """
    node_counts = {
        'a': 0,
        'b': 0,
    }

    link_counts = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
        ('b', 'a'): 0,
    }

    g_groups = nx.get_node_attributes(g,'group')
    edge_idx_list = list(range(g.number_of_edges()))

    if e_sample >= len(edge_idx_list):
        sampled_edges = set(edge_idx_list)
    else:
        sampled_edges = set(
            np.random.choice(edge_idx_list, size=e_sample, replace=False)
        )

    for idx, edge in enumerate(g.edges_iter()):
        if idx in sampled_edges:
            n1, n2 = edge
            g1, g2 = g_groups[n1], g_groups[n2]
            link_counts[(g1, g2)] += 1
            node_counts[g1] += 1
            node_counts[g2] += 1

    return node_counts, link_counts

if __name__ == "__main__":
    g = generate_powerlaw_group_graph(1000, 2, [0.8, 0.8], .5)
    counts = sample_random_edges(g, 200)
    print(counts)
