# -*- coding: utf-8 -*-

# Scrapy settings for spider_news_all project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'spider_news_all'

SPIDER_MODULES = ['spider_news_all.spiders']
NEWSPIDER_MODULE = 'spider_news_all.spiders'
ITEM_PIPELINES = ['spider_news_all.pipelines.SpiderNewsAllPipeline']

LOG_LEVEL = 'INFO'
# LOG_LEVEL = 'ERROR'
# LOG_FILE = 'info.log'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'spider_news_finance (+http://www.yourdomain.com)'
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:24.0) Gecko/20100101 Firefox/24.0"
CONCURRENT_REQUESTS_PER_DOMAIN = 4
COOKIES_ENABLED = False
