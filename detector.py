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
   SUBJECT = '!ALERT! ' + time.strftime("%d/%m/%Y %H:%M:%S")
   BODY = msg_body
   	 
   message = 'Subject: %s\n\n%s' % (SUBJECT, BODY)

   s = smtplib.SMTP('localhost')
   s.sendmail('localhost', RECIPIENTS, message)
   s.quit()

if __name__ == "__main__":

	import requests, bs4

	KEYWORDS = ["震災","地震","津波","震度"] # Earthquake disaster, earthquake, tsunami, seismic activity

	page = requests.get('https://news.google.co.jp/news')
	try: # doubt google will go anywhere anytime soon
		page.raise_for_status()
		page = bs4.BeautifulSoup(page.text, "lxml")
		page = page.select('.esc-lead-article-title')

		alerts = ""

		for article in page:
			if any(key in str(article) for key in KEYWORDS):
				alerts += str(article)
		
		if len(alerts > 0):		
			send_alert(alerts)

	except Exception as ex:
		print('Script failed: %s' % (ex))