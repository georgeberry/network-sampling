'''
Unlike misclassify_odds, which takes one element of the parameter space of
homophily tuple and majority group size to generate graphs from, then
misses with a variable rate, misclassify_params misses at a fixed rate but
takes random elements of the parameter space of homophily tuples and
majority group sizes.

More precisely, it generates symmetric homophily parameters in [0,1)
and group proportions from the same range.

This code is primarily used in conjunction with mathtest.py
'''
import sampling.graph_gen as graph_gen
import random
from sampling.lazy_population import population
from misclassify_odds import get_metrics, misclassify
import pandas as pd

if __name__ == "__main__":
	N_MISSES = 1
	N_GRAPHS = 1000
	GRAPH_SIZE = 500
	GRAPH_MEANDEG = 2
	P_MISCLASSIFY = 0.1
	OUTFILE_NAME = "../sim_output/randoutput.tsv"

	metrics_list = []

	for i_graph in range(N_GRAPHS):
		r1 = random.uniform(.2,.8)
		r2 = random.uniform(.2,.8)

		GRAPH_HOM = (r1, r1)
		GRAPH_GROUP_SIZE = r2

		print('Computing graph: {}'.format(i_graph))
		g = graph_gen.generate_powerlaw_group_digraph(
			GRAPH_SIZE,
			GRAPH_MEANDEG,
			GRAPH_HOM,
			GRAPH_GROUP_SIZE,
		)
		true_node_totals, true_edge_totals = population(g)

		epsilon = 1/(2*GRAPH_SIZE)
		if true_node_totals['a'] < epsilon or true_node_totals['b'] < epsilon:
			print("Skipped graph " + str(i_graph) + ".")
			continue # Unfortunately the homophily index is undefined in this case.

		true_results = get_metrics(
			true_node_totals,
			true_edge_totals,
		)
		true_results = {'true_' + x: y for x, y in true_results.items()}
		true_results['graph_idx'] = i_graph

		# bootstrap misses
		for i_miss in range(N_MISSES):
			bad_g = misclassify(g, P_MISCLASSIFY)
			node_totals, edge_totals = population(bad_g)
			miss_results = get_metrics(
				node_totals,
				edge_totals,
			)
			true_results['sim_idx'] = i_miss
			true_results['p_misclassify'] = P_MISCLASSIFY
			miss_results.update(true_results)
			metrics_list.append(miss_results)

	df = pd.DataFrame(metrics_list)
	df.to_csv(OUTFILE_NAME, sep='\t')
