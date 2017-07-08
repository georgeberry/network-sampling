import random
import networkx as nx
import numpy as np
import pandas as pd
from graph_gen import generate_powerlaw_group_graph
from graph_gen import generate_powerlaw_group_digraph
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
        return 1
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

def bootstrap_true_dist(degree_vector, mean_deg):
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


g = generate_powerlaw_group_graph(1000, 4, (0.6, 0.6), 0.6)
rds_df = sample_rds(g, 200, node_statistic_grp_deg)

boot_deg = bootstrap_true_dist(rds_df.degree, 8)
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





# old stuff


def sample_rds_directed(g, n, node_statistic):
    """
    Does a single chain starting from a random seed
    If you want multiple chains, run this multiple times

    Differs from undirected in that it samples uniformly from the successors
    and predecessors of the source node. In other words, take node i and
    get its outlinks (successors) and inlinks (predecessors)

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

    # random seed
    source = random.choice(g.nodes())
    degree_list.append(g.degree(source))
    node_statistic_list.append(node_statistic(g, source))

    # choose an inlink or outlink w equal probability
    while len(degree_list) < n:
        # Pick an edge to follow
        # So if we can jump either way, RDS works
        successors = g.successors(source)
        predecessors = g.predecessors(source)
        destination = random.choice(successors + predecessors)

        # destination = random.choice(g.neighbors(source))
        # add data here
        # do this for destination node
        degree_list.append(g.degree(destination))
        node_statistic_list.append(node_statistic(g, destination))
        # update
        source = destination
    deg_arr = np.array(degree_list)
    node_stat_arr = np.array(node_statistic_list)
    return deg_arr, node_stat_arr


def link_ratios_directed(g, n):
    """
    Follow outlinks (successors) only

    Samples a->b, b->a
    """
    counts = {
        ('a', 'b'): 0,
        ('b', 'a'): 0,
    }

    # random seed
    source = random.choice(g.nodes())
    hops = 0

    # choose an inlink or outlink w equal probability
    while hops < n:
        # Pick an edge to follow
        # So if we can jump either way, RDS works
        destination = random.choice(g.successors(source))

        # destination = random.choice(g.neighbors(source))
        # add data here
        # do this for destination node
        g1, g2 = g.node[source]['group'], g.node[destination]['group']
        if (g1, g2) in counts:
            counts[(g1, g2)] += 1
        # update
        source = destination
        hops += 1
    return counts

def restrict_graph(g):
    """
    Returns a new grpah with the 10pct most connected nodes removed
    """
    g = g.copy()
    degree_list = [
        {'idx': idx, 'degree': degree} for idx, degree in g.degree().items()
    ]
    df = pd.DataFrame(listg.degree().values())
    cutoff = df.degree.quantile(q=0.9)
    df = df.loc[df.degree > cutoff]
    g.remove_nodes_from(set(df.idx))
    return g


if __name__ == '__main__':
    g = generate_powerlaw_group_graph(1000, 4, (0.8, 0.8), 0.5)
    # deg_arr, node_stat_arr = sample_rds(g, 200, node_statistic_degree)
    # print(np.mean(deg_arr))
    # print(rds_estimate(deg_arr, node_stat_arr))

    # g = generate_powerlaw_group_digraph(2000, 4, (0.8, 0.8), 0.8)
    # deg_arr, node_stat_arr = sample_rds_directed(g, 200, node_statistic_degree)
    # print(np.mean(deg_arr))
    # print(rds_estimate(deg_arr, node_stat_arr))


    """
    pop = next(population(g))
    ratio = pop[1][('a', 'b')] / pop[1][('b', 'a')]

    samples = []
    for _ in range(100):
        counts = link_ratios_directed(g, 200)
        print(counts)
        samples.append(counts[('a', 'b')] / counts[('b', 'a')])

    print(pop)
    print(ratio)
    print(np.mean(samples))
    """


    """
    print(deg_arr)
    print(node_stat_arr)
    print(weight_rds(deg_arr, node_stat_arr))
    print(next(population(g)))
    """
