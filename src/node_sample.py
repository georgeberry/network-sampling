import networkx as nx
import numpy as np
from graph_gen import generate_powerlaw_group_graph


def sample_random_nodes(g, n_sample):
    """
    This function samples nodes and computes the within- and cross-group links
    Note that we assume that we don't see the group at the other end of a link
        unless we visit that node as well

    So we only obtain a measurement (e.g. a-a, a-b, etc.) if we sample nodes
        at both ends
    """
    link_counts = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
        ('b', 'a'): 0,
    }

    node_list = list(range(g.number_of_nodes()))
    sampled_nodes = np.random.choice(node_list, size=n_sample, replace=False)

    s = g.subgraph(sampled_nodes) # s for subgraph

    for n1, n2 in s.edges_iter():
        link_counts[(s.node[n1]['group'], s.node[n2]['group'])] += 1

    return link_counts

def sample_ego_networks(g, n_sample):
    """
    Sample ego networks, assume that we see the identity of people on the other
        end
    """
    link_counts = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
        ('b', 'a'): 0,
    }

    node_list = list(range(g.number_of_nodes()))
    sampled_nodes = np.random.choice(node_list, size=n_sample, replace=False)

    for ego in sampled_nodes:
        s = nx.ego_graph(g, ego)
        ego_group = s.node[ego]['group']
        s.remove_node(ego)
        for alter, attr in s.nodes_iter(data=True):
            alter_group = attr['group']
            link_counts[ego_group, alter_group] += 1

    return link_counts


if __name__ == "__main__":
    g = generate_powerlaw_group_graph(1000, 2, [0.8, 0.8], .5)
    counts = sample_random_nodes(g, 200)
    print(counts)
    counts = sample_ego_networks(g, 20)
    print(counts)
