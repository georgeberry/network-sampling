import networkx as nx

def population(g):
    """
    Gives node and edge counts by group
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

    for edge in g.edges_iter():
        link_counts[
            (g_groups[edge[0]], g_groups[edge[1]])
        ] += 1
    for grp in g_groups.values():
        node_counts[grp] += 1


    return node_counts, link_counts
