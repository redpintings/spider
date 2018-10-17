# -*- coding: utf-8 -*-
# @Time    : 2018/7/16 2:01
# @Author  : 蛇崽
# @Email   : 643435675@QQ.com
# @File    :头条精品内容
import scrapy
import requests
import json
import re
import time
from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem
from scrapy_redis.spiders import RedisSpider


from News_scrapy.utils.toutiaomedialist import usermediaList


class BesttoutiaoSpider(RedisSpider):
    name = 'toutiaoquality'
    allowed_domains = ['toutiao.com']
    # start_urls = ['http://www.toutiao.com/']
    baseurl = 'https://www.toutiao.com'
    redis_key = 'toutiaoquality:start_urls'

    UserMediaList = usermediaList

    def parse(self, response):
        for media_id in self.UserMediaList:
            media_url = 'https://www.toutiao.com/api/pc/media_hot/?media_id={}'.format(media_id)
            yield scrapy.Request(url=media_url,callback=self.get_main)

    def get_main(self,response):
        infos = json.loads(response.body.decode('utf-8'))
        item = NewsItem()
        if 'success' in infos['message']:
            hot_articles = infos['data']['hot_articles']
            for article in hot_articles:
                if article.get('has_video'):
                    print('this is video ---->> ',article)
                else:
                    detailurl = self.baseurl+article.get('url')
                    title = article.get('title')
                    item['title'] = title
                    item_id = Util.to_md5(title)
                    item['item_id'] = item_id
                    yield scrapy.Request(detailurl,callback=self.parse_detail,meta={'item':item})


    def parse_detail(self,response):
        item = response.meta['item']

        DealWithBody = re.findall(r"content: '(.*?)'", response.body.decode('utf-8'))[0].replace('&lt;', '<').replace(
            '&gt;', '>').replace('&quot;', '"').replace('&#x3D;', '=').replace('img_width=', '').replace('img_height=',
            '').replace('inline=', '')
        ImageUrls = re.findall(r'src="(.*?)"', DealWithBody)
        if ImageUrls:
            item['image_urls'] = ImageUrls
        try:
            Temp_Content = DealWithBody
            for content_img_url in ImageUrls:
                content_url_temp = Util.generate_pic_time(content_img_url)
                Temp_Content = Temp_Content.replace(content_img_url, content_url_temp)
            item['body'] = Temp_Content
        except Exception as e:
            print(e)
            return

        try:
            item['images'] = []
            data_echo_url = re.findall(r'data-echo="(.*?)"', item['body'])
            for num, image_url in enumerate(data_echo_url):
                temp_image_url = Util.generate_images_pic(image_url)
                image_dict = {"index": num, "url": temp_image_url, "title": ""}
                item['images'].append(image_dict)
        except Exception as e:
            return
        try:
            UserSource = re.findall(r"source: '(.*?)',", response.body.decode('utf-8'))[0]
            if UserSource:
                item['name'] = UserSource
        except Exception as e:
            item['name'] = '今日头条'
        try:
            UserTime = re.findall(r"time: '(.*?)'", response.body.decode('utf-8'))[0]
            if UserTime:
                item['release_time'] = UserTime
        except:
            item['release_time'] = Util.local_time()
        try:
            GetTagAll = re.findall(r'tags: \[(.*?)\],', response.body.decode('utf-8'))[0]
            EndTag = re.findall('\{"name":"(.*?)"\}', GetTagAll)
            if EndTag:
                item['tag'] = EndTag
        except Exception as e:
            tag = Util.get_tags_by_jieba(item['body'])
            if tag:
                item['tag'] = tag
            else:
                item['tag'] = []
        try:
            Channel = re.findall(r"chineseTag: '(.*?)',", response.body.decode('utf-8'))[0]
            if Channel:
                item['channel'] = Channel
        except Exception as e:
            item['channel'] = '社会'
        item['item_type'] = 'ARTICLE'
        item['source'] = '今日头条'

        item['comment'] = Util.random_number()
        item['duration'] = 0
        item['size'] = 0
        item['topic'] = []
        item['keyword'] = []
        item['region'] = ''
        item['category'] = {"channel": item['channel'], "topic": [], "tag": item['tag'],
                            "keyword": [], "region": ''}
        item['create_type'] = ''
        item['original_url'] = response.url
        item['avatar'] = ''
        item['type'] = 0
        item['fans_count'] = 0
        item['scan_count'] = 0
        item['collect_count'] = 0
        item['is_delete'] = '0'
        janesi_time = Util.local_time()
        item['gmt_create'] = janesi_time
        item['gmt_modified'] = janesi_time
        item['videos'] = []
        item['audios'] = []
        item['copyright'] = ''
        item['janesi_time'] = janesi_time
        # item['release_time'] = janesi_time
        item['scan'] = Util.random_number()
        item['like'] = 0
        item['share'] = 0
        item['play'] = Util.random_number()
        item['forward'] = 0
        item['collect'] = 0
        item['upload_file_flag'] = 'true'
        item['platform'] = 'jinritoutiao'
        item['author_id'] = None
        if item['channel'] == '视频':
            return
        if not item['body']:
            return
        if len(item['body']) < 200:
            return
        CheckItem = Util.check_item(item)
        print('----------', CheckItem, '------------')
        if CheckItem == 1:
            return
        print('打印开始========================（）（）（）=============================')
        yield item

