# -*- coding: utf-8 -*-
# @Time    : 18-8-23 下午u
#3:12
# @Author  : 杨星星
# @Email   : yangshilong_liu@163.com
# @Software: PyCharm


import scrapy
import json
from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem
import re
from scrapy_redis.spiders import RedisSpider
from News_scrapy.toutiao_region_city import ALLCITY
import urllib.parse
import random

class ToutiaoRegionsSpider(RedisSpider):

    name = 'toutiao_regions'
    allowed_domains = ["toutiao.com"]
    redis_key = 'toutiaoregion:start_urls'
    # start_urls = ["https://is.snssdk.com/api/news/feed/v46/?category=news_local&user_city=%E9%9D%92%E5%B2%9B"]
    start_urls_data = ALLCITY

    def parse(self, response):
        for region_p, region_c, region_ip in self.start_urls_data:
            print(region_p, '>>>>>>>>>>>>>>>')
            city_data_decode = urllib.parse.quote(region_c)
            print(city_data_decode, '>>>>>>>>>>')
            try:
                url = "https://is.snssdk.com/api/news/feed/v46/?category=news_local&user_city={}".format(city_data_decode)
                yield scrapy.Request(url=url, callback=self.parse_item,meta={"region_code": region_ip, "region_keyword": [region_p, region_c]},dont_filter=True, )
            except:
                return

    def parse_item(self, response):
        if not response.body:
            return
        try:
            json_data = json.loads(response.body.decode('utf-8'))
            list_original_data = json_data.get('data')
            for dict_original_msg in list_original_data:
                str_original_content = dict_original_msg.get("content")
                dict_article_url = json.loads(str_original_content)
                article_url = dict_article_url.get("article_url")
                print('***' * 10)
                print(article_url)
                print('***' * 10)
                if article_url and "toutiao.com" in article_url:
                    yield scrapy.Request(url=article_url, callback=self.parse_page_detail, meta=response.meta)
        except Exception as e:
            print(e)
            return


    def parse_page_detail(self,response):
        if not response.body:
            return
        item = NewsItem()
        try:
            # print(response.body.decode('utf-8'))
            region_code = response.meta['region_code']
            region_keyword = response.meta['region_keyword']
            content = re.findall(r'(content: .*?) groupId:',response.body.decode('utf-8'),re.S)[0]
            content = re.findall(r"content: '(.*)',",content)[0]
            content_body = content.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#x3D;', '=').replace('img_width=', '').replace('img_height=', '').replace('inline="0"', '')
            image_urls = re.findall(r'src="(.*?)"',content_body)
            if image_urls:
                item['image_num'] = len(image_urls)
                item['image_urls'] = image_urls
            else:
                return
            title = re.findall(r" title: '(.*?)',",response.body.decode('utf-8'))[0]
            article_time = re.findall(r"time: '(.*?)'",response.body.decode('utf-8'))[0]
            article_name = re.findall(r"source: '(.*?)',",response.body.decode('utf-8'))[0]
            article_avatar = re.findall(r" avatar: '(.*?)',",response.body.decode('utf-8'))[0]

            if title:
                item['title'] = title
            else:
                return
            item_id = Util.to_md5(title)
            item['item_id'] = item_id
            item['item_type'] = "ARTICLE"
            item['source'] = '今日头条'
            item['channel'] = '地区'
            item['comment'] = Util.random_number()
            item['duration'] = 0
            item['size'] = 0
            item['topic'] = []
            item['keyword'] = region_keyword
            if region_code:
                item['region'] = region_code

            if article_time:
                item['release_time'] = article_time
            else:
                item['release_time'] = Util.local_time()

            if article_name:
                item['name'] = article_name
            else:
                item['name'] = '今日头条'

            item['create_type'] = '4'
            item['original_url'] = response.url
            if article_avatar:
                item['avatar'] = article_avatar
            else:
                item['avatar'] = ''
            item['type'] = 0
            item['fans_count'] = 0
            item['scan_count'] = 0
            item['collect_count'] = 0
            item['is_delete'] = '0'
            janesi_time = Util.local_time()
            item['gmt_create'] = janesi_time
            item['gmt_modified'] = janesi_time

            tag = Util.get_tags_by_jieba(content_body)
            if tag:
                item['tag'] = tag
            else:
                item['tag'] = item['channel']

            item['category'] = {"channel": item['channel'], "topic": [], "tag": item['tag'],
                                "keyword": [], "region": item['region']}

            try:
                Temp_Content = content_body
                for content_img_url in image_urls:
                    content_url_temp = Util.generate_pic_time(content_img_url)
                    Temp_Content = Temp_Content.replace(content_img_url, content_url_temp)
                item['body'] = Temp_Content
            except Exception as e:
                print(e,'BODY ERROR  RETURN ')
                return
            try:
                item['images'] = []
                data_echo_url = re.findall(r'data-echo="(.*?)"', item['body'])
                for num, image_url in enumerate(data_echo_url):
                    temp_image_url = Util.generate_images_pic(image_url)
                    image_dict = {"index": num, "url": temp_image_url, "title": ""}
                    item['images'].append(image_dict)
            except Exception as e:
                print( e, '--IMAGES---ERROR----')
                return
        except Exception as e:
            print(response.url,'>>>>>>>>>>>>>>>>>')
            print(e,'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            return

        item['videos'] = []
        item['audios'] = []
        item['copyright'] = ''
        item['janesi_time'] = janesi_time
        item['scan'] = Util.random_number()
        item['like'] = 0
        item['share'] = 0
        item['play'] = Util.random_number()
        item['forward'] = 0
        item['collect'] = 0
        item['upload_file_flag'] = 'true'
        item['platform'] = 'jinritoutiao'
        item['author_id'] = None
        if not item['body']:
            return
        if len(item['body']) < 200:
            return
        CheckItem = Util.check_item(item)
        print( CheckItem,'CHECK ITEM >>>>> ')
        if CheckItem == 1:
            return
        yield item





