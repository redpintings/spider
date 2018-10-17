# -*- coding: utf-8 -*-
import scrapy
import csv
import re

from scrapy_redis.spiders import RedisSpider
from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem
import logging
import requests

# id_list =[]
# with open('../id.csv',newline='') as csvfile:
#   csvReader = csv.reader(csvfile)
#   for content in csvReader:
#       content = str(content)
#       if 'l.' in content:
#           continue
#       id_list.append(content.split('\\')[0].replace("['",""))


class BobovideoSpider(RedisSpider):
    name = 'bobovideo'
    allowed_domains = ['bbobo.com']
    # start_urls = ['http://bbobo.com/']
    base_url = "https://show.bbobo.com/show/"
    redis_key = 'bobovideo:start_urls'

    id_list = []
    with open('/home/admin/janesi-spider/News_scrapy/id.csv', newline='') as csvfile:
        csvReader = csv.reader(csvfile)
        for content in csvReader:
            content = str(content)
            if 'l.' in content:
                continue
            id_list.append(content.split('\\')[0].replace("['", ""))
    # print(id_list)
    def get_id(self):
        for id in self.id_list:
            yield id

    def parse(self, response):
        for UrlId in self.get_id():
            url = self.base_url + str(UrlId)
            print(url)
            yield scrapy.Request(url=url,callback=self.parse_item)

    def parse_item(self,response):
        # print(response.url)
        item = NewsItem()
        VideoUrl = re.findall(r'"videourl":"(.*?)",', response.body.decode('utf-8'))[0].replace('\\u002F', '/')
        title = re.findall(r'"videotitle":"(.*?)",', response.body.decode('utf-8'))[0]
        cut_url = re.findall(r'"videoposter":"(.*?)"', response.body.decode('utf-8'))[0].replace('\\u002F', '/')
        author_name = re.findall(r'"username":"(.*?)",', response.body.decode('utf-8'))[0]
        time = re.findall(r'"time1":"(.*?)",', response.body.decode('utf-8'))[0]

        if title:
            item['title'] = title
            item_id = Util.to_md5(title)
            item['item_id'] = item_id

        else:
            return
        item['item_type'] = 'VIDEO'
        item['create_type'] = ''
        item['source'] = '秒拍视频'
        item['original_url'] = response.url
        if author_name:
            item['name'] = author_name
        else:
            item['name'] = ''
        item['channel'] = '搞笑'
        item['avatar'] = ''
        item['type'] = 0
        item['fans_count'] = ''
        item['scan_count'] = ''
        item['platform'] = 'miaopaishipin'
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
        item['duration'] = 0
        item['size'] = 0
        item['topic'] = []
        item['keyword'] = []
        item['region'] = ''
        item['category'] = {"channel": item['channel'], "child_channel": '', "topic": [], "tag": item['tag'],
                            "keyword": [], "region": ''}

        item['image_urls'] = []
        if VideoUrl:
            item['body'] = VideoUrl
        else:
            return
        item['images'] = []
        item["duration"] = ''
        try:
            item['videos'] = [{"index": 1, "url": item["body"], "cut_url": cut_url, "title": item["title"],
                               "duration": item["duration"], "size": ''}]
        except:
            return
        item['audios'] = []
        item['copyright'] = ''
        if time:
            item['release_time'] = time
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





