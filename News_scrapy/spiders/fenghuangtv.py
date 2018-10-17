# -*- coding: utf-8 -*-
# @Author  : 杨星星
# @Email   : yangshilong_liu@163.com

import re

import scrapy
from scrapy_redis.spiders import RedisSpider
from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem
import logging
import requests
import time


class FenghuangtvSpider(RedisSpider):
    name = 'fenghuangtv'
    allowed_domains = ['v.ifeng.com']
    start_urls = ['http://v.ifeng.com/film/']
    redis_key = 'fenghuangtv:start_urls'
    MeiPai = [
        ('科技','118'),
        ('影视', '70'),
        ('人物', '10155'),
        ('娱乐', '61'),
        ('人文', '129'),
        ('体育', '81'),
        ('旅游', '145'),
        ('生活', '140'),
        ('时尚', '110'),
        ('美食', '91'),
        ('社会', '55'),
        ('时尚', '85'),
        ('搞笑', '105'),
        ('音乐', '66'),
        ('搞笑', '101'),
        ('游戏', '172'),
        ('生活', '149'),
        ('纪录片', '94'),
        ('社会', '114'),
        ('动画', '135'),
        ('纪录片', '171'),
    ]
    def parse(self, response):
        for Channel,Id in self.MeiPai:
            JsOriginalUrl = 'http://v.ifeng.com/vlist/channel/{}/showData/first_more.js'.format(Id)
            yield scrapy.Request(url=JsOriginalUrl,callback=self.parse_detail_url,meta={'channel':Channel},dont_filter=True)

    def parse_detail_url(self,response):
        channel = response.meta['channel']
        HtmlUrlPartList = re.findall(r'http://v.ifeng.com/(.*?).shtml', response.body.decode('utf-8'))
        for PartList in HtmlUrlPartList:
            DetailUrl = "http://v.ifeng.com/" + str(PartList) + '.shtml'
            yield scrapy.Request(url=DetailUrl,callback=self.parse_detail_data,meta={'channel':channel},)



    def parse_detail_data(self,response):
        item = NewsItem()
        channel = response.meta['channel']
        title = re.findall(r'"name": "(.*?)"', response.body.decode('utf-8'))[0]
        Author_name = re.findall(r'"mediaName": "(.*?)",', response.body.decode('utf-8'))[0]
        Video_url = re.findall(r'"videoPlayUrl": "(.*?)"', response.body.decode('utf-8'))[0]
        cut_url = re.findall(r'"videoLargePoster": "(.*?)",', response.body.decode('utf-8'))[0]
        duration = re.findall(r'"duration": "(.*?)",', response.body.decode('utf-8'))[0]
        fh_time = re.findall(r'"createdate": "(.*?)",', response.body.decode('utf-8'))[0]
        try:
            if duration:
                data = time.strftime("%M:%S", time.gmtime(int(duration)))
                item['duration'] = data
            else:
                item['duration'] = ''
        except Exception as e:
            logging.info('-------error---duration---',e)
        if title:
            item['title'] = title
            item_id = Util.to_md5(title)
            item['item_id'] = item_id

        else:
            return
        if channel:
            item['channel'] = channel
        else:
            item['channel'] = '社会'
        if Author_name:
            item['name'] = Author_name
        else:
            item['name'] = '凤凰网'
        item['item_type'] = 'VIDEO'
        item['create_type'] = ''
        item['original_url'] = response.url
        item['source'] = '凤凰网视频'

        item['avatar'] = ''
        item['type'] = 0
        item['fans_count'] = ''
        item['scan_count'] = ''
        item['platform'] = 'fenghuangshipin'
        item['collect_count'] = ''
        item['is_delete'] = '0'
        janesi_time = Util.local_time()
        item['gmt_create'] = janesi_time
        item['gmt_modified'] = janesi_time

        tag = Util.tag_by_jieba_title(item['title'])
        try:
            tags = tag[:3]
            tags.append(item['channel'])
            item['tag'] = tags
        except:
            item['tag'] = item['channel']

        item['comment'] = Util.random_number()
        item['topic'] = []
        item['keyword'] = []
        item['region'] = ''
        item['category'] = {"channel": item['channel'], "child_channel": '', "topic": [], "tag": item['tag'],
                            "keyword": [], "region": ''}

        item['image_urls'] = []
        if Video_url:
            item['body'] = Video_url
        else:
            return
        item['images'] = []
        try:
            item['videos'] = [{"index": 1, "url": item["body"], "cut_url": cut_url, "title": item["title"],"duration": item["duration"], "size":''}]
        except:
            return
        item['size'] = 0
        item['audios'] = []
        item['copyright'] = ''
        if fh_time:
            item['release_time'] = fh_time
        else:
            item['release_time'] = janesi_time
        item['janesi_time'] = janesi_time
        item['scan'] = Util.random_number()
        item['like'] = 0
        item['share'] = 0
        item['play'] = 0
        item['forward'] = 0
        item['collect'] = 0
        item['upload_file_flag'] = 'true'

        if not item['body']:
            return
        if not item['videos']:
            return
        item['author_id'] = None
        check = Util.check_item(item)
        if check == 1:
            logging.info('----CHACK----ERROR------')
            return
        yield item







