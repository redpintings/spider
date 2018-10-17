# -*- coding: utf-8 -*-

import re

import scrapy
from scrapy_redis.spiders import RedisSpider

from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem


class QingNianCYeSpider(RedisSpider):

    name = 'qncye'

    allowed_domains = ['www.qncye.com']

    # start_urls = ['http://www.qncye.com/data/sitemap.html']

    redis_key = 'qncye:start_urls'

    def parse(self, response):
        site_link = response.xpath("//*[@class='linkbox']")
        for link in site_link:
            ul_links = link.xpath("./ul[@class='f6']/li")
            for u_link in ul_links:
                per_link = response.urljoin(u_link.xpath("./a/@href").extract_first())
                tag = u_link.xpath("./a/text()").extract_first()
                if per_link:
                    yield scrapy.Request(url=per_link,callback=self.parse_list,meta={'tag':tag})

    def parse_list(self,response):
        item = NewsItem()
        item['tag'] = ['创业']+[response.meta['tag']]
        article_list = response.xpath("//*[@class='ptb25']")
        for article in article_list:
            link = article.xpath("./div[@class='clearfix']/div/h3[@class='fz18 YaHei fbold']/a/@href").extract_first()
            title = article.xpath("./div[@class='clearfix']/div/h3[@class='fz18 YaHei fbold']/a/text()").extract_first()
            time = article.xpath("./div[@class='clearfix']/div/div[@class='txtBox']/div[@class='txt']/p/span/text()").extract_first()
            link = response.urljoin(link)
            if  title and link:
                item['release_time'] = time
                item['title'] = title
                yield scrapy.Request(url=link,callback=self.parse_detail,meta={'item':item})

    def parse_detail(self,response):
        item = response.meta['item']
        content = response.xpath("//*[@id='ctrlfscont']").extract_first()
        content =  str(content).replace('oldsrc=','')
        content = Util.remove_impurity(content)
        content = Util.replace_style(content)

        image_urls = re.findall(r'src="(.*?)"', content)
        target_image_urls = []
        for v_image in image_urls:
            t_image = Util.generate_pic_time(v_image)
            content = content.replace(v_image, t_image)
            target_image_urls.append(response.urljoin(v_image))
        item['body'] = content
        item['image_urls'] = target_image_urls
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

        item_id = Util.to_md5(item['title'])
        item['item_id'] = item_id
        item['item_type'] = 'ARTICLE'
        # 原创还是转载，
        item['create_type'] = ''
        item['source'] = '青年创业网'
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

        item['category'] = {"channel": '创业',  "topic": [], "tag": item['tag'], "keyword": [],
                            "region": ''}

        item['channel'] = '创业'

        item['comment'] = Util.random_number()
        item['duration'] = 0
        item['size'] = 0
        item['topic'] = []
        item['keyword'] = []
        item['region'] = ''
        item['name'] = '青年创业网'
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
        item['platform'] = 'qncye'
        if content:
            check = Util.check_item(item)
            print('--------------  qncye  --------  ',check)
            if check == 1:
                return
            yield item
        else:
            print('-----------  pengfu  parse  error --------')
