import random
import networkx as nx
import numpy as np
import pandas as pd
#from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
#import plotly.graph_objs as go
from plotnine import *
from itertools import product

from population import population
import graph_gen

def misclassify(g, p_wrong):
	bad_g = g.copy()
	for node in bad_g.nodes_iter(data=True):
		r = random.random()
		if r < p_wrong and node[1]['group'] == 'a':
			bad_g.node[node[0]]['group'] = 'b'
		elif r < p_wrong:
			bad_g.node[node[0]]['group'] = 'a'
	return bad_g

def analyze(big_group, homophily1, homophily2):
	mat = np.genfromtxt('../data/misclassify-' + '-'.join([str(x) for x in [big_group,homophily1,homophily2]]) + '.csv')
	print("True Homophily - True Inbreeding - Average Misclassified Homophily - Average Misclassified Inbreeding - "
		+ "Average Delta Homophily from Misclassification - Average Delta Inbreeding - "
		+ "Variance in Misclassified Homophily - Variance in Misclassified Inbreeding")
	print(np.mean(mat,axis=0))


def get_metrics(node_totals, edge_totals):
	d_aa = edge_totals[('a','a')]
	d_ab = edge_totals[('a','b')]
	d_ba = edge_totals[('b','a')]
	d_bb = edge_totals[('b','b')]

	N = node_totals['a'] + node_totals['b']
	p_a = node_totals['a']/N
	p_b = node_totals['b']/N

	homophily_a = (d_aa / (d_aa + d_ab) - p_a)/(1 - p_a)
	homophily_b = (d_bb / (d_bb + d_bb) - p_b)/(1 - p_b)

	result = {
		'd_aa': d_aa,
		'd_ab': d_ab,
		'd_ba': d_ba,
		'd_bb': d_bb,
		'p_a': p_a,
		'p_b': p_b,
		'homophily_a': homophily_a,
		'homophily_b': homophily_b,
	}
	return result

P_MISCLASSIFY = [0.00, 0.03, 0.06, 0.09, 0.12, 0.15, 0.18, 0.21]
N_GRAPHS = 100
N_MISSES = 100
GRAPH_SIZE = 100
GRAPH_MEANDEG = 2
GRAPH_HOM = (0.8,0.8)
GRAPH_GROUP_SIZE = .5
OUTFILE_NAME = '../sim_output/output.tsv'

if __name__ == "__main__":

	metrics_list = []

	#print(population(g))
	for i_graph, p_misclassify in product(range(N_GRAPHS), P_MISCLASSIFY):
		print('Computing graph: {}'.format(i_graph))
		g = graph_gen.generate_powerlaw_group_graph(
			GRAPH_SIZE,
			GRAPH_MEANDEG,
			GRAPH_HOM,
			GRAPH_GROUP_SIZE,
		)
		true_node_totals, true_edge_totals = population(g)

		true_results = get_metrics(
			true_node_totals,
			true_edge_totals,
		)
		true_results = {'true_' + x: y for x, y in true_results.items()}
		true_results['graph_idx'] = i_graph

		# bootstrap misses
		for i_miss in range(N_MISSES):
			bad_g = misclassify(g, p_misclassify)
			node_totals, edge_totals = population(bad_g)
			miss_results = get_metrics(
				node_totals,
				edge_totals,
			)
			true_results['sim_idx'] = i_miss
			true_results['p_misclassify'] = p_misclassify
			miss_results.update(true_results)
			metrics_list.append(miss_results)

	df = pd.DataFrame(metrics_list)
	df.to_csv(OUTFILE_NAME, sep='\t')
