def graph_filter(graph, group, min_h=0, max_h=1):
    filtered = set()
    g_nodes = graph.nodes(data=True)
    for node in graph:

        # conditionals for exclusion from the filtered graph
        # has to be in targeted group
        if g_nodes[node][1]['group'] == group:
            ingrp_count = 0
            total = 0
            for neighbor in graph[node]:
                if g_nodes[neighbor][1]['group'] == group:
                    ingrp_count += 1
                total += 1
            # homophily has to be out of parameters
            if total <= 0 or ingrp_count/total < min_h or ingrp_count/total > max_h:
                filtered.add(node)

    # remove the filtered nodes
    newgraph = graph.copy()
    for node in filtered:
        newgraph.remove_node(node)

    return newgraph

if __name__ == "__main__":
    import graph_gen as gg

    g = gg.generate_powerlaw_group_graph(1000, 2, [0.8, 0.8], .5)
    filtered= filter(g, 'b', .5)
    print(filtered)
