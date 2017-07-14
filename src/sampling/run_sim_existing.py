import networkx as nx
import pandas as pd
import pickle
import sys, os

# Sampling methods
from sampling_methods import sample_edges, sample_nodes, sample_ego_networks
from sampling_methods import sample_random_walk, sample_snowball, population

# Helpers
from helpers import get_n_samples

#### Params ####################################################################
INPUT_FILE = sys.argv[1]

OUTPUT_DIR = "/mnt/md0/network_sampling_data/sim_output/"
OUTPUT_FILE = OUTPUT_DIR + os.path.split(INPUT_FILE)[1]
print(OUTPUT_FILE)

# Total number of lines given by:
# Number of graphs * SAMPLES_PER_GRAPH *
SAMPLES_PER_GRAPH = 100
SAMPLE_SIZE = 1000

#### Run sim ###################################################################
output_list = list()

g = nx.read_gpickle(INPUT_FILE)
homophily_pair = g.graph['params']['homophily']
g.graph['params'].update({
	'h_a': homophily_pair[0],
	'h_b': homophily_pair[1],
})
for samp_idx in range(SAMPLES_PER_GRAPH):
	sampling_methods = {
		'sample_edges': sample_edges(g),
		'sample_nodes': sample_nodes(g),
		'sample_ego_networks': sample_ego_networks(g),
		'sample_random_walk': sample_random_walk(g),
		'sample_snowball': sample_snowball(g),
		'population': population(g),
	}
	for method, fn in sampling_methods.items():
		node_counts, link_counts = get_n_samples(fn, n=SAMPLE_SIZE)
		entry = {
			'graph_idx': graph_idx,
			'samp_idx': samp_idx,
			'samp_size': SAMPLE_SIZE,
			'method': method,
		}
		# Included in g.graph['params']:
		# num_nodes, mean_degree, h_a, h_b, majority_size, idx
		entry.update(g.graph['params'])
		entry.update(
			{'d_' + nodetype: count for nodetype, count in node_counts.items()}
		)
		entry.update(
			{'d_' + linktype[0] + linktype[1]: count for linktype, count in link_counts.items()}
		)
		output_list.append(entry)
print("Processed '{}' ({} of {}).".format(graph_file,graph_idx,dir_len))

with open(OUTPUT_FILE, 'wb') as f:
	pickle.dump(output_list, f)
