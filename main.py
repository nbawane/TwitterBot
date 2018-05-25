import requests
import base64
import time
import datetime
from urllib.parse import urlparse


def search(access_token):

	header = {'Authorization': 'Bearer {}'.format(access_token)}

	data = {'grant_type': 'client_credentials'}

	# auth_resp = requests.get(auth_url, headers=header, data=data)
	if not None:
		search_url = 'https://api.twitter.com/1.1/search/tweets.json?q=Tron&result_type=recent&count=100'
		search_resp = requests.get(search_url, headers=header)
		search_data = search_resp.json()
		statuses = search_data['statuses']
		users = []
		times = []
		for status in statuses:
			users.append(status['user']['name'])
			times.append(status['created_at'])

		print(users)
		user_stats = get_number_of_tweets_byuser(users)
		links_stats = get_links_stats(statuses)
		#print all the user tweeted the name and the number of tweets by that person
		for user in user_stats:
			limiter = '#'*100
			print(limiter)
			print("User : Tweets on Tron")
			print("{} : {}".format(user,user_stats[user]))

	pass
def get_links_stats(data):
	'''
	need to find total number of links used in tweets
	get unique domains and total number of times the domain used
	:param data: json data of statuses
	:return:
	'''
	urls_in_tweets = []	#text:  urls
	domain_list = []
	domain_dict = {}
	for status in data:
		print("#"*100)
		print(status["text"])
		print(status["entities"])

		urls_list = status["entities"]["urls"]
		for url_element in urls_list:
			url_append = url_element["expanded_url"]
			if not('twitter' in url_append and 'status' in url_append):
				urls_in_tweets.append(url_append)
				urlobj = urlparse(url_append)
				domain_list.append(urlobj.netloc)

	print(urls_in_tweets)
	print("Total number of links :: {}".format(len(urls_in_tweets)))
	for domain in domain_list:
		if domain not in domain_dict:
			domain_dict[domain] = 1
		else:
			domain_dict[domain] = domain_dict[domain]+1
	ascending_order_domains_usage = sorted(domain_dict.items(), key=lambda elem: -elem[1])
	for domain in ascending_order_domains_usage:
		print(domain)
	return


def get_number_of_tweets_byuser(users):
	'''
	:param user: list of users twitted the keyword
	:return:
	'''
	user_dict = {}
	for user in users:
		if user not in user_dict:
			user_dict[user] = 1
		else:
			user_dict[user] = user_dict[user]+1
	return user_dict

def Oauth(consumer_key,consumer_secret):
	'''
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
	print(auth_jsondata['access_token'])
	return auth_jsondata['access_token']

if __name__ == '__main__':
	consumer_key = 'NiBKgW5YIu2TKm3kJE4RZKRXz'
	consumer_secret = '8ZPCDCTREa6DF4tm7NpInP1iDq9a7bkPIBQRVyH2Q1cBlLqPHo'
	access_token = Oauth(consumer_key,consumer_secret)
	print(datetime.datetime.now())
	while True:
		time.sleep(60)
		search(access_token)