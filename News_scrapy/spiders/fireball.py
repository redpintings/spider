# -*- coding: utf-8 -*-
import scrapy
import re

from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem
from scrapy_redis.spiders import RedisSpider


class FireballSpider(RedisSpider):
    name = 'fireball'
    allowed_domains = ["huoqiucj.com"]
    base_url = "http://huoqiucj.com"
    # start_urls = ['http://huoqiucj.com/']
    redis_key = 'fireball:start_urls'

    def parse(self, response):
        original_base_urls = ['http://huoqiucj.com/Home/information?data=W9F3j2vgufgdWZmdtGFOlg__2C__2C&pageIndex=1']
        for original_base_url in  original_base_urls:
            print(original_base_url)
            yield scrapy.Request(url=original_base_url,callback=self.parse_article_link,dont_filter=True)


    def parse_article_link(self, response):
        article_links = re.findall(r'<a target="_blank" href="(/Content/information?.*?)">', response.body.decode('utf-8'))
        for article_link in article_links:
            article_link = self.base_url + str(article_link)
            yield scrapy.Request(url=article_link, callback=self.parse_article_info)

    def parse_article_info(self,response):
        item = NewsItem()

        item['source'] = '火球财经'

        item['channel'] = "区块链"

        item['item_type'] = 'ARTICLE'
        title = re.findall(r' <p class="hq_information_title">(.*?)</p>', response.body.decode('utf-8'))[0]
        if title:
            item["title"] = title
        else:
            return
        item_id = Util.to_md5(title)
        item['item_id'] = item_id

        item['comment'] = Util.random_number()
        item['duration'] = 0
        item['size'] = 0
        item['topic'] = []
        item['keyword'] = []
        item['region'] = ''

        nowTime = re.findall(r' <span class="hq_information_datetime">(.*?)</span>', response.body.decode('utf-8'))[0]
        if nowTime:
            item['release_time'] = nowTime
        content = re.findall(r' <div class="hq_information_content">(.*?)<div class="hq_information_author">', response.body.decode('utf-8'),re.S)[0]
        articleTag = re.findall(r' <span class="hq_information_tag">(.*?)</span>', response.body.decode('utf-8'))[0]
        authorName = re.findall(r'<p class="hq_userInfo_title_name">(.*?)</p>',response.body.decode('utf-8'))[0]
        if articleTag:
            item_tag = articleTag.split(' ')
            item['tag'] = item_tag[:-1]
        else:
            item['tag'] = ['区块链']
        imageUrl = re.findall(r'<img src="(.*?)"', content)
        if imageUrl:
            item['image_urls'] = imageUrl
        else:
            return

        if authorName:
            item['name'] = authorName
        else:
            item['name'] = '火球财经'
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

        contentRemoveHref = re.sub(r' href=".*?"', '', content)
        contentRemoveClass = re.sub(r'<div class=".*?">', '', contentRemoveHref)
        replaceContent = contentRemoveClass.replace("</div>", ',').replace(' <link rel="stylesheet">','').strip()
        DealWithBody = Util.remove_impurity(replaceContent)
        try:
            Temp_Content = DealWithBody
            for content_img_url in imageUrl:
                content_url_temp = Util.generate_pic_time(content_img_url)
                Temp_Content = Temp_Content.replace(content_img_url, content_url_temp)
            item['body'] = Temp_Content
        except Exception as e:
            print(e)
            return

        try:
            item['images'] = []
            data_echo_url = re.findall(r'data-echo="(.*?)"', item['body'])
            for num, image_url in enumerate(data_echo_url):
                temp_image_url = Util.generate_images_pic(image_url)
                image_dict = {"index": num, "url": temp_image_url, "title": ""}
                item['images'].append(image_dict)
        except Exception as e:
            print('-----ERROR----', e)
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
        item['platform'] = 'huoqiucaijing'
        item['author_id'] = None
        if not item['body']:
            return
        if len(item['body']) < 200:
            return
        CheckItem = Util.check_item(item)
        print('-------------##------', CheckItem,)
        if CheckItem == 1:
            return
        yield item

