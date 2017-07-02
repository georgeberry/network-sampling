from graph_gen import generate_powerlaw_group_graph
import networkx as nx
import node_sample
import edge_sample
import random_walk
import snowball
import itertools
import graph_filter
import json
import random
import numpy as np
import types


def population(g):
    link_counts = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
        ('b', 'a'): 0,
    }
    node_counts = dict()

    g_groups = nx.get_node_attributes(g,'group')

    for edge in g.edges_iter():
        link_counts[(g_groups[edge[0]],
                g_groups[edge[1]])] += 1
    for node in g.nodes_iter():
        group = g_groups[node]
        if group not in node_counts.keys():
            node_counts[group] = 0
        node_counts[g_groups[node]] += 1

    print(node_counts)
    return (node_counts,link_counts)


def multiseed(sampler, n_seeds=1, seeds=None, samplername=""):
    """
    Returns a generator which instantiates multiple copies of a sampler with different seeds,
    and samples from them in parallel
    """
    def multisampler(g, seeds=seeds):
        if not seeds:
            seeds = np.random.choice(g.nodes(), n_seeds, replace=False)
        samples = [sampler(g, seed=seed) for seed in seeds]
        counts = {}
        while True:
            for sample in samples:
                counts[sample] = next(sample)
                summed_node_counts = {}
                summed_edge_counts = {}
                for item in counts.values():
                    # maybe we should be using counters...
                    for nkey in item[0]:
                        if nkey in summed_node_counts:
                            summed_node_counts[nkey] += item[0][nkey]
                        else:
                            summed_node_counts[nkey] = item[0][nkey]
                    for ekey in item[1]:
                        if ekey in summed_edge_counts:
                            summed_edge_counts[ekey] += item[1][ekey]
                        else:
                            summed_edge_counts[ekey] = item[1][ekey]
                yield summed_node_counts, summed_edge_counts
    multisampler.__name__ = 'multisampler_' + samplername
    return multisampler


def sample_at(
    sampler,
    g,
    n_edges=None,
    n_nodes=None,
    *sampler_args,
    **sampler_kwargs
):
    """
    Samples the graph using a given method until you have n_edges edges or n_nodes nodes.
    n_edges: edgecounts for which to get outputs; integer or list of integers (in ascending order)
    n_nodes: nodecounts for which to get outputs
    Do not specify both n_edges and n_nodes.

    output: count pair or list of count pairs, one at each edgecount or nodecount benchmark
    """
    sample = sampler(g, *sampler_args, **sampler_kwargs)

    assert not (n_edges and n_nodes)
    mode = 'edges'
    n_things = set(np.ravel(n_edges))
    if n_nodes:
        mode = 'nodes'
        n_things = set(np.ravel(n_nodes))

    if not isinstance(sample,types.GeneratorType):
        return {-1: sample}

    counts = {}
    while n_things:
        node_counts, edge_counts = next(sample)
        if mode == 'edges':
            thingcount = sum(edge_counts.values())
        elif mode == 'nodes':
            thingcount = sum(node_counts.values())
        if thingcount in n_things:
            n_things.remove(thingcount)
            counts[thingcount] = (node_counts, edge_counts)

    return counts


def filter_none(g):
    return g


def stringify_parameters(parameters):
    stringified = ""
    connect = "-"
    for i,p in enumerate(parameters):
        if i == 0 and connect == "-":
            connect = ""
        if type(p) is tuple or type(p) is list:
            if len(p) != 0:
                stringified += (connect + stringify_parameters(p))
                connect = "-"
        elif callable(p):
            stringified += (connect + p.__name__)
            connect = "-"
        else:
            stringified += (connect + str(p))
            connect = "-"
    return stringified

if __name__ == "__main__":
    # homophily_values = [(0.8,0.8),(0.5,0.5),(0.2,0.2)]
    # majority_sizes = [0.8,0.5]
    # mean_deg = [4]
    # filters = [ (filter_none , ()),
    # 			(graph_filter.graph_filter , ('b',0,0.2)),
    # 			(graph_filter.graph_filter , ('a',0,0.2)),
    # 			(graph_filter.graph_filter , ('a',0.8,1))]

    # sampling_methods = [(node_sample.sample_random_nodes , ()),
    # 					(node_sample.sample_ego_networks , ()),
    # 					(edge_sample.sample_random_edges , ()),
    # 					(multiseed(random_walk.sample_random_walk, 5) , ()),
    # 					(multiseed(snowball.sample_snowball,3)),
    # 					(population , ())]
    # graph_size = 1000
    # sample_size = 1000
    # samples_per_graph = 1000
    # nodes_to_sample = [200]

    homophily_values = [(0.5,0.5)]
    majority_sizes = [0.8]
    mean_deg = [4]
    filters = [ (filter_none , ()),
                (graph_filter.graph_filter , ('b',0,0.2))]

    sampling_methods = [(node_sample.sample_random_nodes , ()),
                        (node_sample.sample_ego_networks , ()),
                        (edge_sample.sample_random_edges , ()),
                        (multiseed(random_walk.sample_random_walk, 5, samplername="random_walk") , ()),
                        (multiseed(snowball.sample_snowball,3, samplername="snowball"), ()),
                        (population , ())]
    graph_size = 100
    sample_size = 100
    samples_per_graph = 100
    nodes_to_sample = (20,)

    for parameters in itertools.product(
        homophily_values,
        majority_sizes,
        mean_deg,
        filters):

        h, s, deg, fil = parameters
        s_params = stringify_parameters(parameters)

        g = None
        counts = {k[0]+(k[1],):list() for k in itertools.product(sampling_methods,nodes_to_sample + (-1,))}
        for i in range(sample_size):
            if i % samples_per_graph == 0:
                g = generate_powerlaw_group_graph(
                    graph_size, deg, h, s)
                g = fil[0](g, *fil[1])
            for method, args in sampling_methods:
                for sampled,results in sample_at(method,g,nodes_to_sample,*args).items():
                    counts[(method,args,sampled)] += [{str(k):v
                        for k,v in results[1].items()}]
        for c_method, sample in counts.items():
            f = open('data/{}-{}-{}.json'.format(
                    c_method[0].__name__, s_params, c_method[2]), 'w+')
            json.dump(sample,f)
            f.close()

        print("Completed {}.".format(s_params))
