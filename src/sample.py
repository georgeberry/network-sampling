from graph_gen import generate_powerlaw_group_graph
import networkx
import node_sample
import edge_sample
import random_walk
import snowball
import itertools
import graph_filter
import json

def population(g):
    link_counts = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
        ('b', 'a'): 0,
    }

    for edge in g.edges_iter():
        link_counts[(g.node[edge[0]]['group'],g.node[edge[1]]['group'])] += 1

    return link_counts

def filter_none(g):
    return g

# homophily_values = [(1.0,1.0), (0.8,0.8), (0.5,0.5), (0.2,0.2), (0.0,0.0)]
# majority_sizes = [0.8,0.5]
# mean_deg = [2,4]
homophily_values = [(0.5,0.5)]
majority_sizes = [0.8,0.5]
mean_deg = [2]
filters = { filter_none : (),
            graph_filter.filter : ('b',0,0.2),
            graph_filter.filter : ('a',0,0.2),
            graph_filter.filter : ('a',0.8,1)}

sampling_methods = {node_sample.sample_random_nodes : (200,),
                    node_sample.sample_ego_networks : (20,),
                    edge_sample.sample_random_edges : (200,),
                    random_walk.sample_random_walk : (10,20),
                    snowball.sample_snowball : (5,3),
                    population: ()}
graph_size = 1000
sample_size = 1000
samples_per_graph = 1000

for parameters in itertools.product(
    homophily_values,
    majority_sizes,
    mean_deg,
    filters.items()):
    h, s, deg, fil = parameters
    g = None
    counts = {k:list() for k in sampling_methods}
    for i in range(sample_size):
        if i % samples_per_graph == 0:
            g = generate_powerlaw_group_graph(
                graph_size, deg, h, s)
            g = fil[0](g, *fil[1])
        for method, args in sampling_methods.items():
            counts[method] += [{str(k):v 
                for k,v in method(g, *args).items()}]
    for c_method, sample in counts.items():
        f = open('data/{}{}.json'.format(
                c_method.__name__, hash(str(parameters))),'w+') #sorry, temporary
        json.dump(sample,f)
        f.close()
    print("Completed h: {}, s: {}, deg: {}.".format(h,s,deg))

