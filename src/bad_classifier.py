import graph_gen
import random
import networkx as nx
import numpy as np
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go

def misclassify(g, p_wrong):
	bad_g = g.copy()
	for node in bad_g.nodes_iter(data=True):
		r = random.random()
		if r < p_wrong and node[1]['group'] == 'a':
			bad_g.node[node[0]]['group'] = 'b'
		elif r < p_wrong:
			bad_g.node[node[0]]['group'] = 'a'
	return bad_g

def analyze(ggz, gh1, gh2):
	mat = np.genfromtxt('../data/misclassify-' + '-'.join([str(x) for x in [ggz,gh1,gh2]]) + '.csv')
	print(np.mean(mat,axis=0))


if __name__ == "__main__":
	# g = graph_gen.generate_powerlaw_group_graph(1000, 2, (.5, .5), 0.5)
	# bad_g = misclassify(g,.5)
	from population import population
	# print(g.nodes(data=True))
	# print(bad_g.nodes(data=True))

	# node_totals, edge_totals = population(g)
	# print(edge_totals)
	# homophily_a = edge_totals[('a','a')]/(edge_totals[('a','a')]+edge_totals[('a','b')])
	# pop_frac_a = node_totals['a']/(node_totals['a']+node_totals['b'])
	# inbreeding_homophily_a = (homophily_a - pop_frac_a)/(1 - pop_frac_a)
	# print(homophily_a)
	# print(inbreeding_homophily_a)

	csv_lines = list()

	P_MISCLASSIFY = 0.1
	N_GRAPHS = 100
	N_MISSES = 1000
	GRAPH_SIZE = 100
	GRAPH_MEANDEG = 2
	GRAPH_HOM = (0.2,0.2)
	GRAPH_GROUP_SIZE = .5

	#print(population(g))
	with open('../data/misclassify-' + '-'.join([str(x) for x in [GRAPH_GROUP_SIZE,GRAPH_HOM[0],GRAPH_HOM[1]]]) + '.csv', 'a+') as output:
		for i_graph in range(N_GRAPHS):
			print('Graph: ' + str(i_graph))
			g = graph_gen.generate_powerlaw_group_graph(GRAPH_SIZE, GRAPH_MEANDEG, GRAPH_HOM, GRAPH_GROUP_SIZE)

			true_node_totals, true_edge_totals = population(g)
			true_hom_a = true_edge_totals[('a','a')]/(true_edge_totals[('a','a')]+true_edge_totals[('a','b')])
			true_pop_frac_a = true_node_totals['a']/(true_node_totals['a']+true_node_totals['b'])
			true_inbreeding_hom_a = (true_hom_a - true_pop_frac_a)/(1 - true_pop_frac_a)

			miss_homs_a = list()
			miss_inbreeding_homs_a = list()
			for i_miss in range(N_MISSES):
				bad_g = misclassify(g, P_MISCLASSIFY)

				node_totals, edge_totals = population(bad_g)
				homophily_a = edge_totals[('a','a')]/(edge_totals[('a','a')]+edge_totals[('a','b')])
				pop_frac_a = node_totals['a']/(node_totals['a']+node_totals['b'])
				inbreeding_homophily_a = (homophily_a - pop_frac_a)/(1 - pop_frac_a)

				miss_homs_a.append(homophily_a)
				miss_inbreeding_homs_a.append(inbreeding_homophily_a)

			avg_miss_hom = np.mean(miss_homs_a)
			avg_miss_inbreeding_hom = np.mean(miss_inbreeding_homs_a)
			delta_miss_hom = avg_miss_hom - true_hom_a
			delta_miss_inbreeding_hom = avg_miss_inbreeding_hom - true_inbreeding_hom_a
			var_miss_hom = np.var(miss_homs_a)
			var_miss_inbreeding_hom = np.var(miss_inbreeding_homs_a)

			out = [true_hom_a, true_inbreeding_hom_a, avg_miss_hom, avg_miss_inbreeding_hom,
				delta_miss_hom, delta_miss_inbreeding_hom, var_miss_hom, var_miss_inbreeding_hom,
				1 if np.abs(true_hom_a) > np.abs(avg_miss_hom) else 0,
				1 if np.abs(true_inbreeding_hom_a) > np.abs(avg_miss_inbreeding_hom) else 0]
			csv_lines.append(out)
			output.write(' '.join([str(x) for x in out]) + '\n')

			if i_graph == 0:
				layout = {'shapes':[
				{
					'type': 'line',
					'x0': true_inbreeding_hom_a,
					'y0': 0,
					'x1': true_inbreeding_hom_a,
					'y1': 100,
					'line': {
						'color': 'rgb(0, 0, 0)',
						'width': 4,
					}
				}]}
				data = [go.Histogram(x=miss_inbreeding_homs_a)]
				fig = go.Figure(data=data, layout=layout)
				plot(fig, filename='../plots/no_homophily.html')
				print("Done plot.")


	# print("Starting analysis.")
	# total_less_interesting = 0
	# total_inbreeding_less_interesting = 0
	# total_delta = 0
	# total_inbreeding_delta = 0
	# total_hom = 0
	# total_inbreeding_hom = 0
	# for line in csv_lines:
	# 	if np.abs(line[0]) > np.abs(line[2]):
	# 		total_less_interesting += 1
	# 	if np.abs(line[1]) > np.abs(line[3]):
	# 		total_inbreeding_less_interesting += 1
	# 	total_delta += line[4]
	# 	total_inbreeding_delta += line[5]
	# 	total_hom += line[0]
	# 	total_inbreeding_hom += line[1]

	# avg_delta = total_delta / N_GRAPHS
	# avg_inbreeding_delta = total_inbreeding_delta / N_GRAPHS
	# avg_hom = total_hom / N_GRAPHS
	# avg_inbreeding_hom = total_inbreeding_hom / N_GRAPHS

	# print("Real homophily: " + str(avg_hom) + "/" + str(avg_inbreeding_hom))
	# print("Total less interesting: " + str(total_less_interesting) + '/' + str(total_inbreeding_less_interesting))
	# print("Overall average delta: " + str(avg_delta) + '/' + str(avg_inbreeding_delta))