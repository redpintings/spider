# -*- coding: utf-8 -*-
import scrapy
import json
import re
import time
from scrapy_redis.spiders import RedisSpider

from News_scrapy.items import NewsItem
from News_scrapy.MyUtils import Util
import random


class VmovSpider(RedisSpider):
    name = 'vmov'
    allowed_domains = ['vmovier.com']
    # start_urls = ['http://vmovier.com/']
    redis_key = 'vmov:start_urls'

    start_urls = ['https://www.vmovier.com/post/getbytab?tab=new&page=0&pagepart=0&controller=index']  # page=1&pagepart=1
    page_num = 0

    def parse(self, response):
        node_list = json.loads(response.body.decode('utf-8'))["data"]
        if not node_list:
            return
        res = re.compile(r'<li(.*?)</li>', re.S)
        nodes = res.findall(node_list)
        for node in nodes:
            item = NewsItem()
            detail_link = re.findall(r'<h1><a.*?href="(.*?)"', node)[0]
            detail_link = "https://www.vmovier.com" + detail_link
            title = re.findall(r'<h1><a.*?href=".*?" title="(.*?)"', node)[0]
            item["title"] = title

            item_id = Util.to_md5(title)
            item['item_id'] = item_id
            # item['_id'] = item_id
            item["cut_url"] = re.findall(r'<img src="(.*?)"', node)[0]
            yield scrapy.Request(url=detail_link, meta={"item": item}, callback=self.parse_detail,dont_filter=True)


    def parse_detail(self, response):
        item = response.meta["item"]
        item['original_url'] = response.url
        item["item_type"] = "VIDEO"
        item['create_type'] = '原创'

        try:
            item["source"] = "v电影"
        except:
            item["source"] = "v电影"
        try:

            author = re.findall(r'<span class="author">(.*?)</span>', response.body.decode('utf-8'))[0]
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

        except:
            item["author"] = ''
        try:
            tag = response.xpath('//div[@class="post-tag"]//a/text()').extract()
            tag.append("视频")
            channel = re.findall(r'<a href="/channel.*?" title=".*?">(.*?)</a>', response.body.decode('utf-8'))[0]
            tag.append(channel)
            item['tag'] = tag
            item['comment'] = Util.random_number()

            item['topic'] = []
            item['keyword'] = []
            item['region'] = ''
            item['channel'] = channel
            item["category"] = {'channel': channel,'keyword': [],'region': '','tag': tag,'topic': []}
        except:
            item["category"] = {'channel': '', 'keyword': [], 'region': '', 'tag': ['视频'], 'topic': []}
        item["image_urls"] = []
        item['copyright'] = ""

        item['scan'] = Util.random_number()


        item['like'] = 0
        item['share'] = 0
        item['play'] = Util.random_number()
        item['forward'] = 0
        item['collect'] = 0
        item['platform'] = 'vmov'

        try:
            item["release_time"] = re.findall(r' <span class="time">(.*?)</span>', response.body.decode('utf-8'))[0]
        except:
            item["release_time"] = ''
        item["janesi_time"] = Util.local_time()
        try:
            html_tag = re.search(r'vtom_vid', response.body.decode("utf-8"))
            if html_tag:
                res = re.findall(r"vtom_vid='(.*?)'", response.body.decode("utf-8"))[0]
                res_1 = "https://openapi-vtom.vmovier.com/video/" + res
            else:
                res_1 = re.findall(r"vid='' src='(.*?)'", response.body.decode("utf-8"))[0]
            yield scrapy.Request(url=res_1, meta={"item": item}, callback=self.parse_video_link)
        except:
            print('--VIDEO-DETAIL--ERROR--')

    def parse_video_link(self, response):
        item = response.meta["item"]
        try:
            item["duration"] = re.findall(r'"duration":(.*?),', response.body.decode("utf-8"), re.S)[-3]
        except:
            item["duration"] = re.findall(r'"duration":(.*?),', response.body.decode("utf-8"), re.S)[0]
        try:
            item["size"] = re.findall(r'"filesize":(.*?),', response.body.decode("utf-8"), re.S)[-3]
        except:
            item["size"] = re.findall(r'"filesize":(.*?),', response.body.decode("utf-8"), re.S)[0]
        try:
            content = re.findall(r'<video id=.*? src="(.*?)"', response.body.decode('utf-8'))[0]
            item["body"] = "https:" + content
        except:
            return
        item["images"] = []
        duration_data = int(item["duration"])/1000
        duration_fina = time.strftime("%M:%S", time.gmtime(int(duration_data)))
        item["duration"] = duration_fina
        item['upload_file_flag'] = 'true'
        if len(item['body']) < 5:
            return
        item['videos'] = [{"index": 1, "url": item["body"], "cut_url": item["cut_url"], "title": item["title"],
                           "duration": item["duration"], "size": item["size"]}]
        item['audios'] = []
        item['author_id'] = None
        check = Util.check_item(item)
        if check == 1:
            return
        yield item

