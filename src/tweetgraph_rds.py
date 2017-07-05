import twitter
import random
from time import strptime, mktime
from datetime import datetime
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

''' Get the first 100 statuses of a twitter User object.
Used for logging people's timelines. '''
def get_statuses(user):
	return api.GetUserTimeline(user_id = user.id,
			include_rts = True,
			trim_user = False,
			count = 100)

''' Converts twitter's obnoxious timestamp format to UNIX time '''
def timestamp_after(timestamp,compare_to):
	return (mktime(strptime(timestamp,"%a %b %d %H:%M:%S %z %Y")) > compare_to)

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

''' Finds a new valid user to jump to from the given user.'''
def get_next_user_follow(user):
	total_links = user.followers_count + user.friends_count
	if total_links == 0:
		return None

	''' 
	We can't just use the reported friends and followers count
	here because reasonably often twitter misreports it. 
	Or maybe we could, but when I tried it got complicated.
	'''
	friends = get_friends(user, user.friends_count <= 400)
	followers = get_followers(user, user.followers_count <= 400)
	no_valid_next = True
	selected_user = None
	while no_valid_next:
		user.friends_count = len(friends)
		user.followers_count = len(followers)
		total_links = user.followers_count + user.friends_count
		if user.friends_count == 0 and user.followers_count == 0:
			return None
		selection = random.randint(0, total_links - 1)
		if selection < user.friends_count:
			selected_user = friends[selection]
			''' It's ok to delete these because if we come back to this
			code, it means they weren't valid to sample anyway. '''
			del friends[selection]
		else:
			selected_user = followers[selection - user.friends_count]
			del followers[selection - user.friends_count]

		if type(selected_user) is int or type(selected_user) is str:
			selected_user = get_user(selected_user)

		if valid_user(selected_user):
			no_valid_next = False

	return selected_user

def valid_user(user):
	return user.followers_count < 20000 and user.friends_count < 20000

def get_user(user_id):
	return api.GetUser(user_id = user_id)

def save_user(user, timeline, nextu, prev, run):
	d = dict()
	d['twitter_id'] = user.id
	d['full_name'] = user.name
	d['screen_name'] = user.screen_name
	d['next'] = nextu.id if nextu is not None else None
	d['prev'] = prev.id if prev is not None else None
	d['tweets'] = [tweet._json for tweet in timeline]
	d['friends'] = user.friends_count
	d['followers'] = user.followers_count
	d['run'] = run
	return d

'''
There's two different forms of get_friends. One gets the user objects but 
returns fewer items per API call. The other only returns user ids. We pick
the optimal one in terms of calls with the assumption that we'll only make one.
'''
def get_friends(user, include_users):
	cursor = -1
	friends = list()
	while cursor != 0:
		if include_users:
			cursor, prev_cursor, users = api.GetFriendsPaged(user_id=user.id, cursor=cursor, skip_status=True)
		else:
			cursor, prev_cursor, users = api.GetFriendIDsPaged(user_id=user.id, cursor=cursor)
		friends.extend(users)
	return friends

def get_followers(user, include_users):
	cursor = -1
	followers = list()
	while cursor != 0:
		if include_users:
			cursor, prev_cursor, users = api.GetFollowersPaged(user_id=user.id, cursor=cursor, skip_status=True)
		else:
			cursor, prev_cursor, users = api.GetFollowerIDsPaged(user_id = user.id, cursor=cursor)
		followers.extend(users)
	return followers

''' This should probably be refactored but
given a user, it returns a list containing
everything needed to save that user's node
and the next node to jump to. '''
def process_user(user, prev, run):
	try:
		if user is None:
			return (None, None)
		if hasattr(user, 'user_timeline'):
			if len(user.user_timeline > 100):
				timeline = user.user_timeline[:100]
			else:
				timeline = user.user_timeline
		else:
			timeline = get_statuses(user)

		nextu = get_next_user_follow(user)

		return ([user,timeline,prev],nextu)
	except twitter.error.TwitterError as e:
		print("Error getting user.")
		return (None, None)

def grab_graph(login = False, max_grab = 10000):
	if not login:
		client = MongoClient()
	else:
		uname = input("Username: ")
		pwd = input("Password: ")
		client = MongoClient('mongodb://' + uname + ':' + pwd + '@127.0.0.1')

	restore_settings = client['fake_news']['TW_sample_stats'].find_one({'cursor':{'$exists':True}})
	finder = UserFinder(cursor = int(restore_settings['cursor']), subcursor = int(restore_settings['subcursor']))

	try:
		i = 0
		run = 0
		for curru in finder():
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
					print("Chain End")
					break
				elif (curru_a is not None and prevu_a is not None):
					save_dict = save_user(prevu_a[0],prevu_a[1],curru_a[0],prevu_a[2],run)
					insert.append(save_dict)
					i += 1
					if (i % 100) == 0:
						print(i)
					print("Chain Element")
				elif (prevu_a is None and curru_a is not None):
					print("Chain Start")
					pass
				else:
					'''
					If prevu_a is none then that means there was an error accessing
					its members, so we can't count it as a valid link.
					Sometimes this happens.
					'''
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