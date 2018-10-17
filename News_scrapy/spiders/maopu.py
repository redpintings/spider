# -*- coding: utf-8 -*-
import scrapy
import re
import json

from scrapy_redis.spiders import RedisSpider
import time
from News_scrapy.items import NewsItem
from News_scrapy.MyUtils import Util

class MaopuSpider(RedisSpider):
    name = 'maopu'
    allowed_domains = ['mop.com']
    # start_urls = ['http://tv.mop.com/life.html']
    redis_key = 'maopu:start_urls'

    def parse(self, response):
        # print(response.body.decode('utf-8'))
        channel_urls = ["vyule","vgaoxiao","vyouxi","vdianying","vkeji","vqiche","vtiyu","vlvyou"]
        for channel_url in channel_urls:
            for i in range(1,31):
                url = "http://xspapi.mop.com/mopvideo/moppc/listpg?jtype=" + channel_url +"&pgnum={}".format(i)

                yield  scrapy.Request(url=url, callback=self.parse_json,dont_filter=True)

    def parse_json(self, response):
        # print(type(response.body.decode('utf-8')))
        # print(response.body.decode('utf-8'))
        html = response.body.decode('utf-8')
        info = re.findall(r'"data":(.*)}',str(html))[0]

        json_datas = json.loads(info)
        # print(type(data))
        # print(data)
        # print(type(info))
        for json_data in json_datas:
            item = NewsItem()
            title = json_data.get('topic')
            item['title'] = title
            item['item_id'] = Util.to_md5(title)
            item['item_type'] = 'VIDEO'
            item['create_type'] = ''
            try:
                source_ = json_data.get('source')
                if source_:
                    source = source_
                else:
                    source = "猫扑视频"
                item['source'] = "猫扑视频"
                janesi_time = Util.local_time()
                item['name'] = source
                item['avatar'] = ''
                item['type'] = 0
                item['fans_count'] = 0
                item['scan_count'] = 0
                item['collect_count'] = 0
                item['is_delete'] = '0'
                item['gmt_create'] = janesi_time
                item['gmt_modified'] = janesi_time

            except:
                item["author"] = ''
                item['source'] = '  '
            item['original_url'] = response.url
            channel = json_data.get('type')

            tags = ['视频']
            topic = []
            region = ''


            item['comment'] = Util.random_number()

            item['topic'] = []
            item['keyword'] = []
            item['region'] = ''



            
            if channel == "vyouxi":
                channel = '游戏'
                tags.append(channel)
                item['tag'] = tags
                item['channel'] = channel
                item['category'] = {"channel": channel, "tag": tags, "topic": topic, "keyword": [], "region": region}

            if channel == "vyule":
                channel = '娱乐'
                tags.append(channel)
                item['tag'] = tags
                item['channel'] = channel
                item['category'] = {"channel": channel, "tag": tags, "topic": topic, "keyword": [], "region": region}

            if channel == "vgaoxiao":
                channel = '搞笑'
                tags.append(channel)
                item['tag'] = tags
                item['channel'] = channel
                item['category'] = {"channel": channel, "tag": tags, "topic": topic, "keyword": [], "region": region}

            if channel == "vqiche":
                channel = '汽车'
                tags.append(channel)
                item['tag'] = tags
                item['channel'] = channel
                item['category'] = {"channel": channel, "tag": tags, "topic": topic, "keyword": [], "region": region}

            if channel == "vdianying":
                channel = '影视'
                tags.append(channel)
                item['tag'] = tags
                item['channel'] = channel
                item['category'] = {"channel": channel,  "tag": tags, "topic": topic, "keyword": [],"region": region}
            if channel == "vkeji":
                channel = '科技'
                tags.append(channel)
                item['tag'] = tags
                item['channel'] = channel
                item['category'] = {"channel": channel,  "tag": tags, "topic": topic, "keyword": [],"region": region}

            if channel == "vlvyou":
                channel = '旅游'
                tags.append(channel)
                item['tag'] = tags
                item['channel'] = channel
                item['category'] = {"channel": channel,  "tag": tags, "topic": topic, "keyword": [],"region": region}
            if channel == "vtiyu":
                channel = '体育'
                tags.append(channel)
                item['tag'] = tags
                item['channel'] = channel
                item['category'] = {"channel": channel,  "tag": tags, "topic": topic, "keyword": [],"region": region}
            else:
                item['tag'] = tags
                item['channel'] = channel
                item['category'] = {"channel": '视频', "tag": ['视频'], "topic": [], "keyword": [],"region": []}
            item['body'] = json_data.get('video_link')
            item['images'] = []
            item['audios'] = []
            item['copyright'] = ''
            item['release_time'] = json_data.get('date')
            item['janesi_time'] = Util.local_time()
            item['scan'] = Util.random_number()
            item['like'] = 0
            item['share'] = 0
            item['play'] = Util.random_number()
            item['forward'] = 0
            item['collect'] = 0
            item['platform'] = 'maopu'
            item['upload_file_flag'] = 'true'
            item['image_urls'] = []
            # item['duration'] = json_data.get('videoalltime')
            duration = json_data.get('videoalltime')
            duration_data = int(duration) / 1000
            duration_fina = time.strftime("%M:%S", time.gmtime(int(duration_data)))
            item['duration'] = duration_fina
            item['duration'] = duration_fina
            item['size'] =json_data.get('filesize')
            try:
                cut_url_link = json_data.get('url')
                cut_url_joint = "http://tv.mop.com/video/" + str(cut_url_link)
                yield scrapy.Request(url=cut_url_joint, callback=self.parse_cut_url, meta={"item":item})
            except:
                return

    def parse_cut_url(self, response):
        item = response.meta['item']
        data = response.body.decode('utf-8')
        cut_url = re.findall(r'poster="(.*?)"', data)[0]
        try:
            item['videos'] = [{"index": 1, "url": item["body"], "cut_url": cut_url, "title": item["title"],"duration": item["duration"], "size": item["size"]}]
        except:
            return
        if item['videos'] == [] or None:
            return
        item['author_id'] = None
        check = Util.check_item(item)
        if check == 1:
            return
        yield item





