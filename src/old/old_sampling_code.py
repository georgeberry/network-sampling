from __future__ import division
import sys
sys.path.append('../../')
from science.constants import *
import networkx as nx
import numpy as np
import os
import random
from create_matched_network import random_edges, random_triad_edges_iter, random_unobserved_edges
import statsmodels.api as sm
import pandas as pd
import math
import json

"""
Sample on nodes unevenly based on characteristic
Look at real and sample homophily
Here's a run output:
"""

def edge_df_from_graph(g, edges, cov_name, tie_present=None):
    """
    graph must have node properties
    """
    diff_vals = []
    sum_vals = []
    for edge in edges:
        n1, n2 = edge
        attr1, attr2 = g.node[n1][cov_name], g.node[n2][cov_name]
        diff_vals.append(abs(attr1 - attr2))
        sum_vals.append(attr1 + attr2)
    df = pd.DataFrame({'diff': diff_vals, 'sum': sum_vals})
    df['constant'] = 1
    df['tie_present'] = tie_present
    return df

def create_df(
    g,
    samp_method,
    cov_name='cov'
    ):
    """
    Create n_rep replicants of the edge differences
    Create stacked df of event number of present/absent edges
    We can use these to look at the variability in our estimates due to sampling
    """
    assert samp_method in ['random', 'triad'], \
        '{} is not a valid sampling method'.format(samp_method)
    present_edges = list(g.edges_iter())
    triad_edge_iter = random_triad_edges_iter(g)
    if samp_method == 'random':
        absent_edges = random_edges(g)
    elif samp_method == 'triad':
        absent_edges = next(triad_edge_iter)
    present_df = edge_df_from_graph(
        g,
        present_edges,
        cov_name,
        tie_present=1,
    )
    absent_df = edge_df_from_graph(
        g,
        absent_edges,
        cov_name,
        tie_present=0,
    )
    assert len(present_edges) == len(absent_edges), \
        "Edge len diff {} to {}".format(
            len(present_edges),
            len(absent_edges),
        )
    combined_df = present_df.append(absent_df)
    return combined_df

def sample_from_graph(g, keep_pos=0.75, keep_neg=0.5):
    """
    remove nodes with bias
    keep cov=1 with prob keep_pos
    keep cov=0 with prob keep_neg
    """
    new_g = g.copy()
    rand_list = np.random.uniform(size=new_g.number_of_nodes())
    nodes_to_delete = []
    for node, attrs in new_g.nodes_iter(data=True):
        cov = attrs['cov']
        if cov == 1:
            if rand_list[node] > keep_pos:
                nodes_to_delete.append(node)
        elif cov == 0:
            if rand_list[node] > keep_neg:
                nodes_to_delete.append(node)
    new_g.remove_nodes_from(nodes_to_delete)
    return new_g

def test_coef_diff(b1, b2, se1, se2):
    Z = (b1 - b2) / math.sqrt(se1**2 + se2**2)
    return Z

def run_sim(
    g,
    homophily_param=0.7,
    selection_dict=None,
    ):
    covariate = np.random.randint(2, size=g.number_of_nodes())
    for node, attr in g.nodes_iter(data=True):
        attr['cov'] = covariate[node]
    # add homophily
    for n1, n2 in g.edges_iter():
        attr1, attr2 = g.node[n1]['cov'], g.node[n2]['cov']
        if attr1 != attr2:
            draw = np.random.uniform()
            if draw > homophily_param:
                g.node[n2]['cov'] = attr1
    samp_g = sample_from_graph(g, **selection_dict)
    #print(nx.attribute_mixing_matrix(g, 'cov', normalized=False))
    #print(nx.attribute_mixing_matrix(samp_g, 'cov', normalized=False))
    df = create_df(g, 'random')
    samp_df = create_df(samp_g, 'random')
    y_full = df['tie_present']
    X_full = df[['constant', 'diff', 'sum']]
    mod_full = sm.OLS(y_full, X_full)
    res_full = mod_full.fit()
    y_samp = samp_df['tie_present']
    X_samp = samp_df[['constant', 'diff', 'sum']]
    mod_samp = sm.OLS(y_samp, X_samp)
    res_samp = mod_samp.fit()
    b1, b2 = res_full.params[1], res_samp.params[1]
    se1, se2 = res_full.bse[1], res_samp.bse[1]
    Z_val = test_coef_diff(b1, b2, se1, se2)
    return Z_val

def sim_rep(
    g,
    n,
    homophily_param=0.7,
    selection_dict={'keep_pos': 0.75, 'keep_neg': 0.5},
    ):
    sim_results = {'reject null': 0, 'dont reject null': 0}
    for _ in range(n):
        z = run_sim(g.copy())
        if abs(z) > 1.96:
            sim_results['reject null'] += 1
        else:
            sim_results['dont reject null'] += 1
    return sim_results

def write_output(
    results,
    graph_type,
    homophily_param,
    pos_param,
    neg_param,
    cov_name=None
    ):
    output_dict = {
        'graph_type': graph_type,
        'homophily_param': homophily_param,
        'positive_keep_param': pos_param,
        'negative_keep_param': neg_param,
        'results': results,
        'cov_name': cov_name,
    }
    print('{} with [{}, {}, {}]'.format(
        graph_type,
        homophily_param,
        pos_param,
        neg_param)
    )
    with open('sim_runs.json', 'a') as f:
        f.write(json.dumps(output_dict) + '\n')



# empirical fns #

def sample_from_graph_empirical(g, cov_name, keep_pos=0.75, keep_neg=0.5):
    """
    remove nodes with bias
    keep cov=1 with prob keep_pos
    keep cov=0 with prob keep_neg
    """
    new_g = g.copy()
    rand_list = np.random.uniform(size=new_g.number_of_nodes())
    nodes_to_delete = []
    for node, attrs in new_g.nodes_iter(data=True):
        cov = attrs[cov_name]
        if cov == 1:
            if rand_list[node] > keep_pos:
                nodes_to_delete.append(node)
        elif cov == 0:
            if rand_list[node] > keep_neg:
                nodes_to_delete.append(node)
    new_g.remove_nodes_from(nodes_to_delete)
    return new_g

def run_sim_empirical(
    g,
    selection_dict,
    cov_name,
    ):
    samp_g = sample_from_graph_empirical(g, cov_name, **selection_dict)
    #print(nx.attribute_mixing_matrix(g, 'cov', normalized=False))
    #print(nx.attribute_mixing_matrix(samp_g, 'cov', normalized=False))
    df = create_df(g, 'random', cov_name)
    samp_df = create_df(samp_g, 'random', cov_name)
    y_full = df['tie_present']
    X_full = df[['constant', 'diff', 'sum']]
    mod_full = sm.OLS(y_full, X_full)
    res_full = mod_full.fit()
    y_samp = samp_df['tie_present']
    X_samp = samp_df[['constant', 'diff', 'sum']]
    mod_samp = sm.OLS(y_samp, X_samp)
    res_samp = mod_samp.fit()
    b1, b2 = res_full.params[1], res_samp.params[1]
    se1, se2 = res_full.bse[1], res_samp.bse[1]
    Z_val = test_coef_diff(b1, b2, se1, se2)
    return Z_val

def sim_rep_empirical(
    g,
    n,
    cov_name,
    selection_dict,
    ):
    sim_results = {'reject null': 0, 'dont reject null': 0}
    for _ in range(n):
        z = run_sim(g.copy(), selection_dict, cov_name)
        if abs(z) > 1.96:
            sim_results['reject null'] += 1
        else:
            sim_results['dont reject null'] += 1
    return sim_results

def check_not_all_same(g):
    attrs_to_check = {}
    for node, attrs in g.nodes_iter(data=True):
        for k, v in attrs.items():
            if k in attrs_to_check:
                # if the attribute is different from one we've seen
                if attrs_to_check[k] != v:
                    return True
            else:
                attrs_to_check[k] = v
    return False

def clean_empirical_graph(g):
    """pop names"""
    for node, attrs in g.nodes_iter(data=True):
        attrs.pop('name')

if __name__ == '__main__':
    n_node = 1000
    n_rep = 100
    homophily_params = np.linspace(0.1, 0.9, num=9)
    pos_keep_probs = np.linspace(0.1, 0.9, num=9)
    neg_keep_probs = np.linspace(0.1, 0.9, num=9)

    # sim using empirical graph #

    path = '/Users/g/Google Drive/project-RA/educ/myp/data/empirical_graphs/graphml/'

    graph_files = os.listdir(path)
    for gf in graph_files:
        g = nx.read_graphml(path + gf)
        clean_empirical_graph(g)
        cov_names = g.node[g.node.keys()[0]].keys()
        if check_not_all_same(g):
            for cov_name in cov_names:
                for pkp in pos_keep_probs:
                    for nkp in neg_keep_probs:
                        res = sim_rep(
                            g,
                            n_rep,
                            cov_name,
                            selection_dict={'keep_pos':pkp, 'keep_neg':nkp},
                        )
                        write_output(
                            res,
                            gf,
                            'empirical',
                            pkp,
                            nkp,
                            cov_name,
                        )


    """
    # pure simulation #
    for hp in homophily_params:
        for pkp in pos_keep_probs:
            for nkp in neg_keep_probs:
                name = 'watts strogatz'
                g = nx.watts_strogatz_graph(n_node, 10, .1)
                res = sim_rep(
                    g,
                    n_rep,
                    homophily_param=hp,
                    selection_dict={'keep_pos':pkp, 'keep_neg':nkp},
                )
                write_output(res, name, hp, pkp, nkp)
                name = 'powerlaw'
                h = nx.barabasi_albert_graph(n_node, 5)
                res = sim_rep(
                    h,
                    n_rep,
                    homophily_param=hp,
                    selection_dict={'keep_pos':pkp, 'keep_neg':nkp},
                )
                write_output(res, name, hp, pkp, nkp)
                name = 'powerlaw + clustering'
                i = nx.powerlaw_cluster_graph(n_node, 5, .1)
                res = sim_rep(
                    i,
                    n_rep,
                    homophily_param=hp,
                    selection_dict={'keep_pos':pkp, 'keep_neg':nkp},
                )
                write_output(res, name, hp, pkp, nkp)
    """
