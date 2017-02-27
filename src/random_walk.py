import random
from graph_gen import generate_powerlaw_group_graph

def sample_random_walk(
	g, # Graph to sample from
	n_seeds,
	n_steps):

	sampled_nodes = []
	sampled_edges = []
	link_counts = {
		('a','a') : 0,
		('a','b') : 0,
		('b','b') : 0,
		('b','a') : 0,
	}

	"""
	Sample the initial set of seed nodes.
	Right now this is being done with replacement,
	is that okay?
	"""
	g_nodes = g.nodes(data=True)
	sampling_nodes = random.sample(g.nodes(),n_seeds)

	for step in range(n_steps):
		# We store all sampled nodes just in case
		sampled_nodes += sampling_nodes

		new_nodes = []
		for node in sampling_nodes:
			# For each node, pick an edge to follow
			next_node = random.choice(list(g[node]))

			# The nodes at the end of these edges are the new batch.
			new_nodes += [next_node]
			sampled_edges += [(node,next_node)]
			# Update the list of link counts for the sampled edge
			link_counts[(g_nodes[node][1]['group'],
				g_nodes[next_node][1]['group'])] += 1

		sampling_nodes = new_nodes

	sampled_nodes += sampling_nodes

	return link_counts, sampled_nodes, sampled_edges


if __name__ == "__main__":
	g = generate_powerlaw_group_graph(1000, 2, [0.8,0.8], .5)
	counts = sample_random_walk(g, 10, 50)[0]
	print(counts)
