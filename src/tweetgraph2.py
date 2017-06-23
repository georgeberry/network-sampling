import twitter
import random
from pymongo import MongoClient

api = twitter.Api(consumer_key = 'biSMSPUJdGmWkfZTA7SzTjfov',
		consumer_secret = 'EMgEUz7Xs3Zo0BlzGswmLnmBSFowcUgiCUVtmIk9cprH6r9Rq3',
		access_token_key = '547328231-8WNipAFTBlaePvV8jytKiZ2z5hsojIZb2AIbIqGM',
		access_token_secret = 'eAHzdiAly20SXKUCFDsbhFzMzadb9PqXcuufv5lk3QBR5',
		sleep_on_rate_limit = True)

# We have to modify User here to make it hashable.
twitter.User.__hash__ = lambda self: self.id
twitter.User.__eq__ = lambda self, other: self.id == other.id

def get_statuses(user):
	return api.GetUserTimeline(user_id = user.id,
			include_rts = False,
			trim_user = True,
			count = 100)

class UserFinder(object):
	def __init__(self, cursor = -1, subcursor = 0):
		self.cursor = cursor
		self.subcursor = subcursor
	def __call__(self):
		self.cursor, prev, working_list = api.GetFollowersPaged(user_id = '783214',
										cursor = self.cursor, skip_status = True,
										include_user_entities = False)

		working_list = working_list[self.subcursor:]
		while len(working_list) > 0:
			yield working_list.pop()
			self.subcursor += 1
			if len(working_list) == 0:
				self.cursor, prev, working_list = api.GetFollowersPaged(
						user_id = '783214',
						cursor = self.cursor, skip_status = True,
						include_user_entities = False)
				self.subcursor = 0

def get_next_users(timeline, num, exclude, self):
	mentioned = set()
	for status in timeline:
		for user in status.user_mentions:
			mentioned.add(user)

	excluded_ids = [d['twitter_id'] for d in exclude]
	excluded_ids.append(self.id)
	mentioned = {mention for mention in mentioned if mention.id not in excluded_ids}
	mentioned = list(mentioned)
	if len(mentioned) >= num:
		if num == 1:
			return [random.choice(mentioned)]
		else:
			raise NotImplementedError("Multiple users hasn't been implemented yet.")
	elif len(mentioned) > 0:
		return mentioned
	else:
		return None

def save_user(user, timeline, nextu, prev, run):
	d = dict()
	d['twitter_id'] = user.id
	d['full_name'] = user.name
	d['screen_name'] = user.screen_name
	d['next'] = [n.id for n in nextu]
	d['prev'] = prev.id if prev is not None else None
	d['tweets'] = [tweet._json for tweet in timeline]
	d['run'] = run
	return d

def process_user(user, prev, tosave, run, parent_pos = -1, depth = 0, maxdepth = 10):
	timeline = None
	nextu = None
	try:
		timeline = get_statuses(user)
		if depth < maxdepth:
			nextu = get_next_users(timeline, 1, tosave, user)
		else:
			nextu = []
	except twitter.error.TwitterError as e:
		if parent_pos >= 0:
			print(user.id)
			print(prev.id)
			tosave[parent_pos]['next'].remove(user.id)
			
		print(e)
	parent_pos = len(tosave)

	if timeline is not None and nextu is not None:
		tosave.append(save_user(user, timeline, nextu, prev, run))

	if nextu is not None and depth < maxdepth:
		for u in nextu:
			process_user(u, user, tosave, run, parent_pos, depth = depth + 1, maxdepth = maxdepth)

def grab_graph(login = False, max_grab = 10000):
	#fake_news -> network-sampling
	#twittersample -> TW_sample
	#twittersamplestats -> TW_sample_stats
	if not login:
		client = MongoClient()
	else:
		uname = input("Username: ")
		pwd = input("Password: ")
		client = MongoClient('mongodb://' + uname + ':' + pwd + '@127.0.0.1')
	#client = MongoClient('mongodb://' + login + '@127.0.0.1')
	restore_settings = client['fake_news']['TW_sample_stats'].find_one({'cursor':{'$exists':True}})
	finder = UserFinder(cursor = int(restore_settings['cursor']), subcursor = int(restore_settings['subcursor']))

	i = 0
	try:
		run = 0
		for start_user in finder():
			to_save = list()
			process_user(start_user, None, to_save, run, maxdepth = 10)
			if len(to_save) > 0:
				client['fake_news']['TW_sample'].insert_many(to_save, ordered=False)

			run += 1
			i = i + len(to_save)
			if i > max_grab:
				break
	except Exception as e:
		client['fake_news']['TW_sample_stats'].update({'cursor':{'$exists':True}},
			{'cursor':finder.cursor,'subcursor':finder.subcursor})
		client.close()
		raise e

	client['fake_news']['TW_sample_stats'].update({'cursor':{'$exists':True}},
			{'cursor':finder.cursor,'subcursor':finder.subcursor})
	client.close()
	print("Completed collection.")