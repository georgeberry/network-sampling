# Graph operations
from graph_filter import graph_filter
from graph_gen import generate_powerlaw_group_graph

# Sampling methods
from edge_sample import sample_random_edges
from node_sample import sample_random_nodes, sample_ego_networks
from random_walk import sample_random_walk
from snowball import sample_snowball

#### Params ####################################################################

OUTPUT_FILE = '../sim_output/output.csv'

GRAPH_SIZE = 1000

# Total simulation runs given by:
# N_GRAPHS * SAMPLES_PER_GRAPH * len(HOMOPHILY_VALUES) * len(MAJORITY_SIZES) * len(MEAN_DEG)
# OR: 100 * 100 * 5 * 2 * 2 = 200000
#     with 100 graphs created
N_GRAPHS = 100
SAMPLES_PER_GRAPH = 100

# homophily_values = [(1.0,1.0), (0.8,0.8), (0.5,0.5), (0.2,0.2), (0.0,0.0)]
# majority_sizes = [0.8,0.5]
# mean_deg = [2,4]
HOMOPHILY_VALUES = [(0.5,0.5)]
MAJORITY_SIZES = [0.8,0.5]
MEAN_DEG = [2]

# These are the various filters we apply to the graph
#
FILTERS = {
    filter_none : (),
    graph_filter.filter : ('b', 0, 0.2),
    graph_filter.filter : ('a', 0, 0.2),
    graph_filter.filter : ('a', 0.8, 1),
}

# function: param_tuple
SAMPLING_METHODS = {
    sample_random_nodes : (200,), # how many nodes?
    sample_ego_networks : (20,), # how many ego networks?
    sample_random_edges : (200,), # how many edges?
    sample_random_walk : (10,20), #
    sample_snowball : (5,3), #
    population: (), # true val
}

#### Functions #################################################################

def population(g):
    link_counts = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
        ('b', 'a'): 0,
    }

    for edge in g.edges_iter():
        link_counts[(g.node[edge[0]]['group'], g.node[edge[1]]['group'])] += 1

    return link_counts

def filter_none(g):
    return g

#### Run sim ###################################################################

for H, M_SZ, DEG,  in itertools.product(
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
