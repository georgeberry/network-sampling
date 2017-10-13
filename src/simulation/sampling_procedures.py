import random
import networkx as nx
import numpy as np
from numpy.linalg import inv
import pandas as pd
import math
# from plotnine import *
import collections
from typing import Dict, Callable

#### Some helpers ##############################################################

def misclassify_nodes(g, p):
    """
    Returns deepcopy of g with p percent of every group misclassified
    """
    for node, attr in g.nodes_iter(data=True):
        group = attr['group']
        if random.random() < p:
            if group == 'a':
                attr['group'] = 'b'
            elif group == 'b':
                attr['group'] = 'a'
    return g

def get_correct_group_proportions(m_a, m_b, p_misclassify):
    m = np.array([m_a, m_b])
    p = 1 - p_misclassify
    e = p_misclassify
    C = np.array([
        [p, e],
        [e, p],
    ])
    m_a, m_b = inv(C).dot(m)
    return m_a, m_b

def get_correct_crosslink_proportions(
    l_aa_hat,
    l_ab_hat,
    l_bb_hat,
    p_misclassify,
):
    link_sum = l_aa_hat + l_ab_hat + l_bb_hat
    t = np.array([l_aa_hat, l_ab_hat, l_bb_hat]) / link_sum
    p = 1 - p_misclassify # p right
    e = p_misclassify     # p wrong
    M = np.array([
        [  p*p,     p*e,   e*e],
        [2*p*e, p*p+e*e, 2*p*e],
        [  e*e,     e*p,   p*p],
    ])
    return inv(M).dot(t)


def get_correct_top20(df, p_misclassify):
    rows, cols = df.shape
    top_20_df = df.head(math.floor(rows/5))
    m_b = top_20_df.group.mean()
    m_a = 1 - m_b
    p_hat = get_correct_group_proportions(m_a, m_b, p_misclassify)
    return p_hat[1]


def update_crosslink_dict(g, edge, crosslink_dict):
    n1, n2 = edge
    src_grp = g.node[n1]['group']
    dst_grp = g.node[n2]['group']
    sorted_edge_grps = tuple(sorted((src_grp, dst_grp)))
    crosslink_dict[sorted_edge_grps] += 1

#### RDS functions #############################################################

def sample_reweighted(g, n, node_statistic):
    rds_sample, crosslink_dict = sample_rds(g, n, node_statistic)
    mu = rds_estimate(rds_sample, 'degree')
    boot_df = boot_with_attr(rds_sample, mu)
    return boot_df

def boot_with_attr(df, mean_deg, n=1000):
    """
    pass df with degree col
    """
    p = (mean_deg / df.degree) / sum((mean_deg / df.degree))
    sample_idxs =  list(
        np.random.choice(list(range(len(df))), size=n, replace=True, p=p)
    )
    return df.iloc[sample_idxs,:]

def rds_estimate(rds_df, focal_column):
    """
    Inputs:
        deg_arr: vector of degrees
        stat_arr: vector of measurements
    Outputs:
        p_hat = 1 / (sum (1 / d_i)) * sum (statistic / d_i)
            aka the RDS estimate of p
    """
    left_hand = 1 / np.sum(1 / rds_df['degree'])
    right_hand = np.sum(rds_df[focal_column] / rds_df['degree'])
    return left_hand * right_hand


#### Homophily function ########################################################

def colemans_h(group_proportion, ingroup_link_proportion):
    p_x = group_proportion
    p_xx = ingroup_link_proportion

    # handle p_x = 0 or 1
    if p_x >= 1:
        return None
    elif p_x <= 0:
        return None

    if p_xx >= p_x:
        return (p_xx - p_x) / (1 - p_x)
    if p_xx < p_x:
        return (p_xx - p_x) / p_x


#### statistic functions #######################################################

def node_statistic_grp_b(g, node):
    """
    Node in b
    """
    if g.node[node]['group'] == 'b':
        return 1, ['group']
    return 0, ['group']


#### sample functions ##########################################################

def population(g):
    """
    True values in the graph
    """
    node_counts = {
        'a': 0,
        'b': 0,
    }
    link_counts = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
    }
    for n1, n2 in g.edges_iter():
        grp1, grp2 = g.node[n1]['group'], g.node[n2]['group']
        sorted_edge_grps = tuple(sorted((grp1, grp2)))
        link_counts[sorted_edge_grps] += 1
    for idx, attr in g.nodes_iter(data=True):
        node_counts[attr['group']] += 1
    return node_counts, link_counts


def sample_rds(
    g: nx.Graph,
    n: int,
    node_statistic: Callable,
):
    """
    Does a single chain starting from a random seed
    If you want multiple chains, run this multiple times

    Inputs:
        g: graph
        n: number of nodes to sample
        node_statistic: a function of a node to compute, takes (g, node)
    Outputs:
        node_statistic_list
        degree_list
    """
    node_statistic_list = []
    degree_list = []
    colnames = None

    crosslink_dict = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
    }

    nodes = g.nodes()

    # random seed
    source = random.choice(nodes)
    degree_list.append(g.degree(source))
    node_stat, colnames = node_statistic(g, source)
    node_statistic_list.append(node_stat)

    while len(degree_list) < n:
        # Pick an edge to follow
        destination = random.choice(g.neighbors(source))
        update_crosslink_dict(g, (source, destination), crosslink_dict)
        # add data here
        degree_list.append(g.degree(destination))
        node_stat, colnames = node_statistic(g, destination)
        node_statistic_list.append(node_stat)
        # update
        source = destination
    df = pd.DataFrame(node_statistic_list)
    df.columns = colnames
    df['degree'] = degree_list
    return df, crosslink_dict


def sample_edges(g, n, node_statistic):
    node_statistic_list = []
    degree_list = []
    visited_nodes = set()
    colnames = None
    crosslink_dict = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
    }
    edges = g.edges()


    while len(degree_list) < n:
        edge = random.choice(edges)
        update_crosslink_dict(g, edge, crosslink_dict)
        for node in edge:
            if len(degree_list) < n:
                degree_list.append(g.degree(node))
                node_stat, colnames = node_statistic(g, node)
                node_statistic_list.append(node_stat)
                visited_nodes.add(node)

    df = pd.DataFrame(node_statistic_list)
    df.columns = colnames
    df['degree'] = degree_list
    return df, crosslink_dict


def sample_nodes(g, n, node_statistic):
    node_statistic_list = []
    degree_list = []
    visited_nodes = set()
    colnames = None
    crosslink_dict = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
    }
    nodes = g.nodes()

    while len(degree_list) < n:
        node = random.choice(nodes)
        visited_nodes.add(node)
        degree_list.append(g.degree(node))
        node_stat, colnames = node_statistic(g, node)
        node_statistic_list.append(node_stat)

    s = g.subgraph(nbunch=visited_nodes)
    for edge in s.edges_iter():
        update_crosslink_dict(g, edge, crosslink_dict)

    df = pd.DataFrame(node_statistic_list)
    df.columns = colnames
    df['degree'] = degree_list
    return df, crosslink_dict

"""
def sample_ego_networks(g, n, node_statistic):
    node_statistic_list = []
    degree_list = []
    colnames = None

    while len(degree_list) < n:
        node = random.choice(g.nodes())
        degree_list.append(g.degree(node))
        node_stat, colnames = node_statistic(g, node)
        node_statistic_list.append(node_stat)

        s = nx.ego_graph(g, node)
        s.remove_node(node)
        for alter in random.sample(s.nodes(), k = len(s.nodes())):
            if len(degree_list) < n:
                degree_list.append(g.degree(alter))
                node_stat, colnames = node_statistic(g, alter)
                node_statistic_list.append(node_stat)

    df = pd.DataFrame(node_statistic_list)
    df.columns = colnames
    df['degree'] = degree_list
    return df
"""


def sample_snowball(g, n, node_statistic):
    node_statistic_list = []
    degree_list = []
    colnames = None
    crosslink_dict = {
        ('a', 'a'): 0,
        ('a', 'b'): 0,
        ('b', 'b'): 0,
    }

    seed = random.choice(g.nodes())
    visited_nodes = set()
    frontier = set([seed])
    degree_list.append(g.degree(seed))
    node_stat, colnames = node_statistic(g, seed)
    node_statistic_list.append(node_stat)

    while frontier and len(degree_list) < n:
        next_frontier = set()
        for node in frontier:
            for neighbor in g.neighbors(node):
                if neighbor not in visited_nodes and len(degree_list) < n:
                    visited_nodes.add(neighbor)
                    degree_list.append(g.degree(neighbor))
                    node_stat, colnames = node_statistic(g, neighbor)
                    node_statistic_list.append(node_stat)
                    next_frontier.add(neighbor)
                    update_crosslink_dict(g, (node, neighbor), crosslink_dict)

                if len(degree_list) >= n:
                    break
            if len(degree_list) >= n:
                break
        frontier = next_frontier

    df = pd.DataFrame(node_statistic_list)
    df.columns = colnames
    df['degree'] = degree_list
    return df, crosslink_dict

#### begin hacking #############################################################

def test_rank(df, q=0.8):
    s = df.degree
    cutoff = s.quantile(q=q)
    df['group_a'] = [1 if x == 'a' else 0 for x in df.group]
    df['top_twenty'] = [1 if x >= cutoff else 0 for x in df.degree]
    df['top_twenty_grp_a'] = df.group_a.multiply(df.top_twenty)
    left_hand = 1 / np.sum(1 / df.degree)
    right_hand = np.sum(df.top_twenty_grp_a / df.degree)
    return left_hand * right_hand / .2

def true_rank(g):
    degree_dict = g.degree()
    record_list = []
    for idx, attr in g.nodes_iter(data=True):
        attr['degree'] = degree_dict[idx]
        attr['idx'] = idx
        record_list.append(attr)
    df = pd.DataFrame(record_list)
    cutoff = df.degree.quantile(q=0.8)
    df['group_a'] = [1 if x == 'a' else 0 for x in df.group]
    df['top_twenty'] = [1 if x >= cutoff else 0 for x in df.degree]
    df['top_twenty_grp_a'] = df.group_a.multiply(df.top_twenty)
    return df.top_twenty_grp_a.mean()


def get_true_top_20pct_minority_grp(
    g: nx.Graph,
) -> float:
    record_list = []
    for idx, attr in g.nodes_iter(data=True):
        record = {
            'degree': g.degree(idx),
            'group': attr['group'] == 'b'
        }
        record_list.append(record)
    df = pd.DataFrame(record_list)
    df = df.sort_values('degree', ascending=False)
    df = df.head(math.floor(df.shape[0]/5))
    return df['group'].mean()

def get_top_20pct_true(g: nx.Graph) -> pd.DataFrame:
    degree_dict = g.degree()
    record_list = []
    for idx, attr in g.nodes_iter(data=True):
        attr['degree'] = degree_dict[idx]
        attr['idx'] = idx
        record_list.append(attr)
    df = pd.DataFrame(record_list)
    return get_top_20pct(df)

def get_top_20pct(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns top 20% of data frame sorted by 'degree' column
    """
    df = df.sort_values('degree', ascending=False)
    rows, cols = df.shape
    df = df.head(math.floor(rows/5))
    return df.group.mean()

def importance_resample(degree_vector, mean_deg):
    """
    samples from degree vector where each element is pulled with probability proportional to mean_deg / d

    we make this into a probability for sampling with
        (mean_deg / d) / (sum mean_deg / d)
    """
    p = (mean_deg / degree_vector) / sum((mean_deg / degree_vector))
    return list(np.random.choice(degree_vector, size=1000, replace=True, p=p))


def get_importance_resample_top20_with_correction(
    df: pd.DataFrame,
    mean_deg: float, # mean degree or its estimate
    p_misclassify: float, # probability of misclassifying groups
) -> float:
    # resamp_df = boot_with_attr(df, mean_deg, n=20000)
    resamp_df = df

    C = np.array([
        [1 - p_misclassify, p_misclassify],
        [p_misclassify, 1 - p_misclassify],
    ])
    resamp_df = resamp_df.sort_values('degree', ascending=False)
    rows, cols = resamp_df.shape
    top_20_df = resamp_df.head(math.floor(rows/5))
    m_b = top_20_df.group.mean()
    m_a = 1 - m_b

    m = np.array([m_a, m_b])

    p_hat = inv(C).dot(m)
    p_b_hat = p_hat[1]

    return p_b_hat

    """
    # correct here for classifier error
    m_b = resamp_df.group.mean()
    m_a = 1 - m_b

    c_ab, c_ba = p_misclassify, p_misclassify
    c_aa, c_bb = 1 - p_misclassify, 1 - p_misclassify

    # p convert to a given classified as b
    # a_given_b_correction_factor = (c_ab / m_b) * (m_a * c_bb - m_b * c_ba) / (c_aa * c_bb - c_ba * c_ab)

    p_a_hat = (m_a * c_bb - m_b * c_ba) / (c_aa * c_bb - c_ba * c_ab)
    p_b_hat = (m_b * c_aa - m_a * c_ab) / (c_aa * c_bb - c_ba * c_ab)

    # p convert to b given classified as a
    b_given_a_correction_factor = (c_ba / m_a) * p_b_hat

    # p convert to b given classified as b
    b_given_b_correction_factor = (c_bb / m_b) * p_b_hat

    # get top 20pct
    resamp_df = resamp_df.sort_values('degree', ascending=False)
    rows, cols = resamp_df.shape

    top_20_df = resamp_df.head(math.floor(rows/5))

    mm_b = top_20_df.group.mean()
    mm_a = 1 - mm_b

    print(
        p_a_hat,
        p_b_hat,
        b_given_a_correction_factor,
        b_given_b_correction_factor,
    )

    print('estimate: {}'.format(mm_b))

    better_estimate = mm_b * b_given_b_correction_factor + mm_a * b_given_a_correction_factor


    print('better estimate: {}'.format(better_estimate))

    return better_estimate
    """
