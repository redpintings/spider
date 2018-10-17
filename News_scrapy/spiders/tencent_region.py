# -*- coding: utf-8 -*-
# @Author  : 杨星星
# @Email   : yangshilong_liu@163.com

import re
import scrapy
import json
from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem
import re
from scrapy_redis.spiders import RedisSpider
from News_scrapy.tecent_region_id import region_list

class TencentregionSpider(RedisSpider):

    name = 'tencentregion'
    allowed_domains = ['qq.com']
    redis_key = 'tengxunregion:start_urls'
    # start_urls = ["https://xw.qq.com/service/api/proxy?key=Xw@2017Mmd&charset=utf-8&url=http:%2F%2Fopenapi.inews.qq.com%2FgetQQNewsIndexAndItems%3Fchlid%3Dnews_news_{}%26refer%3Dmobilewwwqqcom%26srcfrom%3Dnewsapp%26otype%3Djson%26ext_action%3DFimgurl33,Fimgurl32,Fimgurl30".format("chengdu")]

    def get_dif_region_url(self):
        for region_flag,region_p,region_c,region_code in region_list:
            print(region_code,'>>>>>>>>')
            url = "https://xw.qq.com/service/api/proxy?key=Xw@2017Mmd&charset=utf-8&url=http:%2F%2Fopenapi.inews.qq.com%2FgetQQNewsIndexAndItems%3Fchlid%3Dnews_news_{}%26refer%3Dmobilewwwqqcom%26srcfrom%3Dnewsapp%26otype%3Djson%26ext_action%3DFimgurl33,Fimgurl32,Fimgurl30".format(region_flag)
            yield url, region_p,region_c,region_code

    def parse(self,response):
        for region_url,region_p,region_c,region_name in self.get_dif_region_url():

            yield scrapy.Request(url=region_url,callback=self.parse_item,meta={"region_name":region_name,"region_k":[region_p,region_c]},dont_filter=True)

    def parse_item(self, response):

        dict_data = json.loads(response.body.decode('utf-8'))
        id_data = dict_data.get('idlist')[0].get('ids')
        for id in id_data:
            url_part = id.get('id')
            article_url = "https://xw.qq.com/cmsid/{}".format(url_part)
            yield scrapy.Request(url=article_url,callback=self.parse_page_data,meta = response.meta)

    def parse_content_body(self, content_html):
        try:
            contents = re.findall(r'ext_data:(.*?)fisoriginal', content_html, re.S)[0]
            return contents
        except Exception as e:
            print('PARSE BODY ERROR',e)
            return None

    def parse_page_data(self,response):
        item = NewsItem()
        if "VIDEO_" in response.body.decode('utf-8'):
            print('VIDEO DATA WE DID NOT NEED GIVE UP')
            return

        region_name = response.meta['region_name']
        try:
            region_k = response.meta['region_k']
            item['keyword'] = region_k
        except:
            item['keyword'] = ''
        article_time = re.findall(r'pubtime: "(.*?)",',response.body.decode('utf-8'))[0]
        article_name = re.findall(r'src: "(.*?)",',response.body.decode('utf-8'))[0]
        title = re.findall(r'title: "(.*?)",',response.body.decode('utf-8'))[0]
        contents = self.parse_content_body(response.body.decode('utf-8'))
        if not contents:
            return
        cnt_html = re.findall(r'(<p.*/p>)', contents, re.S)[0]
        pic_html = re.findall(r'"pic":"(.*?)",', contents)
        item["image_num"] = len(pic_html)
        pic_flag = re.findall(r'<!--IMG_.*?-->', contents)
        cnt_html_cn = cnt_html.encode('utf-8').decode('unicode-escape')
        body = cnt_html_cn
        for p_flag, p_img in zip(pic_flag, pic_html):
            p_img = '<img src="' + str(p_img) + '" alt="" >'
            body = body.replace(p_flag, p_img)
        article_body = body.replace('\\', '')
        if title:
            item['title'] = title
        else:
            return

        item['item_id'] = ''
        item['item_type'] = "ARTICLE"
        item['source'] = '腾讯新闻'
        item['channel'] = '地区'
        item['comment'] = Util.random_number()
        item['duration'] = 0
        item['size'] = 0
        item['topic'] = []
        # item['keyword'] = ''
        item['region'] = region_name

        if article_time:
            item['release_time'] = article_time
        else:
            item['release_time'] = Util.local_time()

        if article_name:
            item['name'] = article_name
        else:
            item['name'] = '腾讯新闻'

        item['create_type'] = '4'
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

        tag = Util.get_tags_by_jieba(article_body)
        if tag:
            item['tag'] = tag
        else:
            item['tag'] = item['channel']

        image_urls = re.findall('src="(.*?)"',article_body)
        if image_urls:
            item['image_urls'] = image_urls
        else:
            return

        item['category'] = {"channel": item['channel'], "topic": [], "tag": item['tag'],
                            "keyword": [], "region": ''}

        try:
            Temp_Content = article_body
            for content_img_url in image_urls:
                content_url_temp = Util.generate_pic_time_qq_lazy(content_img_url)
                Temp_Content = Temp_Content.replace(content_img_url, content_url_temp)
            item['body'] = Temp_Content
        except Exception as e:
            print(e,'BODY ERROR  RETURN ')
            return
        try:
            item['images'] = []
            data_echo_url = re.findall(r'data-echo="(.*?)"', item['body'])
            for num, image_url in enumerate(data_echo_url):
                temp_image_url = Util.generate_pic_time_qq(image_url)
                image_dict = {"index": num, "url": temp_image_url, "title": ""}
                item['images'].append(image_dict)
        except Exception as e:
            print( e, '--IMAGES---ERROR----')
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
        print( CheckItem,'CHECK ITEM >>>>> ')
        if CheckItem == 1:
            return
        yield item


