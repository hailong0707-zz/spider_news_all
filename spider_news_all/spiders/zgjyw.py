# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from scrapy import log
import threading
import MySQLdb
from datetime import date, timedelta
import re
from spider_news_all.items import SpiderNewsAllItem

class ZgjywSpider(scrapy.Spider):
    name = "zgjyw"
    allowed_domains = ["www.cb.com.cn"]
    start_urls = (
        'http://www.cb.com.cn/deep/',
        'http://www.cb.com.cn/economy/',
        'http://www.cb.com.cn/companies/',
    )
    handle_httpstatus_list = [521]

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
            article = soup.find(class_='art fix').text.strip()
        except:
            log.msg("News " + title + " dont has article!", level=log.INFO)
        item['title'] = title
        item['day'] = day
        item['_type'] = _type
        item['url'] = url
        item['keywords'] = keywords
        item['article'] = article
        item['site'] = u'中国经营网'
        return item

    def get_type_from_url(self, url):
    	if 'deep' in url:
    		return u'深度阅读'
    	elif 'economy' in url:
    		return u'经济'
    	elif 'companies' in url:
    		return u'公司'
    	else:
    		return ''

    def parse(self, response):
    	log.msg("Start to parse page " + response.url, level=log.INFO)
    	url = response.url
    	_type = self.get_type_from_url(url)
    	items = []
    	try:
    		response = response.body
    		soup = BeautifulSoup(response)
    		links = soup.find_all(class_='cblb_list fix')
    	except:
    		items.append(self.make_requests_from_url(url))
    		log.msg("Page " + url + " parse ERROR, try again !", level=log.ERROR)
    		return items
        need_parse_next_page = True
        if len(links) > 0:
        	for i in range(0, len(links)):
        		url_news_base = links[i].a['href']
        		if url_news_base.startswith('http://'):
        			url_news = 'http://www.cb.com.cn/index.php?m=content&c=index&a=show&catid=26&id=%s&all' % url_news_base.split('.')[3].split('/')[3]
        			day = url_news_base.split('.')[3].split('/')[2].replace('-', '')
        		else:
        			url_news = 'http://www.cb.com.cn/index.php?m=content&c=index&a=show&catid=26&id=%s&all' % url_news_base.split('.')[0].split('/')[3]
        			day = url_news_base.split('.')[0].split('/')[2].replace('-', '')
        		title = links[i].a['title'].strip()
        		need_parse_next_page = self.is_news_not_saved(title, url_news)
        		if not need_parse_next_page:
        			break
        		items.append(self.make_requests_from_url(url_news).replace(callback=self.parse_news, meta={'_type': _type, 'day': day, 'title': title}))
        	if (u'下一页' in soup.find(class_='page_ch').text) and (url != 'http://www.cb.com.cn/' + soup.find('a', text=u'下一页')['href']):
        		page_next_tail = soup.find('a', text=u'下一页')['href']
                if not page_next_tail.startswith('/'):
                    page_next_tail = '/' + page_next_tail
                page_next = 'http://www.cb.com.cn' + page_next_tail
                if need_parse_next_page:
        			items.append(self.make_requests_from_url(page_next))
        	return items
