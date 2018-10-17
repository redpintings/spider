# -*- coding: utf-8 -*-
# @Time    : 2018/3/1 14:08
# @Author  : 蛇崽
# @Email   : 643435675@QQ.com
# @File    : zaker.py(http://www.myzaker.com  zaker 新闻)
import re

import scrapy
from scrapy_redis.spiders import RedisSpider

from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem


class ZakerSpider(RedisSpider):

    name = 'zaker'

    allowed_domains = ['www.myzaker.com']

    redis_key = 'zaker:start_urls'

    # start_urls = ['http://www.myzaker.com']

    def parse(self, response):
        base_url = 'http://www.myzaker.com/channel/4'

        v1_dict = {
            '财经':'4',
            '科技':'13',
            '体育': '8',
            '军事': '3',
            '娱乐': '9',
            '汽车': '7',
            '时尚': '12',
            '旅游': '981',
            '游戏': '10376',
            '健康': '10802',
            '美食': '10386',
            '星座': '1014',
        }

        for channel, tag_link in v1_dict.items():
            type_link ='http://www.myzaker.com/channel/{}'.format(tag_link)
            yield scrapy.Request(url=type_link,callback=self.get_main_link,meta={'channel':channel},dont_filter=True)

    def get_main_link(self,response):

        channel = response.meta['channel']

        article_list = response.xpath("//*[@class='figure flex-block']")
        for article in article_list:
            a_link = article.xpath("./a[@class='img']/@href").extract_first()
            if a_link:
                item_link = response.urljoin(a_link)
                yield scrapy.Request(url=item_link,callback=self.parse_detail,meta={'channel':channel})

    def parse_detail(self,response):
        item=NewsItem()
        channel = response.meta['channel']

        article_title = response.xpath("//*[@class='article_header']/h1/text()").extract_first()

        _article_author = response.xpath("//*[@class='article_tips']/a/span[@class='auther']/text()").extract_first()
        article_author = 'ZAKER'
        if _article_author:
            article_author = _article_author
        article_retime = response.xpath("//*[@class='article_tips']/a/span[@class='time']/text()").extract_first()

        tag = [channel]
        article_tags = response.xpath("//*[@class='article_more']/a/text()").extract()
        article_tags = tag + article_tags

        article_content = response.xpath("//*[@id='content']").extract()[1]
        temp_content_origin = article_content
        if 'video_container' in temp_content_origin:
            print('sorry, I am get the video')
            return
        if '</iframe>' in temp_content_origin:
            print('sorry, I have get the article with video ')
            return
        if 'data-gif-url=' in temp_content_origin:
            print('sorry, I do not want get the gif pic ')
            return
        image_urls = re.findall(r'data-original="(.*?)"', article_content)
        item_image_urls = []
        for v_image in image_urls:
            item_image_urls.append(response.urljoin(v_image))
            v_url = Util.generate_pic_time(v_image)
            temp_content_origin = temp_content_origin.replace(v_image, v_url)
        item['image_urls'] = item_image_urls
        temp_content_origin = temp_content_origin.replace('data-original','src')
        temp_content_origin = Util.remove_impurity(temp_content_origin)
        item['body'] = Util.replace_style(temp_content_origin) if not None else ''
        try:
            item['images'] = []
            data_echo_url = re.findall(r'data-echo="(.*?)"', item['body'])
            for num, image_url in enumerate(data_echo_url):
                temp_image_url = Util.generate_images_pic(image_url)
                image_dict = {"index": num, "url": temp_image_url, "title": ""}
                item['images'].append(image_dict)
        except:
            item['images'] = []

        item['title']=article_title
        item_id=Util.to_md5(article_title)
        item['item_id']=item_id
        # item['_id']=item_id
        item['item_type'] = 'ARTICLE'
        # 原创还是转载，
        item['create_type']=''
        item['source']='ZAKER'
        item['original_url']=response.url
        janesi_time = Util.local_time()
        article_author = article_author if not None else 'ZAKER'

        item['name'] = article_author
        item['avatar'] = ''
        item['type'] = 0
        item['fans_count'] = 0
        item['scan_count'] = 0
        item['collect_count'] = 0
        item['is_delete'] = '0'
        item['gmt_create'] = janesi_time
        item['gmt_modified'] = janesi_time
        item['platform'] = 'zaker'

        item['category']={"channel":channel,
                           "topic":[],
                           "tag":article_tags,
                           "keyword":[],
                           "region":''}

        item['tag'] = article_tags
        item['channel'] = channel
        item['comment'] = Util.random_number()
        item['duration'] = 0
        item['size'] = 0
        item['topic'] = []
        item['keyword'] = []
        item['region'] = ''

        item["videos"] = []
        item["audios"] = []
        item['videos']=[]
        item['audios']=[]
        item['copyright']=''
        item['release_time']=article_retime
        item['janesi_time']=janesi_time
        item['scan']=Util.random_number()
        item['like']=0
        item['share']=0
        item['play']=Util.random_number()
        item['forward']=0
        item['collect']=0
        item['upload_file_flag'] = 'true'

        check = Util.check_item(item)
        if check == 1:
            return
        yield item


