# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from scrapy import log
import threading
import MySQLdb
from datetime import date, timedelta
import re
from spider_news_all.items import SpiderNewsAllItem

class CjwSpider(scrapy.Spider):
    name = "cjw"
    allowed_domains = ["caijing.com.cn"]
    start_urls = (
        'http://economy.caijing.com.cn/economynews/',
        'http://economy.caijing.com.cn/observation/',
        'http://economy.caijing.com.cn/economics/',
        'http://economy.caijing.com.cn/region/',
        'http://economy.caijing.com.cn/policy/',
        'http://economy.caijing.com.cn/report/',
        'http://industry.caijing.com.cn/industrianews/',
        'http://industry.caijing.com.cn/steel/index.html',
        'http://industry.caijing.com.cn/energy/',
        'http://industry.caijing.com.cn/aviations/',
        'http://industry.caijing.com.cn/traffic/',
        'http://industry.caijing.com.cn/food/',
        'http://industry.caijing.com.cn/medicals/',
        'http://industry.caijing.com.cn/consumption/',
        'http://industry.caijing.com.cn/industrys/',
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
        try:
            items_keywords = soup.find(class_='ar_keywords').find_all('a')
            for i in range(0, len(items_keywords)):
                keywords += items_keywords[i].text.strip() + ' '
        except:
            log.msg("News " + title + " dont has keywords!", level=log.INFO)
        try:
            article = soup.find(class_='article-content').text.strip()
        except:
            log.msg("News " + title + " dont has article!", level=log.INFO)
        item['title'] = title
        item['day'] = day
        item['_type'] = _type
        item['url'] = url
        item['keywords'] = keywords
        item['article'] = article
        item['site'] = u'财经网'
        return item

    def get_type_from_url(self, url):
        if 'economynews' in url:
            return u'宏观频道首页.每日要闻宏观'
        elif 'observation' in url:
            return u'宏观频道首页.观察'
        elif 'economics' in url:
            return u'宏观频道首页.经济'
        elif 'region' in url:
            return u'宏观频道首页.区域'
        elif 'policy' in url:
            return u'宏观频道首页.政策'
        elif 'report' in url:
            return u'宏观频道首页.报告'
        elif 'industrianews' in url:
            return u'产经频道首页.每日要闻产经'
        elif 'steel' in url:
            return u'产经频道首页.钢铁'
        elif 'energy' in url:
            return u'产经频道首页.能源'
        elif 'aviations' in url:
            return u'产经频道首页.航空'
        elif 'traffic' in url:
            return u'产经频道首页.交通'
        elif 'food' in url:
            return u'产经频道首页.食品'
        elif 'medicals' in url:
            return u'产经频道首页.医疗'
        elif 'consumption' in url:
            return u'产经频道首页.消费品'
        elif 'industrys' in url:
            return u'产经频道首页.综合'
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
            lists = soup.find(class_='list')
            links = lists.find_all('li')
        except:
            items.append(self.make_requests_from_url(url))
            log.msg("Page " + url + " parse ERROR, try again !", level=log.ERROR)
            return items
        need_parse_next_page = True
        if len(links) > 0:
            for i in range(0, len(links)):
                url_news = links[i].a['href']
                day = links[i].find(class_='time').text.strip()
                title = links[i].a.text.strip()
                need_parse_next_page = self.is_news_not_saved(title, url_news)
                if not need_parse_next_page:
                    break
                items.append(self.make_requests_from_url(url_news).replace(callback=self.parse_news, meta={'_type': _type, 'day': day, 'title': title}))
            if (soup.find('a', text=u'下一页')['href'].startswith('http://')):
                page_next = soup.find('a', text=u'下一页')['href']
                if need_parse_next_page:
                    items.append(self.make_requests_from_url(page_next))
            return items