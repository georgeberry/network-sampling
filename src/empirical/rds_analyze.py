"""
Each user in the crawl has the following field:

_id: mongo id
twitter_id: {'$numberLong': 'tw_id'}
full_name: string name
screen_name: string screen name
next: {'$numberLong': 'tw_id'}
prev: {'$numberLong': 'tw_id'}
tweets: [tweet_dict1, ...]
friends: num friends
followers: num followers
run: not used
percent_male: percent male of name, -1 for does not appear
i: number in chain of graph

"""
import json
import networkx as nx
import pandas as pd

FILE_PATH = '/mnt/md0/network_sampling_data/TW_sample_single.json'

g = nx.Graph()

def get_id(candidate):
    if type(candidate) == dict:
        return candidate['$numberLong']
    if type(candidate) == int:
        return candidate
    if type(candidate) == str:
        return int(candidate)
    return None

with open(FILE_PATH, 'r') as f:
    counter = 0
    for line in f:
        record = {}
        j = json.loads(line)
        percent_male = j['percent_male']
        if percent_male == -1:
            continue

        twitter_id = get_id(j['twitter_id'])
        next_id = get_id(j['next'])
        prev_id = get_id(j['prev'])

        g.add_node(twitter_id)
        g.node[twitter_id]['male'] = percent_male
        g.node[twitter_id]['degree'] =  j['friends'] + j['followers']

        if next_id:
            g.add_edge(twitter_id, next_id)
        if prev_id:
            g.add_edge(twitter_id, prev_id)

        counter += 1
        if counter % 100 == 0:
            print(counter)

record_list = []
for n, attr in g.nodes_iter(data=True):
    if len(attr) > 0:
        record_list.append(attr)

df = pd.DataFrame(record_list)
print(df.head())
print(df.shape)

# what fraction of the population is male
left_hand = 1 / sum(1 / df['degree'])
right_hand = sum(df['male'] / df['degree'])

print('The percentage of males is {}'.format(left_hand * right_hand))

# what's the number of crosslinks


# what's the coleman homophily measure
