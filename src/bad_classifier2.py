import graph_gen
import random
from population import population
from bad_classifier import get_metrics, misclassify
import pandas as pd

if __name__ == "__main__":

	N_MISSES = 1
	N_GRAPHS = 1000
	GRAPH_SIZE = 500
	GRAPH_MEANDEG = 2
	P_MISCLASSIFY = 0.1
	OUTFILE_NAME = "../sim_output/randoutput.tsv"

	metrics_list = []

	#print(population(g))
	for i_graph in range(N_GRAPHS):
		r1 = (random.random()*.8)+.1 #[.1,.9]
		r2 = (random.random()*.8)+.1
		print(r1)
		print(r2)
		GRAPH_HOM = (r1, r1)
		GRAPH_GROUP_SIZE = r2

		print('Computing graph: {}'.format(i_graph))
		g = graph_gen.generate_powerlaw_group_graph(
			GRAPH_SIZE,
			GRAPH_MEANDEG,
			GRAPH_HOM,
			GRAPH_GROUP_SIZE,
		)
		true_node_totals, true_edge_totals = population(g) ##################

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
