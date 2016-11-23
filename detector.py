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
   message['Subject'] = 'EARTHQUAKE/TSUNAMI ALERT! ' + time.strftime("%m/%d/%Y %H:%M:%S")

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

	styles = "<style>body,html{font-size:small;font-family: 'Noto Sans', 'Noto Sans CJK JP', sans-serif;width:550px;}.container{border-radius:2px;box-shadow:0px 1px 4px 0px rgba(0,0,0,0.2)}._xYj{background:#f44336;padding:18px 24px 18px 24px}._fWj{color:#fff;font-size:24px;line-height:32px}._K3j{color:rgba(255,255,255,.7);font-size:15px;line-height:24px}</style>"
	headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
	page = requests.get('https://www.google.com/search?q=japan+earthquake', stream=True, headers=headers)
	try: # doubt google will go anywhere anytime soon
		page.raise_for_status()
		page = bs4.BeautifulSoup(page.text, "lxml")
		# extract google g-card (class names/selectors may change later)
		alert_head = page.select('._xYj')[0]
		alert_map = page.select('.pa-eq-map-div')[0]
		# reformat and additional attributes to map image
		alert_map.find('img')['data-bsrc'] = "https://google.com" + alert_map.find('img')['data-bsrc']
		alert_map.find('img')['src'] = alert_map.find('img')['data-bsrc'] + "?scale=1&h=192&w=550"
		alert_map.find('img')['height'] = "192"
		alert_map.find('img')['width'] = "550"
		alert_map.find('img')['style'] = ""

		full_html_notification = styles + '<div class="container">' + str(alert_head) + str(alert_map) + '</div>'

		page = requests.get('https://news.google.co.jp/news')
		try: 
			page.raise_for_status()
			page = bs4.BeautifulSoup(page.text, "lxml")
			page = page.select('.esc-lead-article-title')
			
			alerts = ""

			for article in page:
				if any(key in str(article) for key in KEYWORDS):
					alerts += str(article)

			full_html_notification = full_html_notification + "<br><br><hr>トップニュース<hr>" + alerts + '<hr><footer>Dynamically generated ' + time.strftime("%m/%d/%Y %H:%M:%S") + '</footer>'
			# only send if big earthquake occurred recently
			if len(alert_head) > 0:		
				send_alert(full_html_notification)

		except Exception as ex:
			print('Script failed on second link: %s' % (ex))

	except Exception as ex:
		print('Script failed on first link: %s' % (ex))