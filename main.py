from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import sqlite3
import json
import threading
import time
import requests
from urllib.parse import urlparse

consumer_key = 'NiBKgW5YIu2TKm3kJE4RZKRXz'
consumer_secret = '8ZPCDCTREa6DF4tm7NpInP1iDq9a7bkPIBQRVyH2Q1cBlLqPHo'
Access_Token = "935063873115140096-9GdSJ3uOmyK5gTtZbo4yKURijH64t2b"
Access_Token_Secret  = "RjWCAsWJwfP3HuaPgIWFAlEHtJfDMqbMbnDk3zfBgBtUH"

class listener(StreamListener):

	def __init__(self):
		threading.Timer(15, self.generate_report).start()
		self.conn = sqlite3.connect('twitter.db')    #initialize db

		self.dbobj = self.conn.cursor()

		try:
			self.dbobj.execute('''CREATE TABLE tweets
             (user text,url text, time bigint)''')

		except sqlite3.OperationalError as e:
			print('Table already present, no need to create')
		try:

			self.dbobj.execute('''CREATE TABLE urls
			 (url text, time bigint)''')
		except sqlite3.OperationalError as e:
			print('Table already present, no need to create')

	def on_data(self, data):
		data = json.loads(data)
		user = data['user']['name']
		tweet_time = int(time.time())	#timestamp when twwet recieved by programm to be changed to created_at
		self.urls_in_tweets = data["entities"]["urls"]
		final_url = ''
		for url_element in self.urls_in_tweets:
			url_append = url_element["expanded_url"]
			if not('twitter' in url_append and 'status' in url_append):  #twitter statuses to ignored
				final_url += url_append+','
				self.dbobj.execute("insert into urls values(?,?)",(url_append,tweet_time))
		if len(final_url)==0:
			final_url = None
		self.dbobj.execute("insert into tweets values(?,?,?)",(user,tweet_time,final_url))

		# print(user)
		self.conn.commit()
		return(True)

	def on_error(self, status):
		print(status)

	def generate_report(self):
		'''
		process data from db at the interval of 1 minute
		:return:
		'''
		threading.Timer(15,self.generate_report).start()	#self calling logic, call after 1 min
		self.process = sqlite3.connect('twitter.db')    #initialize db
		self.processdbobj = self.process.cursor()
		self.urls = []
		thread_objs = []
		domain_list = []
		domain_dict = {}
		# self.processurl = sqlite3.connect('urls.db')
		# self.processurldbobj = self.processurl.cursor()
		print("#"*100)

		#Get Users from last 5 mins
		for i in self.processdbobj.execute("select user,count(user) from tweets where time>? group by user",(time.time()-300,)):	#should give data for last 5 mins, 5*60
			print(i)
		#Get total numbers of urls
		url_count =  self.processdbobj.execute("select count(url) from urls where time>?",((time.time()-300),))
		print("Total number of URLS mentioned ::  {}".format(url_count.fetchone()))

		#Extract domain Info
		for i in self.processdbobj.execute("select url from urls where time>?", ((time.time() - 300),)):	#accumulating urls
			self.urls.append(i[0])

		for url_append in self.urls:
			if not ('twitter' in url_append and 'status' in url_append):  # twitter statuses to ignored
				tobj = threading.Thread(target=self.unshorten_url, args=(url_append,))
				thread_objs.append(tobj)
				tobj.start()
		for obj in thread_objs:
			obj.join()

		for link in self.urls:
			print('%s' % link)
			urlobj = urlparse(link)
			domain_list.append(urlobj.netloc)

		for domain in domain_list:
			if domain not in domain_dict:
				domain_dict[domain] = 1
			else:
				domain_dict[domain] = domain_dict[domain] + 1
		ascending_order_domains_usage = sorted(domain_dict.items(), key=lambda elem: -elem[1])
		print('-' * 100)
		print('\n')
		print('Unique domains and number of times the domain used::::::\n')
		for domain in ascending_order_domains_usage:

			print('{}  :  {}'.format(domain[0], domain[1]))
		#Extract domain Info finished
	def unshorten_url(self,url):
		#shorten the expanded URLs
		try:
			self.urls.append(requests.head(url, allow_redirects=True).url)
		except requests.exceptions.ConnectionError as e:
			print("Connection Error, Check connection")



auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(Access_Token, Access_Token_Secret)

twitterStream = Stream(auth, listener())
twitterStream.filter(track=["bitcoin"],languages=["en"])