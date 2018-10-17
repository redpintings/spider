# -*- coding: utf-8 -*-
# @Time    : 2018/5/23 13:56
# @Author  : 蛇崽
# @Email   : 643435675@QQ.com
# @File    : wangyi3g.py
import json

import re
import scrapy
from bs4 import BeautifulSoup
from scrapy_redis.spiders import RedisSpider

from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem


class Wangyi3GSpider(RedisSpider):

    name = 'wangyi3g'
    allowed_domains = ['3g.163.com']
    # start_urls = ['http://3g.163.com/touch/news/']
    redis_key = 'wangyi3g:start_urls'
    """
    //网易新闻类型 误删除:首页，社会.....
    String[] typeArray={"BBM54PGAwangning","BCR1UC1Qwangning",
    "BD29LPUBwangning","BD29MJTVwangning","C275ML7Gwangning"};
    String type = typeArray[width];
    """
    baseurl = 'http://3g.163.com/touch/reconstruct/article/list/BBM54PGAwangning/{}-10.html'
    def parse(self, response):
        # 10 20
        for page in range(0,150,10):
            jsonurl = self.baseurl.format(page)
            yield scrapy.Request(jsonurl,callback=self.parse_li_json)

    def parse_li_json(self,response):
        item = NewsItem()
        res = response.body.decode('utf-8')
        res = str(res).replace('artiList(','')
        res = res.replace(')','')
        j = json.loads(res)
        datas = j['BBM54PGAwangning']

        for data in datas:
            title = data['title']
            ptime = data['ptime']
            url = data['url']
            url =response.urljoin(url)
            name = data['source']
            if url:
                item['title'] = title
                item['name'] = name
                item['release_time'] = ptime
                yield scrapy.Request(url,callback=self.parse_detail,meta={'item':item})

    def parse_detail(self,response):
        item = response.meta['item']

        soup = BeautifulSoup(response.body,'lxml')
        content = soup.find('div','content')
        content = Util.remove_impurity(str(content))
        content = Util.replace_style(content)
        if '<video' in content:
            return

        image_urls = re.findall(r'data-src="(.*?)"', content)
        content = content.replace('data-src=', 'src=')
        target_image_urls = []

        for v_image in image_urls:
            t_image = Util.generate_pic_time_pengpai_lazy(v_image)
            content = content.replace(v_image, t_image)
            v_image = 'SUPERLAZYSUB'+response.urljoin(v_image)
            target_image_urls.append(v_image)
        item['body'] = content
        item['image_urls'] = target_image_urls

        try:
            item['images'] = []
            data_echo_url = re.findall(r'data-echo="(.*?)"', item['body'])
            for num, image_url in enumerate(data_echo_url):
                t_image = Util.generate_pic_time_pengpai(image_url)
                image_dict = {"index": num, "url": t_image, "title": ""}
                item['images'].append(image_dict)

        except:
            item['images'] = []
        channel = '社会'
        item_id = Util.to_md5(item['title'])
        item['item_id'] = item_id
        item['item_type'] = 'ARTICLE'
        # 原创还是转载，
        item['create_type'] = ''
        item['source'] = '网易新闻'
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
            tags.append('社会')
        except:
            tags = ['社会']

        item['tag'] =tags

        item['category'] = {"channel": channel, "topic": [], "tag": item['tag'], "keyword": [],
                            "region": ''}

        item['channel'] = channel
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
        item['janesi_time'] = janesi_time
        item['scan'] = Util.random_number()
        item['like'] = 0
        item['share'] = 0
        item['play'] = Util.random_number()
        item['forward'] = 0
        item['collect'] = 0
        item['upload_file_flag'] = 'true'
        item['platform'] = 'wangyi3g'
        if content:
            check = Util.check_item(item)
            print('--------------  budejie  --------  ', check)
            if check == 1:
                return
            yield item
        else:
            print('-----------  pengpai  parse  error --------')