# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from scrapy import log
import threading
import MySQLdb
from datetime import date, timedelta
import re
from spider_news_all.items import SpiderNewsAllItem


class HejjwSpider(scrapy.Spider):
    name = "hejjw"
    allowed_domains = ["wallstreetcn.com"]
    start_urls = (
        'http://wallstreetcn.com/news?status=published&type=news&cid=17&order=-created_at&limit=100&page=1',
        'http://wallstreetcn.com/news?status=published&type=news&cid=22&order=-created_at&limit=100&page=1',
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
        #     items_keywords = soup.find(class_='ar_keywords').find_all('a')
        #     for i in range(0, len(items_keywords)):
        #         keywords += items_keywords[i].text.strip() + ' '
        # except:
        #     log.msg("News " + title + " dont has keywords!", level=log.INFO)
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
        item['site'] = u'华尔街见闻'
        return item

    def get_type_from_url(self, url):
        if 'cid=17' in url:
            return u'新闻咨询.中国'
        elif 'cid=22' in url:
            return u'新闻咨询.公司'
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
            lists = soup.find(class_='news-list with-img')
            links = lists.find_all('li', class_='news')
        except:
            items.append(self.make_requests_from_url(url))
            log.msg("Page " + url + " parse ERROR, try again !", level=log.ERROR)
            return items
        need_parse_next_page = True
        if len(links) > 0:
            for i in range(0, len(links)):
                url_news = links[i].div.a['href']
                day = links[i].find(class_='meta time visible-lg-inline-block').text.strip()
                title = links[i].div.a.text.strip()
                need_parse_next_page = self.is_news_not_saved(title, url_news)
                if not need_parse_next_page:
                    break
                items.append(self.make_requests_from_url(url_news).replace(callback=self.parse_news, meta={'_type': _type, 'day': day, 'title': title}))
            if len(soup.find_all(class_='fa fa-angle-right')) > 0 :
                navi = soup.find(class_='pagination').find_all('li')
                page_next = navi[len(navi) - 2].a['href']
                if need_parse_next_page:
                    items.append(self.make_requests_from_url(page_next))
            return items
