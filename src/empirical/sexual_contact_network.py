"""
Data from:
  http://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1001109

# 1st column: Female-id
# 2nd column: Male-id
# 3rd column: Date (in days) of posting
# 4th column: Female grade given by the male (Bad: -1, Neutral: 0, Good: +1)
# 5th column: Anal sex with/without condom?  (Yes: +1, No: -1, Information not available: 0)
# 6th column: Oral sex with condom?          (Yes: +1, No: -1, Information not available: 0)
# 7th column: Mouth kiss?                    (Yes: +1, No: -1, Information not available: 0)
"""
import networkx as nx
import pandas as pd

import sys
sys.path.append('..')

from simulation.rds import *

#### node statistic functions ##################################################

def node_statistic_female(g, node):
    if g.node[node]['gender'] == 'female':
        return 1, ['gender']
    return 0, ['gender']

#### do the thing! #############################################################

df = pd.read_csv(
    '/Users/g/Drive/project-RA/network-sampling/data/sexual_contact/journal.pcbi.1001109.s001.csv',
    sep=';',
    skiprows=24,
    header=None)
df.columns = [
    'female_id',
    'male_id',
    'date',
    'female_grade',
    'anal_sex',
    'oral_sex',
    'kiss',
]

edges = [
    (series['female_id'], series['male_id']) for idx, series in df.iterrows()
]

node_to_gender_dict = {}
for female, male in edges:
    node_to_gender_dict[female] = 'female'
    node_to_gender_dict[male] = 'male'

g = nx.Graph()
g.add_edges_from(edges)
nx.set_node_attributes(g, 'gender', node_to_gender_dict)
nx.set_node_attributes(g, 'degree', g.degree())
g = max(nx.connected_component_subgraphs(g), key=len)

gender_sum = 0
degree_sum = 0
for _, attr in g.nodes_iter(data=True):
    if attr['gender'] == 'female':
        gender_sum += 1
    degree_sum += attr['degree']

print((
    'True gender: {}'
    'True degree: {}'.format(gender_sum / len(g), degree_sum / len(g))
))

rds_df = sample_rds(g, 1000, node_statistic_female)
mu_gender = rds_estimate(rds_df, 'gender')
mu_degree = rds_estimate(rds_df, 'degree')

print((
    'Estimated gender: {}'
    'Estimated degree: {}'.format(mu_gender, mu_degree)
))
