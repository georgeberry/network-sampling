"""
All sampling methods should be contained in a single function which yields
samples.

Sample functions take

The sampling methods we consider are:
- Edge
- Node
- Ego network
- Random walk
- Snowball
"""

import random
import networkx as nx
import numpy as np
from graph_gen import generate_powerlaw_group_graph

def sample_edges(g):
    """
    Randomly sample edges
    Yield after each edge is added
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
    edges = g.edges()
    np.random.shuffle(edges)
    for edge in edges:
        n1, n2 = edge
        g1, g2 = g.node[n1]['group'], g.node[n2]['group']
        link_counts[(g1, g2)] += 1
        node_counts[g1] += 1
        node_counts[g2] += 1
        yield node_counts, link_counts


def sample_nodes(g):
    """
    Sample random nodes, only add edges if we get both ends

    Yield after each node is added
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
    sampled_nodes = set()
    nodes = list(g.nodes())
    np.random.shuffle(nodes)
    for node in nodes:
        g1 = g.node[node]['group']
        node_counts[g1] += 1
        for potential_neighbor in sampled_nodes:
            if g.has_edge(node, potential_neighbor):
                g2 = g.node[potential_neighbor]['group']
                link_counts[(g1, g2)] += 1
        sampled_nodes.add(node)
        yield node_counts, link_counts


def sample_ego_networks(g):
    """
    Sample ego networks

    Yield after each link is added
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


def sample_random_walk(g):
    """
    Random walk from a single random seed
    Yield after each hop
    """
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
    # random seed
    source = random.choice(g.nodes())
    while True:
        # Pick an edge to follow
        destination = random.choice(g.neighbors(source))
        # Update the list of link counts for the sampled edge
        g1, g2 = g.node[source]['group'], g.node[destination]['group']
        link_counts[(g1, g2)] += 1
        node_counts[g1] += 1 # add only seed to avoid double counting
        source = destination
        yield node_counts, link_counts


def sample_snowball(g, directed=False):
    """
    Snowball out from a random seed
    Keep track of what we've already visited to avoid double counting
    Yield after each edge is added
    """

    # stuff to output
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

    seed = random.choice(g.nodes())

    # algorithm:
    # get neighbors of a focal node
    # add these to frontier nodes
    # add the edges to frontier edges
    # record the values of frontier edges
    # when there are no edges, go to next node

    visited_nodes = set()
    visited_edges = set()

    frontier = set([seed])
    # tally the seed, since we only tally nodes when they're discovered.
    node_counts[g.node[seed]['group']] += 1

    while frontier:
        next_frontier = set()  # the nodes we will discover on this pass
        for node in frontier: # for every newly discovered node
            for neighbor in g.neighbors(node): # for every neighbor
                # if the node is undiscovered, make it discovered
                # tally its group and add it to the frontier
                if neighbor not in visited_nodes:
                    visited_nodes.add(neighbor)
                    node_counts[g.node[neighbor]['group']] += 1
                    next_frontier.add(neighbor)
                # if the edge is undiscovered
                # make it discovered, and tally its type
                # this assumes undirected graph
                if directed:
                    if (node, neighbor) not in visited_edges:
                        visited_edges.add((node, neighbor))
                        link_counts[(g.node[node]['group'],
                                     g.node[neighbor]['group'])] += 1
                elif not directed:
                    if (node, neighbor) not in visited_edges and\
                        (neighbor, node) not in visited_edges:
                        link_counts[(g.node[node]['group'],
                                     g.node[neighbor]['group'])] += 1
                yield node_counts, link_counts
        # all the nodes we just discovered are now the frontier
        frontier = next_frontier

def population(g):
    """
    True values of node and edge counts for a graph
    """
    node_counts = {
        'a': 0,
        'b': 0,
    }
    link_counts = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'a'): 0,
    }
    for n1, n2 in g.edges_iter():
        edge_sorted_by_grp = tuple(sorted([
            g.node[n1]['group'],
            g.node[n2]['group'],
        ]))
        link_counts[edge_sorted_by_grp] += 1
    for idx, attr in g.nodes_iter(data=True):
        node_counts[attr['group']] += 1
    while True:
        yield node_counts, link_counts

# mostly for testing
if __name__ == '__main__':
    g = generate_powerlaw_group_graph(1000, 4, (0.5, 0.5), 0.5)
    sampling_methods = [
        sample_edges(g),
        sample_nodes(g),
        sample_ego_networks(g),
        sample_random_walk(g),
        sample_snowball(g, directed=False),
        sample_snowball(g, directed=True),
        population(g),
    ]
    for _ in range(100):
        for method in sampling_methods:
            print(next(method))
