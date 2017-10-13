import networkx as nx
import pandas as pd
import numpy as np
import pickle
import sys, os
import itertools
from copy import deepcopy
import collections
import math

"""
Run this:
    find /mnt/md0/network_sampling_data/graphs -type f | parallel python run_sim_existing.py

To test:
    python run_sim_existing.py /mnt/md0/network_sampling_data/network-sampling/sim_output/graphs/10000_2_0.2_0.2_0.5_0.p

To test locally:
    python run_sim_existing.py /Users/g/Documents/network-sampling/graphs/10000_2_0.2_0.2_0.5_0.p

Run with sexual contact network
    python run_sim_existing.py ../../data/sexual_contact/graph.p


Requires GNU parallel. This file operates on one graph file and outputs one
output file. Then, aggregate_runs.py joins them together into one big df
for analysis.
"""

# Sampling methods
from sampling_procedures import sample_edges
from sampling_procedures import sample_nodes
from sampling_procedures import sample_rds
from sampling_procedures import sample_snowball
from sampling_procedures import population
# Compute measures
from sampling_procedures import get_top_20pct
from sampling_procedures import get_true_top_20pct_minority_grp
from sampling_procedures import node_statistic_grp_b
from sampling_procedures import colemans_h
from sampling_procedures import rds_estimate
from sampling_procedures import boot_with_attr
# Some other functions
from sampling_procedures import misclassify_nodes
# Correctors
from sampling_procedures import get_correct_group_proportions
from sampling_procedures import get_correct_crosslink_proportions
from sampling_procedures import get_importance_resample_top20_with_correction
from sampling_procedures import get_correct_top20

#### Params ####################################################################
INPUT_FILE = sys.argv[1]
# INPUT_FILE = '/mnt/md0/network_sampling_data/network-sampling/sim_output/graphs/10000_4_0.8_0.8_0.8_3.p'
# print(INPUT_FILE)

# OUTPUT_DIR = '/Users/g/Documents/network-sampling/'
OUTPUT_DIR = '/mnt/md0/network_sampling_data/stats/'
OUTPUT_FILE = OUTPUT_DIR + os.path.split(INPUT_FILE)[1]

# Total number of lines given by:
# N_GRAPHS * SAMPLES_PER_GRAPH * len(SAMPLE_SIZE_INCREMENTS) * num sampling methods
SAMPLES_PER_GRAPH = 100
SAMPLE_SIZE = 3000 # 25% of simulation graphs
INCREMENT_SIZE = 500
SAMPLE_SIZE_INCREMENTS = np.arange(
    start=INCREMENT_SIZE,
    stop=SAMPLE_SIZE + INCREMENT_SIZE,
    step=INCREMENT_SIZE,
)

#### Read and preprocess #######################################################

g = nx.read_gpickle(INPUT_FILE)
ingroup_pref_pair = g.graph['params'].pop('homophily')
g.graph['params'].update({
    'ingrp_pref_a': ingroup_pref_pair[0],
    'ingrp_pref_b': ingroup_pref_pair[1],
})
graph_idx = g.graph['params'].pop('idx')

#### Run samples ###############################################################

sampling_methods = {
    'sample_edges':sample_edges,
    'sample_nodes':sample_nodes,
    # 'sample_ego_networks':sample_ego_networks,
    'sample_rds': sample_rds,
    # 'sample_rds_double': sample_rds,
    'sample_snowball': sample_snowball,
    'sample_ideal': (sample_nodes, sample_edges),
}

misclassification_probs = [
    0.0,
    0.1,
    0.2,
    0.3,
]

#### Get true values for graph #################################################

true_top_20pct_minority_grp = get_true_top_20pct_minority_grp(g)
true_node_grp_counts, true_link_grp_counts = population(g)

l_a, l_b = true_node_grp_counts['a'], true_node_grp_counts['b']

p_a = l_a / (l_a + l_b)
p_b = l_b / (l_a + l_b)

l_aa = true_link_grp_counts[('a','a')]
l_ab = true_link_grp_counts[('a','b')]
l_bb = true_link_grp_counts[('b','b')]

s_a = (2 * l_aa) / (2 * l_aa + l_ab)
s_b = (2 * l_bb) / (2 * l_bb + l_ab)

# print(s_a, s_b)

h_a, h_b = colemans_h(p_a, s_a), colemans_h(p_b, s_b)

#### Set up sim space and run ##################################################

space = itertools.product(
    range(SAMPLES_PER_GRAPH),
    SAMPLE_SIZE_INCREMENTS,
    sampling_methods.items(),
    misclassification_probs,
)

# Store records here that will convert to df
record_list = list()

"""
We need to convert the large amount of information in df, crosslink_dict
to one record for output (e.g. one row in a df)

df looks like:
    degree, node_statistic

This allows RDS weighting and importance resampling of the df itself

Note that we don't need to do this with crosslink counts because RDS
    provides a true random sample of edges in the network

Measures:
    - true a, b proportions
    - 	estimated a, b proportions from the sample
    - true aa, bb proportions (proportion of a's links that are ingroup)
    - 	estiamted aa, ab, bb proportions from the sample
    - true mean degree
    - 	estimated mean degree
    - true fraction of b in top 20% of degree
    - 	estimated fraction of b in top 20% of degree
    - true homophily for a, b
    - 	estimated homophily for a, b

The strategy is to minimize the amount of additional work that needs to
    happen in R. We should be able to load up this big df and get 100% of
    the measures we need to make all plots about the graph in question for
    the paper.

Conventions:
    t_a or m_a for the measured proportions
    s_a_hat or p_a_hat for the estimated after correction
    s_a or p_a for the true values
    l_aa_hat for raw counts from the crawl

For misclassify probs: we make a deepcopy of g and operate on that
Fixes directly applied to:
    - m_a
    - m_b
    - t_a
    - t_b
"""

for samp_idx, sample_size, sampling_method, p_misclassify in space:
    if p_misclassify > 0:
        gg = deepcopy(g)
        gg = misclassify_nodes(gg, p_misclassify)
    else:
        gg = deepcopy(g)

    method, fn = sampling_method
    if 'sample_rds' in method:
        if method == 'sample_rds':
            df, crosslink_dict = fn(gg, sample_size, node_statistic_grp_b)
            m_b = rds_estimate(df, 'group')
            m_a = 1 - m_b
            mu = rds_estimate(df, 'degree')
            df = boot_with_attr(df, mu, n=20000)
        if method == 'sample_rds_double':
            df, crosslink_dict = fn(
                gg,
                sample_size,
                node_statistic_grp_b,
            )
            m_b = rds_estimate(df, 'group')
            m_a = 1 - m_b
            df, crosslink_dict = fn(
                gg,
                sample_size,
                node_statistic_grp_b,
            )
            mu = rds_estimate(df, 'degree')
            df = boot_with_attr(df, mu, n=20000)

            sample_size = 2 * sample_size
    elif method == 'sample_ideal':
        fn_node, fn_edge = fn
        df, _ = fn_node(
            gg,
            sample_size,
            node_statistic_grp_b,
        )
        m_b = df.group.mean()
        m_a = 1 - df.group.mean()
        _, crosslink_dict = fn_edge(
            gg,
            sample_size,
            node_statistic_grp_b,
        )
    else:
        df, crosslink_dict = fn(gg, sample_size, node_statistic_grp_b)
        # janky: assume node stat is group b
        m_b = df.group.mean()
        m_a = 1 - df.group.mean()

    l_aa_hat = crosslink_dict[('a','a')]
    l_ab_hat = crosslink_dict[('a','b')]
    l_bb_hat = crosslink_dict[('b','b')]

    # for sample_ideal this is done with nodes
    top_20_hat = get_top_20pct(df)

    t_a = l_aa_hat / (l_aa_hat + l_ab_hat)
    t_b = l_bb_hat / (l_bb_hat + l_ab_hat)

    h_a_hat = colemans_h(m_a, t_a)
    h_b_hat = colemans_h(m_b, t_b)

    # We need to convert all of this data into one record
    record = collections.OrderedDict([
        # params
        ('graph_idx', graph_idx),
        ('samp_idx', samp_idx),
        ('samp_size', sample_size),
        ('method', method),
        ('p_misclassify', p_misclassify),
        ('clf_err_corrected', False),

        # true values
        ('p_a', p_a),
        ('p_b', p_b),
        ('s_a', s_a),
        ('s_b', s_b),
        ('top_20_true', true_top_20pct_minority_grp),
        ('h_a', h_a),
        ('h_b', h_b),

        # raw sample values for cov analysis
        ('m_a_raw', m_a),
        ('m_b_raw', m_b),
        ('t_aa_raw', l_aa_hat / (l_aa_hat + l_ab_hat + l_bb_hat)),
        ('t_ab_raw', l_ab_hat / (l_aa_hat + l_ab_hat + l_bb_hat)),
        ('t_bb_raw', l_bb_hat / (l_aa_hat + l_ab_hat + l_bb_hat)),

        # estimates
        ('m_a', m_a),
        ('m_b', m_b),
        ('t_a', t_a),
        ('t_b', t_b),
        ('h_a_hat', h_a_hat),
        ('h_b_hat', h_b_hat),
        ('top_20_hat', top_20_hat),
    ])
    # print('Finished {} {} {} {}'.format(
    #     samp_idx,
    #     sample_size,
    #     sampling_method,
    #     p_misclassify)
    # )
    # Included in g.graph['params']:
    # num_nodes, mean_degree, h_a, h_b, majority_size, idx
    record.update(gg.graph['params'])
    record_list.append(record)

    # handle missclassify correction here
    # write another row if we do
    # all measures appended with _crct
    if p_misclassify > 0:
        m_a, m_b = get_correct_group_proportions(m_a, m_b, p_misclassify)
        l_aa_hat, l_ab_hat, l_bb_hat = \
            get_correct_crosslink_proportions(
                l_aa_hat,
                l_ab_hat,
                l_bb_hat,
                p_misclassify,
        )
        if 'sample_rds' in method:
            top_20_hat = get_importance_resample_top20_with_correction(
                df,
                mu,
                p_misclassify,
            )
        else:
            top_20_hat = get_correct_top20(
                df,
                p_misclassify,
            )

        t_a = l_aa_hat / (l_aa_hat + l_ab_hat)
        t_b = l_bb_hat / (l_bb_hat + l_ab_hat)

        h_a_hat = colemans_h(m_a, t_a)
        h_b_hat = colemans_h(m_b, t_b)

        # update and save record
        record = deepcopy(record)
        record['clf_err_corrected'] = True
        record['m_a'] = m_a
        record['m_b'] = m_b
        record['t_a'] = t_a
        record['t_b'] = t_b
        record['h_a_hat'] = h_a_hat
        record['h_b_hat'] = h_b_hat
        record['top_20_hat'] = top_20_hat

        record_list.append(record)

print("Processed {}: {}.".format(INPUT_FILE,graph_idx))

with open(OUTPUT_FILE, 'wb') as f:
    pickle.dump(record_list, f)
