# -*- coding: utf-8 -*-
import scrapy
import requests
import json
import re
import time
from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem
from scrapy_redis.spiders import RedisSpider

import urllib.parse


class BesttoutiaoSpider(RedisSpider):
    name = 'besttoutiao'
    allowed_domains = ['toutiao.com']
    start_urls = ['http://toutiao.com/']
    BaseUrl = 'https://www.toutiao.com'
    redis_key = 'besttoutiao:start_urls'
    offset = 0
    # UserMediaList = ["中华健康学习网", "陈鹏解梦", "情感两性学", "星座百科", "育儿网", "水煮百年", "耶律萧", "热点第一时间", "优居山西", "中国农贸网", "挖财钱堂社区", ]

    UserMediaList = ['翠红姐的情感地带', '麦田娱乐', '一直陪在你身边', '聆影', '就你最嗨', '眉目传情', '碧玺品鉴', '民间奇葩事', '大熊来扒扒', '不负如来', '可言带你追味美食',
        '史海说', '扭曲的年华', '娱乐小小星', '键盘上的跳跃', '青灯与你', '穷大方的你', '你饿唔饿啊', '娱乐热度', '小妖娱记', '今夜忆风尘', '韵动旋录', '自由自在的旅行', '沐夏繁华',
        '漂亮的瓦力', '丹萌物语', '勾引你的小眼神', '朱亮量爱生活', '如果没有来世', '怎么不晃荡', '育儿团团长', '开良看历史', '光晖岁月', '阿春娱乐', '经典电视电影无极限',
        '足篮排等球类赛事', '娱乐心跳', '老街满桃花', '足坛侦探', '华哥说', '热剧抢先看4', '新豆腐汤', '未知往事', '游戏之道', '最新时光', 'jacky污妖王', '鱼儿的动物天地',
        '划船不靠桨全靠浪', '妄断弥空', '我还没做好准备', '味觉上的思念', '夏日流行时', '月伴小夜曲', '悸动的小四', '夕萌萌的龙猫', '娱乐我最嗨', '仗剑走天涯', '语话良多',
        '生活因拼搏而存在', ]

    def parse(self, response):
        for UserMedia in self.UserMediaList:
            keyword = urllib.parse.quote(UserMedia)
            print(keyword, '*******keyword*********')
            for PageNum in range(0, 120, 20):
                StartUrl = 'https://www.toutiao.com/search_content/?offset={}&format=json&keyword={}&autoload=true' \
                           '&count=20&cur_tab=1&from=search_tab'.format(keyword, str(PageNum))
                print(StartUrl, '******** StartUrl**********')
                yield scrapy.Request(url=StartUrl, callback=self.GetDetailPageUrl)

    def GetDetailPageUrl(self, response):
        PythonObjHtml = json.loads(response.body.decode())
        # print(type(PythonObjHtml))
        if 'data' in PythonObjHtml:
            Data = PythonObjHtml.get('data')
            for WeNeedMsgInData in Data:
                # print(WeNeedMsgInData)
                if 'item_source_url' in WeNeedMsgInData:
                    PartUrl = WeNeedMsgInData.get('item_source_url')
                    EndUrl = self.BaseUrl + PartUrl
                    print(EndUrl)
                    yield scrapy.Request(url=EndUrl, callback=self.ParseDetailPage)

    def ParseDetailPage(self, response):
        item = NewsItem()
        if 'videoID' in response.body.decode('utf-8'):
            print('这条数据为视频数据 >>>>>  pass')
            return
        else:
            try:
                title = re.findall(r"title: '(.*?)',", response.body.decode('utf-8'))[0]
                if title:
                    item['title'] = title
                    item_id = Util.to_md5(title)
                    item['item_id'] = item_id
            except:
                return

            DealWithBody = re.findall(r"content: '(.*?)'", response.body.decode('utf-8'))[0].replace('&lt;',
                                                                                                     '<').replace(
                '&gt;', '>').replace('&quot;', '"').replace('&#x3D;', '=').replace('img_width=', '').replace(
                'img_height=', '').replace('inline=', '')
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
                print('>>>>>>>>> BODY---ERROR >>>>>>>>>>>>>')
                return

            try:
                item['images'] = []
                data_echo_url = re.findall(r'data-echo="(.*?)"', item['body'])
                for num, image_url in enumerate(data_echo_url):
                    temp_image_url = Util.generate_images_pic(image_url)
                    image_dict = {"index": num, "url": temp_image_url, "title": ""}
                    item['images'].append(image_dict)
            except Exception as e:
                print('>>>>>-ERROR->>>>>>', e, '>>> IMAGES---ERROR >>>>-')
                return
            # UserSource = re.findall(r"source: '(.*?)',", response.body.decode('utf-8'))[0]
            try:
                UserSource = re.findall(r"source: '(.*?)',", response.body.decode('utf-8'))[0]
                if UserSource:
                    item['name'] = UserSource
            except Exception as e:
                print('*****name***error******', e)
                item['name'] = '今日头条'
            try:
                UserTime = re.findall(r"time: '(.*?)'", response.body.decode('utf-8'))[0]
                if UserTime:
                    item['release_time'] = UserTime
            except:
                item['release_time'] = Util.local_time()
            # GetTagAll = re.findall(r'tags: \[(.*?)\],', response.body.decode('utf-8'))[0]
            try:
                GetTagAll = re.findall(r'tags: \[(.*?)\],', response.body.decode('utf-8'))[0]
                EndTag = re.findall('\{"name":"(.*?)"\}', GetTagAll)
                if EndTag:
                    item['tag'] = EndTag
            except Exception as e:
                print('*****tag***error******', e)
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
                print('*****channel***error******', e)
                item['channel'] = '社会'
            item['item_type'] = 'ARTICLE'
            item['source'] = '今日头条'

            item['comment'] = Util.random_number()
            item['duration'] = 0
            item['size'] = 0
            item['topic'] = []
            item['keyword'] = []
            item['region'] = ''
            item['category'] = {"channel": item['channel'], "child_channel": '', "topic": [], "tag": item['tag'],
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
            yield item
