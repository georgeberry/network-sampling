import networkx as nx
import pandas as pd
import pickle
import sys, os

"""
find /mnt/md0/network_sampling_data/graphs -type f | parallel python run_sim_existing_degreedist.py
"""

# Sampling methods
from rds import sample_edges, sample_nodes, sample_ego_networks
from rds import sample_rds, sample_snowball, population
from rds import sample_rds

from rds import top_20pct, top_20pct_true
from rds import node_statistic_grp_deg
#### Params ####################################################################
INPUT_FILE = sys.argv[1]
print("Starting.")

OUTPUT_DIR = "/mnt/md0/network_sampling_data/sim_output_dd/"
OUTPUT_FILE = OUTPUT_DIR + os.path.split(INPUT_FILE)[1]

# Total number of lines given by:
# Number of graphs * SAMPLES_PER_GRAPH *
SAMPLES_PER_GRAPH = 100
SAMPLE_SIZE = 1000

#### Run sim ###################################################################
output_list = list()

g = nx.read_gpickle(INPUT_FILE)
homophily_pair = g.graph['params'].pop('homophily')
g.graph['params'].update({
	'h_a': homophily_pair[0],
	'h_b': homophily_pair[1],
})
graph_idx = g.graph['params'].pop('idx')

true_20pct = top_20pct_true(g)
true_prob_a = true_20pct['a']/true_20pct.sum()
true_prob_b = true_20pct['b']/true_20pct.sum()

for samp_idx in range(SAMPLES_PER_GRAPH):
	sampling_methods = {
		'sample_edges':sample_edges,
		'sample_nodes':sample_nodes,
		'sample_ego_networks':sample_ego_networks,
		'sample_rds': sample_rds,
		'sample_snowball':sample_snowball
	}
	for method, fn in sampling_methods.items():
		df = fn(g, SAMPLE_SIZE, node_statistic_grp_deg)
		measure_20pct = top_20pct(df)
		measure_prob_a = measure_20pct['a']/measure_20pct.sum()
		measure_prob_b = measure_20pct['b']/measure_20pct.sum()

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
			{
				'true_prob_a': true_prob_a,
				'true_prob_b': true_prob_b,
				'prob_a': measure_prob_a,
				'prob_b': measure_prob_b,
				'err_prob_a': measure_prob_a - true_prob_a,
				'err_prob_b': measure_prob_b - true_prob_b
			}
		)

		output_list.append(entry)
print("Processed {}: {}.".format(INPUT_FILE,graph_idx))

with open(OUTPUT_FILE, 'wb') as f:
	pickle.dump(output_list, f)
