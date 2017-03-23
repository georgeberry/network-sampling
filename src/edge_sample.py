import networkx as nx
import numpy as np
from graph_gen import generate_powerlaw_group_graph


def sample_random_edges(g, seed=None):
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

    g_groups = nx.get_node_attributes(g, 'group')

    edges = g.edges()
    np.random.shuffle(edges)

    for edge in edges:
        n1, n2 = edge
        g1, g2 = g_groups[n1], g_groups[n2]
        link_counts[(g1, g2)] += 1
        node_counts[g1] += 1
        node_counts[g2] += 1

        yield node_counts, link_counts

if __name__ == "__main__":
    g = generate_powerlaw_group_graph(1000, 2, [0.8, 0.8], .5)
    counts = sample_random_edges(g, 200)
    print(counts)
