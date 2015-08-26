# -*- coding: utf-8 -*-
import scrapy


class ZqsbwSpider(scrapy.Spider):
    name = "zqsbw"
    allowed_domains = ["news.stcn.com"]
    start_urls = (
        'http://news.stcn.com/xwyw/',
    )

    def parse(self, response):
        pass
