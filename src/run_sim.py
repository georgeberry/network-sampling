import csv
import itertools
import networkx as nx

# Graph operations
from graph_filter import graph_filter
from graph_gen import generate_powerlaw_group_graph

# Sampling methods
from edge_sample import sample_random_edges
from node_sample import sample_random_nodes, sample_ego_networks
from random_walk import sample_random_walk
from snowball import sample_snowball

#### Functions #################################################################

def population(g):
    link_counts = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
        ('b', 'a'): 0,
    }

    g_groups = nx.get_node_attributes(g,'group')

    for edge in g.edges_iter():
        link_counts[(g_groups[edge[0]],
                g_groups[edge[1]])] += 1

    return link_counts

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
HOMOPHILY_VALUES = [(0.8,0.8), (0.5,0.5), (0.2,0.2)]
MAJORITY_SIZES = [0.8, 0.5]
MEAN_DEG = [4]

# These are the various filters we apply to the graph
#
FILTERS = [(filter_none , ())]
           # (graph_filter, ('b',0,0.2)),
           # (graph_filter, ('a',0,0.2)),
           # (graph_filter, ('a',0.8,1))]

# function: param_tuple
SAMPLING_METHODS = [(sample_random_nodes, (200,)),
                    (sample_ego_networks, (20,)),
                    (sample_random_edges, (200,)),
                    (sample_random_walk, (10,20)),
                    (sample_snowball, (5,3)),
                    (population, ())]

#### Run sim ###################################################################

"""
Big loop here, each sim run writes to one line of csv
CSV scheme:
    g_idx,
    samp_idx,
    homophily_a,
    homophily_b,
    maj_size,
    mean_deg,
    filter_fn,
    filter_fn_args,
    samp_fn,
    samp_args,
    aa,
    ab,
    ba,
    bb,
"""
csv_colnames = [
    'g_idx',
    'samp_idx',
    'homophily_a',
    'homophily_b',
    'maj_size',
    'mean_deg',
    'filter_fn',
    'filter_fn_args',
    'samp_fn',
    'samp_args',
    'aa',
    'ab',
    'ba',
    'bb',
]

with open('../sim_output/output.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(csv_colnames)
    # Start big loop here
    for h, s, d, f in itertools.product(
        HOMOPHILY_VALUES,
        MAJORITY_SIZES,
        MEAN_DEG,
        FILTERS
    ):
        for g_idx in range(N_GRAPHS):
            g = generate_powerlaw_group_graph(GRAPH_SIZE, d, h, s)
            for samp_idx in range(SAMPLES_PER_GRAPH):
                for filter_fn, filter_args in FILTERS:
                    g_filtered = filter_fn(g, *filter_args)
                    for samp_fn, samp_args in SAMPLING_METHODS:
                        samp_result = samp_fn(g_filtered, *samp_args)
                        output_line = [
                            g_idx,
                            samp_idx,
                            h[0],
                            h[1],
                            s,
                            d,
                            filter_fn.__name__,
                            str(filter_args),
                            samp_fn.__name__,
                            str(samp_args),
                            samp_result[('a','a')],
                            samp_result[('a','b')],
                            samp_result[('b','a')],
                            samp_result[('b','b')],
                        ]
                        writer.writerow(output_line)
            break
