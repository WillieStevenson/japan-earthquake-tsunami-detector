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
	RECIPIENTS = ['example@domain.com']

	message = MIMEMultipart('alternative')
	message['Subject'] = 'EARTHQUAKE/TSUNAMI ALERT! ' + time.strftime("%m/%d/%Y %H:%M:%S")
	message.attach(MIMEText(msg_body, 'html'))

	s = smtplib.SMTP('localhost')
	s.sendmail('localhost', RECIPIENTS, message.as_string())
	s.quit()

def get_response(link, headers):
	page = requests.get(link, stream=True, headers=headers)
	
	try:
		page.raise_for_status()
	except Exception as exc:
		print('Bad response for : %s : %s' % (link, exc))
	# return the beautiful soup response
	return bs4.BeautifulSoup(page.text, "lxml")

def write_to_file(path, file, string, mode):
	f = open(path + file, mode)
	f.write(string)
	f.close()


if __name__ == "__main__":

	import requests
	import bs4
	import smtplib
	import time

	from os.path import expanduser, isfile
	from email.mime.multipart import MIMEMultipart
	from email.mime.text import MIMEText

	HEADERS = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
	KEYWORDS = ["震災","地震","津波","震度"] # Earthquake disaster, earthquake, tsunami, seismic activity
	WRITE_PATH = expanduser("~/")
	FILE_NAME = '.e-temp'
	LOG_NAME = '.e-log'
	
	# START SCRAPING
	page = get_response('https://www.google.com/search?q=japan+earthquake', HEADERS)
	# extract google g-card
	alert_head = page.select('._xYj')[0]
	alert_map = page.select('.pa-eq-map-div')[0]
	# reformat and add/change attributes to map image
	alert_map.find('img')['data-bsrc'] = "https://google.com" + alert_map.find('img')['data-bsrc']
	alert_map.find('img')['src'] = alert_map.find('img')['data-bsrc'] + "?scale=1&h=192&w=550"
	alert_map.find('img')['height'] = "192"
	alert_map.find('img')['width'] = "550"
	alert_map.find('img')['style'] = ""
	# use in-line styles because gmail blocks all external (referenced) assets - stylesheets, images, scripts, etc.
	alert_head.find("div", class_="_fWj")['style'] = 'color:#fff;font-size:24px;line-height:32px'
	alert_head.find("div", class_="_K3j")['style'] = 'color:rgba(255,255,255,.7);font-size:15px;line-height:24px'
	# build html
	full_html_notification = '<div class="container" style="font-size:small;width:550px;border-radius:2px;box-shadow:0px 1px 4px 0px rgba(0,0,0,0.2)">' + '<div style="background:#f44336;padding:18px 24px 18px 24px">' + str(alert_head) + "</div>" + str(alert_map) + '</div>'

	# 2ND SCRAPE
	page = get_response('https://news.google.co.jp/news', HEADERS)
	# get top news
	page = page.select('.esc-lead-article-title')
	
	alerts = ""
	# build alert with top news containing keywords
	for article in page:
		if any(key in str(article) for key in KEYWORDS):
			alerts += str(article)
	# build html
	full_html_notification = full_html_notification + "<br><hr>トップニュース<hr>" + alerts + '<hr><footer>Dynamically generated ' + time.strftime("%m/%d/%Y %H:%M:%S") + '</footer>'
	# extract alert_head text from the html 
	alert_head_text = alert_head.find("div", class_="_fWj").text.encode('ascii', 'ignore') + "\t" + alert_head.find("div", class_="_K3j").text.encode('ascii', 'ignore')
	
	if len(alert_head) > 0:
		if isfile(WRITE_PATH + FILE_NAME):
			if open(WRITE_PATH + FILE_NAME, "r").read() != alert_head_text:
				write_to_file(WRITE_PATH, FILE_NAME, alert_head_text, "w")
				send_alert(full_html_notification)
				write_to_file(WRITE_PATH, LOG_NAME, alert_head_text, "a")
		else:
			# write for first time
			write_to_file(WRITE_PATH, FILE_NAME, alert_head_text, "w")
			send_alert(full_html_notification)
			write_to_file(WRITE_PATH, LOG_NAME, alert_head_text, "a")