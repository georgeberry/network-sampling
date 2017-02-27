import random


def sample_random_walk(
        g,  # Graph to sample from
        n_seeds,
        n_steps):
    sampled_nodes = set()
    sampled_edges = set()
    frontier = set()
    link_counts = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
        ('b', 'a'): 0
    }

    """
    Sample the initial set of seed nodes.
    Right now this is being done without replacement,
    is that okay?
    """
    g_nodes = g.nodes(data=True)
    frontier |= set(random.sample(g.nodes(), n_seeds))

    for _ in range(n_steps):
        next_frontier = set()
        sampled_nodes |= frontier
        for node in frontier:
            for neighbor in g[node].keys():
                if neighbor not in sampled_nodes:
                    # note that a node can only be sampled once. this might not be correct.
                    next_frontier.add(neighbor)
                    sampled_edges.add((node, neighbor))
                    link_counts[(g_nodes[node][1]['group'],
                                 g_nodes[neighbor][1]['group'])] += 1
        frontier = next_frontier
    sampled_nodes |= frontier

    return link_counts, sampled_nodes, sampled_edges


if __name__ == "__main__":
    import graph_gen as gg

    g = gg.generate_powerlaw_group_graph(1000, 2, [0.8, 0.8], .5)
    counts = sample_random_walk(g, 10, 50)[0]
    print(counts)
