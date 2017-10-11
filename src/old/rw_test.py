import networkx as nx
import random

"""
DiGraph with nodes 0, 1, 2
Directed eges from
    0 --> 1
    1 --> 0
    0 --> 2
    2 --> 1

Record both node visits & edge traversals
"""

def random_walk(g, steps = 1000):
    current_node = random.choice(g.nodes())

    for _ in range(steps - 1):
        g.node[current_node]['visits'] += 1
        nbrs = g.neighbors(current_node)
        transition_node = random.choice(nbrs)
        g.edge[current_node][transition_node]['traversals'] += 1
        current_node = transition_node

def summarize_jumps(g):
    print(g.node)
    print(g.edge)

#

g = nx.DiGraph()
g.add_edges_from([[0, 1], [1, 0], [0, 2], [2, 1]])

for idx, attr in g.nodes_iter(data=True):
    attr['visits'] = 0

for e1, e2, attr in g.edges_iter(data=True):
    attr['traversals'] = 0

random_walk(g)
summarize_jumps(g)

#

g = nx.Graph()
g.add_edges_from([[0, 1], [1, 2], [0, 2], [2, 3], [3, 4], [4,5]])

for idx, attr in g.nodes_iter(data=True):
    attr['visits'] = 0

for e1, e2, attr in g.edges_iter(data=True):
    attr['traversals'] = 0

random_walk(g, steps=10000)
summarize_jumps(g)
