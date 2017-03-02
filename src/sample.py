from graph_gen import generate_powerlaw_group_graph
import networkx
import node_sample
import edge_sample
import random_walk
import snowball
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

homophily_values = [(1.0,1.0), (0.8,0.8), (0.5,0.5), (0.2,0.2), (0.0,0.0)]
majority_sizes = [0.8,0.5]
mean_deg = [2,4]
sampling_methods = {node_sample.sample_random_nodes : (200,),
                    node_sample.sample_ego_networks : (20,),
                    edge_sample.sample_random_edges : (200,),
                    random_walk.sample_random_walk : (10,20),
                    snowball.sample_snowball : (5,3),
                    population: ()}
graph_size = 1000
sample_size = 1000
samples_per_graph = 100

for h in homophily_values:
    for s in majority_sizes:
        for deg in mean_deg:
            g = None
            counts = {k:list() for k in sampling_methods}
            for i in range(sample_size):
                if i % samples_per_graph == 0:
                    g = generate_powerlaw_group_graph(
                        graph_size, deg, h, s)
                for method, args in sampling_methods.items():
                    counts[method] += [{str(k):v 
                        for k,v in method(g, *args).items()}]
            for c_method, sample in counts.items():
                f = open('data/{}{}{}{}.json'.format(
                        c_method.__name__, h, s, deg),'w+')
                json.dump(sample,f)
                f.close()
            print("Completed h: {}, s: {}, deg: {}.".format(h,s,deg))

