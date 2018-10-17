# -*- coding: utf-8 -*-
# @Time    : 2018/5/10 14:14
# @Author  : 蛇崽
# @Email   : 643435675@QQ.com
# @File    : pengpai.py(澎湃新闻热点)
import scrapy
import re

from bs4 import BeautifulSoup
from scrapy_redis.spiders import RedisSpider

from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem


class PengPaiSpider(RedisSpider):
    name = 'thepaper'
    allowed_domains = ['www.thepaper.cn']
    # start_urls = ['https://www.thepaper.cn']

    redis_key = 'thepaper:start_urls'

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        news_li = soup.find('div', class_='newsbox').find_all('div', class_='news_li')
        for news in news_li:
            try:
                title = news.find('h2').find('a').get_text()
                newslink = news.find('h2').find('a')['href']
                newslink = response.urljoin(newslink)
                if title and newslink:
                    yield scrapy.Request(url=newslink, callback=self.parse_detail,meta={'title':title})
            except:
                print('error ---- parse ', response)
                continue
        hot_li = soup.find('ul', class_='list_hot').find_all('li')
        for hot in hot_li:
            try:
                title = hot.find('a').get_text()
                link = hot.find('a')['href']
                link = response.urljoin(link)
                if title and link:
                    print('title', title, 'link ', link)
                    yield scrapy.Request(url=link, callback=self.parse_detail,meta={'title':title})
            except:
                print('error ----parse hot', response)
                continue

    def parse_detail(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        item = NewsItem()
        item['title'] = response.meta['title']
        try:
            author = soup.find('div', class_='news_about').find('p').get_text()
            content = soup.find('div', class_='news_txt')

            k_word = soup.find('div', class_='news_keyword').get_text()
            k_word = str(k_word).replace('关键词 >> ', '')
            tags = []
            tags.append('社会')
            if ',' in k_word:
                t_k = k_word.split(',')
                for t in t_k:
                    tags.append(t)
            elif ' ' in k_word:
                t_k = k_word.split(' ')
                for t in t_k:
                    tags.append(t)
            else:
                tags.append(k_word)


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
            item['source'] = '澎湃新闻'
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
            item['tag'] = tags
            item['category'] = {"channel": channel, "topic": [], "tag": item['tag'], "keyword": [],
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
            item['platform'] = 'pengpai'
            if content:
                check = Util.check_item(item)
                print('--------------  pengpai  --------  ', check)
                if check == 1:
                    return
                yield item
            else:
                print('-----------  pengpai  parse  error --------')

        except:
            print('parse_detail  error ', response)
            return
