# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from scrapy import log
import threading
import MySQLdb
from datetime import date, timedelta
import re
from spider_news_all.items import SpiderNewsAllItem

class JjgcbSpider(scrapy.Spider):
    name = "jjgcb"
    allowed_domains = ["eeo.com.cn"]
    start_urls = (
        'http://www.eeo.com.cn/politics/bjxx/',
        'http://www.eeo.com.cn/politics/shengyin/',
        'http://www.eeo.com.cn/politics/shuju/',
        'http://www.eeo.com.cn/nation/shiju/',
        'http://www.eeo.com.cn/comment/commentsygc/commentsygccjsd/',
        'http://www.eeo.com.cn/comment/commentsygc/commentsygczcxj/',
        'http://www.eeo.com.cn/comment/commentsygc/commentsygccyzs/',
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
            article = soup.find(class_='wz_zw mt8').text.strip()
        except:
            log.msg("News " + title + " dont has article!", level=log.INFO)
        item['title'] = title
        item['day'] = day
        item['_type'] = _type
        item['url'] = url
        item['keywords'] = keywords
        item['article'] = article
        item['site'] = u'经济观察报'
        return item

    def get_type_from_url(self, url):
        if 'bjxx' in url:
            return u'政经要闻.北京消息'
        elif 'shengyin' in url:
            return u'政经要闻.声音'
        elif 'shuju' in url:
            return u'政经要闻.宏观数据'
        elif 'shiju' in url:
            return u'区域新闻.时局'
        elif 'commentsygccjsd' in url:
            return u'评论.商业观察.财经速评'
        elif 'commentsygczcxj' in url:
            return u'评论.商业观察.政策解码'
        elif 'commentsygccyzs' in url:
            return u'评论.商业观察.产业走势'
        else:
            return ''

    def parse(self, response):
        log.msg("Start to parse page " + response.url, level=log.INFO)
        url = response.url
        if url == 'http://www.eeo.com.cn/':
            return
        _type = self.get_type_from_url(url)
        items = []
        try:
            response = response.body
            soup = BeautifulSoup(response)
            links = soup.find_all(class_=' li_blue font16 mtcs')
        except:
            items.append(self.make_requests_from_url(url))
            log.msg("Page " + url + " parse ERROR, try again !", level=log.ERROR)
            return items
        need_parse_next_page = True
        if len(links) > 0:
            for i in range(0, len(links)):
                url_news = links[i].a['href']
                day = links[i].span.text.strip()
                title = links[i].a.text.strip()
                need_parse_next_page = self.is_news_not_saved(title, url_news)
                if not need_parse_next_page:
                    break
                items.append(self.make_requests_from_url(url_news).replace(callback=self.parse_news, meta={'_type': _type, 'day': day, 'title': title}))
            if ((soup.find('a', text=u'下一页')['href'] != soup.find(class_='wzlist_page font14').find_all('li')[7].a['href']) and soup.find('a', text=u'下一页')['href'].startswith('http://')):
                page_next = soup.find('a', text=u'下一页')['href']
                if need_parse_next_page:
                    items.append(self.make_requests_from_url(soup.find('a', text=u'下一页')['href']))
            return items