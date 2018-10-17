# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import traceback

import pymysql
import scrapy
import json

from elasticsearch import Elasticsearch
from scrapy.pipelines.images import ImagesPipeline
import re

from News_scrapy import settings_bak
from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem
import pymongo
from cos_lib3.cos import Cos

cos = Cos(app_id=1255701127, secret_id='AKIDTmphJj8ta1C7mGbXNzMUO3TfcLq7azZd',
          secket_key='xkHYYJrCJxLTMzMTQ9dtugEXbR2OYT9a', region='sh')
# 测试COS
bucket = cos.get_bucket("matrix-dev")
# 生产COS
# bucket = cos.get_bucket("matrix-pro")
# 开发环境ES
#es_url = 'http://118.25.10.151'
# 测试环境ES（搜索引擎）
#es_url = 'http://118.25.0.190:9200/'
# 生产环境ES
#es_url = 'http://111.231.94.168:9200/'
## ------------------  合并前原始备份文件  ------------------- ##

class NewsPipeline(object):
    def open_spider(self, spider):
        self.filename = open('data.json', 'w')

    def process_item(self, item, spider):
        content = json.dumps(dict(item)) + "\n"
        self.filename.write(content.encode('utf-8').decode('unicode-escape'))
        return item

    def close_spider(self, spider):
        self.filename.close()


class NewsImagesPipeline(ImagesPipeline):


    # 发送图片链接的请求
    try:
        def get_media_requests(self, item, info):
            flags = ['true']
            if isinstance(item, NewsItem):
                for image_url in item['image_urls']:
                    # 发送图片的请求，响应会保存在settings里IMAGES_STORE指定的路径下
                    print('*' * 40, '==========image_url==========',image_url)
                    if "inews.gtimg.com" in image_url:
                        data_name = Util.generate_pic_time_qq(image_url,cos_type='cos_insert')
                    elif "php" in image_url:
                        data_name = Util.generate_pic_time_yd(image_url, cos_type='cos_insert')
                    else:
                        data_name = Util.generate_pic_time(image_url, cos_type='cos_insert')

                    upload_code = bucket.upload_file_from_url(image_url, file_name=data_name)
                    print('bucket  get_media_requests   upload_code  == ',upload_code)
                    if int(upload_code) !=0:
                      flags.append('false')
                    else:
                        flags.append('true')
                    item['upload_file_flag'] =flags
                    print('#' * 40, '====================')
    except Exception as e:
        print('-----error---image_url  -', e)


class MongoAndESPipeline(object):

    collection_name = 'article'

    def __init__(self, mongo_uri, mongo_db,mongo_user,mongo_pwd,
                 mysql_host,mysql_dbname,mysql_user,mysql_passwd,mysql_port):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_user = mongo_user
        self.mongo_pwd = mongo_pwd
        self.type_dev = settings_bak.TYPE_DEV

        self.mysql_host = mysql_host
        self.mysql_dbname = mysql_dbname
        self.mysql_user = mysql_user
        self.mysql_passwd = mysql_passwd
        self.mysql_port = mysql_port
        # 开发环境
        es_url = 'http://118.25.10.151'
        self.es=Elasticsearch(es_url)

        #
        # if settings.TYPE_DEV:
        #     es_url = 'http://118.25.0.190:9200/'
        #     self.es = Elasticsearch(es_url)
        # else:
        #     es_url = 'es-cn-mp90jhkbl0003q4fw.elasticsearch.aliyuncs.com'
        #     self.es = Elasticsearch([{'host': es_url, 'port': 9200}],http_auth=('elastic', 'EO1N7zNvAIiZ'))
        print('>>>>>>>>>>>>>>>>>>>>      es_url >>>>>>>>>>>  ',es_url)


    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URL'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'news'),
            mongo_user = crawler.settings.get('MONGO_USER'),
            mongo_pwd = crawler.settings.get('MONGO_PWD'),

            mysql_host =crawler.settings.get('MYSQL_HOST'),
            mysql_dbname =crawler.settings.get('MYSQL_DBNAME'),
            mysql_user =crawler.settings.get('MYSQL_USER'),
            mysql_passwd =crawler.settings.get('MYSQL_PASSWD'),
            mysql_port=crawler.settings.get('MYSQL_PORT')

        )

    def open_spider(self, spider):
        if self.type_dev:
            print('开发环境;dev_env ----')
            self.client = pymongo.MongoClient(self.mongo_uri, port=27017, maxPoolSize=15)
        else:
            self.client = pymongo.MongoClient(self.mongo_uri, port=3717, maxPoolSize=15)
            self.client.admin.authenticate(self.mongo_user,self.mongo_pwd)
        print('MOGO_DB  start        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  ')
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()
        # self.cursor.close()

    def process_item(self, item, spider):
        upload_file_flag = item['upload_file_flag']
        if 'false' in upload_file_flag:
            print('upload_file_flag  failed ###################  ')
            return
        else:
            self.db[self.collection_name].insert_one(dict(item))
            print('MOGO_DB_COLLECTION_NAME   start        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ')

            _body = {"item_id": item['item_id'], "title": item['title'],
                                    "janesi_time": item['janesi_time'], "tag": item['tag'],
                                    'item_type': item['item_type'],'channel':item['channel'],
                     'child_channel':item['child_channel'],'topic':item['topic'],'keyword':item['keyword'],
                     'region':item['region'],
                     }
            try:
                # 将refresh设为true，使得添加的文档可以立即搜索到；
                # 默认为false，可能会导致下面的search没有结果
                print('ES 当前插入数据为:======================',_body)
                self.es.index(index='news',
                              doc_type='article',
                              refresh=True,
                              id=item['item_id'],
                              body=_body)
            except:
                print('>>>>>> ------------- error es insert ------------ ')
                traceback.print_exc()

            print ('-----MYSQL------START------')

            #con = pymysql.connect(host=host, user=user, passwd=password, db=db, charset='utf8', port=port)
            con =  pymysql.connect(host=self.mysql_host,
                                   port=self.mysql_port,
                                   user=self.mysql_user,
                                   password=self.mysql_passwd,
                                   db=self.mysql_dbname,
                                   charset='utf8',
                                   use_unicode=True
                                         )
            cue = con.cursor()
            print ("-----##-------mysql connect succes--------##----")
            try:

                print("-----##-------mysql update start--------##----")
                result_code = cue.execute("UPDATE  tb_author set avatar=%s,type=%s,fans_count=%s,scan_count=%s,collect_count=%s,is_delete=%s where tb_author.name = %s and tb_author.platform = %s",
                                          [item['avatar'], item['type'], item['fans_count'], item['scan_count'],item['collect_count'],item['name'], item['name'], item['platform']
                             ])
                print('result_code ',result_code)
                print("-----##-------mysql update success--------##----")
                if not result_code:
                    print('------ result_code -----执行了。。。。。。')
                    cue.execute("insert into tb_author (name,platform,avatar,type,fans_count,scan_count,collect_count,is_delete,gmt_create,gmt_modified) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                (item['name'],item['platform'],item['avatar'],item['type'],item['fans_count'], item['scan_count'], item['collect_count'],
                                 item['is_delete'],item['gmt_create'], item['gmt_modified']))
                print("insert success")  # 测试语句
            except Exception as e:
                print('--------Insert error:', e)
                con.rollback()
            else:
                con.commit()
            con.close()
            return item
