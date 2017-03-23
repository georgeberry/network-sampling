import networkx as nx
import numpy as np
from graph_gen import generate_powerlaw_group_graph


def sample_random_nodes(g, seed=None):
    """
    This function samples nodes and computes the within- and cross-group links
    Note that we assume that we don't see the group at the other end of a link
        unless we visit that node as well

    So we only obtain a measurement (e.g. a-a, a-b, etc.) if we sample nodes
        at both ends
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

    sampled_nodes = set()
    nodes = list(g.nodes())
    np.random.shuffle(nodes)

    for node in nodes:
        for potential_neighbor in sampled_nodes:
            if g.has_edge(node, potential_neighbor):
                g1, g2 = g_groups[node], g_groups[potential_neighbor]
                link_counts[(g1, g2)] += 1
        node_counts[g_groups[node]] += 1
        sampled_nodes.add(node)

        yield node_counts, link_counts


def sample_ego_networks(g, seed=None):
    """
    Sample ego networks, assume that we see the identity of people on the other
        end
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

    nodes = list(g.nodes())
    np.random.shuffle(nodes)

    for ego in nodes:
        s = nx.ego_graph(g, ego)
        ego_group = s.node[ego]['group']
        node_counts[ego_group] += 1
        s.remove_node(ego)
        for alter, attr in s.nodes_iter(data=True):
            alter_group = attr['group']
            link_counts[ego_group, alter_group] += 1
            node_counts[alter_group] += 1

        yield node_counts, link_counts

if __name__ == "__main__":
    g = generate_powerlaw_group_graph(1000, 2, [0.8, 0.8], .5)
    counts = sample_random_nodes(g, 200)
    print(counts)
    counts = sample_ego_networks(g, 20)
    print(counts)
