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

import math
import random
from collections import Counter
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

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
    Pull all the random numbers at once and store in generator
    Much faster
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
    Logic:

    Store two lists of repeated_nodes, one for each group
    The tricky part is that they need to be weighed by the h_a and h_b numbers
    Assume that h_a = .7, then all a-nodes must be weighted by .7 / .3 while
        all b-nodes must be weighted by .3 / .7
    Seems like simplest way to do this would be to add any a-node to r_a
        7 times while adding a b-node to r_a 3 times
    Can simply give people a warning that we're multiplying by 10
    10x memory hit during graph creation isn't the end of the world

    Algo:

    1. Initialize empty graph
    2. Add m nodes with random groups
    3. Create node with a random group and attach its links at random to the m
        seed nodes
    4. Add all nodes to the repeated_nodes_a and repeated_nodes_b lists
    5. Then, while the number of nodes less than n
        5a. Create a new node
        5b. Give it a random group
        5c. Choose m targets from the repeated_nodes_a or repeated_nodes_b lists
            based on group
        5d. Add edges from source to targets
        5e. Depending on groups of target nodes, add to repeated_nodes_a or
            repeated_nodes_b
        5f. Add source node to repeated_nodes_a and repeated_nodes_b
        5g. Increment source


    TODO:
    - clean up assertions
    - reduce number of parameters?
    - clean up while loop (explicit init?)


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


def group_log_log_plots(g):
    """
    Pass this a graph, generates log log plots for groups separately
        y axis: log(p(degree | group))
        x axis: log(degree | group)
    """
    a_nodes = set([x for x, y in g.node.items() if y['group'] == 'a'])
    # node: deg
    degrees = nx.degree(g)

    a_deg_seq = {k: v for k, v in degrees.items() if k in a_nodes}
    b_deg_seq = {k: v for k, v in degrees.items() if k not in a_nodes}
    a_size = len(a_deg_seq)
    b_size = len(b_deg_seq)

    a_counts = [
        (deg, count / a_size) for (deg, count) in
        Counter(a_deg_seq.values()).items()
    ]
    b_counts = [
        (deg, count / b_size) for (deg, count) in
        Counter(b_deg_seq.values()).items()
    ]

    a_deg = [x[0] for x in a_counts]
    a_prob = [x[1] for x in a_counts]
    b_deg = [x[0] for x in b_counts]
    b_prob = [x[1] for x in b_counts]

    plt.yscale('log')
    plt.xscale('log')
    plt.scatter(a_deg, a_prob, color='b', marker='o')
    plt.scatter(b_deg, b_prob, color='r', marker='s')

    plt.xlabel('Log10 degree')
    plt.ylabel('Log10 probability')
    plt.show()

if __name__ == '__main__':
    # error with this one
    # g = generate_powerlaw_group_graph(1000, 8, [1.0, 0.0], [.8, .2])
    # group_log_log_plots(g)

    """
    g = generate_powerlaw_group_graph(1000, 8, [0.8, 0.2], [.8, .2])
    group_log_log_plots(g)
    """
    g = generate_powerlaw_group_graph(1000, 8, [0.5, 0.5], [.8, .2])
    group_log_log_plots(g)
    """
    g = generate_powerlaw_group_graph(1000, 8, [0.2, 0.8], [.8, .2])
    group_log_log_plots(g)
    """

    # g = generate_powerlaw_group_graph(1000, 8, [0.0, 1.0], [.8, .2])
    # group_log_log_plots(g)
