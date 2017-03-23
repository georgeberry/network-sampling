import random
import networkx as nx


def sample_snowball(
        g,  # Graph to sample from
        seed=None
        ):

    # stuff to output
    node_counts = {
        'a': 0,
        'b': 0,
    }

    link_counts = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
        ('b', 'a'): 0,
    }

    g_groups = nx.get_node_attributes(g,'group')

    if not seed:
        seed = random.sample(g.nodes(), 1)

    # algorithm:
    # get neighbors of a focal node
    # add these to frontier nodes
    # add the edges to frontier edges
    # record the values of frontier edges
    # when there are no edges, go to next node

    sampled_nodes = set()
    sampled_edges = set()

    frontier = set([seed])
    # tally the seed, since we only tally nodes when they're discovered.
    node_counts[g_groups[seed]] += 1

    while frontier:
        next_frontier = set()  # the nodes we will discover on this pass
        # for every newly discovered node
        for node in frontier:
            # for every neighbor
            for neighbor in g[node].keys():
                # if the node is undiscovered, make it discovered, tally its group and add it to the frontier
                if neighbor not in sampled_nodes:
                    sampled_nodes.add(neighbor)
                    node_counts[g_groups[neighbor]] += 1
                    next_frontier.add(neighbor)
                # if the edge is undiscovered, make it discovered, and tally its type
                if (node, neighbor) not in sampled_edges and (neighbor, node) not in sampled_edges:
                    sampled_edges.add((node, neighbor))
                    link_counts[(g_groups[node],
                                 g_groups[neighbor])] += 1
                yield node_counts, link_counts
        # all the nodes we just discovered are now the frontier
        frontier = next_frontier


if __name__ == "__main__":
    import graph_gen as gg
    import sample

    g = gg.generate_powerlaw_group_graph(1000, 2, [0.8, 0.8], .5)
    counts = sample_snowball(g, 200, 2)
    print(counts)
