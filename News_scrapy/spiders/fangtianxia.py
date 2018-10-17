# -*- coding: utf-8 -*-
# @Time    : 2018/5/16 17:16
# @Author  : 蛇崽
# @Email   : 643435675@QQ.com
# @File    : fangtianxia.py(爬取房天下)
import re
import scrapy
from bs4 import BeautifulSoup
from scrapy_redis.spiders import RedisSpider

from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem


class FangtianxiaSpider(RedisSpider):
    name = 'fangtianxia'

    allowed_domains = ['m.fang.com']

    #start_urls = ['https://m.fang.com/news/bj.html']
    redis_key = 'fangtianxia:start_urls'
    def parse(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        li_list = soup.find('ul',attrs={'type_id':'content'}).find_all('li',class_='')
        for li in li_list:
            try:
                link = li.find('a')['href']
                title = li.find('h3').get_text()
                link = response.urljoin(link)
                if link:
                    yield scrapy.Request(link, callback=self.parse_detail,meta={'title':title})
            except:
                print('error ----parse ----- ',response)
                continue
                pass

    def parse_detail(self,response):
        soup = BeautifulSoup(response.body,'lxml')
        title = response.meta['title']
        item = NewsItem()
        channel = '房产'
        tag_list = [channel]
        try:
            source = soup.find('div', class_='k-conName').find_all('span', class_='')
            if len(source) <2:
                return
        except:
            print('parse_detail error ========  ',response)
            return

        author = str(source[0].get_text()).replace('来源：','').strip(' ')
        if not author:
            author = '房天下'
        release_time = source[1].get_text()
        item['release_time'] = release_time
        item['title'] = title
        tags = soup.find('div',class_='k-stagBox').find_all('a',class_='')
        for tag in tags:
            v_t = tag.get_text()
            tag_list.append(v_t)

        content = soup.find('div',class_='k-conWord articleN')
        content = Util.remove_impurity(str(content))
        content = Util.replace_style(content)
        content = content.replace('data-original', 'src')

        image_urls = re.findall(r'src="(.*?)"',content)

        target_image_urls = []
        for v_image in image_urls:
            t_image = Util.generate_pic_time_pengpai_lazy(v_image)
            content = content.replace(v_image, t_image)
            target_image_urls.append(response.urljoin(v_image))

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


        item_id = Util.to_md5(item['title'])
        item['item_id'] = item_id
        item['item_type'] = 'ARTICLE'
        # 原创还是转载，
        item['create_type'] = ''
        item['source'] = '房天下'
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

        item['tag'] = tag_list
        item['category'] = {"channel": channel, "child_channel": '', "topic": [], "tag": item['tag'], "keyword": [],
                            "region": ''}


        item['channel'] = channel

        item['comment'] = Util.random_number()
        item['duration'] = 0
        item['size'] = 0
        item['topic'] = []
        item['keyword'] = []
        item['region'] = ''
        item['name'] = author
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
        item['platform'] = 'fangtianxia'
        if content:
            check = Util.check_item(item)
            print('--------------  fangtianxia  --------  ', check)
            if check == 1:
                return
            yield item
        else:
            print('-----------  fangtianxia  parse  error --------')