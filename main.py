import requests
import base64
import time
import datetime
from urllib.parse import urlparse
import threading


urls_in_tweets = []
def search(access_token,search_word='python'):

	header = {'Authorization': 'Bearer {}'.format(access_token)}

	if not None:
		print('Getting data....\n')
		search_url = 'https://api.twitter.com/1.1/search/tweets.json?q={}&result_type=recent&count=100'.format(search_keyword)	#need to add until, to limit search till previous day
		try:
			search_resp = requests.get(search_url, headers=header)
		except requests.exceptions.ConnectionError as e:
			print("Connection Error, Check connection")
			sys.exit()
		search_data = search_resp.json()
		statuses = get_data_from_last_mins(search_data['statuses'],5)	#returns the list of tweets from last 5 mins
		if len(statuses)==0:
			print('No Tweets in last 5 mins on %s'%search_word)
			return	#it sshould search again
		users = []
		# times = []
		for status in statuses:
			users.append(status['user']['name'])	#get all the users who tweeted
		get_number_of_tweets_byuser(users)
		print('Processing data....\n')
		get_links_stats(statuses)
		print('\n\n'+'='*100)

def get_data_from_last_mins(data, mins):
	'''
	:param data:list of statuses
	:param mins: limit of time, till the tweets needed
	:return: list of tweets for last 'mins'
	'''
	current_time = get_current_time()
	limit_time = mins*60
	index = 0
	for index,status in enumerate(data):
		tweet_time = convert_twitter_time(status['created_at'])
		if (current_time-tweet_time)<= limit_time:
			continue
		else:
			break
	return data[:index]



def get_current_time():
	'''
	:return: total number of seconds, corresponding to mins and secs
	'''
	current_time = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S")
	hr, min, sec = current_time.split(':')
	total_secs = int(min) * 60 + int(sec)
	return total_secs


def convert_twitter_time(time_str):
	#'Sun May 27 07:29:28 +0000 2018'
	'''
	:param time_str: time string returned by twitter(timestamp)
	:return: total number of seconds, from min and secs
	'''
	timestamp_elem = time_str.split(' ')
	time_elem = timestamp_elem[3].split(':')

	hr = int(time_elem[0])
	min = int(time_elem[1])
	sec = int(time_elem[2])
	total_secs = min*60+sec
	return total_secs


def get_links_stats(data):
	'''
	need to find total number of links used in tweets
	get unique domains and total number of times the domain used
	:param data: json data of statuses
	:return:
	'''
	thread_objs = []
	# urls_in_tweets = []	#text:  urls
	domain_list = []
	domain_dict = {}
	print('#' * 50 + 'Links Stats' + '#' * 50)
	print('\n')
	for status in data:
		urls_list = status["entities"]["urls"]
		for url_element in urls_list:
			url_append = url_element["expanded_url"]
			if not('twitter' in url_append and 'status' in url_append):  #twitter statuses to ignored
				tobj = threading.Thread(target=unshorten_url, args=(url_append,))
				thread_objs.append(tobj)
				tobj.start()
	for obj in thread_objs:
		obj.join()


	print("Total number of links in tweets :: {}\n".format(len(urls_in_tweets)))
	for link in urls_in_tweets:
		print('%s'%link)
		urlobj = urlparse(link)
		domain_list.append(urlobj.netloc)


	for domain in domain_list:
		if domain not in domain_dict:
			domain_dict[domain] = 1
		else:
			domain_dict[domain] = domain_dict[domain]+1
	ascending_order_domains_usage = sorted(domain_dict.items(), key=lambda elem: -elem[1])
	print('-'*100)
	print('\n')
	print('Unique domains and number of times the domain used::::::\n')
	for domain in ascending_order_domains_usage:
		print('{}  :  {}'.format(domain[0],domain[1]))
	return

def unshorten_url(url):
	try:
		urls_in_tweets.append(requests.head(url, allow_redirects=True).url)
	except requests.exceptions.ConnectionError as e:
		print("Connection Error, Check connection")
		sys.exit()

def get_number_of_tweets_byuser(users):
	'''
	Print users and number of tweets by user
	:param user: list of users twitted the keyword
	'''
	user_dict = {}
	for user in users:
		if user not in user_dict:
			user_dict[user] = 1
		else:
			user_dict[user] = user_dict[user]+1
	userdict_sorted = sorted(user_dict.items(), key=lambda elem: -elem[1])
	print('#'*50+'User Stats'+'#'*50)
	print('user  :   Number of times the user has tweeted the word\n')
	for user in userdict_sorted:
		print('%s   :   %s'%(user[0],user[1]))

def Oauth(consumer_key,consumer_secret):
	'''
	authentication step
	:param consumer_key:
	:param consumer_secret:
	:return: access_token
	'''
	base_url = 'https://api.twitter.com/'
	auth_url = '{}oauth2/token'.format(base_url)

	key = '{}:{}'.format(consumer_key, consumer_secret).encode('ascii')
	b64_encoded_key = base64.b64encode(key)
	b64_encoded_key = b64_encoded_key.decode('ascii')

	header = {'Authorization': 'Basic {}'.format(b64_encoded_key),
			  'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}

	data = {'grant_type': 'client_credentials'}

	auth_resp = requests.post(auth_url, headers=header, data=data)
	auth_jsondata = auth_resp.json()
	# print(auth_jsondata['access_token'])
	return auth_jsondata['access_token']

if __name__ == '__main__':
	import sys
	consumer_key = 'NiBKgW5YIu2TKm3kJE4RZKRXz'
	consumer_secret = '8ZPCDCTREa6DF4tm7NpInP1iDq9a7bkPIBQRVyH2Q1cBlLqPHo'
	print('Authentication...')
	try:
		access_token = Oauth(consumer_key,consumer_secret)
	except requests.exceptions.ConnectionError as e:
		print("Connection Error, Check connection")
		sys.exit()
	print('Authentication done')
	search_keyword = input("Enter the search keyword  : ")
	while True:

		search(access_token,search_keyword)
		time.sleep(60)