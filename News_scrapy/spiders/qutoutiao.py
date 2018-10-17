# -*- coding: utf-8 -*-
import logging
import scrapy
import json
from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem
import re
from scrapy_redis.spiders import RedisSpider


class QutoutiaoSpider(RedisSpider):
    name = 'qutoutiao'
    allowed_domains = ["hoseceo.cn"]
    # start_urls = ['http://home.qutoutiao.net/pages/home.html?']
    redis_key = 'qutoutiqo:start_urls'
    channel_dict = {'娱乐': 'cid=6'
        , '财经': 'cid=10'
        , '科技': 'cid=7'
        , '体育': 'cid=13'
        , '军事': 'cid=15'
        , '时尚': 'cid=14'
        , '旅游': 'cid=16'
        , '游戏': 'cid=19'
        , '汽车': 'cid=9'
        , '历史': 'cid=23'
        , '美食': 'cid=12'
        , '健康': 'cid=42'
        , '星座': 'cid=18'
        , '文化': 'cid=4'}
    def parse(self, response):
        for offset in range(5):
            for channel,url_cid in self.channel_dict.items():
                channel_url = "http://api.1sapp.com/content/outList?{}&tn=1&page={}&dtu=200".format(url_cid,offset)
                print('---channel_url ----------- ',channel_url)
                yield scrapy.Request(url=channel_url,callback=self.parse_item_detail_page_url,meta={'channel':channel},dont_filter=True)


    def parse_item_detail_page_url(self, response):
        item = NewsItem()
        channel = response.meta['channel']
        PythonObjectData = json.loads(response.body.decode('utf-8'))
        DataList = PythonObjectData['data']['data']
        for list in DataList:

            item['source'] = '趣头条'
            page_url  = list['url']
            page_url_d = page_url.split('?')[0]
            item['channel'] = channel
           

            item['item_type'] = 'ARTICLE'
            yield scrapy.Request(url=page_url_d, callback=self.parse_detaile_page, meta={'item': item})

    def parse_detaile_page(self, response):

        item = response.meta['item']

        title = re.findall(r'<h1>(.*?)</h1>', response.body.decode('utf-8'))[0]
        if title:
            item['title'] = title
        else:
            logging.info('-------------TITLE---ERROR---------------')
            return


        item_id = Util.to_md5(title)
        item['item_id'] = item_id

        item['comment'] = Util.random_number()
        item['duration'] = 0
        item['size'] = 0
        item['topic'] = []
        item['keyword'] = []
        item['region'] = ''



        TimeDate = re.findall(r'<div class="info">(.*?)</div>', response.body.decode('utf-8'))[0]
        BodyData = re.findall(r'<div class="content">(.*?)</div>', response.body.decode('utf-8'))[0]
        if BodyData:
            DealWithBody = BodyData.replace('data-size=', '').replace('data-src', 'src')
        else:
            logging.info('-------------BODY---ERROR---------------')
            return

        tag = Util.get_tags_by_jieba(DealWithBody)
        if tag:
            tag.append(item['channel'])
            item['tag'] = tag
        else:
            item['tag'] = item['channel']



        DataJoinTime = ' '.join(TimeDate.split()[:2])
        if DataJoinTime:
            item['release_time'] = DataJoinTime
        else:
            item['release_time'] = Util.local_time()

        name = TimeDate.split()[-1]
        if name:
            item['name'] = name
        else:
            item['name'] = '趣头条'
        item['category'] = {"channel": item['channel'], "topic": [], "tag": item['tag'],
                            "keyword": [],"region": ''}
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


        ImageUrl = re.findall(r'src="(.*?)"', DealWithBody)
        if ImageUrl:
            item['image_urls'] = ImageUrl
        else:
            logging.info('-------------IMAGE_URL---ERROR---------------')
            return
        try:
            Temp_Content = DealWithBody
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
        item['platform'] = 'qutoutiao'
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
