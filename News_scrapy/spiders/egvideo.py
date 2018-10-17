# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import re
import json

from scrapy_redis.spiders import RedisSpider

from News_scrapy.items import NewsItem
from News_scrapy.MyUtils import Util

class EgvideoSpider(RedisSpider):
    name = 'egvideo'
    allowed_domains = ['ergengtv.com']
    # start_urls = ['http://www.ergengtv.com/video/list/0_1.html']
    redis_key = 'egvideo:start_urls'
    page = 1

    def parse(self, response):
        # print(response.body.decode('utf-8'), '-------')
        soup = BeautifulSoup(response.body.decode('utf-8'), 'lxml')
        data = soup.select('#eg-content li')
        for node in data:

            data_link = "http:" + node.select('.box1 a')[0].get('href')
            # print("http:" + data_link)
            yield scrapy.Request(url=data_link,callback=self.parse_video_json_url)



    def parse_video_json_url(self, response):

        item = NewsItem()
        item['original_url'] = response.url
        # source = re.search(r'"user_nickname": "(.*?)",', response.body.decode('utf-8')).group(1)
        item["source"] = "二更视频"
        channel = re.search(r' "category_name": "(.*?)",', response.body.decode('utf-8')).group(1)

        item['channel'] = channel

        item['comment'] = Util.random_number()

        item['topic'] = []
        item['keyword'] = []
        item['image_urls'] = []
        item['region'] = ''

        author_ = re.findall(r'"user_nickname": "(.*?)",',response.body.decode('utf-8'))[0]
        if author_:
            author = author_
        else:
            author = "二更视频"
        janesi_time = Util.local_time()
        item['name'] = author
        item['avatar'] = ''
        item['type'] = 0
        item['fans_count'] = 0
        item['scan_count'] = 0
        item['collect_count'] = 0
        item['is_delete'] = '0'
        item['gmt_create'] = janesi_time
        item['gmt_modified'] = janesi_time


        item["cut_url"] = re.search(r'"cover": "(.*?)",', response.body.decode('utf-8')).group(1)
        duration = re.search(r'"duration_format": "(.*?)",', response.body.decode('utf-8')).group(1)
        item["duration"] = duration

        html_num = re.search(r'"media_id":(.*?),', response.body.decode('utf-8')).group(1)
        title = re.findall(r'"title": "(.*?)",', response.body.decode('utf-8'))[0]
        item["title"] = title
        if title:
            tags = Util.tag_by_jieba_title(title)
            item['tag'] = tags
        if channel:
            item['tag'].append(channel)
        item['item_id'] = Util.to_md5(title)
        item['item_type'] = 'VIDEO'
        item['create_type'] = '原创'
        item['body'] = ''
        item['size'] = ''
        item['images'] = []
        item['audios'] = []
        item['copyright'] = ''
        item['release_time'] = ''
        item['janesi_time'] = Util.local_time()
        item['scan'] = Util.random_number()
        item['like'] = 0
        item['share'] = 0
        item['play'] = Util.random_number()
        item['forward'] = 0
        item['collect'] = 0
        item['platform'] = 'ergeng'
        item['upload_file_flag'] = 'true'
        item['category'] = {"channel": item['channel'], "child_channel": '', "topic": [], "tag": item['tag'],"keyword": [], "region": ''}

        video_json_url = "http://member.ergengtv.com/api/video/vod/?id=" + html_num

        yield scrapy.Request(url=video_json_url, callback=self.parse_video_url, meta={"item":item})
    def parse_video_url(self,response):
        # print(response.body.decode('utf-8'),'12345--------')
        item = response.meta["item"]
        if "msg" in response.body.decode('utf-8'):

            video_url = re.search(r'"url":"(.*?)",', response.body.decode('utf-8')).group(1)
            item['videos'] = [{"index": 1, "url": video_url, "cut_url": item["cut_url"], "title": item["title"],"duration": item["duration"], "size": ''}]
        item['author_id'] = None
        check = Util.check_item(item)
        if check == 1:
            return
        yield item

"""


    scan = scrapy.Field()  # 阅读数
    like = scrapy.Field()  # 喜欢
    share = scrapy.Field()  # 分享
    play = scrapy.Field()  # 播放次数
    forward = scrapy.Field()  # 转发次数
    collect = scrapy.Field()  # 收藏数
    image_urls = scrapy.Field()

"""
