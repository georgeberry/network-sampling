import csv
import itertools
import networkx as nx

# Graph operations
from graph_gen import generate_powerlaw_group_graph

# Sampling methods
from sampling_methods import sample_edges, sample_nodes, sample_ego_networks
from sampling_methods import sample_random_walk, sample_snowball, population

# Helpers
from helpers import stringify_parameters, get_n_samples

#### Functions #################################################################

def filter_none(g):
    return g

#### Params ####################################################################

OUTPUT_FILE = '../../sim_output/output.csv'

GRAPH_SIZE = 1000

# Total simulation runs given by:
# N_GRAPHS * SAMPLES_PER_GRAPH * len(HOMOPHILY_VALUES) * len(MAJORITY_SIZES) * len(MEAN_DEG)
# OR: 100 * 100 * 5 * 2 * 2 = 200000
#     with 100 graphs created
N_GRAPHS = 100
SAMPLES_PER_GRAPH = 100
SAMPLE_SIZE = 100

# homophily_values = [(1.0,1.0), (0.8,0.8), (0.5,0.5), (0.2,0.2), (0.0,0.0)]
# majority_sizes = [0.8,0.5]
# mean_deg = [2,4]
HOMOPHILY_VALUES = [(0.8,0.8), (0.5,0.5), (0.2,0.2)]
MAJORITY_SIZES = [0.8, 0.5]
MEAN_DEG = [4]

# These are the various filters we apply to the graph
# FILTERS = [(filter_none , ())]
           # (graph_filter, ('b', 0, 0.2)),
           # (graph_filter, ('a', 0, 0.2)),
           # (graph_filter, ('a', 0.8, 1))]

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
    'samp_size',
    'sample_method',
    'homophily_a',
    'homophily_b',
    'maj_size',
    'mean_deg',
    'a',
    'b',
    'aa',
    'ab',
    'ba',
    'bb',
]

with open(OUTPUT_FILE, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(csv_colnames)
    # Start big loop here
    for m, h, f in itertools.product(
        MEAN_DEG,
        HOMOPHILY_VALUES,
        MAJORITY_SIZES,
    ):
        for g_idx in range(N_GRAPHS):
            g = generate_powerlaw_group_graph(GRAPH_SIZE, m, h, f)
            for samp_idx in range(SAMPLES_PER_GRAPH):
                sampling_methods = {
                    'sample_edges': sample_edges(g),
                    'sample_nodes': sample_nodes(g),
                    'sample_ego_networks': sample_ego_networks(g),
                    'sample_random_walk': sample_random_walk(g),
                    'sample_snowball': sample_snowball(g),
                    'population': population(g),
                }
                for method, fn in sampling_methods.items():
                    node_counts, link_counts = get_n_samples(fn, n=SAMPLE_SIZE)
                    output_line = [
                        g_idx,
                        samp_idx,
                        SAMPLE_SIZE,
                        method,
                        h[0],
                        h[1],
                        f,
                        m,
                        node_counts['a'],
                        node_counts['b'],
                        link_counts[('a','a')],
                        link_counts[('a','b')],
                        link_counts[('b','a')],
                        link_counts[('b','b')],
                    ]
                    writer.writerow(output_line)
            print('Done with {}'.format(output_line[:6]))
