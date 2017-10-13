"""
2 files
- an edgelist
- profiles
"""

edgelist_path = '/mnt/md0/geb97/network-sampling/data/pokec/soc-pokec-relationships.txt'
edgelist_output_path = '/mnt/md0/geb97/network-sampling/data/pokec/mutual_graph.tsv'

edge_dict = {}

with open(edgelist_path, 'r') as f:
    for line in f:
        n1, n2 = line.split('\t')
        edge = tuple(sorted((n1, n2)))
        if edge not in edge_dict:
            edge_dict[edge] = 0
        edge_dict[edge] += 1

with open(edgelist_output_path, 'w') as f:
    for edge, count in edge_dict.items():
        if count == 2:
            f.write('{}\t{}\n'.format(edge[0], edge[1]))
