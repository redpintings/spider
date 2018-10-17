# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import random
import traceback
import redis
import pymysql
import scrapy
import json

from elasticsearch import Elasticsearch
from scrapy.pipelines.images import ImagesPipeline
import re
import requests
from News_scrapy.t_avatar_data_list import PICURL
from News_scrapy.spider_monitoring import MonitoringErrorMsg
from News_scrapy import settings, uautil
from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem
import pymongo
# from cos_lib3.cos import Cos

# cos = Cos(app_id=1255701127, secret_id='AKIDTmphJj8ta1C7mGbXNzMUO3TfcLq7azZd',
#           secket_key='xkHYYJrCJxLTMzMTQ9dtugEXbR2OYT9a', region='sh')

import oss2

auth = oss2.Auth('LTAIt1aWL6gEopIk', '8bOHy8aCWnjlyv1JWeVxDdXJ4siVWN')

class NewsPipeline(object):
    def open_spider(self, spider):
        self.filename = open('data.json', 'w')

    def process_item(self, item, spider):
        content = json.dumps(dict(item)) + "\n"
        self.filename.write(content.encode('utf-8').decode('unicode-escape'))
        return item

    def close_spider(self, spider):
        self.filename.close()


class Images_ES_Mongo_Mysql(object):

    print(">>>>>>>>>>>>>>>>>>>>>>>>>" + 'Images_ES_Mongo_Mysql' + ">>>>>>>>>>>>>>>>>>")
    def __init__(self):
        """
        :param 进行各项服务的初始化
        """
        CONFIG_TYPE = settings.CONFIG_TYPE

        # redis connection
        self.title_pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT,password=settings.REDIS_PWD,decode_responses=True)
        self.title_r = redis.StrictRedis(connection_pool=self.title_pool)

        # ----  mongo start  -----

        # if CONFIG_TYPE == 'TYPE_DEV':
        #     print('=========  开发环境下的mongo  ==========',settings.MONGO_HOST)
        #     pass
        # elif CONFIG_TYPE == 'TYPE_TEST':
        #     print('=========  测试环境下的mongo  ==========',settings.MONGO_HOST)
        #     self.client = pymongo.MongoClient("mongodb://{0}:{1}@{2}:{3}/news".format('janesi_all', 'janesi_all', '118.25.0.170', 27017))
        # else:
        #     print('=========  生产环境下的mongo  ==========',settings.MONGO_HOST)
        #     self.client = pymongo.MongoClient(host=settings.MONGO_HOST, port=settings.MONGO_PORT)
        #     self.client.admin.authenticate(settings.MONGO_USER, settings.MONGO_PWD)
        #     pass
        # self.db = self.client[settings.MONGO_DB]  # 获得数据库的句柄
        # self.coll = self.db[settings.MONGO_COLL]  # 获得collection的句柄
        #

        #  ----  oss start -----
        self.oss_bucketname = settings.OSS_BUCKETNAME
        self.oss_endpoint = settings.OSS_ENDPOINT

        self.oss_bucket = oss2.Bucket(auth, self.oss_endpoint, self.oss_bucketname)
        # ----  es start -------
        if CONFIG_TYPE == 'TYPE_PRO':
            print('=========  生产环境下的es  ==========', settings.ES_URL)
            self.es = Elasticsearch([{'host': settings.ES_URL, 'port': 9200}], http_auth=('elastic', 'EO1N7zNvAIiZ'))
            pass
        else:
            print('=========  非生产环境下的es  ==========', settings.ES_URL)
            self.es = Elasticsearch(settings.ES_URL)
            pass

        # *** content mysql start ****
        self.conn = pymysql.connect(host=settings.MYSQL_HOST,
                               port=settings.MYSQL_PORT,
                               user=settings.MYSQL_USER,
                               password=settings.MYSQL_PASSWD,
                               db=settings.MYSQL_DBNAME,
                               charset='utf8',
                               use_unicode=True)
        self.cursor = self.conn.cursor()

        # *** get channel_id  mysql connect ****
        self.channel_db = pymysql.connect(host=settings.MYSQL_HOST,
                                     port=settings.MYSQL_PORT,
                                     user=settings.MYSQL_USER,
                                     password=settings.MYSQL_PASSWD,
                                     db=settings.MYSQL_DBNAME,
                                     charset='utf8',
                                     use_unicode=True)
        self.channel_cursor = self.channel_db.cursor()

    def get_channel_id(self,item_type):
        """
         进行数据　channel_id 的查询
        :param item_type:
        :return:
        """
        if item_type == 'VIDEO':
            self.channel_cursor.execute("select channel_id,channel_name from channel where channel_classify=1;")
        elif item_type == 'ARTICLE':
            self.channel_cursor.execute("select channel_id,channel_name from channel where channel_classify=0;")
        else:
            return
        # 使用 fetchall() 方法获取所有数据.
        # data_one = cursor.fetchone()
        data_all = self.channel_cursor.fetchall()

        channel_dict = {}
        for id, channel in data_all:
            channel_dict[channel] = id

        # print(channel_dict)
        self.channel_db.commit()


        return channel_dict


    def process_item(self, item, spider):
        """
        进行管道操作 顺序：1 mysql  2 mongo  3 es
        :param item: 
        :param spider: 
        :return: 
        """
        # 进行重复title数据校验
        target_md5 = Util.to_md5(item["title"])
        redis_lrange_list = self.title_r.lrange("title_md5", 0, -1)

        if target_md5 in redis_lrange_list:
            print("^^^" * 30)
            print("^^^" * 30)
            print("^^^" * 30)
            return
        else:
            self.title_r.lpush("title_md5", target_md5)
            print("%%%%" * 30)
            print("%%%%" * 30)
            print("%%%%" * 30)
        # 获取sequence item_id
        db = pymysql.connect(host=settings.MYSQL_HOST,
                                    port=settings.MYSQL_PORT,
                                    user=settings.MYSQL_USER,
                                    password=settings.MYSQL_PASSWD,
                                    db=settings.MYSQL_ID_DB,
                                    charset='utf8',
                                   )
        cursor = db.cursor()
        cursor.execute("SELECT NEXTVAL('item_id');")
        # 使用 fetchone() 方法获取单条数据.
        data = cursor.fetchone()
        db.commit()
        item_id = list(data)[0]
        item['item_id'] = '10' + str(item_id)
        db.close()
        # ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊

        channel_id_dict = self.get_channel_id(item['item_type'])
        try:
            name_id = channel_id_dict[item['channel']]
            item["channel_id"] = name_id
        except Exception as e:
            print('************  channel_id id not find   default num 0')
            item["channel_id"] = 0
        # ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
        # public dispose
        item['scan'] = Util.random_number()
        item['like'] = Util.random_number()
        item['image_num'] = len(item['image_urls'])
        strip_title = item['title']
        item['title'] = str(strip_title).strip()
        if item['channel'] == '地区':
            item['create_type'] = 6
        else:
            item['create_type'] = 1

        if not item["avatar"]:
            item["avatar"] = random.choice(PICURL)

        item['type'] = 0
        item['fans_count'] = 0
        item['scan_count'] = 0
        item['is_delete'] = 0
        item['collect_count'] = 0


        # 进行图片下载
        flags = []
        try:
            if isinstance(item, NewsItem):
                for image_url in item['image_urls']:
                    if "inews.gtimg.com" in image_url:
                        data_name = Util.generate_pic_time_qq(image_url, oss_type='cos_insert')
                    elif "go2yd.com" in image_url:
                        data_name = Util.generate_pic_time_yd(image_url, oss_type='cos_insert')
                    elif 'SUPERLAZYSUB' in image_url:
                        image_url = image_url.replace('SUPERLAZYSUB','')
                        data_name = Util.generate_pic_time_pengpai_lazy(image_url,oss_type='cos_insert')
                    else:
                        data_name = Util.generate_images_pic(image_url, oss_type='cos_insert')

                    # upload_code = self.bucket.upload_file_from_url(image_url, file_name=data_name)
                    input = requests.get(image_url,headers={'User-Agent':random.choice(uautil.USER_AGENT_LIST)})
                    result = self.oss_bucket.put_object(data_name,input)
                    print('result ==========  ',result.status,)
                    if result.status == 200:
                        flags.append('true')
                    else:
                        flags.append('false')

        except Exception as e:
            flags.append('false')
            print('**********error*******image_url*************', e)
            print(item)

        if 'false' in flags:
            print(' 插入图片失败:  ',flags)
        else:
            ## （一）insert into mysql
            global author_id
            try:
                # 查重处理
                self.cursor.execute("""select author_id from author where name = %s and platform = %s """,[item['name'], item['platform']])
                # author是否有重复数据
                repetition = self.cursor.fetchone()
                if repetition:
                    if len(repetition) > 0:
                        self.cursor.execute("select avatar from author where author_id =%s", [repetition[0]])
                        avatar_data = self.cursor.fetchone()
                        # print(data[0])
                        item['avatar'] = str(avatar_data[0])
                        author_id = repetition[0]
                else:
                    # 第一次插入
                    self.cursor.execute(
                        "insert into author (name,platform,avatar,type,fans_count,scan_count,collect_count,is_delete,gmt_create,gmt_modified) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (item['name'], item['platform'], item['avatar'], item['type'], item['fans_count'],
                         item['scan_count'], item['collect_count'], item['is_delete'], item['gmt_create'],
                         item['gmt_modified']))
                    author_id = self.cursor.lastrowid
                print('author_id  ======================= > ',author_id)
            except Exception as e:
                self.conn.rollback()
                print('insert author error >>>>>>>>>>>>>>>>>>>>> ',e)
            self.conn.commit()

            #  （二）insert into mysql  tb:quality_content
            print('insert content to mysql table  start ==== >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ')
            if author_id:
                item['author_id'] = author_id
                item['author'] = {'author_id': item['author_id'], 'author_name': item['name'], 'avatar': item['avatar'], 'platform': item['platform'],
                                  'type': item['type'], 'fans_count': item['fans_count'], 'scan_count': item['scan_count'], 'collect_count': item['collect_count'],
                                  'is_delete': item['is_delete'], 'gmt_create': item['gmt_create'], 'gmt_modified': item['gmt_modified']}
                # sql = "INSERT INTO quality_content (item_id,title,item_type,create_type,source,original_url,category,body,images,videos,audios,copyright,release_time,janesi_time,scan,share,play,forward,collect,tag,channel,child_channel,topic,keyword,region,author_name,author_id,author,avatar,author_type,fans_count,scan_count,collect_count,is_delete,gmt_create,gmt_modified,platform,upload_file_flag,jslike) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                data = (item['item_id'],item['title'],item['item_type'],item['create_type'],item['source'],item['original_url'],json.dumps(item['category'], ensure_ascii=False),item['body'],
                        json.dumps(item['images'], ensure_ascii=False),json.dumps(item['videos'], ensure_ascii=False),json.dumps(item['audios'], ensure_ascii=False),item['copyright'],item['release_time'],item['janesi_time'],item['scan'],item['share'],item['play'],item['forward'],item['collect'],json.dumps(item['tag'], ensure_ascii=False),item['channel'],item['topic'],json.dumps(item['keyword'], ensure_ascii=False),item['region'],item['name'],item['author_id'],json.dumps(item['author'],ensure_ascii=False),str(item['avatar']),item['type'],item['fans_count'],item['scan_count'],item['collect_count'],item['is_delete'],item['gmt_create'],item['gmt_modified'],
                        item['platform'],item['upload_file_flag'],item['like'],item['channel_id'],item['image_num'],item['comment'],item['duration'],item['size'])
                sql = "INSERT INTO base_content (item_id,title,item_type,create_type,source,original_url,category,body,images,videos,audios,copyright,release_time,janesi_time,scan,share,play,forward,collect,tag,channel,topic,keyword,region,author_name,author_id,author,avatar,author_type,fans_count,scan_count,collect_count,is_delete,gmt_create,gmt_modified,platform,upload_file_flag,jslike,channel_id,image_num,comment,duration,`size`) values (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')" %(data)
                try:
                    self.cursor.execute(sql)
                except Exception as e:
                    # 发生错误时回滚
                    print(e,'>>>>>>>>>>>>>>>>>>>>>>>>MYSQL>>>>>>>>>>ERROE>>>>')
                    self.conn.rollback()
                self.conn.commit()
                print("insert ok")
            else:
                print('insert failed')
            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            ## （二）insert into mongo (精品库只插mysql，全部的只插mongo)

            print('insert into es  start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ')
            if author_id:
                print('author_id ',author_id)
                item['author_id'] = author_id

                item['author'] = {'author_id': item['author_id'], 'name': item['name'], 'avatar': item['avatar'], 'platform': item['platform'],
                                  'type': item['type'], 'fans_count': item['fans_count'], 'scan_count': item['scan_count'], 'collect_count': item['collect_count'],
                                  'is_delete': item['is_delete'], 'gmt_create': item['gmt_create'], 'gmt_modified': item['gmt_modified']}

                # self.coll.insert_one(dict(item))
                # print('pipelines ====== >>>>>> ',item)
                #（三）insert into elasticsearch

                _body = {"item_id": item['item_id'], "title": item['title'], "janesi_time": item['janesi_time'],
                         "tag": item['tag'], 'item_type': item['item_type'], 'channel': item['channel'],
                         'topic': item['topic'], 'keyword': item['keyword'],
                         'region': item['region'], "author_id": item['author_id'],"is_recommend":0,"image_num":item['image_num'],"create_type":item['create_type']}

                try:
                    # 将refresh设为true，使得添加的文档可以立即搜索到
                    self.es.index(index='news', doc_type='article', refresh=True, id=item['item_id'], body=_body)
                except Exception as e :
                    print('ES ERROR FLAG **********',e)
                    traceback.print_exc()

            return item
    def open_spider(self, spider):
        pass

    def close_spider(self,spider):
        self.channel_db.close()
        self.cursor.close()
        self.conn.close()
        # self.client.close()
        self.title_pool.disconnect()

        pass