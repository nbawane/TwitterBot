from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import sqlite3
import json
import threading
import requests
from urllib.parse import urlparse
from  datetime import  datetime


consumer_key = 'NiBKgW5YIu2TKm3kJE4RZKRXz'
consumer_secret = '8ZPCDCTREa6DF4tm7NpInP1iDq9a7bkPIBQRVyH2Q1cBlLqPHo'
Access_Token = "935063873115140096-9GdSJ3uOmyK5gTtZbo4yKURijH64t2b"
Access_Token_Secret  = "RjWCAsWJwfP3HuaPgIWFAlEHtJfDMqbMbnDk3zfBgBtUH"

class listener(StreamListener):

	def __init__(self):
		self.conn = sqlite3.connect('twitter.db')    #initialize db
		threading.Timer(300, self.generate_report).start()	#first thread will be triggered after 5 minutes

		self.dbobj = self.conn.cursor()

		try:
			self.dbobj.execute('''CREATE TABLE tweets
             (user text,url text, time bigint)''')

		except sqlite3.OperationalError as e:
			# print('Table already present, no need to create')
			pass
		try:

			self.dbobj.execute('''CREATE TABLE urls
			 (url text, time bigint)''')
		except sqlite3.OperationalError as e:
			# print('Table already present, no need to create')
			pass
		self.month_dict = {'Jan': 1,
					  'Feb': 2,
					  'Mar': 3,
					  'Apr': 4,
					  'May': 5,
					  'Jun': 6,
					  'Jul': 7,
					  'Aug': 8,
					  'Sep': 9,
					  'Oct': 10,
					  'Nov': 11,
					  'Dec': 12
					  }


	def on_data(self, data):
		'''fetch streaming data'''

		data = json.loads(data)
		user = data['user']['name']
		tweet_time = self.date_conversion(data['created_at'])	#timestamp when twwet recieved by programm to be changed to created_at
		self.urls_in_tweets = data["entities"]["urls"]
		final_url = ''

		for url_element in self.urls_in_tweets:
			url_append = url_element["expanded_url"]
			if not('twitter' in url_append and 'status' in url_append):  #twitter statuses to ignored
				final_url += url_append+','
				self.dbobj.execute("insert into urls values(?,?)",(url_append,tweet_time))
		if len(final_url)==0:
			final_url = None
		self.dbobj.execute("insert into tweets values(?,?,?)",(user,final_url,tweet_time))

		self.conn.commit()
		return(True)

	def on_error(self, status):
		print(status)

	def generate_report(self):
		'''
		process data from db at the interval of 1 minute
		:return:
		'''
		threading.Timer(60, self.generate_report).start()  # self calling logic, call after 1 min,to generate 5 mins report after every 5 mins
		self.process = sqlite3.connect('twitter.db')    #initialize db
		self.processdbobj = self.process.cursor()
		self.urls = []
		thread_objs = []
		domain_list = []
		domain_dict = {}
		self.short_urls = []
		# self.processurl = sqlite3.connect('urls.db')
		# self.processurldbobj = self.processurl.cursor()
		print("#"*100)

		currtime = datetime.utcnow().timestamp()

		# currtime = time.time()
		threshold_time = currtime-300
		# Get Users from last 5 mins
		for user in self.processdbobj.execute("select user,count(user) from tweets where time>? group by user",(threshold_time,)):	#should give data for last 5 mins, 5*60
			print("%s : %s "%(user[0],user[1]))
			# print(currtime)
			# print(user)
		#Get total numbers of urls
		print("\n\nURL stats")
		url_count =  self.processdbobj.execute("select count(url) from urls where time>?",(threshold_time,))
		print("Total number of URLS mentioned ::  {}".format(url_count.fetchone()[0]))

		#Extract domain Info
		for url_data in self.processdbobj.execute("select url from urls where time>?",(threshold_time,)):	#accumulating urls
			self.urls.append(url_data[0])
			# print(url_data)

		for url_append in self.urls:
			if not ('twitter' in url_append and 'status' in url_append):  # twitter statuses to be ignored
				tobj = threading.Thread(target=self.unshorten_url, args=(url_append,))
				thread_objs.append(tobj)
				tobj.start()
		for obj in thread_objs:
			obj.join()

		for link in self.short_urls:
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
			self.short_urls.append(requests.head(url, allow_redirects=True).url)	#append shortened urls
		except requests.exceptions.TooManyRedirects as e:
			#sometime the url redirects to itself
			# print('Cannot be shorten at the moment, too many redirects on ::  %s'%url)
			self.short_urls.append(url)
		except requests.exceptions.ConnectionError as e:
			print("Connection Error, Check connection")

	def date_conversion(self,str_date):
		#convert as string date provided by tweeter into seconds, based on epoch concept
		datelist = str_date.split(' ')[1:]
		monthdata = int(self.month_dict[datelist[0]])
		datedate = int(datelist[1])
		hourslist = datelist[2].split(':')
		hourdata = int(hourslist[0])
		minutedata = int(hourslist[1])
		secondsdata = int(hourslist[2])
		yeardata = int(datelist[-1])
		exdatetime = datetime(yeardata, monthdata, datedate, hourdata, minutedata, secondsdata)
		epochseconds = exdatetime.timestamp()
		return  epochseconds

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(Access_Token, Access_Token_Secret)
keyword = input('enter the keyword to search searches :: ')
twitterStream = Stream(auth, listener())
twitterStream.filter(track=[keyword],languages=["en"])