import random
import networkx as nx
import numpy as np
import pandas as pd
from graph_gen import generate_powerlaw_group_graph
from sampling_methods import population
import math
from plotnine import *
import collections

"""
Record data for rds analysis
"""

### statistic functions
"""
node statistics accept (g, node)
edge statistics accept (g, source, destination)

these must return a number
"""


def node_statistic_group_a(g, node):
    """
    Node group
    """
    if g.node[node]['group'] == 'a':
        return 1, ['group']
    return 0, ['group']

def node_statistic_degree(g, node):
    """
    Node degree
    """
    return g.degree(node), ['degree_2']

def node_statistic_grp_deg(g, node):
    """
    Want to sample the fraction of group 'a' nodes in top 20 pct of degree
    """
    deg = g.degree(node)
    grp = g.node[node]['group']
    return (deg, grp), ['degree_2', 'group']

### sample function

def sample_rds(g, n, node_statistic):
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

    # random seed
    source = random.choice(g.nodes())
    degree_list.append(g.degree(source))
    node_stat, colnames = node_statistic(g, source)
    node_statistic_list.append(node_stat)

    while len(degree_list) < n:
        # Pick an edge to follow
        destination = random.choice(g.neighbors(source))
        # add data here
        # do this for destination node
        degree_list.append(g.degree(destination))
        node_stat, colnames = node_statistic(g, destination)
        node_statistic_list.append(node_stat)
        # update
        source = destination
    df = pd.DataFrame(node_statistic_list)
    df.columns = colnames
    df['degree'] = degree_list
    return df

def sample_reweighted(g, n, node_statistic):
    rds_sample = sample_rds(g, n, node_statistic)
    mu = rds_estimate(rds_sample, 'degree')
    boot_df = boot_with_attr(rds_sample, mu)
    return boot_df

def sample_edges(g, n, node_statistic):
    node_statistic_list = []
    degree_list = []
    colnames = None

    while len(degree_list) < n:
        edge = random.choice(g.edges())
        for node in edge:
            if len(degree_list) < n:
                degree_list.append(g.degree(node))
                node_stat, colnames = node_statistic(g, node)
                node_statistic_list.append(node_stat)
    df = pd.DataFrame(node_statistic_list)
    df.columns = colnames
    df['degree'] = degree_list
    return df

def sample_nodes(g, n, node_statistic):
    node_statistic_list = []
    degree_list = []
    colnames = None

    while len(degree_list) < n:
        node = random.choice(g.nodes())
        degree_list.append(g.degree(node))
        node_stat, colnames = node_statistic(g, node)
        node_statistic_list.append(node_stat)
    df = pd.DataFrame(node_statistic_list)
    df.columns = colnames
    df['degree'] = degree_list
    return df

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

def sample_snowball(g, n, node_statistic):
    node_statistic_list = []
    degree_list = []
    colnames = None

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

                if not len(degree_list) < n:
                    break
            if not len(degree_list) < n:
                break
        frontier = next_frontier

    df = pd.DataFrame(node_statistic_list)
    df.columns = colnames
    df['degree'] = degree_list
    return df

def rds_estimate(df, focal_column):
    """
    Inputs:
        deg_arr: vector of degrees
        stat_arr: vector of measurements
    Outputs:
        p_hat = 1 / (sum (1 / d_i)) * sum (statistic / d_i)
            aka the RDS estimate of p
    """
    left_hand = 1 / np.sum(1 / df['degree'])
    right_hand = np.sum(df[focal_column] / df['degree'])
    return left_hand * right_hand

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

def top_20pct_true(g):
    degree_dict = g.degree()
    record_list = []
    for idx, attr in g.nodes_iter(data=True):
        attr['degree'] = degree_dict[idx]
        attr['idx'] = idx
        record_list.append(attr)
    df = pd.DataFrame(record_list)
    return top_20pct(df)

def top_20pct(df):
    """
    top 20pct of the df by degree
    """
    df = df.sort_values('degree', ascending=False)
    rows, cols = df.shape
    head = df.head(math.floor(rows/5))
    return head.group.value_counts()

def importance_resample(degree_vector, mean_deg):
    """
    samples from degree vector where each element is pulled with probability proportional to mean_deg / d

    we make this into a probability for sampling with
        (mean_deg / d) / (sum mean_deg / d)
    """
    p = (mean_deg / degree_vector) / sum((mean_deg / degree_vector))
    return list(np.random.choice(degree_vector, size=1000, replace=True, p=p))

def boot_with_attr(df, mean_deg):
    """
    pass df with degree col
    """
    p = (mean_deg / df.degree) / sum((mean_deg / df.degree))
    sample_idxs =  list(
        np.random.choice(list(range(len(df))), size=1000, replace=True, p=p)
    )
    return df.iloc[sample_idxs,:]

def deg_prob(deg_list):
    c = collections.Counter(deg_list)
    total = sum(list(c.values()))
    prob_dict = {k: v / total for k, v in c.items()}
    return [prob_dict[x] for x in deg_list]

def misclassify_nodes(g, p):
    for n, attr in g.nodes_iter(data=True):
        grp = attr['group']
        if random.random() < p:
            if grp == 'a':
                attr['group'] = 'b'
            if grp == 'b':
                attr['group'] = 'a'
    return g

def importance_resample_with_correction(
    focal_vector,
    degree_vector,
    mean_deg,
    p_misclassify, # probability of misclassifying focal vector
):
    # importance sampling weights
    p = (mean_deg / degree_vector) / sum((mean_deg / degree_vector))

    resample = np.random.choice(focal_vector, size=5000, replace=True, p=p)

    #print('naive estimate: {}'.format(resample.mean()))

    # correct here for classifier error
    m_a = resample.mean()
    m_b = 1 - m_a

    c_ab, c_ba = p_misclassify, p_misclassify
    c_aa, c_bb = 1 - c_ab, 1 - c_ba

    # p convert to a given classified as b
    a_given_b_correction_factor = (c_ab / m_b) * (m_a * c_bb - m_b * c_ba) / (c_aa * c_bb - c_ba * c_ab)
    print(a_given_b_correction_factor)

    # p convert to b given classified as a
    b_given_a_correction_factor = (c_ba / m_a) * (m_b * c_aa - m_a * c_ab) / (c_aa * c_bb - c_ba * c_ab)
    print(b_given_a_correction_factor)

    f = []

    for val in resample:
        if val == 1 and random.random() < b_given_a_correction_factor:
            f.append(0)
        elif val == 0 and random.random() < a_given_b_correction_factor:
            f.append(1)
        else:
            f.append(val)

    s = pd.Series(f)

    #print('better estimate: {}'.format(s.mean()))

    output_list = [
        {'kind': 'uncorrected', 'value': resample.mean()},
        {'kind': 'corrected', 'value': s.mean()},
    ]

    return output_list

if __name__ == '__main__':
g = generate_powerlaw_group_graph(10000, 4, (0.6, 0.6), 0.6)
g = misclassify_nodes(g, p=0.3)

rds_df = sample_rds(g, 1000, node_statistic_group_a)
mean_deg_hat = rds_estimate(rds_df, 'degree')

m_a = rds_df.group.mean()
m_b = 1 - m_a

c_ab, c_ba = 0.3, 0.3
c_aa, c_bb = 1 - c_ab, 1 - c_ba

# p convert to a given classified as b
a_given_b_correction_factor = (c_ab / m_b) * (m_a * c_bb - m_b * c_ba) / (c_aa * c_bb - c_ba * c_ab)

# p convert to b given classified as a
b_given_a_correction_factor = (c_ba / m_a) * (m_b * c_aa - m_a * c_ab) / (c_aa * c_bb - c_ba * c_ab)

m_a * b_given_a_correction_factor + m_b * (1 - a_given_b_correction_factor)

m_b * a_given_b_correction_factor + m_a * (1 - b_given_a_correction_factor)

m = np.array([m_a, 1 - m_a])
C = np.array([
    [c_aa, c_ba],
    [c_ab, c_bb],
])

print(m)
print(inv(C).dot(m))





vals = []
while len(vals) < 1000:
    boot_deg = importance_resample_with_correction(
        rds_df.group,
        rds_df.degree,
        mean_deg_hat,
        p_misclassify=0.3,
    )
    vals.extend(boot_deg)

pd.DataFrame(vals).to_csv('/Users/g/Documents/network-sampling/test_resample.tsv', sep='\t')

    """
    boot_deg = importance_resample(rds_df.degree, 8)
    true_deg = list(g.degree().values())

    df = pd.DataFrame(
        [(x, 'boot') for x in boot_deg] + [(x, 'true') for x in true_deg]
    )
    df.columns = ['degree', 'kind']
    (ggplot(df) +
        geom_density(aes('degree', color='kind')) +
        theme_bw()
    )

    df = pd.DataFrame({
        'log_prob': deg_prob(boot_deg) + deg_prob(true_deg),
        'log_degree': boot_deg + true_deg,
        'kind': ['boot' for x in boot_deg] + ['true' for x in true_deg],
    })
    (ggplot(df) +
        aes(x='log_degree', y='log_prob', color='kind') +
        geom_point() +
        coord_trans(x = "log10", y = "log10")
    )





    # estimate proportion of group b in top 20pct
    diffs = []

    for _ in range(10):
        g = generate_powerlaw_group_graph(1000, 4, (0.7, 0.7), 0.7)
        for _ in range(100):
            rds_df = sample_rds(g, 200, node_statistic_grp_deg)
            mu = rds_estimate(rds_df, 'degree')
            boot_df = boot_with_attr(rds_df, mu)
            true = top_20pct_true(g)
            true_prob = true['b'] / true.sum()
            test = top_20pct(boot_df)
            test_prob = test['b'] / test.sum()
            diffs.append(true_prob - test_prob)
        print(np.mean(diffs))
        diffs = []

    df = sample_rds(g, 200, node_statistic_degree)
    rds_estimate(df, 'degree')
    """
