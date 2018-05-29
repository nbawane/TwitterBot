from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import sqlite3
import json
import threading


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
             (user text, time text, urls text)''')
		except sqlite3.OperationalError as e:
			print('Table already present, no need to create')


	def on_data(self, data):
		data = json.loads(data)
		user = data['user']['name']
		tweet_time = data['created_at']
		urls_list = data["entities"]["urls"]
		final_url = ''
		for url_element in urls_list:
			url_append = url_element["expanded_url"]
			if not('twitter' in url_append and 'status' in url_append):  #twitter statuses to ignored
				final_url += url_append
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
		print("#"*100)
		for i in self.processdbobj.execute("select * from tweets"):
			print(i)



auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(Access_Token, Access_Token_Secret)

twitterStream = Stream(auth, listener())
twitterStream.filter(track=["india"],languages=["en"])