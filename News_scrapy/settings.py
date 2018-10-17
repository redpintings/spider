# -*- coding: utf-8 -*-

# Scrapy settings for News_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
import sys
sys.path.append('../News_scrapy/')
from config import serviceConfig

BOT_NAME = 'News_scrapy'

SPIDER_MODULES = ['News_scrapy.spiders']
NEWSPIDER_MODULE = 'News_scrapy.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"

DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True

IMAGES_STORE ="/home/admin/janesi-spider/Daily_crawler/log/image"
# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 10

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.6
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False


# 下载超时时间　爬虫优化
DOWNLOAD_TIMEOUT = 10

# 禁止重试，对不必要的http 请求禁止　重试
# RETRY_ENABLED = False

# 禁止重定向，如果不必要的话
# REDIRECT_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'News_scrapy.middlewares.NewsScrapySpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html

DOWNLOADER_MIDDLEWARES = {
   'News_scrapy.middlewares.UserAgentMiddleware': 100,
   'News_scrapy.middlewares.ProxyMiddleware': 200,
   'News_scrapy.middlewares.PhantomJSMiddleware':300,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
     'News_scrapy.pipelines.Images_ES_Mongo_Mysql': 200,
     # 'News_scrapy.pipelines.NewsPipeline': 100,


}


## -------------------------- 环境配置 开始--------------------------------  ##

#  test  测试服务器　　　　pro　正式服务器
test_conf = serviceConfig.settings('pro')
print(test_conf)
# mongo_list = test_conf.get('mongo_list')
mysql_list = test_conf.get('mysql_list')
oss_list = test_conf.get('oss_list')
es_list = test_conf.get('es_list')
redis_list = test_conf.get('redis_list')
config_type = test_conf.get('config_type')

# mongo start ------------
# MONGO_URL = mongo_list.get('MONGO_URL')
# MONGO_HOST = mongo_list.get('MONGO_HOST')
# MONGO_USER = mongo_list.get('MONGO_USER')
# MONGO_PWD = mongo_list.get('MONGO_PWD')
# MONGO_PORT = mongo_list.get('MONGO_PORT')
# MONGO_DB = mongo_list.get('MONGO_DB')
# MONGO_COLL = mongo_list.get('MONGO_COLL')

# mysql start -------------
MYSQL_HOST = mysql_list.get('MYSQL_HOST')
MYSQL_DBNAME = mysql_list.get('MYSQL_DBNAME')
MYSQL_ID_DB =  mysql_list.get('MYSQL_ID_DB')
MYSQL_USER = mysql_list.get('MYSQL_USER')
MYSQL_PASSWD = mysql_list.get('MYSQL_PASSWD')
MYSQL_PORT = mysql_list.get('MYSQL_PORT')

# cos start ----------------
OSS_ENDPOINT = oss_list.get('OSS_ENDPOINT')
OSS_BUCKETNAME = oss_list.get('OSS_BUCKETNAME')
# es start  ----------------
ES_URL = es_list.get('ES_URL')
ES_AUTH = es_list.get('ES_AUTH')

# redis start --------------
REDIS_HOST = redis_list.get('REDIS_HOST')
REDIS_PORT = redis_list.get('REDIS_PORT')
REDIS_PWD = redis_list.get('REDIS_PWD')
REDIS_PARAMS  = {
 'password': REDIS_PWD,
}

# config_type
CONFIG_TYPE = config_type.get('CONFIG_TYPE')
WEBSITE = config_type.get('WEBSITE')

print('$$$'*20)
print('redis --- params  ',REDIS_PARAMS,WEBSITE)
print('$$$'*20)
LOG_LEVEL = 'DEBUG'
## -------------------------- 环境配置 结束--------------------------------  ##

