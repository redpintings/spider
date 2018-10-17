# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy_redis.spiders import RedisSpider
from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem
import jieba.posseg as pseg
import logging


class TencenthouseSpider(RedisSpider):
    name = 'tencenthouse'
    allowed_domains = ['house.qq.com']
    # start_urls = ['http://house.qq.com/l/201804/scroll_19.htm']
    redis_key = 'tencenthouse:start_urls'
    def parse(self, response):
        # print(response.body.decode('gbk'))
        Article_Urls = re.findall(r'href="(http://house.qq.com/a/.*?.htm)"',response.body.decode('gbk'))
        # print(Article_Url)
        for Article_Url in Article_Urls:
            yield scrapy.Request(url=Article_Url,callback=self.parse_page_detail)


    def parse_page_detail(self,response):
        item = NewsItem()
        title = re.findall(r'<h1>(.*?)</h1>',response.body.decode('gbk'))[0]
        AuthorName = response.xpath('//div[@class="a_Info"]/span[2]/text()').extract_first()
        if AuthorName:
            item['name'] = AuthorName
        else:
            item['name'] = '腾讯房产'
        PlatFormTime = response.xpath('//div[@class="a_Info"]/span[3]/text()').extract_first()
        if PlatFormTime and PlatFormTime.startswith('2'):
            item['release_time'] = PlatFormTime
        else:
            item['release_time'] = Util.local_time()
        if title:
            item['title'] = title
            item_id = Util.to_md5(title)
            item['item_id'] = item_id
            # item['_id'] = item_id
        else:
            return
        item['channel'] = '房产'
        item['item_type'] = 'ARTICLE'
        item['create_type'] = ''
        item['original_url'] = response.url
        item['source'] = '腾讯房产'

        item['avatar'] = ''
        item['type'] = 0
        item['fans_count'] = 0
        item['scan_count'] = 0
        item['platform'] = 'tengxunfangchan'
        item['collect_count'] = 0
        item['is_delete'] = '0'
        janesi_time = Util.local_time()
        item['gmt_create'] = janesi_time
        item['gmt_modified'] = janesi_time

        item['comment'] = Util.random_number()
        item['duration'] = 0
        item['size'] = 0
        item['topic'] = []
        item['keyword'] = []
        item['region'] = ''

        OriginalBody = re.findall(r'<div id="Cnt-Main-Article-QQ" class="Cnt-Main-Article-QQ" bossZone="content">(.*)</P>',
                          response.body.decode('gbk'))[0]
        if not OriginalBody:
            return
        WipeOutBody = Util.remove_impurity(OriginalBody)
        ImageUrls = re.findall(r'src="(.*?)"', WipeOutBody)
        item['image_urls'] = ImageUrls
        if len(item['image_urls']) < 1:
            return
        tags = Util.get_tags_by_jieba(WipeOutBody)
        if tags:
            tags.append(item['channel'])
            item['tag'] = tags
        else:
            item['tag'] = item['channel']

        try:
            Temp_Content = WipeOutBody.replace('align="center"','')
            for content_img_url in ImageUrls:
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
            print('-----ERROR----', e, '-----ERROR----')
            logging.info('-------------IMAGES---ERROR---------------')
            return
        item['category'] = {"channel": '房产', "child_channel": '', "topic": [], "tag": item['tag'],"keyword": [], "region": ''}
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
        item['platform'] = 'tengxunfangchan'
        item['author_id'] = None
        Util.check_body(item['body'])
        CheckItem = Util.check_item(item)
        print('-------------------', CheckItem, '-------------------')
        if CheckItem == 1:
            return
        yield item





