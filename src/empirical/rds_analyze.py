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
import pandas as pd

FILE_PATH = '/mnt/md0/network_sampling_data/TW_sample_single.json'

records = []

with open(FILE_PATH, 'r') as f:
    for line in f:
        record = {}
        j = json.loads(line)
        percent_male = j['percent_male']
        if percent_male == -1:
            continue
        record['male'] = round(percent_male)
        record['degree'] = j['friends'] + j['followers']
        records.append(record)

df = pd.DataFrame(records)
print(df.head())
print(df.shape)

# what fraction of the population is male
left_hand = 1 / (1 / df['degree'])
right_hand = df['male'] / df['degree']

print('The percentage of males is {}'.format(left_hand * right_hand))

# what's the number of crosslinks

# what's the coleman homophily measure
