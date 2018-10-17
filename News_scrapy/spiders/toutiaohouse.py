# -*- coding: utf-8 -*-
# @Author  : 杨星星
# @Email   : yangshilong_liu@163.com

import scrapy
import re
import json
from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem
import logging
from scrapy_redis.spiders import RedisSpider

class SnssdkComSpider(RedisSpider):
    name = 'toutiaohouse'
    allowed_domains = ['toutiao.com/']
    # start_urls = ['https://www.toutiao.com/']
    redis_key = 'toutiaohouse:start_urls'
    offset = 1
    url = 'http://is.snssdk.com/api/news/feed/v82/?fp=92TqFMGeFrxOFlHWcrU1Flx7PzwW&version_code=6.7.0&app_name=news_article_social' \
                   '&vid=632BC0D3-070C-4646-9E5F-653F1D7EF608&device_id=6451058272&channel=App%20Store&resolution=750*1334&aid=19&ab_version' \
                   '=304490,314992,346138,349322,271178,345493,326590,326524,326532,338589,336927,346298,295827,345775,315440,239095,348853,' \
                   '344350,170988,346542,332099,325198,331423,338955,330633,297058,276204,286211,313219,338068,348321,349110,277769,310595,34' \
                   '6210,349012,349167,334583,339207,323233,328673,346556,280773,338894,319959,344870,345191,348455,349018,321404,345844,348671' \
                   ',343721,343439,214069,31210,338061,348939,348776,247849,280447,281295,328218,325613,330457,348989,347923,349229,288416,2901' \
                   '94,326194,339904,345202&ab_feature=201617,z1&ab_group=201617&openudid=8dde15c476e11cf243e6f9d4fc8b2d5356c9d107&idfv=632BC0D3' \
                   '-070C-4646-9E5F-653F1D7EF608&ac=WIFI&os_version=11.2.1&ssmix=a&device_platform=iphone&iid=32617735615&ab_client=a1,f2,f7,e1' \
                   '&device_type=iPhone%206&idfa=BB7350ED-5273-4BEF-908D-DCEE2C03A46C&language=zh-Hans-CN&support_rn=4&image=1&list_count=33&count=20' \
                   '&tt_from=pull&category=news_house&city=&last_refresh_sub_entrance_interval=1216&user_city=%E5%8C%85%E5%A4%B4&refer=1&refresh_reason=1' \
                   '&concern_id=6215497897127971330&st_time=1480&session_refresh_idx=2&strict=0&LBS_status=deny&detail=1&min_behot_time=1526369943&loc_mode=0' \
                   '&cp=5bAaF3A489EA1q1&as=a255f8df906a4a6eca8608&ts=1526369952'
    def parse(self, response):
        yield scrapy.Request(url=self.url,callback=self.parse_article_url,dont_filter=True)

    def parse_article_url(self,response):
        HTML = json.loads(response.body.decode('utf-8'))
        print(type(HTML))
        # print(HTML)
        if 'data' in HTML:
            node_list = HTML.get('data')
            for node in node_list:
                url = re.findall(r'"article_url":"(.*?)"', node.get('content'))[0]
                if 'wukong' in url:
                    continue
                if 'toutiao.com' in url:
                    yield scrapy.Request(url=url,callback=self.parse_page_content,dont_filter=True)

    def parse_page_content(self,response):
        item = NewsItem()
        title = re.findall(r'<title>(.*?)</title>', response.body.decode('utf-8'))[0]
        if title:
            item['title'] = title
        else:
            logging.info('-------------TITLE---ERROR---------------')
            return

        item_id = Util.to_md5(title)
        item['item_id'] = item_id
        # item['_id'] = item_id

        item['item_type'] = 'ARTICLE'
        item['create_type'] = ''
        item['original_url'] = response.url
        item['channel'] = '房产'
        item['comment'] = Util.random_number()
        item['duration'] = 0
        item['size'] = 0
        item['topic'] = []
        item['keyword'] = []
        item['region'] = ''


        item['source'] = '今日头条'
        content = re.findall(r"content: '(.*?)',", response.body.decode('utf-8'))[0]
        content = content.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#x3D;','=')\
                .replace('img_width=', '').replace('img_height=', '').replace('inline="0"', '')
        name = re.findall(r"source: '(.*?)',", response.body.decode('utf-8'))[0]
        tags = Util.get_tags_by_jieba(content)
        if tags:
            tags.append(item['channel'])
            item['tag'] = tags
        else:
            item['tag'] = item['channel']

        if name:
            item['name'] = name
        else:
            item['name'] = '今日头条'
        time = re.findall(r"time: '(.*?)'", response.body.decode('utf-8'))[0]
        if time:
            item['release_time'] = time
        else:
            item['release_time'] = Util.local_time()
        #  -----
        ImageUrl = re.findall(r'src="(.*?)"', content)
        if ImageUrl:
            item['image_urls'] = ImageUrl
        else:
            logging.info('-------------IMAGE_URL---ERROR---------------')
            return

        try:
            Temp_Content = content
            for content_img_url in ImageUrl:
                content_url_temp = Util.generate_pic_time(content_img_url)
                Temp_Content = Temp_Content.replace(content_img_url, content_url_temp)
            item['body'] = Temp_Content
        except Exception as e:
            print(e)
            logging.info('-------------BODY---ERROR---------------')
            return
        try:
            item['images'] = []
            data_echo_url = re.findall(r'data-echo="(.*?)"', item['body'])
            for num, image_url in enumerate(data_echo_url):
                temp_image_url = Util.generate_images_pic(image_url)
                image_dict = {"index": num, "url": temp_image_url, "title": ""}
                item['images'].append(image_dict)
        except Exception as e:
            print('-----ERROR----', e, '--IMAGES---ERROR----')
            logging.info('-------------IMAGES---ERROR---------------')
            return
        item['category'] = {"channel": item['channel'], "topic": [], "tag": item['tag'],
                            "keyword": [],"region": ''}
        item['avatar'] = ''
        item['type'] = 0
        item['fans_count'] = ''
        item['scan_count'] = ''
        item['collect_count'] = ''
        item['is_delete'] = '0'
        janesi_time = Util.local_time()
        item['gmt_create'] = janesi_time
        item['gmt_modified'] = janesi_time

        item['videos'] = []
        item['audios'] = []
        item['copyright'] = ''
        janesi_time = Util.local_time()
        item['janesi_time'] = janesi_time
        item['scan'] = Util.random_number()
        item['like'] = 0
        item['share'] = 0
        item['play'] = Util.random_number()
        item['forward'] = 0
        item['collect'] = 0
        item['upload_file_flag'] = 'true'
        item['platform'] = 'toutiao'
        item['author_id'] = None
        if not item['body']:
            return
        if len(item['body']) < 200:
            return
        CheckItem = Util.check_item(item)
        print('-------------##------', CheckItem, '-----------##--------')
        if CheckItem == 1:
            return
        yield item

        while self.offset < 4:
            yield scrapy.Request(url=self.url, callback=self.parse_article_url, dont_filter=True)
            self.offset += 1



            # for title, content, name, time in zip(titles, contents, names, times):
        #     content = content.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#x3D;','=')\
        #         .replace('img_width=', '').replace('img_height=', '').replace('inline="0"', '')
        #     print(title, name, time, content)





