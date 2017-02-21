"""
Adapted from Karimi et al. (2017), "Visibility of Minorities in Social Networks"

For each of f_a is the fraction in group a, 1 - f_a is in group b
By convention, f_a is the majority
Each node attaches to m existing nodes in proportion to
    - Degree
    - Group
By convention, multiple links are disallowed

p(j connects to i) = h_ij k_i / sum_l (h_lj k_l)

k_i is the degree of node i
h_ij is the homophily parameter for a connection between i and j based on group

There are two homophily parameters in this model, h_ii and h_jj
Note that since there are only two groups complements follow, (1 - h_ii, 1 - h_jj)

We can simplify to a single homophily parameter (h = h_ii = h_jj)

"""

import random
import numpy as np
import networkx as nx

def _random_subset(seq, m):
    """
    Taken from the NetworkX codebase
    https://networkx.readthedocs.io/en/stable/
    _modules/networkx/generators/random_graphs.html

    Return m unique elements from seq.

    This differs from random.sample which can return repeated
    elements if seq holds repeated elements.
    """
    targets = set()
    while len(targets) < m:
        x = random.choice(seq)
        targets.add(x)
    return targets

def _gen_groups(n, f_a):
    """
    Fast random groups
    """
    for rand in np.random.uniform(size=n):
        if rand < f_a:
            yield 'a'
        else:
            yield 'b'

def generate_powerlaw_group_graph(
        n, # number of nodes
        m, # mean degree
        h, # two-vector of homophily
        f): # two-vector of class fractions
    """

    Pretty simple algo:


    Store two lists of repeated_nodes, one for each group
    The tricky part is that they need to be weighed by the h_a and h_b numbers
    Assume that h_a = .7, then all a-nodes must be weighted by .7 / .3 while
        all b-nodes must be weighted by .3 / .7
    Seems like simplest way to do this would be to add any a-node to r_a
        7 times while adding a b-node to r_a 3 times
    Can simply give people a warning that we're multiplying by 10
    10x memory hit during graph creation isn't the end of the world
    """
    h_aa, h_bb = [10 * x for x in h]
    h_ab, h_ba = [10 * (1 - x) for x in h]
    f_a, f_b = f
    grps_itr = _gen_groups(n, f_a)
    # Assertions
    assert n > 0
    assert m > 0
    assert h_aa % 1 == h_bb % 1 == 0
    assert (10 >= h_aa >= 0) and (10 >= h_bb >= 0)
    assert (f_a + f_b == 1) and (1 > f_a > 0) and (1 > f_b > 0)
    # This has to come after assertions to avoid truncating floats to ints
    h_aa, h_bb = int(h_aa), int(h_bb)
    h_ab, h_ba = int(h_ab), int(h_ba)
    # Create graph with seed nodes
    # See template here: https://networkx.readthedocs.io/en/stable/
    # _modules/networkx/generators/random_graphs.html#barabasi_albert_graph
    G = nx.Graph()
    G.add_nodes_from([(x, {'group': next(grps_itr)}) for x in range(m)])
    G.name = "powerlaw_group_graph({},{})".format(n,m)
    # Hold differently weighted targets for each group
    repeated_nodes_a, repeated_nodes_b = [], []
    # Index by source
    source = m
    while source < n:
        # Choose group for new node
        source_grp = next(grps_itr)
        G.add_node(source, group=source_grp)
        # Generate targets based on group identity
        if G.number_of_edges() == 0:
            # initialize uniform links
            targets = list(range(m))
        else:
            if source_grp == 'a':
                targets = _random_subset(repeated_nodes_a, m)
            else:
                targets = _random_subset(repeated_nodes_b, m)
        # Add edges specified in targets
        G.add_edges_from(zip([source]*m, targets))
        # Get groups of nodes in targets: (node, group)
        targets_grps = [(x, G.node[x]['group']) for x in targets]
        # Add the destination nodes to repeated nodes
        for node, target_grp in targets_grps:
            if target_grp == 'a':
                repeated_nodes_a.extend([node]*h_aa)
                repeated_nodes_b.extend([node]*h_ba)
            else:
                repeated_nodes_a.extend([node]*h_ab)
                repeated_nodes_b.extend([node]*h_bb)
        # Add the source node to repeated nodes
        if source_grp == 'a':
            repeated_nodes_a.extend([source]*h_aa*m)
            repeated_nodes_b.extend([source]*h_ba*m)
        else:
            repeated_nodes_a.extend([source]*h_ab*m)
            repeated_nodes_b.extend([source]*h_bb*m)
        # Increment
        source += 1
    return G

if __name__ == '__main__':
    g = generate_powerlaw_group_graph(10000, 8, [.6, .4], [.8, .2])
