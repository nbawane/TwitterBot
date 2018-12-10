# TwitterBot
This twitter bot uses twitter stream API to search a particular keyword used in tweets and generates report. The report is generated after every 1 miniute for last 5 mins of data.

Report generated is as follows:
1) All the users who used the word in their tweet along with the number of times the user twitted the word.
2) number of links used in the tweets along with the domain name. Any domain if used multiple times then such domains are displayed in ascending order along with the number of times the domain used.

requirement:
python 3.x.x
SQliteDB


Setup:
execute the code with 'python main.py'
code will prompt to enter a keyword for which the report is be generated
the programm should start generating report 
