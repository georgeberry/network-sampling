import networkx as nx
import random
import itertools

# Currently the code seems to work semi-acceptably
# but the final degree distribution doesn't match the
# initial one exactly, because there's a good chance
# that nodes with high numbers of edge stubs will only
# have self-links as options, which isn't allowed at the
# moment. This might be fixable by weighting edge
# connections to favor nodes with high edge stub count.

m = 100
n = 3
p = 0 # Clustering parameter

# Probabilities that a given node will be in each class
class_probabilities = [.5,.5]
self_interaction_rates = [.5,.5]

def pick_class():
	r = random.random()
	cum = 0
	for c, prob in enumerate(class_probabilities):
		cum += prob
		if r < prob:
			return c
	#If this happens there was probably just a rounding error
	return len(class_probabilities)-1

def generate_class_powerlaw_graph(m,n,p,
	class_probabilities, self_interaction_rates):
	# Generate a powerlaw graph using Holme and Kim's method
	# If p = 0, this should be equivalent to BA.
	# We only use the edge counts from this graph.
	g = nx.powerlaw_cluster_graph(m,n,p)

	# Generate a dictionary which has the nodes of the
	# random network as keys and a tuple of vertex count
	# and class as the values.
	edges = {node:(len(g[node]),pick_class()) for node in g.nodes_iter()}

	# print g.edges()
	# hist = nx.degree_histogram(g)
	# hist.sort()
	# print hist

	new_graph = nx.Graph()

	for i,c in enumerate(class_probabilities):
		# This long list comprehension creates a list of nodes
		# representing edge stubs belonging to the class of interest
		edge_stubs = list(itertools.chain.from_iterable(
			itertools.repeat(node, edges[node][0]) 
			for node in edges if edges[node][1] == i and edges[node][0] > 0))

		#Get the stubs for other nodes
		other_stubs = list(itertools.chain.from_iterable(
			itertools.repeat(node, edges[node][0])
			for node in edges if edges[node][1] != i and edges[node][0] > 0))


		random.shuffle(edge_stubs)

		# This should be the only part that won't work right
		# for n > 2 classes. And should only require minor mods.
		for k,stub in enumerate(edge_stubs):
			r = random.random()
			potential_ends = []
			if r < self_interaction_rates[i] or i == len(class_probabilities)-1:
				# Internal link
				potential_ends = [q for q in edge_stubs if not q == stub]
			else:
				# External link
				potential_ends = other_stubs

			if len(potential_ends) == 0:
				continue
				
			r_n = random.randint(0,len(potential_ends)-1)

			edge_end = potential_ends[r_n]

			edge_stubs = [j for (p,j) in enumerate(potential_ends)
				if not (p == r_n or p == k)]

			edges[edge_end] = (edges[edge_end][0] - 1, edges[edge_end][1])

			new_graph.add_edge(stub, edge_end)

	# print new_graph.edges()
	# hist = nx.degree_histogram(new_graph)
	# hist.sort()
	# print hist

	return new_graph


generate_class_powerlaw_graph(m,n,p,
	class_probabilities,self_interaction_rates)