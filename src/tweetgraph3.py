import twitter
import random
from pymongo import MongoClient
from collections import deque

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

def get_next_user(user):
	if user.followers_count == 0 or user.friends_count == 0:
		return None

	followers = get_followers(user)
	friends = get_friends(user)

	options = list(set(friends) & set(followers))

	print("Options: " + str(len(options)))
	if len(options) > 0:
		return random.choice(options)
	else:
		return None

def save_user(user, timeline, nextu, prev, run):
	d = dict()
	d['twitter_id'] = user.id
	d['full_name'] = user.name
	d['screen_name'] = user.screen_name
	d['next'] = nextu.id if nextu is not None else None
	d['prev'] = prev.id if prev is not None else None
	d['tweets'] = [tweet._json for tweet in timeline]
	d['run'] = run
	return d

def get_friends(user):
	cursor = -1
	friends = list()
	while cursor != 0:
		cursor, prev_cursor, users = api.GetFriendsPaged(user_id=user.id, cursor=cursor, skip_status=True)
		print(cursor)
		friends.extend(users)
	return friends

def get_followers(user):
	cursor = -1
	followers = list()
	while cursor != 0:
		cursor, prev_cursor, users = api.GetFollowersPaged(user_id=user.id, cursor=cursor, skip_status=True)
		followers.extend(users)
	return followers

def process_user(user, prev, run):
	try:
		if user is None:
			return (None, None)
		timeline = get_statuses(user)

		nextu = get_next_user(user)

		return ([user,timeline,prev],nextu)
	except twitter.error.TwitterError as e:
		print("Error getting user.")
		return (None, None)

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

	try:
		i = 0
		run = 0
		for curru in finder():
			# [User, Timeline, Prev]
			insert = deque()
			prevu_a = None
			while True:
				curru_a, nextu = process_user(curru, prevu_a[0] if prevu_a is not None else None, run)

				while len(insert) > 2:
					client['fake_news']['TW_sample'].insert_one(insert.popleft())

				if (curru_a is None and prevu_a is not None) or (i >= max_grab and prevu_a is not None):
					if len(insert) != 0:
						save_dict = save_user(prevu_a[0],prevu_a[1],None,prevu_a[2],run)
						insert.append(save_dict)
					i += 1
					print("a")
					break
				elif (curru_a is not None and prevu_a is not None):
					save_dict = save_user(prevu_a[0],prevu_a[1],curru_a[0],prevu_a[2],run)
					insert.append(save_dict)
					i += 1
					if (i % 100) == 0:
						print(i)
					print("b")
				elif (prevu_a is None and curru_a is not None):
					print("Did a pass.")
					pass
				else:
					# If prevu_a is none then that means there was an error accessing
					# its members, so we can't count it as a valid link.
					if len(insert) > 0:
						if insert[-1]['prev'] is None:
							print("Error on first.")
							insert.pop()
						else:
							print("Error on later.")
							insert[-1]['next'] = None
					print("c")
					break

				prevu_a = curru_a
				curru = nextu
				# print(insert)
			if len(insert) > 0:
				client['fake_news']['TW_sample'].insert_many(list(insert),ordered=False)
			run += 1
			if i >= max_grab:
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

if __name__ == "__main__":
	grab_graph(login=True)