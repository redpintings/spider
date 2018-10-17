# -*- coding: utf-8 -*-
import scrapy
import re
import json
import time
from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem
import re
from scrapy_redis.spiders import RedisSpider


class DftoutiaoSpider(RedisSpider):
    name = 'dftoutiao'
    allowed_domains = ['eastday.com']
    # start_urls = ['https://toutiao.eastday.com/toutiao_h5/NextJP?htps=1&type={}&pgnum={}']
    redis_key = 'dftoutiao:start_urls'
    channel_list = [
    ("娱乐","yule"),
    ("社会", "shehui"),
    ("健康", "jiankang"),
    ("社会", "guoji"),
    ("军事", "junshi"),
    ("汽车", "qiche"),
    ("搞笑", "xiaohua"),
    ("体育", "tiyu"),
    ("游戏", "wzry"),
    ("财经", "caijing"),
    ("科技", "keji"),
    ("历史", "lishi"),
    ("星座", "xingzuo"),
    ("体育", "nba"),
    ("时尚", "shishang"),
    ("游戏", "youxi"),
    ("社会", "guonei"),
    ("科技", "kexue"),
    ("科技", "hulianwang"),
    ("科技", "shuma"),
    ("健康", "baojian"),
    ("健康", "jianshen"),
    ("美食", "yinshi"),
    ("社会", "jiaju"),
    ("财经", "waihui"),
    ("财经", "baoxian"),
    ("房产", "budongchan"),
    ("财经", "huangjin"),
    ("财经", "xinsanban"),
    ("股票", "xinsanban"),
    ("期货", "qihuo"),
    ("基金", "jijin"),
    ("娱乐", "dianying"),
    ("娱乐", "dianshi"),
    ("娱乐", "bagua"),
    ("社会", "toutiao")]


    def parse(self, response):

        for channel,df_flag in self.channel_list:
            url = 'https://toutiao.eastday.com/toutiao_h5/NextJP?htps=1&type={}&pgnum=1'
            channel_url = url.format(df_flag)
            print("++++"*12)
            print("++++"*12)
            print("++++"*12)
            print(channel_url)
            print("++++" * 12)
            print("++++" * 12)
            print("++++" * 12)
            yield scrapy.Request(url=channel_url,callback=self.parse_item,meta={"channel":channel},dont_filter=True)

    def parse_item(self,response):
        re_data = re.findall(r'null\((.*?)\)', response.body.decode('utf-8'), )[0]
        js_list_data = json.loads(re_data).get('data')
        print(len(js_list_data))
        for js_data in js_list_data:
            content_url = js_data.get('url')
            if "video" in content_url:
                print('VIDEO DATA')
                print(content_url)
                yield scrapy.Request(url=content_url,callback=self.dispose_video_data,meta=response.meta)

            else:
                # pass
                # print('ARTICLE DATA')
                print(content_url)
                yield scrapy.Request(url=content_url,callback=self.dispose_article_data,meta=response.meta)

    def same_item(self,item):

        item['avatar'] = ''
        item['type'] = 0
        item['fans_count'] = ''
        item['scan_count'] = ''
        item['platform'] = 'dongfangtoutiao'
        item['collect_count'] = ''
        item['is_delete'] = '0'
        janesi_time = Util.local_time()
        item['gmt_create'] = janesi_time
        item['gmt_modified'] = janesi_time

        item['comment'] = Util.random_number()
        item['topic'] = []
        item['keyword'] = []
        item['region'] = ''
        item['category'] = {"channel": item['channel'], "topic": [], "tag": item['tag'],
                            "keyword": [], "region": ''}
        item['source'] = '东方头条'
        item['create_type'] = ''

        item['audios'] = []
        item['copyright'] = ''

        item['release_time'] = janesi_time
        item['janesi_time'] = janesi_time
        item['scan'] = Util.random_number()
        item['like'] = 0
        item['share'] = 0
        item['play'] = 0
        item['forward'] = 0
        item['collect'] = 0
        item['upload_file_flag'] = 'true'

        return item
               
    def dispose_video_data(self,response):

        title = re.findall(r'<title>(.*?)</title>', response.body.decode('utf-8'))[0]
        video_url = re.findall(r'src="(.*?.mp4)', response.body.decode('utf-8'))[0]
        source_name = re.findall(r'data-source="(.*?)"', response.body.decode('utf-8'))[0]
        cut_url = re.findall(r'poster="(.*?)"', response.body.decode('utf-8'))[0]
        data_duration = re.findall(r'data-duration="(.*?)"', response.body.decode('utf-8'))[0]
        data_size = re.findall(r'data-size="(.*?)"', response.body.decode('utf-8'))[0]
        channel = response.meta['channel']
        item = NewsItem()
        if data_size:
            item['size'] = data_size
        else:
            item['size'] = ''
        try:
            if data_duration:
                data = time.strftime("%M:%S", time.gmtime(int(data_duration)))
                item['duration'] = data
            else:
                item['duration'] = ''
        except Exception as e:
            print('--error-duration---',e)
        if title:
            item['title'] = title
        else:
            return
        if channel:
            item['channel'] = channel
        else:
            item['channel'] = ''
        if source_name:
            item['name'] = source_name
        else:
            item['name'] = '东方头条'
        item['item_type'] = 'VIDEO'
        item['original_url'] = response.url

        tag = Util.tag_by_jieba_title(item['title'])
        if tag:
            item["tag"] = tag
        else:
            item['tag'] = []

        item['image_urls'] = []
        item['image_num'] = ''
        if video_url:
            item['body'] = video_url
        else:
            return
        item['images'] = []
        try:
            item['videos'] = [{"index": 1, "url": item["body"], "cut_url": cut_url, "title": item["title"],"duration": item["duration"], "size":''}]
        except:
            return

        item = self.same_item(item)
        yield item

    
    def dispose_article_data(self,response):

        item = NewsItem()
        channel = response.meta['channel']
        article_body = re.findall(r'(<p.*/p>)', response.body.decode('utf-8'), re.S)[0]
        title = re.findall(r'<title>(.*?)</title>', response.body.decode('utf-8'))[0]
        time_and_name = re.findall(r'<span class="src">(.*?)</span>', response.body.decode('utf-8'))[0]
        time = time_and_name[0:16]
        name = time_and_name.split('来源：', )[-1]
        item["channel"] = channel
        if title:
            item['title'] = title
        else:
            return

        if article_body:
            DealWithBody = article_body.replace("data-weight=","").replace("data-width=","").replace("data-height=","").replace("width=","")
            sub_body = re.sub(r'(data-href=".*?")', '', DealWithBody)
            deal_with_body = Util.remove_impurity(sub_body)
        else:
            print('--BODY--ERROR--')
            return
        tag = Util.get_tags_by_jieba(deal_with_body)
        if tag:
            item['tag'] = tag
        else:
            item['tag'] = item['channel']


        if time:
            item['release_time'] = time
        else:
            item['release_time'] = Util.local_time()

        if name:
            item['name'] = name
        else:
            item['name'] = '东方头条'
        item['category'] = {"channel": item['channel'], "topic": [], "tag": item['tag'],
                            "keyword": [], "region": ''}
        item['original_url'] = response.url
        item['item_type'] = 'ARTICLE'
        ImageUrl = re.findall(r'src="(.*?)"', sub_body)
        if ImageUrl:
            item['image_urls'] = ImageUrl
            item['image_num'] = len(ImageUrl)
        else:
            print('--IMAGE_URL---ERROR---')
            return
        try:
            Temp_Content = sub_body
            for content_img_url in ImageUrl:
                content_url_temp = Util.generate_pic_time(content_img_url)
                Temp_Content = Temp_Content.replace(content_img_url, content_url_temp)
            item['body'] = Temp_Content
        except Exception as e:
            print('-BODY---ERROR--',e)
            return
        try:
            item['images'] = []
            data_echo_url = re.findall(r'data-echo="(.*?)"', item['body'])
            for num, image_url in enumerate(data_echo_url):
                temp_image_url = Util.generate_images_pic(image_url)
                image_dict = {"index": num, "url": temp_image_url, "title": ""}
                item['images'].append(image_dict)
        except Exception as e:
            print(e,'--IMAGES---ERROR----')
            return
        item['videos'] = []
        item['duration'] = ''
        item['size'] = ''
        item = self.same_item(item)
        yield item

