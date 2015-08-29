##README

-------------------------------

- 当前的`settings.py`经过调试相对比较稳定，不要轻易修改！！！
- 当前，所有爬虫**增量**抓取的开关已经打开，如果需要，可以手动关闭，`/spiders/***.py`文件的`FLAG_INTERRUPT = True`常量

- 证券日报 2007.09.17~ http://zqrb.ccstock.cn/ `scrapy crawl zqrb`
- 证券时报 2010.12.17~ http://epaper.stcn.com/paper/zqsb/html/2010-12/17/node_2.htm `scrapy crawl zqsb`
- 证券日报网
  http://www.ccstock.cn/finance/hongguanjingji/index.html
  http://www.ccstock.cn/finance/hangyedongtai/index.html
  http://www.ccstock.cn/gscy/gongsi/index.html
  http://www.ccstock.cn/gscy/qiyexinxi/index.html
  `scrapy crawl zqrbw`
- 南华早报
  http://www.nanzao.com/sc/business/more-business-news
  http://www.nanzao.com/sc/national/more-national-news
  'scrapy crawl nhzb'
- 中国经营网
  http://www.cb.com.cn/deep/
  http://www.cb.com.cn/economy/
  http://www.cb.com.cn/companies/
  'scrapy crawl zgjyw'



- 经济观察报
http://www.eeo.com.cn/politics/bjxx/
http://www.eeo.com.cn/politics/shengyin/
http://www.eeo.com.cn/politics/shuju/
http://www.eeo.com.cn/nation/shiju/
http://www.eeo.com.cn/comment/commentsygc/commentsygccjsd/
http://www.eeo.com.cn/comment/commentsygc/commentsygczcxj/
http://www.eeo.com.cn/comment/commentsygc/commentsygccyzs/
'scrapy crawl jjgcb'
- 财经网
http://economy.caijing.com.cn/economynews/
http://economy.caijing.com.cn/observation/
http://economy.caijing.com.cn/economics/
http://economy.caijing.com.cn/region/
http://economy.caijing.com.cn/policy/
http://economy.caijing.com.cn/report/
http://industry.caijing.com.cn/industrianews/
http://industry.caijing.com.cn/steel/index.html
http://industry.caijing.com.cn/energy/
http://industry.caijing.com.cn/aviations/
http://industry.caijing.com.cn/traffic/
http://industry.caijing.com.cn/food/
http://industry.caijing.com.cn/medicals/
http://industry.caijing.com.cn/consumption/
http://industry.caijing.com.cn/industrys/
‘scrapy crawl cjw’
- 证券时报网
http://news.stcn.com/xwyw/
‘scrapy crawl zqsbw’
- 中证网
http://www.cs.com.cn/xwzx/hg/
http://www.cs.com.cn/xwzx/cj/ 
http://www.cs.com.cn/ssgs/gsxw/
三个分类必须分开运行
‘scrapy crawl zzw’
- 华尔街见闻
http://wallstreetcn.com/news?status=published&type=news&cid=17&order=-created_at&limit=100&page=1
http://wallstreetcn.com/news?status=published&type=news&cid=22&order=-created_at&limit=100&page=1
`scrapy crawl hejjw`

- 如果有问题，可以发邮件沟通`hailong0707@gmail.com`
