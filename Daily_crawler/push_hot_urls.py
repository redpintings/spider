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
    # 'thepaper:start_urls':['https://www.thepaper.cn'],
    # 'huanqiuwang:start_urls':['http://huanqiu.com/'],
    # 'wangyi3g:start_urls':['http://3g.163.com/touch/news/'],
    # 'toutiaoquality:start_urls':['http://www.toutiao.com/'],
    # 'atoutiaoqualityvideo:start_urls':['http://www.365yg.com'],
    'tengxunregion:start_urls':['https://xw.qq.com/'],
    'toutiaoregion:start_urls':['https://is.snssdk.com/api/news/feed/v46/?category=news_local&user_city=%E9%9D%92%E5%B2%9B'],
}

# delete keys, and  push start urls to keys

for key, start_urls in dict.items():
    r.delete(key)
    for url in start_urls:
        r.lpush(key, url)
        print('url ', url)
        print('++++++++++++++')
        print(settings.REDIS_HOST, settings.REDIS_PORT)
pool.disconnect()


