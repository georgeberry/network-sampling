"""
Adapted from Karimi et al. (2017), "Visibility of Minorities in Social Networks"

Code from that paper is here:
    https://github.com/frbkrm/HomophilicNtwMinorities/
    blob/master/generate_homophilic_graph_symmetric.py

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

TODO:
- We have a cold-start problem to solve: the _random_subset function can
    loop forever early on because there are not enough unique nodes
    of a certain type to link to. For instance, if there is perfect homophily
    and there are 4 members of group A, but each member of A has 8 links,
    this function will run forever.

    Solution: if there are < m nodes from a given group,
"""

import copy
import math
import random
from collections import Counter
import numpy as np
import networkx as nx
# import matplotlib.pyplot as plt

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

def _gen_groups(n, n_a):
    """
    Pull all the random numbers at once and store in generator
    Much faster
    """
    groups = ['a' if x < n_a else 'b' for x in range(n)]
    random.shuffle(groups)
    return groups

def _pick_targets(G, h_prob, target_list, source, m):
    src_grp = G.node[source]['group']

    target_prob_dict = {}

    for target in target_list:
        tgt_grp = G.node[target]['group']
        # Fudge factor here fixes the cold start problem
        target_prob = h_prob[(src_grp, tgt_grp)] * (0.00001 + G.degree(target))
        target_prob_dict[target] = target_prob

    # targets is the thing we will return
    # it stores the outlinks from source
    targets = set()
    search_count = 0

    rand_numbers = np.random.uniform(size=m)
    while len(targets) < m:
        rand_num = rand_numbers[search_count]

        # Need to update this every time
        prob_sum = sum(target_prob_dict.values())
        if prob_sum == 0:
            return targets

        cumsum = 0.0
        for tgt_idx, prob in target_prob_dict.items():
            cumsum += (prob / prob_sum)
            # If the random number is in the interval, we store it in targets
            # and remove it from target_prob_dict so it's not eligible for
            # a double link
            if rand_num < cumsum:
                targets.add(tgt_idx)
                del target_prob_dict[tgt_idx]
                break

        # we need m links and have gone through the process m times with no luck
        # this means there is nothing to link to, so we stop the iteration
        search_count += 1
        if search_count > m:
            break

    return targets


def generate_powerlaw_group_graph(
        n, # number of nodes
        m, # mean degree
        h, # two-vector of homophily
        f, # probability of majority group
):
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
    2. Add m nodes in each group
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
    # Unpack homophily values
    h_prob = {
        ('a', 'a'): h[0],
        ('a', 'b'): 1 - h[0],
        ('b', 'b'): h[1],
        ('b', 'a'): 1 - h[1],
    }

    # Get number majority nodes
    n_a = int(f * n)

    # See template algorithm here: https://networkx.readthedocs.io/en/stable/
    # _modules/networkx/generators/random_graphs.html#barabasi_albert_graph
    G = nx.Graph()

    # We're going to create all the nodes first, then do link generation
    # Note that we shuffle the indicies
    G.add_nodes_from(
        [(idx, {'group': grp}) for idx, grp in enumerate(_gen_groups(n, n_a))]
    )
    G.name = "powerlaw_group_graph({},{})".format(n,m)

    # Seed nodes, we will weight by probability below
    source = m
    target_list = list(range(m))

    while source < n:
        targets = _pick_targets(G, h_prob, target_list, source, m)

        if len(targets) > 0:
            G.add_edges_from(zip([source]*m, targets))

        # Admit source to be linked to
        target_list.append(source)

        # Increment
        source += 1
    return G



def generate_powerlaw_group_digraph(
        n, # number of nodes
        m, # mean degree
        h, # two-vector of homophily
        f, # probability of majority group
):
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
    2. Add m nodes in each group
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
    # Unpack homophily values
    h_prob = {
        ('a', 'a'): h[0],
        ('a', 'b'): 1 - h[0],
        ('b', 'b'): h[1],
        ('b', 'a'): 1 - h[1],
    }

    # Get number majority nodes
    n_a = int(f * n)

    # See template algorithm here: https://networkx.readthedocs.io/en/stable/
    # _modules/networkx/generators/random_graphs.html#barabasi_albert_graph
    G = nx.DiGraph()

    # We're going to create all the nodes first, then do link generation
    # Note that we shuffle the indicies
    G.add_nodes_from(
        [(idx, {'group': grp}) for idx, grp in enumerate(_gen_groups(n, n_a))]
    )
    G.name = "powerlaw_group_graph({},{})".format(n,m)

    # Seed nodes, we will weight by probability below
    source = m
    target_list = list(range(m))

    # add outlinks from each of the first m nodes to each other
    seed_set = set(list(range(m)))
    for seed_node_idx in seed_set:
        seed_alter_set = seed_set - {seed_node_idx}
        for seed_alter_idx in seed_alter_set:
            G.add_edge(seed_node_idx, seed_alter_idx)

    while source < n:
        targets = _pick_targets(G, h_prob, target_list, source, m)

        if len(targets) > 0:
            G.add_edges_from(zip([source]*m, targets))

        # Admit source to be linked to
        target_list.append(source)

        # Increment
        source += 1
    return G

'''
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
'''

if __name__ == '__main__':
    import pickle
    import itertools
    OUTPUT_PATH = '../../sim_output/graphs/'

    num_nodes = [10000]
    mean_degs = [2, 4]
    homophily_vals = [
        (0.0, 0.0),
        (0.2, 0.2),
        (0.5, 0.5),
        (0.8, 0.8),
        (1.0, 1.0),
    ]
    majority_group_sizes = [0.5, 0.65, 0.8]

    prod = itertools.product(
        num_nodes,
        mean_degs,
        homophily_vals,
        majority_group_sizes
    )
    for v, m, h, f in prod:
        for idx in range(1):
            str_param_list = [str(x) for x in [v,m,*h,f]]
            path = OUTPUT_PATH + '|'.join(str_param_list) + '_{}'.format(idx) + '.p'
            g = generate_powerlaw_group_graph(v, m, h, f)
            nx.write_gpickle(g, path)
