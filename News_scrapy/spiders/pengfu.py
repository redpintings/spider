# -*- coding: utf-8 -*-
# @Time    : 2018/4/18 10:48
# @Author  : 蛇崽
# @Email   : 643435675@QQ.com
# @File    : pengfu.py.py
import re

import scrapy
from scrapy_redis.spiders import RedisSpider

from News_scrapy.MyUtils import Util

from News_scrapy.items import NewsItem


class PengfuSpider(RedisSpider):

    name = 'pengfu'

    allowed_domains = ['www.pengfu.com']

    redis_key = 'pengfu:start_urls'

    # start_urls = ['http://www.pengfu.com']
    def parse(self, response):
        # url = "https://www.pengfu.com/index_1.html"
        for pagesize in range(1,51):
            url = "https://www.pengfu.com/index_{}.html".format(str(pagesize))
            yield scrapy.Request(url=url,callback=self.parse_list)

    def parse_list(self,response):
        item = NewsItem()
        node_list = response.xpath("//*[@class='list-item bg1 b1 boxshadow']")
        for v_node in node_list:
            author_name = v_node.xpath("./dl[@class='clearfix dl-con']/dd/p[@class='user_name_list']/a/text()").extract_first()
            title = v_node.xpath("./dl[@class='clearfix dl-con']/dd/h1[@class='dp-b']/a/text()").extract_first()
            title_link = v_node.xpath("./dl[@class='clearfix dl-con']/dd/h1[@class='dp-b']/a/@href").extract_first()
            item['title'] = title if not None else ''
            item['name'] = author_name if not None else ''
            if title_link:
                yield scrapy.Request(url=title_link,callback=self.parse_detail,meta={'item':item})

    def parse_detail(self,response):
        item = response.meta['item']
        title = item['title']
        content = response.xpath("//*[@class='content-txt pt10']").extract_first()
        if 'type="video/mp4"' in content:
            return

        # 替换src
        content =Util.remove_impurity(content)
        content = Util.replace_style(content)
        content = str(content).replace('oldsrc=','')
        image_urls = re.findall(r'src="(.*?)"', content)
        target_image_urls = []
        for v_image in image_urls:
            t_image = Util.generate_pic_time(v_image)
            content = content.replace(v_image, t_image)
            target_image_urls.append(response.urljoin(v_image))

        item['image_urls'] = target_image_urls
        item['body'] = content
        try:
            item['images'] = []
            data_echo_url = re.findall(r'data-echo="(.*?)"', item['body'])
            for num, image_url in enumerate(data_echo_url):
                t_image = Util.generate_images_pic(image_url)
                temp_image_url = Util.generate_images_pic(t_image)
                image_dict = {"index": num, "url": temp_image_url, "title": ""}
                item['images'].append(image_dict)
        except:
            item['images'] = []

        item_id = Util.to_md5(title)
        item['item_id'] = item_id
        item['item_type'] = 'ARTICLE'
        # 原创还是转载，
        item['create_type'] = ''
        item['source'] = '捧腹网'
        item['original_url'] = response.url
        janesi_time = Util.local_time()
        item['avatar'] = ''
        item['type'] = 0
        item['fans_count'] = 0
        item['scan_count'] = 0
        item['collect_count'] = 0
        item['is_delete'] = '0'
        item['gmt_create'] = janesi_time
        item['gmt_modified'] = janesi_time
        try:
            tags = Util.get_tags_by_jieba(content)
            tags.append('搞笑')
        except:
            tags = ['搞笑']

        item['tag'] =tags
        item['category'] = {"channel": '搞笑', "topic": [], "tag": item['tag'], "keyword": [],
                            "region": ''}


        item['channel'] = '搞笑'

        item['comment'] = Util.random_number()
        item['duration'] = 0
        item['size'] = 0
        item['topic'] = []
        item['keyword'] = []
        item['region'] = ''

        item["videos"] = []
        item["audios"] = []
        item['videos'] = []
        item['audios'] = []
        item['copyright'] = ''
        item['release_time'] = janesi_time
        item['janesi_time'] = janesi_time
        item['scan'] =  Util.random_number()
        item['like'] = 0
        item['share'] = 0
        item['play'] = Util.random_number()
        item['forward'] = 0
        item['collect'] = 0
        item['upload_file_flag'] = 'true'
        item['platform'] = 'pengfu'
        item['author_id'] = None
        if title and content:
            check = Util.check_item(item)
            if check == 1:
                return
            yield item
        else:
            print('-----------  pengfu  parse  error --------')