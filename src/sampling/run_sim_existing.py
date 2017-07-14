from os import listdir
import networkx as nx
import pandas as pd

# Sampling methods
from sampling_methods import sample_edges, sample_nodes, sample_ego_networks
from sampling_methods import sample_random_walk, sample_snowball, population

# Helpers
from helpers import get_n_samples

#### Params ####################################################################
OUTPUT_FILE = "sim_output/output.tsv"
INPUT_DIR = "/mnt/md0/network_sampling_data/graphs"

# Total number of lines given by:
# Number of graphs * SAMPLES_PER_GRAPH * 
SAMPLES_PER_GRAPH = 100
SAMPLE_SIZE = 1000

#### Run sim ###################################################################
out = list()
dir_len = len(listdir(INPUT_DIR))
for graph_idx, graph_file in enumerate(listdir(INPUT_DIR)):
	g = nx.read_gpickle(INPUT_DIR + '/' + graph_file)
	homophily_pair = g.graph['params'].pop('homophily')
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
			entry.update({'d_' + nodetype: count for nodetype, count in node_counts.items()})
			entry.update({'d_' + linktype[0] + linktype[1]: count for linktype, count in link_counts.items()})
			out.append(entry)
	print("Processed '{}' ({} of {}).".format(graph_file,graph_idx,dir_len))
df = pd.DataFrame(out)
df.to_csv(OUTFILE,sep='\t')
