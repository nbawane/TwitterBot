import requests
import base64

def Oauth(consumer_key,consumer_secret):

	base_url = 'https://api.twitter.com/'
	auth_url = '{}oauth2/token'.format(base_url)

	key = '{}:{}'.format(consumer_key, consumer_secret).encode('ascii')
	b64_encoded_key = base64.b64encode(key)
	b64_encoded_key = b64_encoded_key.decode('ascii')

	header = {'Authorization': 'Basic {}'.format(b64_encoded_key),
			  'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}

	data = {'grant_type': 'client_credentials'}

	auth_resp = requests.post(auth_url, headers=header, data=data)
	return auth_resp.status_code

if __name__ == '__main__':
	consumer_key = 'NiBKgW5YIu2TKm3kJE4RZKRXz'
	consumer_secret = '8ZPCDCTREa6DF4tm7NpInP1iDq9a7bkPIBQRVyH2Q1cBlLqPHo'
	if Oauth(consumer_key,consumer_secret)==200:
		print('authentication succsesfull')