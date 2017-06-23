import random
import networkx as nx
from graph_gen import generate_powerlaw_group_graph

def sample_random_walk(
    g, # Graph to sample from
    seed=None):

    sampled_nodes = []
    sampled_edges = []

    node_counts = {
        'a': 0,
        'b': 0,
    }

    link_counts = {
        ('a','a') : 0,
        ('a','b') : 0,
        ('b','b') : 0,
        ('b','a') : 0,
    }

    g_groups = nx.get_node_attributes(g,'group')

    """
    Sample the initial set of seed nodes.
    Right now this is being done with replacement,
    is that okay?
    """

    if not seed:
        seed = random.choice(g.nodes())
    node = seed

    while list(g[node]):
        # Pick an edge to follow
        next_node = random.choice(list(g[node]))

        # Update the list of link counts for the sampled edge
        g1, g2 = g_groups[node], g_groups[next_node]
        link_counts[(g1, g2)] += 1
        node_counts[g1] += 1 # only add one of the nodes

        node = next_node

        yield node_counts, link_counts


if __name__ == "__main__":
    import sample
    g = generate_powerlaw_group_graph(1000, 2, [0.8,0.8], .5)
    counts = sample.sample_at(sample_random_walk, g, n_edges=[200,400])
    print(counts)
