import random
from graph_gen import generate_powerlaw_group_graph

def sample_snowball(
        g, # Graph to sample from
        n_seeds,
        n_steps):

    sampled_nodes_all = []
    sampled_edges_all = []
    link_counts = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
        ('b', 'a'): 0,
    }

    g_nodes = g.nodes(data=True)
    seeds = set(random.sample(g.nodes(), n_seeds))

    for seed in seeds:
        sampled_nodes = set()
        sampled_edges = set()
        frontier = set([seed])

        for _ in range(n_steps):
            next_frontier = set()
            sampled_nodes |= frontier
            for node in frontier:
                for neighbor in g[node].keys():
                    if neighbor not in sampled_nodes:
                        next_frontier.add(neighbor)
                    elif (node, neighbor) not in sampled_edges and (neighbor, node) not in sampled_edges:
                        sampled_edges.add((node, neighbor))
                        link_counts[(g_nodes[node][1]['group'],
                                     g_nodes[neighbor][1]['group'])] += 1
            frontier = next_frontier
        sampled_nodes |= frontier
        sampled_nodes_all += sampled_nodes
        sampled_edges_all += sampled_edges

    return link_counts


if __name__ == "__main__":
    g = gg.generate_powerlaw_group_graph(1000, 2, [0.8, 0.8], .5)
    counts = sample_snowball_walk(g, 10, 2)[0]
    print(counts)