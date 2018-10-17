# -*- coding: utf-8 -*-
import scrapy
import re
import logging
from scrapy_redis.spiders import RedisSpider
from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem


class HuanqiuhotSpider(RedisSpider):
    name = 'huanqiuhot'
    allowed_domains = ['huanqiu.com']
    # start_urls = ['http://huanqiu.com/']
    redis_key = 'huanqiuwang:start_urls'

    def parse(self, response):
        page_hots = response.xpath('//div[@class="rightFir"]//a/@href').extract()
        page_new_list = response.xpath('//div[@class="centerThr"]//a/@href').extract()
        page_hots.extend(page_new_list)
        for page_hot in page_hots:
            yield scrapy.Request(url=page_hot,callback=self.parse_detail,dont_filter=True)

    def parse_detail(self,response):
        if 'la_con' not in response.body.decode('utf-8'):
            return
        item = NewsItem()
        try:
            title = re.findall('<h1 class="tle">(.*?)</h1>',response.body.decode('utf-8'))[0]
            title = title.replace('&quot;', '')
            if title:
                item['title'] = title
            else:
                logging.info('----TITLE---ERROR-----')
                return
        except Exception as error:
            logging.info('-----title---error--reason-- The article is not available ---',error)
            return

        item['item_type'] = 'ARTICLE'
        item['source'] = '环球网'
        item['channel'] = '社会'
        item_id = Util.to_md5(item['title'])
        item['item_id'] = item_id

        item['comment'] = Util.random_number()
        item['duration'] = 0
        item['size'] = 0
        item['topic'] = []
        item['keyword'] = []
        item['region'] = ''

        try:
            BodyData = re.findall(r' <div class="la_con">(.*?) <!',response.body.decode('utf-8'),re.S)[0]

            if '.mp4' in BodyData:
                print('>>>>>>>>>>视频数据')
                return
            if 'video' in BodyData:
                print('>>>>>>>>>视频数据')
                return

            if BodyData:
                BodyData = Util.remove_impurity(BodyData)
            else:
                logging.info('---body--error---')
                return
            if "http://himg2.huanqiu.com/" in BodyData:
                Name = response.xpath('/html/body/div[5]/div[3]/div[1]/div[2]/div[1]/span[2]/a/text()').extract_first()
                Date = response.xpath('/html/body/div[5]/div[3]/div[1]/div[2]/div[1]/span[1]/text()').extract_first()
                if BodyData:
                    DealWithBody = BodyData.replace('align="center"', '')
                else:
                    logging.info('-----BODY---ERROR----')
                    return
                tag = Util.get_tags_by_jieba(DealWithBody)
                if tag:
                    tag.append('社会')
                    item['tag'] = tag
                else:
                    item['tag'] = item['channel']

                if Date:
                    item['release_time'] = Date
                else:
                    item['release_time'] = Util.local_time()

                if Name:
                    item['name'] = Name
                else:
                    item['name'] = '环球网'
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


                ImageUrl = re.findall(r'src="(.*?)"', DealWithBody)
                if ImageUrl:
                    item['image_urls'] = ImageUrl
                else:
                    logging.info('----IMAGE_URL---ERROR---')
                    return
                try:
                    Temp_Content = DealWithBody
                    for content_img_url in ImageUrl:
                        content_url_temp = Util.generate_pic_time(content_img_url)
                        Temp_Content = Temp_Content.replace(content_img_url, content_url_temp)
                    item['body'] = Temp_Content
                except Exception as e:
                    logging.info('-----BODY---ERROR----',e)
                    return
            else:
                print(">>>>>>>>外链数据>>>Pass")
                return
            try:
                item['images'] = []
                data_echo_url = re.findall(r'data-echo="(.*?)"', item['body'])
                for num, image_url in enumerate(data_echo_url):
                    temp_image_url = Util.generate_images_pic(image_url)
                    image_dict = {"index": num, "url": temp_image_url, "title": ""}
                    item['images'].append(image_dict)
            except Exception as e:
                print('-----ERROR----', e, '--IMAGES---ERROR----')
                logging.info('----IMAGES---ERROR------')
                return
        except Exception as error:
            logging.info('error:',error)
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
        item['platform'] = 'huanqiuwang'
        item['author_id'] = None
        if not item['body']:
            return
        if len(item['body']) < 200:
            return
        CheckItem = Util.check_item(item)
        print('------##------', CheckItem, '-------##-----')
        if CheckItem == 1:
            return
        yield item


