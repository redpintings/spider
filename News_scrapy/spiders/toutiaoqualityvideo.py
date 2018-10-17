# -*- coding: utf-8 -*-
# @Time    : 2018/7/16 15:44
# @Author  : 蛇崽
# @Email   : 643435675@QQ.com
# @File    : toutiaoqualityvideo.py(精品头条视频内容爬取)
import base64
import json
import random

import re

import binascii
import scrapy
import time

from scrapy_redis.spiders import RedisSpider

from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem
from News_scrapy.utils.commenutil import CommenUtil
from News_scrapy.utils.toutiaomedialist import usermedia_videolist

class ToutiaoQualityVideoSpider(RedisSpider):
    name = 'atoutiaoqualityvideo'
    allowed_domains = ['365yg.com']
    #start_urls = ['http://www.365yg.com']
    redis_key = 'atoutiaoqualityvideo:start_urls'
    usermidialist = usermedia_videolist

    def parse(self, response):
        for media_id in self.usermidialist:
            media_url = 'http://www.365yg.com/c/user/article/?user_id={}&max_behot_time=0&max_repin_time=0&count=20&page_type=0'.format(media_id)
            yield scrapy.Request(url=media_url,callback=self.get_main,meta={'media_id':media_id})

    def get_main(self,response):
        media_id = response.meta['media_id']
        infos = json.loads(response.body.decode('utf-8'))
        item = NewsItem()
        if 'success' in infos['message']:
            # 解析本页内容
            datas = infos['data']
            for data in datas:
                item['name'] = data['source'] if  None else ''
                item['title'] = data['title']
                item['item_id'] = Util.to_md5(item['title'])
                item['cut_url'] = data['image_url']
                source_url = data['source_url']
                n_url = response.urljoin(source_url)
                # print('parse_detail ===  data_url   ===================  ', n_url)
                yield scrapy.Request(n_url,callback=self.parse_detail,meta={'item':item})

            max_behot_time = infos['next']['max_behot_time']
            # 获取下一页的链接
            if max_behot_time:
                media_url = 'http://www.365yg.com/c/user/article/?user_id={}&max_behot_time={}&max_repin_time=0&count=20&page_type=0'.format(media_id,max_behot_time)
                # print('parse_detail ====  media_url        ==================  ', media_url)
                yield scrapy.Request(media_url,callback=self.get_main,meta={'media_id':media_id})



    def parse_detail(self,response):
        # print('parse_detail ======================  ',response)
        item = response.meta['item']
        res = response.body.decode('utf-8')
        videoId = re.findall(r"videoId: '(.*?)'",res,re.S)[0]
        # print('videoId ====  ',videoId)
        # 获取到videoId
        if videoId:
            url = CommenUtil.get_video_url(videoId)
            if url:
                yield scrapy.Request(url,callback=self.get_video_info,meta={'item':item})

    def get_video_info(self,response):
        item = response.meta['item']
        infos = json.loads(response.body.decode('utf-8'))
        # print('get_video_info  ======  ',response)
        if 'success' in infos['message']:
            duration = infos['data']['video_duration']
            videolist = infos['data']['video_list']
            keys = list(videolist.keys())
            videoinfo = videolist[keys[-1:][0]]
            url = base64.b64decode(videoinfo['main_url']).decode('utf-8')
            # print('get_video_info_base 64  ==============  ',url)
            item['duration'] = duration
            item['body'] = url
            item['item_type'] = 'VIDEO'
            item['create_type'] = ''
            item['source'] = '西瓜视频'
            item['original_url'] = response.url
            item['channel'] = '精品'
            item['avatar'] = ''
            item['type'] = 0
            item['fans_count'] = 0
            item['scan_count'] = 0
            item['platform'] = 'xiguashiping'
            item['collect_count'] = 0
            item['is_delete'] = 0
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
            item['category'] = {"channel": item['channel'], "topic": [], "tag": item['tag'],
                                "keyword": [], "region": ''}

            item['image_urls'] = []
            item['images'] = []
            item["duration"] = ''
            try:
                item['videos'] = [{"index": 1, "url": item["body"], "cut_url": item['cut_url'], "title": item["title"],
                                   "duration": item["duration"], "size": ''}]
            except:
                return
            item['audios'] = []
            item['copyright'] = ''
            item['release_time'] = janesi_time
            item['janesi_time'] = janesi_time
            item['scan'] = Util.random_number()
            item['like'] = 0
            item['share'] = 0
            item['play'] = 0
            item['forward'] = 0
            item['collect'] = 0
            item['upload_file_flag'] = 'true'
            item['author_id'] = None
            check = Util.check_item(item)
            if check == 1:
                return
            # yield item
            print(item)
