from pymongo import MongoClient

def homophily_group_parity(node):
	return (node['twitter_id'] % 2)

def gender_from_database(node):
	if node["percent_male"] >= .5:
		return 1
	elif node["percent_male"] >= 0:
		return 0
	else:
		return -1

class EdgeCounter(object):
	def __init__(self, first_node, h, func, coll):
		self.node = first_node
		self.h = h
		self.func = func
		self.coll = coll

	def __call__(self):
		pass

def compute_edge_types(login = False, func = homophily_group_parity):
	if not login:
		client = MongoClient()
	else:
		uname = input("Username: ")
		pwd = input("Password: ")
		client = MongoClient('mongodb://' + uname + ':' + pwd + '@127.0.0.1')

	coll = client['fake_news']['TW_sample']

	h = {
		(0,0): 0,
		(0,1): 0,
		(1,0): 0,
		(1,1): 0
	}

	#find all starts of chainns
	i = 0
	for start in coll.find({'prev':None}):
		i += 1
		if (i % 100) == 0:
			print('Processed: ' + str(i))
		for next_id in start['next']:
			next_node = coll.find_one({'twitter_id':next_id, 'run':start['run']})
			if next_node is not None:
				process_edge(start, next_node, h, func, coll, 0)

	print(h)


def process_edge(node, next_node, h, func, coll, depth):
	if depth > 100:
		print('Depth: ' + str(depth))
		print(node['twitter_id'])
		return
	group1 = func(node)
	group2 = func(next_node)
	if group1 != -1 and group2 != -1:
		h[(group1,group2)] += 1
	for next_again_id in next_node['next']:
		next_again = coll.find_one({'twitter_id':next_again_id, 'run':next_node['run']})
		if next_again is not None:
			process_edge(next_node, next_again, h, func, coll, depth + 1)