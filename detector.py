#!/usr/bin/python
# encoding: utf-8
##
#
# A quick/naive web scraper that aims to detect earthquakes
# and tsunamis in Japan 
#
# Author: Willie Stevenson
#
##

def send_alert(msg_body):

   RECIPIENTS = ['email@domain.com']
   BODY = msg_body
   
   message = MIMEMultipart('alternative')
   message['Subject'] = '!ALERT! ' + time.strftime("%d/%m/%Y %H:%M:%S")

   message.attach(MIMEText(msg_body, 'html'))

   s = smtplib.SMTP('localhost')
   s.sendmail('localhost', RECIPIENTS, message.as_string())
   s.quit()

if __name__ == "__main__":

	import requests
	import bs4
	import smtplib
	import time

	from email.mime.multipart import MIMEMultipart
	from email.mime.text import MIMEText

	KEYWORDS = ["震災","地震","津波","震度"] # Earthquake disaster, earthquake, tsunami, seismic activity

	page = requests.get('https://news.google.co.jp/news')
	try: # doubt google will go anywhere anytime soon
		page.raise_for_status()
		page = bs4.BeautifulSoup(page.text, "lxml")
		page = page.select('.esc-lead-article-title')
		# print(page)
		# alerts = ""

		# abc = open('new.html','w')

		# for i in page:
		# 	abc.write(str(i))
		# abc.close()

		# q = open('other.html', 'w')

		for article in page:
			if any(key in str(article) for key in KEYWORDS):
				print str(alerts)
				alerts += str(article)
				# q.write(str(article))
		# q.close()

		if len(alerts) > 0:		
			send_alert(alerts)

	except Exception as ex:
		print('Script failed: %s' % (ex))