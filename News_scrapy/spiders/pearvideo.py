# -*- coding: utf-8 -*-
# @Time    : 2018/4/24 11:16
# @Author  : 蛇崽
# @Email   : 643435675@QQ.com
# @File    : pearvideo.py(梨视频)
import json
import re

import scrapy
from scrapy import Spider
from scrapy_redis.spiders import RedisSpider

from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem


class Video_V1(RedisSpider):
    name = 'pearvideo'

    allowed_domains = ['www.pearvideo.com']

    redis_key = 'pearvideo:start_urls'

    # start_urls = ['http://www.pearvideo.com/']

    def parse(self, response):

        v1_dict = {
            '娱乐':'4',
            '社会': '1',
            '生活': '5',
            '音乐': '59',
            '体育': '9',
            '科技': '8',
            '动画': '17',
            '创意': '',
        }
        # reqtype 有 14 5
        type_link  = 'http://www.pearvideo.com/category_loading.jsp?reqType=14&categoryId=&start=12'
        url = "http://www.pearvideo.com/category_loading.jsp?reqType={reqtype}&categoryId={catid}&start={offset}"
        for channel, tag_link in v1_dict.items():
            # type_link = 'http://www.pearvideo.com/category_loading.jsp?reqType=5&categoryId=1&start=24'
            for offset in range(0, 120,12):
                if '创意' in channel:
                    type_link = url.format(reqtype=14,catid=tag_link,offset=offset)
                else:
                    type_link = url.format(reqtype=5, catid=tag_link, offset=offset)
                print('type_link >>>> ',channel,type_link)
                yield scrapy.Request(url=type_link, callback=self.get_main_link, meta={'channel': channel},dont_filter=True)


    def get_main_link(self, response):
        item = NewsItem()
        channel = response.meta['channel']
        item['channel'] = channel
        node_list = response.xpath("//*[@class='vervideo-bd']")
        for node in node_list:
            a_link = node.xpath("./a/@href").extract_first()
            a_link = response.urljoin(a_link)
            title = node.xpath("./a/div[@class='vervideo-title']/text()").extract_first()
            duration = node.xpath("./a/div[@class='vervideo-img']/div[@class='cm-duration']/text()").extract_first()
            cut_url = node.xpath("./a/div[@class='vervideo-img']/div[@class='verimg-view']/div[@class='img']/@style").extract_first()
            cut_url = re.findall(r'url\((.*?)\);',cut_url)[0]
            authorname = node.xpath("./div[@class='actcont-auto']/a/text()").extract_first()
            if a_link and title:
                item['title'] = title
                item['duration'] = duration
                item['cut_url'] = cut_url
                item['name'] = authorname
                yield scrapy.Request(url=a_link,callback=self.parse_detail,meta={'item':item})

    def parse_detail(self,response):
        item = response.meta['item']
        release_time  = response.xpath("//*[@class='brief-box']/div[@class='date']/text()").extract_first()
        mp4_source = re.findall(r'srcUrl="(.*?)"',response.body.decode("utf-8"),re.S)[0]
        if not mp4_source:
            return

        title = item['title']
        channel = item['channel']

        item['item_id'] = Util.to_md5(title)
        item['item_type'] = 'VIDEO'
        item['create_type'] = ''
        item['source'] = '梨视频'
        item['body'] = mp4_source
        item['original_url'] = response.url
        item['copyright'] = ''
        janesi_time = Util.local_time()
        item['release_time'] = release_time if not None else janesi_time
        item['janesi_time'] = janesi_time
        item['scan'] = Util.random_number()
        item['play'] = Util.random_number()
        item['share'] = 0
        item['like'] = 0
        item['forward'] = 0
        item['collect'] = 0
        item['size'] = ''
        item['upload_file_flag'] = 'true'
        tags = []
        try:
            tags = Util.tag_by_jieba_title(title)
            tags.append(channel)
            tags.append('视频')
        except:
            tags.append(channel)
            tags.append('视频')

        item['tag'] = tags

        item['keyword'] = []
        item['topic'] = []

        item['comment'] = Util.random_number()

        item['region'] = ''
        item['avatar'] = ''
        item['type'] = 0

        item['fans_count'] = 0
        item['scan_count'] = 0
        item['collect_count'] = 0
        item['is_delete'] = '0'

        item['gmt_create'] = janesi_time
        item['gmt_modified'] = janesi_time
        item['platform'] = 'pearvideo'

        item['images'] = []
        item['audios'] = []
        item['image_urls'] = []

        item['videos'] = [
            {'cut_url': item['cut_url'], 'duration': item['duration'], 'index': 1, 'size': '', 'title': item['title'],
             'url': mp4_source}]

        item["category"] = {'channel': item['channel'], 'keyword': [], 'region': '', 'tag': item['tag'],
                            'topic': []}

        check = Util.check_item(item)
        if check == 1:
            print(' pearvideo   error status >>>>> ')
            return
        yield item
