# -*- coding: utf-8 -*-
# @Time    : 2018/3/5 11:05
# @Author  : 蛇崽
# @Email   : 643435675@QQ.com
# @File    : jiemian.py（http://www.jiemian.com/ 界面新闻）
import re

import scrapy
from scrapy_redis.spiders import RedisSpider

from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem


class JieMianSpider(RedisSpider):

    name = 'jiemian'

    allowed_domains = ['www.jiemian.com','a.jiemian.com']

    redis_key = 'jiemian:start_urls'

    # start_urls = ['http://www.jiemian.com']

    def parse(self, response):

        v_dict = {
             '财经': '9',
             '科技':'65',
             '体育': '82',
             '军事': '103',
             '娱乐': '63',
             '汽车': '51',
             '时尚': '68',
             '旅游': '105',
             '游戏': '118',
             '文化': '130',
             '房产':'62',
             '创业':'141',
            }

        for channel, tag_link in v_dict.items():
            type_link ='http://www.jiemian.com/lists/{}.html'.format(tag_link)
            cy_link = 'http://www.jiemian.com/article/1974476.html'
            yield scrapy.Request(url=type_link,callback=self.get_main_link,meta={'tag_link':tag_link,'channel':channel},dont_filter=True)

    def get_main_link(self,response):
        # print('get_main_link',response)
        tag_link = response.meta['tag_link']
        channel = response.meta['channel']
        sub_nav = response.xpath("//*[@class='header-nav']/ul[@id='sub-nav']/li")

        if tag_link not in '141':
            for sub in sub_nav:
                sub_link = sub.xpath("./a/@href").extract_first()
                sub_content = sub.xpath("./a/text()").extract_first()
                # print('sub_link',sub_link)
                if sub_link:
                    yield scrapy.Request(url=sub_link,callback=self.get_list_content,meta={'sub_tag':sub_content,'channel':channel})
        # 创业没有左边栏
        else:
            cy_list = response.xpath("//*[@class='news-view left']")
            for cy in cy_list:
                cy_link = cy.xpath("./div[@class='news-img']/a/@href").extract_first()
                if cy_link:
                    yield scrapy.Request(url=cy_link,callback=self.get_detail_content,meta={'sub_tag':'','channel':channel})

    def get_list_content(self,response):
        # print('get_list_content',response)
        sub_tag = response.meta['sub_tag']
        channel = response.meta['channel']

        list_card = response.xpath("//*[@class='news-view left card']")
        for v_card in list_card:
            card_link = v_card.xpath("./div[@class='news-img']/a/@href").extract_first()
            if card_link:
                # card_link = 'http://www.jiemian.com/article/1991349.html'
                yield scrapy.Request(url=card_link,callback=self.get_detail_content,meta={'sub_tag':sub_tag,'channel':channel})


    """
    详情页
    """
    def get_detail_content(self,response):
        # print('get_detail_content ',response)
        sub_tag = response.meta['sub_tag']
        channel = response.meta['channel']
        tag_list = [channel]

        tag_default = response.xpath("//*[@class='main-mate']/a/text()").extract()
        tag_other = response.xpath("//*[@class='main-mate']/span/a/text()").extract()
        tag_list = tag_list + tag_default + tag_other

        article_title = response.xpath("//*[@class='article-header']/h1/text()").extract_first()
        article_abstract = response.xpath("//*[@class='article-header']/p/text()").extract_first()

        # 可能为视频内容，解析出错
        if article_title and article_abstract:
            item = NewsItem()
            author = response.xpath("//*[@class='article-info']/p/span[@class='author']/a/text()").extract_first()
            # 有作者
            if author:
                release_time = response.xpath("//*[@class='article-info']/p/span[2]/text()").extract_first()
                scan = response.xpath("//*[@class='article-info']/p/span[3]/text()").extract_first()
            else:
                release_time = response.xpath("//*[@class='article-info']/p/span[1]/text()").extract_first()
                scan = response.xpath("//*[@class='article-info']/p/span[2]/text()").extract_first()
            print('阅读量：',scan)
            scan = str(scan)
            if 'W' in scan and scan:
                int_str = str(scan).replace('浏览','').strip().replace('W','')
                print('ins_str ',int_str)
                scan = int(float(int_str) * 10000)
                print('scan:',scan)

            if isinstance(scan, int):
                scan = scan
            else:
                scan = Util.random_number()
            temp_content_origin = response.xpath("//*[@class='article-main']").extract_first()
            temp_content_origin = Util.remove_impurity(temp_content_origin)
            # 这里少一个来源
            image_urls = re.findall(r'src="(.*?)"', temp_content_origin)
            target_image_urls = []
            for v_image in image_urls:
                if '?' in v_image:
                    img_target = v_image.split('?')[0]
                    t_image = Util.generate_pic_time(img_target)
                else:
                    t_image = Util.generate_pic_time(v_image)
                temp_content_origin = temp_content_origin.replace(v_image, t_image)
                target_image_urls.append(response.urljoin(v_image))

            item['image_urls'] = target_image_urls
            temp_content_origin = temp_content_origin.replace('figure','p')\
                .replace('<figcaption>','<span class="imgInfo">').replace('</figcaption>','</span>')
            item['body'] = Util.replace_style(temp_content_origin) if not None else ''

            try:
                item['images'] = []
                data_echo_url = re.findall(r'data-echo="(.*?)"', item['body'])
                for num, image_url in enumerate(data_echo_url):
                    if '?' in image_url:
                        img_target = image_url.split('?')[0]
                        t_image = Util.generate_images_pic(img_target)
                    else:
                        t_image = Util.generate_images_pic(image_url)
                    temp_image_url = Util.generate_images_pic(t_image)
                    image_dict = {"index": num, "url": temp_image_url, "title": ""}
                    item['images'].append(image_dict)
            except:
                item['images'] = []

            item['title'] = article_title
            item_id = Util.to_md5(article_title)
            item['item_id'] = item_id
            # item['_id'] = item_id
            item['item_type'] = 'ARTICLE'
            # 原创还是转载，
            item['create_type'] = ''
            item['source'] = '界面新闻'
            item['original_url'] = response.url
            janesi_time = Util.local_time()
            temp_author = '界面新闻'
            if author:
                temp_author = author
            item['name'] = temp_author
            item['avatar'] = ''
            item['type'] = 0
            item['fans_count'] = 0
            item['scan_count'] = 0
            item['collect_count'] = 0
            item['is_delete'] = '0'
            item['gmt_create'] = janesi_time
            item['gmt_modified'] = janesi_time

            item['category'] ={"channel": channel, "topic": [], "tag": tag_list, "keyword": [],
                 "region": ''}

            item['tag'] = tag_list
            item['channel'] = channel

            item['comment'] = Util.random_number()
            item['duration'] = 0
            item['size'] = 0
            item['topic'] = []
            item['keyword'] = []
            item['region'] =''

            item["videos"] = []
            item["audios"] = []
            item['videos'] = []
            item['audios'] = []
            item['copyright'] = ''
            item['release_time'] = release_time
            item['janesi_time'] = janesi_time
            item['scan'] = scan if not None else Util.random_number()
            item['like'] = 0
            item['share'] = 0
            item['play'] = Util.random_number()
            item['forward'] = 0
            item['collect'] = 0
            item['upload_file_flag'] = 'true'
            item['platform'] = 'jiemian'
            item['author_id'] = None
            check = Util.check_item(item)
            if check == 1:
                return
            yield item
        else:
            print('error--pages ',response)
            return
