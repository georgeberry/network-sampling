import twitter
import random
from time import strptime, mktime
from datetime import datetime
from pymongo import MongoClient
from collections import deque
import urllib3
import requests
import ssl
import time

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

twitter.Api._TrueRequestUrl = twitter.Api._RequestUrl
def _AltRequestUrl(self, url, verb, data=None, json=None, enforce_auth=True):
	if enforce_auth:
		if url and not self.sleep_on_rate_limit and not url.endswith('rate_limit_status.json'):
			limit = self.CheckRateLimit(url)
			remaining = limit[1]
			reset_time = limit[2]
			if remaining <= 0 and (reset_time-time.time()) > 0:
				raise twitter.error.TwitterError([
					{
					'message':'Rate limit exceeded',
					'code':88,
					'reset':limit.reset
					}])
	return self._TrueRequestUrl(url,verb,data,json,enforce_auth)

twitter.Api._RequestUrl = _AltRequestUrl

class APIOverride(type):
	def __init__(cls, name, bases, nmspc):
		super(APIOverride, cls).__init__(name,bases,nmspc)

		for method in dir(twitter.Api):
			if method.startswith("Get"):
				setattr(cls,method,
					lambda self, method=method, **kwargs: cls.farm_task(self,method,**kwargs))

class MultiAPI(object, metaclass=APIOverride):
	def __init__(self, params, sleep_on_rate_limit = True):
		self.apis = [twitter.Api(
			consumer_key = param[0],
			consumer_secret = param[1],
			access_token_key = param[2],
			access_token_secret = param[3],
			sleep_on_rate_limit = False)
			for param in params]
		self.sleep_on_rate_limit = sleep_on_rate_limit

	def farm_task(self, method, **kwargs):
		failed_response = True
		ret = None
		least_reset = 15*60
		while failed_response:
			i = 0
			for api in self.apis:
				i += 1
				try:
					ret = getattr(api,method)(
						**kwargs)
					failed_response = False
				except twitter.error.TwitterError as e:
					if 'Rate limit exceeded' in str(e):
						failed_response = True
						if 'reset' in e.args[0][0]:
							least_reset = min(e.args[0][0]['reset'], least_reset)
					else:
						raise e

				if not failed_response:
					break
			if not failed_response:
					break
			if self.sleep_on_rate_limit:
				time.sleep(max(int(least_reset - time.time()) + 2, 0))
			else:
				raise twitter.error.TwitterError([
					{
					'message':'Rate limit exceeded',
					'code':88,
					'reset':least_reset
					}])
		return ret

accounts = list()
with open('tokens.dat','r') as tokenfile:
	working_tuple = list()
	for line in tokenfile:
		working_tuple.append(line.strip())
		if len(working_tuple) == 4:
			accounts.append(working_tuple)
			working_tuple = list()

api = MultiAPI(accounts, sleep_on_rate_limit = True)
# api = twitter.Api(consumer_key = 'biSMSPUJdGmWkfZTA7SzTjfov',
# 		consumer_secret = 'EMgEUz7Xs3Zo0BlzGswmLnmBSFowcUgiCUVtmIk9cprH6r9Rq3',
# 		access_token_key = '547328231-8WNipAFTBlaePvV8jytKiZ2z5hsojIZb2AIbIqGM',
# 		access_token_secret = 'eAHzdiAly20SXKUCFDsbhFzMzadb9PqXcuufv5lk3QBR5',
# 		sleep_on_rate_limit = True)


''' Generator to get seeds for RDS. It just goes through followers of twitter. '''
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
			try:
				selected_user = get_user(selected_user)
			except twitter.error.TwitterError:
				# Bad user for some reason. Pick a different one.
				continue

		if valid_user(selected_user):
			no_valid_next = False

	return selected_user

def valid_user(user):
	return user.followers_count < 20000 and user.friends_count < 20000 and not user.protected

def get_user(user_id):
	return api.GetUser(user_id = user_id)

def save_user(user, timeline, nextu, prev, run, i):
	d = dict()
	d['twitter_id'] = user.id
	d['full_name'] = user.name
	d['screen_name'] = user.screen_name
	d['next'] = nextu.id if nextu is not None else None
	d['prev'] = prev.id if prev is not None else None
	d['tweets'] = [tweet._json if hasattr(tweet,'_json') else tweet for tweet in timeline]
	d['friends'] = user.friends_count
	d['followers'] = user.followers_count
	d['run'] = run
	d['i'] = i
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
		if nextu is None:
			raise twitter.error.TwitterError("Couldn't get a next user.")

		return ([user,timeline,prev],nextu)
	except twitter.error.TwitterError as e:
		raise e
		# print("Error getting user.")
		# return (None, None)

def reset_restore_settings(db_suffix = ""):
	uname = input("Username: ")
	pwd = input("Password: ")
	client = MongoClient('mongodb://' + uname + ':' + pwd + '@127.0.0.1')
	client['fake_news']['TW_sample_stats' + db_suffix].update({},
		{'cursor':-1,'subcursor':0,'insert':None,'prevu_a':None,
		'curru':None,'i': 0, 'run':0})
	
def get_restore_state(db_suffix):
	uname = input("Username: ")
	pwd = input("Password: ")
	client = MongoClient('mongodb://' + uname + ':' + pwd + '@127.0.0.1')
	restore_settings = client['fake_news']['TW_sample_stats' + db_suffix].find_one({'cursor':{'$exists':True}})
	start_insert = restore_settings['insert']
	start_prevu_a = restore_settings['prevu_a']
	start_curru = restore_settings['curru']
	prevu_a = reconstruct_user(start_prevu_a)
	insert = deque(start_insert)
	curru = reconstruct_user(start_curru)
	return prevu_a,insert,curru

def grab_graph(uname, pwd, max_grab = 10000, max_chains = -1, db_suffix = ""):
	if max_chains == -1:
		max_chains = max_grab
	client = MongoClient('mongodb://' + uname + ':' + pwd + '@127.0.0.1')

	restore_settings = client['fake_news']['TW_sample_stats' + db_suffix].find_one({'cursor':{'$exists':True}})
	finder = UserFinder(cursor = int(restore_settings['cursor']), subcursor = int(restore_settings['subcursor']))

	start_insert = restore_settings['insert']
	start_prevu_a = restore_settings['prevu_a']
	start_curru = restore_settings['curru']
	i = restore_settings['i']
	run = restore_settings['run']
	try:
		for curru in finder():
			insert = deque()
			prevu_a = None
			while True:

				# An ugly way to jump back in to wherever we were before.
				if start_insert is not None and start_prevu_a is not None and start_curru is not None:
					prevu_a = reconstruct_user(start_prevu_a)
					insert = deque(start_insert)
					curru = reconstruct_user(start_curru)

					start_insert = None
					start_prevu_a = None
					start_curru = None
				
				'''
				All the actual computation takes place in process_user. 
				This function has two purposes, to convert curru into curru_a and to get nextu.

				nextu represents the next user we're going to look at and is a User object.

				curru is also a User object, and we want to turn it into curru_a, which is a
				3-tuple (actually a list) containing curru, curru's 100 most recent tweets, and 
				the previous user in the chain. curru_a combined with nextu is all the information
				that you need to save one link in the chain.

				If there's a twitter error somewhere processing the user, we just try again.
				This should cause us to get a new user. This is slightly wasteful of API calls
				since we don't remember which users are problematic but errors are rare enough 
				that it isn't a big deal unless every user to jump to is bad.

				In that case, we just throw a hard error.
				'''

				try:
					curru_a, nextu = process_user(curru, prevu_a[0] if prevu_a is not None else None, run)
				except twitter.error.TwitterError as exp:
					if len(insert) == 0:
						print("Twitter error where it shouldn't happen.")
						raise exp
					else:
						curru = prevu_a[0]
						prevu_a = [prevu_a[2],get_statuses(prevu_a[2]),get_user(insert[-1]['prev'])]
						insert.pop()
						continue

				while len(insert) > 2:
					client['fake_news']['TW_sample' + db_suffix].insert_one(insert.popleft())

				if (curru_a is None and prevu_a is not None) or (i >= max_grab and prevu_a is not None):
					'''
					If we don't have a current user but we do have a previous one that
					means we're at the end of a chain and just catching up logging-wise.
					'''
					if len(insert) != 0:
						save_dict = save_user(prevu_a[0],prevu_a[1],None,prevu_a[2],run,i)
						insert.append(save_dict)
					i += 1
					print("Chain End")
					break
				elif (curru_a is not None and prevu_a is not None):
					'''
					This is just a normal chain element insert. The arguments here to save_user
					are user to save, user's last 100 tweets, next user, previous user, run.
					'''
					save_dict = save_user(prevu_a[0],prevu_a[1],curru_a[0],prevu_a[2],run,i)
					insert.append(save_dict)
					i += 1
					if (i % 100) == 0:
						print(i)
					print("Chain Element")
				elif (prevu_a is None and curru_a is not None):
					'''
					If we don't have a previous user that means we're at the start
					of a chain. It's more convenient to log one step behind what we
					scrape since we can correct things if we find out the node
					we wanted to jump to isn't valid, so at the start of a
					chain we just do nothing. It'll be logged next pass.
					'''
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
				client['fake_news']['TW_sample' + db_suffix].insert_many(list(insert),ordered=False)
			run += 1
			if i >= max_grab or run >= max_chains:
				break
	except (Exception, KeyboardInterrupt) as e:
		client['fake_news']['TW_sample_stats' + db_suffix].update({'cursor':{'$exists':True}},
			{'cursor':finder.cursor,'subcursor':finder.subcursor,
			'prevu_a':None if prevu_a is None else save_user(prevu_a[0],prevu_a[1],None,prevu_a[2],run,i),
			'curru':None if curru is None else save_user(curru,[],None,None,-1,i),
			'i':i,'run':run,'insert':list(insert)}, upsert=True)
		client.close()
		raise e

	client['fake_news']['TW_sample_stats' + db_suffix].update({'cursor':{'$exists':True}},
			{'cursor':finder.cursor,'subcursor':finder.subcursor,
			'prevu_a':None if prevu_a is None else save_user(prevu_a[0],prevu_a[1],None,prevu_a[2],run,i),
			'curru':None if curru is None else save_user(curru,[],None,None,-1,i),
			'i':i,'run':run,'insert':list(insert)}, upsert=True)
	client.close()
	print("Completed collection.")

def reconstruct_user(output):
	user = twitter.User(
			id=output['twitter_id'],
			name=output['full_name'],
			screen_name=output['screen_name'],
			friends_count=output['friends'],
			followers_count=output['followers']
		)
	if output['prev'] is not None:
		tweets = output['tweets']
		prev = twitter.User(id=output['prev'])
		return [user, tweets, prev]
	else:
		return user

if __name__ == "__main__":
	uname = input("Username: ")
	pwd = input("Password: ")
	stop = False
	while not stop:
		try:
			grab_graph(uname=uname, pwd=pwd, max_chains = 1, max_grab = 10200, db_suffix = "_single")
			stop = True
		except (ConnectionError,urllib3.exceptions.SSLError,
			requests.exceptions.SSLError,ssl.SSLEOFError,
			requests.exceptions.ConnectionError,
			urllib3.exceptions.ProtocolError):

			print("Connection error. Restarting.")
			continue
		except KeyboardInterrupt:
			print("Interrupted.")
			stop = True