import requests
import base64
import time
import datetime
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
		print(times)
	pass





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