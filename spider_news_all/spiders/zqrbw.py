# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from scrapy import log
import threading
import MySQLdb
from spider_news_all.items import SpiderNewsAllItem

class ZqrbwSpider(scrapy.Spider):
    name = "zqrbw"
    allowed_domains = ["ccstock.cn"]
    start_urls = (
        'http://www.ccstock.cn/finance/hongguanjingji/index.html',
        'http://www.ccstock.cn/finance/hangyedongtai/index.html',
        'http://www.ccstock.cn/gscy/gongsi/index.html',
        'http://www.ccstock.cn/gscy/qiyexinxi/index.html',
    )
    handle_httpstatus_list = [404]

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
        try:
            items_keywords = soup.find_all(class_='hotword')
            for i in range(0, len(items_keywords)):
                keywords += items_keywords[i].text.strip() + ' '
        except:
            log.msg("News " + title + " dont has keywords!", level=log.INFO)
        try:
            article = soup.find(id='newscontent').text.strip()
        except:
            log.msg("News " + title + " dont has article!", level=log.INFO)
        item['title'] = title
        item['day'] = day
        item['_type'] = _type
        item['url'] = url
        item['keywords'] = keywords
        item['article'] = article
        item['site'] = u'证券日报网'
        return item

    def get_type_from_url(self, url):
    	if 'hongguanjingji' in url:
    		return u'宏观经济'
    	elif 'hangyedongtai' in url:
    		return u'行业动态'
    	elif 'gongsi' in url:
    		return u'上市公司'
    	elif 'qiyexinxi' in url:
    		return u'企业信息'
    	else:
    		return ''

    def parse(self, response):
    	url = response.url
    	_type = self.get_type_from_url(url)
    	items = []
    	try:
            response = response.body
            soup = BeautifulSoup(response)
            links = soup.find(class_="listMain").find_all("li")
        except:
            items.append(self.make_requests_from_url(url))
            log.msg("Page " + url + " parse ERROR, try again !", level=log.ERROR)
            return items
        need_parse_next_page = True
        if len(links) > 0:
        	for i in range(0, len(links)):
        		url_news = links[i].a['href']
        		title = links[i].a.text.strip()
        		day = links[i].span.text.split(' ')[0].replace('-', '')
        		need_parse_next_page = self.is_news_not_saved(title, url_news)
        		if not need_parse_next_page:
					break
        		items.append(self.make_requests_from_url(url_news).replace(callback=self.parse_news, meta={'_type': _type, 'day': day, 'title': title}))
        	if u'下一页' in soup.find(class_='page').text:
				page_next = soup.find(title=u'下一页')['href']
				if need_parse_next_page:
					items.append(self.make_requests_from_url(page_next))
        	return items
