# -*- coding: utf-8 -*-
# @Time    : 2018/2/28 11:26
# @Author  : 蛇崽
# @Email   : 643435675@QQ.com
# @File    : video_v1.py(http://www.v1.cn/ 第一视频)
import json
import re

import scrapy
from scrapy import Spider
from scrapy_redis.spiders import RedisSpider

from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem


class Video_V1(RedisSpider):
    name = 'video_v1'

    allowed_domains = ['www.v1.cn']

    redis_key = 'video_v1:start_urls'

    # start_urls = ['http://www.v1.cn/']

    def parse(self, response):

        v1_dict = {
            '新闻':'xinwen',
            '娱乐':'yule',
            '搞笑': 'gaoxiao',
            '旅游': 'lvyou',
            '财经': 'caijing',
            '美食': 'meishi',
            '汽车': 'qiche',
            '社会': 'shehui',
            '原创': 'yuanchuang',
            '两性': 'liangxing', }
        for channel, tag_link in v1_dict.items():
            type_link = 'http://www.v1.cn/{}/'.format(tag_link)
            yield scrapy.Request(url=type_link, callback=self.get_main_link, meta={'channel': channel},dont_filter=True)


    def get_main_link(self, response):

        channel = response.meta['channel']
        item = NewsItem()
        janesi_time = Util.local_time()
        item['janesi_time'] = janesi_time
        item['gmt_create'] = janesi_time
        item['gmt_modified'] = janesi_time
        item['channel'] = channel
        item["item_type"] = 'VIDEO'
        item["create_type"] = ''
        item["source"] = '第一视频'
        item['avatar'] = ''
        item['type'] = 0
        item['fans_count'] = 0
        item['scan_count'] = 0
        item['collect_count'] = 0
        item['is_delete'] = '0'
        item['keyword'] = []
        item['topic'] = []
        item['comment'] = Util.random_number()

        item['region'] = ''
        item['images'] = []
        item['audios'] = []
        item['copyright'] = ''
        item['like'] = 0
        item['share'] = 0
        item['forward'] = 0
        item['collect'] = 0
        item['image_urls'] = []
        item['size'] = ''
        item['upload_file_flag'] = 'true'
        item['platform'] = 'video_v1'

        for pageindex in range(1,2):
            if int(pageindex) == 1:
                # 解析Html
                yield scrapy.Request(url=response.url,callback=self.parse_first_html,meta={'item':item},dont_filter=True)
            else:
                # # 更多的数据查找
                cid = re.findall(r'id="cid" value="(.*?)"', response.body.decode("utf-8"), re.S)[0]
                # print('cid ', cid)
                main_link = 'http://www.v1.cn/index/getList4Ajax'
                for page in range(1, 30):
                    formdata = {'cid': str(cid), 'page': str(page)}
                    yield scrapy.FormRequest(url=main_link, formdata=formdata, callback=self.get_list_res,meta={'item':item})


    def parse_first_html(self,response):
        item = response.meta['item']
        # print('parse_first_html', response)
        # 当前页面视频
        video_list = response.xpath("//*[@class='infoList']/li")
        # print('video_list  ', len(video_list))

        for video in video_list:
            duration = video.xpath("./div[@class='pic']/span[@class='tipTime']/text()").extract_first()
            # print('时长：',tip_time)
            title = video.xpath("./div[@class='tit']/a/text()").extract_first()
            _author = video.xpath("./div[@class='uploadUser']/p/text()").extract_first()
            author = '第一视频'

            if _author:
                author = _author

            scan = video.xpath("./span[@class='icoPv']/text()").extract_first()
            cut_url = video.xpath("./div[@class='pic']/a/img/@src").extract_first()

            next_link = video.xpath("./div[@class='pic']/a/@href").extract_first()
            print('时长：'+duration,'标题：',title,"作者：",author,'阅读量：',scan,'第一帧：',cut_url,'链接：',next_link)
            new_next_url = response.urljoin(next_link)

            if new_next_url:
                item_id = Util.to_md5(title)
                item["title"] = title
                item['item_id'] = item_id
                item["cut_url"] = cut_url if not None else ''
                item["title"] = title
                item["original_url"] = new_next_url
                item['name'] = author
                channel = item['channel']
                tags = []
                try:
                    tags = Util.tag_by_jieba_title(title)
                except:
                    pass
                item['tag'] = [channel] + tags

                item["category"] = {'channel': channel, 'keyword': [], 'region': '',
                                     'tag': item['tag'], 'topic': []}
                # print('这里执行的tag1', [channel])

                if scan:
                    scan = int(scan)
                else:
                    scan = Util.random_number()
                item['scan'] = scan
                item['play'] = scan
                item['cut_url'] = cut_url

                if duration:
                    item['duration'] = duration
                else:
                    item['duration'] = ''
                yield scrapy.Request(url=new_next_url, callback=self.get_mp4_link,meta={'item':item})


    def get_list_res(self, response):
        # print('get_list_res',response)
        item = response.meta['item']
        jsondatas = json.loads(str(response.body.decode('utf-8')))
        if not jsondatas:
            return
        if jsondatas['msg'] == 1:
            lists = jsondatas['list']
            for j_list in lists:
                vid=j_list['vid']
                title=j_list['title']
                tag=j_list['tag']
                duration=j_list['duration']
                pic=j_list['pic']
                playNum=j_list['playNum']
                nickname=j_list['nickname']

                item_id = Util.to_md5(title)
                item["title"] = title
                # item['_id'] = item_id
                item['item_id'] = item_id
                item["cut_url"] = pic if not None else ''
                item["title"] = title
                original_url = 'http://www.v1.cn/video/'+vid+'.shtml'
                item["original_url"] = original_url
                item['name'] = nickname
                channel = item['channel']
                origin_tag = [channel]
                temp_tag= str(tag).split(' ')
                for v_tag in temp_tag:
                    origin_tag.append(v_tag)
                item["category"] = {'channel': channel, 'keyword': [], 'region': '', 'tag': origin_tag, 'topic': []}

                # print('这里执行的tag2',origin_tag)
                if playNum:
                    playNum = int(playNum)
                else:
                    playNum = Util.random_number()
                item['tag'] = origin_tag
                item['scan'] = playNum
                item['play'] = playNum
                if duration:
                    item['duration'] = duration
                else:
                    item['duration'] = ''
                yield scrapy.Request(url=original_url,callback=self.get_mp4_link,meta={'item':item})


    def get_mp4_link(sellf, response):
        item = response.meta['item']
        response = response.body.decode("utf-8")
        mp4_list = re.findall(r'videoUrl=(.*?)\.mp4', response, re.S)[0]

        # 不是有效的视频播放地址
        if not mp4_list:
            return
        else:
            mp4_list = mp4_list + '.mp4'
            release_time = re.findall(r'publishDate">(.*?)</span>', response, re.S)[0]
            item['videos'] = [{'cut_url': item['cut_url'], 'duration': item['duration'],
                               'index': 1, 'size': '', 'title': item['title'],'url': mp4_list}]
            item['release_time'] = release_time
            item['body'] = mp4_list
            item['author_id'] = None
            check = Util.check_item(item)
            if check == 1:
                return
            yield item

