import graph_gen
import random
import networkx as nx
import numpy as np
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
from population import population

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

def simulation_run(big_group = .5, homophily = (0.5,0.5), plot_fig = False):
	P_MISCLASSIFY = 0.1
	N_GRAPHS = 100
	N_MISSES = 1000
	GRAPH_SIZE = 100
	GRAPH_MEANDEG = 2
	GRAPH_HOM = homophily
	GRAPH_GROUP_SIZE = big_group

	#print(population(g))
	with open('../data/misclassify-' + '-'.join([str(x) for x in [GRAPH_GROUP_SIZE,GRAPH_HOM[0],GRAPH_HOM[1]]]) + '.csv', 'a+') as output:
		for i_graph in range(N_GRAPHS):
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
				1 if np.abs(true_hom_a - 0.5) > np.abs(avg_miss_hom - 0.5) else 0,
				1 if np.abs(true_inbreeding_hom_a) > np.abs(avg_miss_inbreeding_hom) else 0]
			output.write(' '.join([str(x) for x in out]) + '\n')

			if plot_fig and i_graph == 0:
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

def simulation_spread(big_group = .5, p_wrong = 0.1):
	P_MISCLASSIFY = p_wrong
	N_GRAPHS = 5
	N_MISSES = 10
	GRAPH_SIZE = 100
	GRAPH_MEANDEG = 2
	GRAPH_GROUP_SIZE = big_group

	miss_ingroup_fracs = list()
	miss_ingroup_x = list()
	with open('../data/spread-vs-expected-' + '-'.join([str(x) for x in [GRAPH_GROUP_SIZE,P_MISCLASSIFY]]) + '.csv', 'a+') as output:

		for hom_param in np.arange(0, 1, 0.01):
			print(hom_param)
			GRAPH_HOM = (hom_param, hom_param)

			for i_graph in range(N_GRAPHS):
				g = graph_gen.generate_powerlaw_group_graph(GRAPH_SIZE, GRAPH_MEANDEG, GRAPH_HOM, GRAPH_GROUP_SIZE)

				true_node_totals, true_edge_totals = population(g)
				true_hom_a = true_edge_totals[('a','a')]/(true_edge_totals[('a','a')]+true_edge_totals[('a','b')])

				for i_miss in range(N_MISSES):
					bad_g = misclassify(g, P_MISCLASSIFY)

					node_totals, edge_totals = population(bad_g)

					hhom = edge_totals[('a','a')]/(edge_totals[('a','a')]+edge_totals[('a','b')])
					miss_ingroup_fracs.append(hhom - true_hom_a)
					miss_ingroup_x.append(true_hom_a)
					output.write(str(miss_ingroup_x[-1]) + ' ' + str(miss_ingroup_fracs[-1]) + '\n')

	trace = go.Scatter(
		x = miss_ingroup_x,
		y = miss_ingroup_fracs,
		mode = 'markers'
		)
	data = [trace]
	plot(data, filename="../plots/spread_vs_expected-" + '-'.join([str(x) for x in [GRAPH_GROUP_SIZE,P_MISCLASSIFY]]))


def simulation_by_homophily(big_group = .5, p_wrong = 0.1):
	P_MISCLASSIFY = p_wrong
	N_GRAPHS = 5
	N_MISSES = 1000
	GRAPH_SIZE = 100
	GRAPH_MEANDEG = 2
	GRAPH_GROUP_SIZE = big_group

	all_out = list()
	with open('../data/vs-expected-' + '-'.join([str(x) for x in [GRAPH_GROUP_SIZE,P_MISCLASSIFY]]) + '.csv', 'a+') as output:
		for hom_param in np.arange(0, 1, 0.01):
			print(hom_param)
			GRAPH_HOM = (hom_param, hom_param)

			hom_out = list()
			for i_graph in range(N_GRAPHS):
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
					1 if np.abs(true_hom_a - 0.5) > np.abs(avg_miss_hom - 0.5) else 0,
					1 if np.abs(true_inbreeding_hom_a) > np.abs(avg_miss_inbreeding_hom) else 0]
				hom_out.append(out)

			hom_averages = np.mean(hom_out, axis=0)
			all_out.append(hom_averages)
			output.write(' '.join([str(x) for x in hom_averages]) + '\n')

		trace = go.Scatter(
			x = [ele[0] for ele in all_out],
			y = [ele[2] for ele in all_out],
			mode = 'lines+markers'
			)
		trace2 = go.Scatter(
			x = [0, 1],
			y = [0, 1],
			mode = 'lines'
			)
		data = [trace, trace2]
		plot(data, filename="../plots/homophily_vs_expected-" + '-'.join([str(x) for x in [GRAPH_GROUP_SIZE,P_MISCLASSIFY]]))

		trace = go.Scatter(
			x = [ele[1] for ele in all_out],
			y = [ele[3] for ele in all_out],
			mode = 'lines+markers'
			)
		trace2 = go.Scatter(
			x = [-1, 1],
			y = [-1, 1],
			mode = 'lines')
		data = [trace, trace2]
		plot(data, filename="../plots/inbreeding_vs_expected-" + '-'.join([str(x) for x in [GRAPH_GROUP_SIZE,P_MISCLASSIFY]]))


if __name__ == "__main__":
	simulation_spread(big_group = 0.2)