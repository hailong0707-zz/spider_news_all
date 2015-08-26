# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from scrapy import log
import threading
import MySQLdb
from datetime import date, timedelta
import re
from spider_news_all.items import SpiderNewsAllItem

class NhzbSpider(scrapy.Spider):
    name = "nhzb"
    allowed_domains = ["www.nanzao.com"]
    start_urls = (
        'http://www.nanzao.com/sc/business/more-business-news',
        'http://www.nanzao.com/sc/national/more-national-news',
    )
    handle_httpstatus_list = []

    FLAG_INTERRUPT = False
    SELECT_NEWS_BY_TITLE_AND_URL = "SELECT * FROM news_all WHERE title='%s' AND url='%s'"

    lock = threading.RLock()
    conn=MySQLdb.connect(user='root', passwd='123123', db='news', autocommit=True)
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    def is_news_not_saved(self, title, url):
        if self.FLAG_INTERRUPT:
            self.lock.acquire()
            rows = self.cursor.execute(self.SELECT_NEWS_BY_TITLE_AND_URL % (title, url))
            if rows > 0:
                log.msg("News saved all finished.", level=log.INFO)
                return False
            else:
                return True
            self.lock.release()
        else:
            return True

    def parse_news(self, response):
        log.msg("Start to parse news " + response.url, level=log.INFO)
        item = SpiderNewsAllItem()
        day = title = _type = keywords = url = article = ''
        url = response.url
        day = response.meta['day']
        title = response.meta['title']
        _type = response.meta['_type']
        response = response.body
        soup = BeautifulSoup(response)
        # try:
        #     items_keywords = soup.find_all(class_='hotword')
        #     for i in range(0, len(items_keywords)):
        #         keywords += items_keywords[i].text.strip() + ' '
        # except:
        #     log.msg("News " + title + " dont has keywords!", level=log.INFO)
        try:
            article = soup.find(class_='story').text.strip()
        except:
            log.msg("News " + title + " dont has article!", level=log.INFO)
        item['title'] = title
        item['day'] = day
        item['_type'] = _type
        item['url'] = url
        item['keywords'] = keywords
        item['article'] = article
        item['site'] = u'南华早报'
        return item

    def get_type_from_url(self, url):
    	if 'www.nanzao.com/sc/business/' in url:
    		return u'财经新闻'
    	elif 'www.nanzao.com/sc/national' in url:
    		return u'大陆新闻'
    	else:
    		return ''

    def parse(self, response):
    	url = response.url
    	_type = self.get_type_from_url(url)
    	items = []
    	try:
            response = response.body
            soup = BeautifulSoup(response)
            links = soup.find_all(class_=re.compile('post-area'))
        except:
            items.append(self.make_requests_from_url(url))
            log.msg("Page " + url + " parse ERROR, try again !", level=log.ERROR)
            return items
        need_parse_next_page = True
        if len(links) > 0:
        	for i in range(0, len(links)):
        		url_news = 'http://www.nanzao.com' + links[i].h2.a['href']
        		title = links[i].h2.a.text.strip()
        		day = links[i].time['datetime'].replace('-', '')
        		need_parse_next_page = self.is_news_not_saved(title, url_news)
        		if not need_parse_next_page:
					break
        		items.append(self.make_requests_from_url(url_news).replace(callback=self.parse_news, meta={'_type': _type, 'day': day, 'title': title}))
        	if u'下一頁>' in soup.find(class_='paging').text:
				page_next = 'http://www.nanzao.com' + soup.find_all("a", text=u"下一頁>")[0]['href']
				if need_parse_next_page:
					items.append(self.make_requests_from_url(page_next))
        	return items

