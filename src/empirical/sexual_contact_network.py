"""
Run this to make the sexual contact network and save it
Then run run_sim_existing.py pointing at it with 100 reps

Males are the larger group so we assign male = a, female = b

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
    node_to_gender_dict[female] = 'b'
    node_to_gender_dict[male] = 'a'

g = nx.Graph()
g.add_edges_from(edges)
nx.set_node_attributes(g, 'group', node_to_gender_dict)
nx.set_node_attributes(g, 'degree', g.degree())
g.graph['params'] = {
    'num_nodes': g.number_of_nodes(),
    'homophily': [None, None],
    'idx': None,
}
g = max(nx.connected_component_subgraphs(g), key=len)

nx.write_gpickle(g, '../../data/sexual_contact/graph.p')
