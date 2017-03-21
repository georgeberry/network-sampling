import random
import networkx as nx

def sample_snowball(
        g, # Graph to sample from
        max_links,
        n_seeds):

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

    sampled_nodes_all = set()
    sampled_edges_all = set()
    edges_per_seed = max_links / n_seeds
    g_groups = nx.get_node_attributes(g,'group')

    seeds = set(random.sample(g.nodes(), n_seeds))

    for seed in seeds:
        sampled_nodes = set()
        group_checked_edges = set() # tally each node's group
        frontier_nodes = set([seed])
        frontier_edges = set()
        sampled_edges = 0

        # algorithm:
        # get neighbors of a focal node
        # add these to frontier nodes
        # add the edges to frontier edges
        # record the values of frontier edges
        # when there are no edges, go to next node

        while len(frontier_nodes) > 0:
            focal_node = frontier_nodes.pop()
            nbrs = g.neighbors(focal_node)
            frontier_nodes |= set(nbrs)
            frontier_edges |= set([(focal_node, x) for x in nbrs])
            while len(frontier_edges) > 0:
                n1, n2 = frontier_edges.pop()
                g1, g2 = g_groups[n1], g_groups[n2]
                link_counts[(g1, g2)] += 1 # increment link count
                sampled_edges += 1

                if n1 not in group_checked_edges:
                    node_counts[g1] += 1
                    group_checked_edges.add(n1)
                if n2 not in group_checked_edges:
                    node_counts[g2] += 1
                    group_checked_edges.add(n2)

                if sampled_edges >= edges_per_seed:
                    break
            sampled_nodes.add(focal_node)
            if sampled_edges >= edges_per_seed:
                break

    return node_counts, link_counts


if __name__ == "__main__":
    import graph_gen as gg

    g = gg.generate_powerlaw_group_graph(1000, 2, [0.8, 0.8], .5)
    counts = sample_snowball(g, 200, 2)
    print(counts)
