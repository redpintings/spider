# -*- coding: utf-8 -*-
# @Time    : 2018/5/24 11:41
# @Author  : 蛇崽
# @Email   : 643435675@QQ.com
# @File    : baisibudejie.py（http://www.budejie.com/）
import re
import scrapy
from bs4 import BeautifulSoup
from scrapy_redis.spiders import RedisSpider

from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem


class BudeJieSpider(RedisSpider):
    name = 'budejie'
    allowed_domains = ['www.budejie.com']
    # start_urls = ['http://www.budejie.com/']
    redis_key = 'budejie:start_urls'
    def parse(self, response):
        soup = BeautifulSoup(response.body,'lxml')
        link = soup. find('div',class_='j-r-list-c-desc').find('a')['href']
        link = response.urljoin(link)
        if link:
            yield scrapy.Request(link,callback=self.parse_detail)

    def parse_detail(self,response):
        item = NewsItem()
        try:
            soup = BeautifulSoup(response.body,'lxml')
            author = soup.find('a', class_='u-user-name').get_text()
            content = soup.find('div', class_='j-r-list-c')
            title = soup.find('div', class_='j-r-list-c-desc').find('h1').get_text()

            content = Util.remove_impurity(str(content))
            content = Util.replace_style(content)

            image_urls = re.findall(r'src="(.*?)"', content)
            target_image_urls = []

            for v_image in image_urls:
                t_image = Util.generate_pic_time_pengpai_lazy(v_image)
                content = content.replace(v_image, t_image)
                v_image = 'SUPERLAZYSUB'+response.urljoin(v_image)
                target_image_urls.append(v_image)
            item['body'] = content
            item['image_urls'] = target_image_urls
            print('target_image_urls' ,target_image_urls)
            item['title'] = title

            try:
                item['images'] = []
                data_echo_url = re.findall(r'data-echo="(.*?)"', item['body'])
                for num, image_url in enumerate(data_echo_url):
                    t_image = Util.generate_pic_time_pengpai(image_url)
                    image_dict = {"index": num, "url": t_image, "title": ""}
                    item['images'].append(image_dict)

            except:
                item['images'] = []
            channel = '搞笑'
            item_id = Util.to_md5(item['title'])
            item['item_id'] = item_id
            item['item_type'] = 'ARTICLE'
            # 原创还是转载，
            item['create_type'] = ''
            item['source'] = '百思不得姐'
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
            item['release_time'] = janesi_time
            item['tag'] = ['搞笑']
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
            item['platform'] = 'baisibudejie'

            if content:
                check = Util.check_item(item)
                print('--------------  budejie  --------  ', check)
                if check == 1:
                    return
                yield item
            else:
                print('-----------  pengpai  parse  error --------')
            next_link = soup.find('a', class_='c-next-btn')['href']
            next_link = response.urljoin(next_link)
            if next_link:
                yield scrapy.Request(next_link, callback=self.parse_detail)
        except:
            print('parse_detail  error ', response)
            return







