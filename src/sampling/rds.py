import random
import networkx as nx
import numpy as np
from graph_gen import generate_powerlaw_group_graph
from graph_gen import generate_powerlaw_group_digraph
from sampling_methods import population

"""
Record data for rds analysis

"""

### statistic functions
"""
node statistics accept (g, node)
edge statistics accept (g, source, destination)

these must return a number
"""

def node_statistic_group_a(g, node):
    """
    Source group
    """
    if g.node[node]['group'] == 'a':
        return 1
    return 0

def node_statistic_degree(g, node):
    """
    Source degree
    """
    return g.degree(node)

### sample function

def sample_rds(g, n, node_statistic):
    """
    Does a single chain starting from a random seed
    If you want multiple chains, run this multiple times

    Inputs:
        g: graph
        n: number of nodes to sample
        node_statistic: a function of a node to compute, takes (g, node)
    Outputs:
        node_statistic_list
        degree_list
    """
    node_statistic_list = []
    degree_list = []

    # random seed
    source = random.choice(g.nodes())
    degree_list.append(g.degree(source))
    node_statistic_list.append(node_statistic(g, source))

    while len(degree_list) < n:
        # Pick an edge to follow
        destination = random.choice(g.neighbors(source))
        # add data here
        # do this for destination node
        degree_list.append(g.degree(destination))
        node_statistic_list.append(node_statistic(g, destination))
        # update
        source = destination
    deg_arr = np.array(degree_list)
    node_stat_arr = np.array(node_statistic_list)
    return deg_arr, node_stat_arr

def normalize_rds_sample(deg_arr, stat_arr):
    """
    Inputs:
        deg_arr: vector of degrees
        stat_arr: vector of measurements
    Outputs:
        p_hat = 1 / (sum (1 / d_i)) * sum (statistic / d_i)
            aka the RDS estimate of p
    """
    left_hand = 1 / np.sum(1 / deg_arr)
    right_hand = np.sum(stat_arr / deg_arr)
    return left_hand * right_hand

def sample_rds_directed(g, n, node_statistic):
    """
    Does a single chain starting from a random seed
    If you want multiple chains, run this multiple times

    Inputs:
        g: graph
        n: number of nodes to sample
        node_statistic: a function of a node to compute, takes (g, node)
    Outputs:
        node_statistic_list
        degree_list
    """
    node_statistic_list = []
    degree_list = []

    # random seed
    source = random.choice(g.nodes())
    degree_list.append(g.degree(source))
    node_statistic_list.append(node_statistic(g, source))

    # choose an inlink or outlink w equal probability
    while len(degree_list) < n:
        # Pick an edge to follow
        # So if we can jump either way, RDS works
        successors = g.successors(source)
        predecessors = g.predecessors(source)
        destination = random.choice(successors + predecessors)

        # destination = random.choice(g.neighbors(source))
        # add data here
        # do this for destination node
        degree_list.append(g.degree(destination))
        node_statistic_list.append(node_statistic(g, destination))
        # update
        source = destination
    deg_arr = np.array(degree_list)
    node_stat_arr = np.array(node_statistic_list)
    return deg_arr, node_stat_arr


def sample_rds_directed(g, n, node_statistic):
    """
    Does a single chain starting from a random seed
    If you want multiple chains, run this multiple times

    Inputs:
        g: graph
        n: number of nodes to sample
        node_statistic: a function of a node to compute, takes (g, node)
    Outputs:
        node_statistic_list
        degree_list
    """
    node_statistic_list = []
    degree_list = []

    # random seed
    source = random.choice(g.nodes())
    degree_list.append(g.degree(source))
    node_statistic_list.append(node_statistic(g, source))

    # choose an inlink or outlink w equal probability
    while len(degree_list) < n:
        # Pick an edge to follow
        # So if we can jump either way, RDS works
        successors = g.successors(source)
        predecessors = g.predecessors(source)
        destination = random.choice(successors + predecessors)

        # destination = random.choice(g.neighbors(source))
        # add data here
        # do this for destination node
        degree_list.append(g.degree(destination))
        node_statistic_list.append(node_statistic(g, destination))
        # update
        source = destination
    deg_arr = np.array(degree_list)
    node_stat_arr = np.array(node_statistic_list)
    return deg_arr, node_stat_arr


if __name__ == '__main__':
    g = generate_powerlaw_group_graph(1000, 4, (0.8, 0.8), 0.5)
    deg_arr, node_stat_arr = sample_rds(g, 200, node_statistic_degree)
    print(np.mean(deg_arr))
    print(normalize_rds_sample(deg_arr, node_stat_arr))

    g = generate_powerlaw_group_digraph(1000, 4, (0.8, 0.8), 0.5)
    deg_arr, node_stat_arr = sample_rds_directed(g, 200, node_statistic_degree)
    print(np.mean(deg_arr))
    print(normalize_rds_sample(deg_arr, node_stat_arr))
    """
    print(next(population(g)))
    print(deg_arr)
    print(node_stat_arr)
    print(weight_rds(deg_arr, node_stat_arr))
    print(next(population(g)))
    """
