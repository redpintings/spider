# -*- coding: utf-8 -*-
# @Time    : 18-5-23 下午2:10
# @Author  : 杨星星
# @Email   : yangshilong_liu@163.com
# @File    : YidianSpider
# @Software: PyCharm


import logging
import scrapy
import re
from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem
import re
from scrapy_redis.spiders import RedisSpider


class YidianSpider(RedisSpider):
    name = 'yidian'
    allowed_domains = ['yidianzixun.com']
    # start_urls = ['http://yidianzixun.com/']
    redis_key = 'yidian:start_urls'
    child_channel_dicts = {"育儿":['t10449','e212806','t9651','u7916','u9392','u7934','e1595662','u7744','e268214','t19398','u7682','t10447','u7699']}
    emotion_channel_dicts =  {"情感":['u141','u9384','u575','u9387','u338','e2654','e288452','e929007','e158508','t9436','u655']}
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        "Referer": "http://www.yidianzixun.com/",
    }
    def parse(self,response):

        for channel, ids in self.child_channel_dicts.items():
            for id in ids:
                print('---id----', id)
                url = "http://www.yidianzixun.com/channel/" + str(id)
                yield scrapy.Request(url=url, callback=self.parse_page_links,headers=self.headers, meta={"channel": channel},dont_filter=True)
        for channel, ids in self.emotion_channel_dicts.items():
            for id in ids:
                print('---id----', id)
                url = "http://www.yidianzixun.com/channel/" + str(id)
                yield scrapy.Request(url=url, callback=self.parse_page_links,headers=self.headers, meta={"channel": channel},dont_filter=True)


    def parse_page_links(self,response):
        channel = response.meta['channel']
        # print(channel)
        # url = response.url
        response_html = response.body.decode('utf-8')
        article_links = re.findall(r'href="(.*?)"',response_html)
        for article_link in article_links:
            if 'article' in article_link:
                article_url = "http://www.yidianzixun.com" + str(article_link)
                print('--flag1---url----',article_url)
                yield scrapy.Request(url=article_url,callback=self.parse_article_detail,meta={"channel": channel},headers=self.headers)
            else:
                continue

    def parse_article_detail(self,response):
        channel = response.meta['channel']
        item = NewsItem()
        #  class="doc-source">福建吃喝玩乐</   <div class="source imedia">福建吃喝玩乐</div><
        name = re.findall(r'<div class="source imedia">(.*?)</div>', response.body.decode('utf-8'))[0]
        title = re.findall(r'<h3>(.*?)</h3>', response.body.decode('utf-8'))[0]
        OriginalBody = re.findall(r'<body>(.*?)</body>', response.body.decode('utf-8'))[0]
        NeedRepImageUrls = re.findall(r'"url":"(.*?)"', re.findall(r'"images":\[(.*?)\]', response.body.decode('utf-8'))[0])
        BodyFlags = re.findall(r'<div id="article-img-\d+"class="a-image" .*?></div>', response.body.decode('utf-8'))
        if '.mp4' in OriginalBody:
            print('>>>-----视频资源----PASS----')
            return
        else:
            rep_body = OriginalBody
            for flag, image in zip(BodyFlags, NeedRepImageUrls):
                rep_body = rep_body.replace(flag, '<img src="http:' + image + '">')

            RemoveBodyId = re.sub(r'id=".*?"', '', rep_body)
            RemoveBodyClass = re.sub(r'class=".*?"', '', RemoveBodyId)
            ImageUrl = re.findall(r'src="(.*?)"', RemoveBodyClass)
            item['image_urls'] = ImageUrl
            try:
                tag = Util.get_tags_by_jieba(RemoveBodyClass)
                if tag:
                    tag.append(channel)
                    item['tag'] = tag
            except Exception as error:
                logging.info(error,'-----tag--error-----')
                return
            if title:
                item['title'] = title
                item_id = Util.to_md5(title)
                item['item_id'] = item_id
            else:
                return

            try:
                Temp_Content = RemoveBodyClass
                for content_img_url in ImageUrl:
                    content_url_temp = Util.generate_pic_time_yidian_lazy(content_img_url)
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
                    image_url = image_url.replace('.jpg', '')
                    temp_image_url = Util.generate_pic_time_yd(image_url) + '.jpg'
                    image_dict = {"index": num, "url": temp_image_url, "title": ""}
                    item['images'].append(image_dict)
            except Exception as e:
                print('-----ERROR----', e, '--IMAGES---ERROR----')
                logging.info('-------------IMAGES---ERROR---------------')
                return
            item['item_type'] = 'ARTICLE'
            item['channel'] = channel
            item['source'] = '一点资讯号'
            if name:
                item['name'] = name
            else:
                item['name'] = '一点资讯号'

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
            item['release_time'] = janesi_time
            item['scan'] = Util.random_number()
            item['like'] = 0
            item['share'] = 0
            item['play'] = Util.random_number()
            item['forward'] = 0
            item['collect'] = 0
            item['upload_file_flag'] = 'true'
            item['platform'] = 'yidianzixun'
            item['author_id'] = None
            if not item['body']:
                return
            if len(item['body']) < 200:
                return
            CheckItem = Util.check_item(item)
            print('----------',CheckItem ,'------------')
            if CheckItem == 1:
                return
            yield item

