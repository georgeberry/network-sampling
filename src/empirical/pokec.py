"""
2 files
- an edgelist
- profiles

We want to get a bidirected edgelist
Plus labels for a high-coverage category

Then put them together into one big graph
"""

import pandas as pd
import networkx as nx

base_path = '/mnt/md0/geb97/network-sampling/data/pokec/'
# base_path = '/Users/g/Drive/project-RA/network-sampling/data/pokec/'

edgelist_path = base_path + 'soc-pokec-relationships.txt'
edgelist_output_path = base_path + 'mutual_graph.tsv'
gender_df_path = base_path + 'gender_df.tsv'

#### parse edgelist ############################################################

edge_dict = {}

with open(edgelist_path, 'r') as f:
    for line in f:
        n1, n2 = [int(x) for x in line.strip().split('\t')]
        edge = tuple(sorted((n1, n2)))
        if edge not in edge_dict:
            edge_dict[edge] = 0
        edge_dict[edge] += 1

with open(edgelist_output_path, 'w') as f:
    for edge, count in edge_dict.items():
        if count == 2:
            f.write('{}\t{}\n'.format(edge[0], edge[1]))

#### make graph ################################################################

attr_dict = {}
with open(gender_df_path, 'r') as f:
    next(f) # skip header
    for line in f:
        user_id, gender = line.strip().split('\t')
        gender = int(gender)
        if gender == 1:
            group = 'a'
        else:
            group = 'b'
        attr_dict[int(user_id)] = group

edges = []
with open(edgelist_output_path, 'r') as f:
    for line in f:
        n1, n2 = [int(x) for x in line.strip().split('\t')]
        if n1 in attr_dict and n2 in attr_dict:
            edges.append((n1, n2))

g = nx.Graph()
g.add_edges_from(edges)

attr_dict = {k:v for k, v in attr_dict.items() if k in g}

nx.set_node_attributes(g, 'group', attr_dict)
nx.set_node_attributes(g, 'degree', g.degree())

g.graph['params'] = {
    'num_nodes': g.number_of_nodes(),
    'homophily': [None, None],
    'idx': None,
}

gc = max(nx.connected_component_subgraphs(g), key=len)

nx.write_gpickle(gc, base_path + 'pokec_graph.p')

g = nx.read_gpickle(base_path + 'pokec_graph.p')
