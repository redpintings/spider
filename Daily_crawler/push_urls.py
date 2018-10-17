# coding=utf-8
import redis
import sys
sys.path.append('../News_scrapy/')
import settings
# connect to redis


REDIS_DB_NUM = 0
# 生产环境
pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT,db=REDIS_DB_NUM,password=settings.REDIS_PWD)
# 开发环境
# 测试环境
r = redis.StrictRedis(connection_pool=pool)


dict = {
    #'besttoutiao:start_urls': ['http://toutiao.com/'],
    # 'bobovideo:start_urls': ['http://bbobo.com/'],
    'egvideo:start_urls': ['http://www.ergengtv.com/video/list/0_1.html'],
    'qutoutiqo:start_urls': ['http://home.qutoutiao.net/pages/home.html?'],
    'qqhistory:start_urls': ['http://view.news.qq.com/c/wqzt11_1.htm?'],
    'tencent:start_urls': ['https://pacaio.match.qq.com/irs/rcd?cid=24&ext=astro&token=6519a55d4dd6c430612bf8c3b6e098fa&num=20&page=0&callback=__jp1'],
    'vmov:start_urls': ['https://www.vmovier.com/post/getbytab?tab=new&page=0&pagepart=0&controller=index'],
    'zaker:start_urls': ["http://www.myzaker.com"],
    'maopu:start_urls': ["http://tv.mop.com/life.html"],
    'jiemian:start_urls': ['http://www.jiemian.com'],
    'pengfu:start_urls': ['http://www.pengfu.com'],
    'qncye:start_urls': ['http://www.qncye.com/data/sitemap.html'],
    "toutiao:start_urls": ["http://open.toutiao.com/?channel=news_tech#channel=news_tech"],
    'tencenthouse:start_urls':['http://house.qq.com/'],
    'fenghuangtv:start_urls':['http://v.ifeng.com/film/'],
    'pearvideo:start_urls':['http://www.pearvideo.com/'],
    'toutiaohouse:start_urls':['https://www.toutiao.com/'],
    'budejie:start_urls':['http://www.budejie.com/'],
    'fangtianxia:start_urls':['https://m.fang.com/news/bj.html'],
    'btc8:start_urls':['http://www.8btc.com/blockchain'],
    'yidian:start_urls':['http://www.yidianzixun.com/'],
    'fireball:start_urls':['http://www.huoqiucj.com/'],
    'dftoutiao:start_urls':['http://mini.eastday.com/']
    # 'tengxunregion:start_urls':['https://xw.qq.com/'],
    # 'toutiaoregion:start_urls':['https://www.toutiao.com/']
        }
# start urls for each website

# delete keys, and  push start urls to keys

for key, start_urls in dict.items():
    r.delete(key)
    for url in start_urls:
        r.lpush(key, url)
        print('url ', url)
        print(settings.REDIS_HOST,settings.REDIS_PORT,'++++++++')

pool.disconnect()