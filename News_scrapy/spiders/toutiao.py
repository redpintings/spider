# -*- coding: utf-8 -*-

import re

import scrapy
from scrapy_redis.spiders import RedisSpider
from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem

class ToutiaoSpider(RedisSpider):

    name = 'toutiao'

    allowed_domains = ['open.toutiao.com']

    redis_key = 'toutiao:start_urls'

    # start_urls = ['http://open.toutiao.com/?channel=news_tech#channel=news_tech']


    def parse(self, response):

        v1_dict = {
            '财经':'news_finance#channel=news_finance',
            '科技':'news_tech#channel=news_tech',
            '体育': 'news_sports#channel=news_sports',
            '军事': 'news_military#channel=news_military',
            '娱乐': 'news_entertainment#channel=news_entertainment',
            '汽车': 'news_car#channel=news_car',
            '时尚': 'news_fashion#channel=news_fashion',
            '旅游': 'news_travel#channel=news_travel',
            '历史': 'news_history#channel=news_history',
            '游戏': 'news_game#channel=news_game',
            '健康': 'news_regimen#channel=news_regimen',
            '美食': 'news_food#channel=news_food',
        }

        for channel, tag_link in v1_dict.items():
            type_link ='http://open.toutiao.com/?channel={}'.format(tag_link)
            request = scrapy.Request(url=type_link, callback=self.get_main_link,dont_filter=True)
            request.meta['PhantomJS_V1'] = True
            request.meta['channel'] = channel
            yield request

    def get_main_link(self,response):
        channel = response.meta['channel']
        list_content = response.xpath("//*[@id='pageletListContent']/div[@class='list_content']/section")
        for v_content in list_content:

            title = v_content.xpath("./a/h3[@class='dotdot line3 ']/text()").extract_first()
            item_source = v_content.xpath("./a/div[@class='item_info']/span[@class='src space']/text()").extract_first()
            item_comments = v_content.xpath("./a/div[@class='item_info']/span[@class='cmt space']/text()").extract_first()
            item_link = v_content.xpath("./a/@href").extract_first()

            # 这里再排除一下悟空问答
            # if item_source is None and '悟空问答'  in item_source:
            #     return
            if 'http:' in item_link:
                item_link = item_link
            else:
                item_link = response.urljoin(item_link)
            # item_link = 'http://open.toutiao.com/a6533089233282793998/?utm_campaign=open&utm_medium=webview&utm_source=toutiao&item_id=6533089233282793998&label=wap'
            request = scrapy.Request(url=item_link, callback=self.parse_detail)
            request.meta['PhantomJS_V2'] = True
            request.meta['channel'] = channel
            yield request


    def parse_detail(self,response):
        channel = response.meta['channel']
        item = NewsItem()
        title = response.xpath("//*[@class='article-detail']/h1[@class='title']/text()").extract_first()
        _nickname = response.xpath("//*[@id='mediaName']/text()").extract_first()
        publish_time = response.xpath("//*[@id='pageletArticleContent']/div[@class='article-detail']/div[@class='article-header']/div[@class='pgc-bar-top clearfix']/div[@class='subtitle']/a[@class='extra']/span[@class='time']/text()").extract_first()

        temp_content_origin = response.xpath("//*[@class='article-content']").extract_first()
        if not temp_content_origin:
            return
        temp_content_origin = Util.remove_impurity(temp_content_origin)
        temp_content_origin = temp_content_origin.replace('src','')
        temp_content_origin = temp_content_origin.replace('data-url','src')
        temp_content_origin = Util.replace_style(temp_content_origin)

        # 这里可能解析到问悟空问答
        try:
            # 找到内容
            image_urls = re.findall(r'src="(.*?)"', temp_content_origin)

            target_image_urls = []
            for v_image in image_urls:
                t_image = Util.generate_pic_time(v_image)
                target_image_urls.append(response.urljoin(v_image))
                temp_content_origin = temp_content_origin.replace(v_image, t_image)
            item['image_urls'] = target_image_urls
            temp_content_origin = Util.remove_impurity(temp_content_origin)
            item['body'] = Util.replace_style(temp_content_origin) if not None else ''

            try:
                item['images'] = []
                data_echo_url = re.findall(r'data-echo="(.*?)"', item['body'])
                for num, image_url in enumerate(data_echo_url):
                    temp_image_url = Util.generate_images_pic(image_url)
                    image_dict = {"index": num, "url": temp_image_url, "title": ""}
                    item['images'].append(image_dict)
            except:
                item['images'] = []

            if title is not None:
                title = title.strip()
            else:
                return
            item['title'] = title
            nickname = '今日头条'
            if _nickname:
                nickname = _nickname.strip()

            janesi_time = Util.local_time()
            if publish_time is None:
                publish_time = janesi_time
            else:
                publish_time = publish_time.strip()

            item_id = Util.to_md5(title)
            item['item_id'] = item_id
            item['item_type'] = 'ARTICLE'
            # 原创还是转载，
            item['create_type'] = ''
            item['source'] = '今日头条'
            item['original_url'] = response.url

            item['name'] = nickname
            item['avatar'] = ''
            item['type'] = 0
            item['fans_count'] = 0
            item['scan_count'] = 0
            item['collect_count'] = 0
            item['is_delete'] = '0'
            item['gmt_create'] = janesi_time
            item['gmt_modified'] = janesi_time
            tags = []
            try:
                tags =Util.get_tags_by_jieba(item['body'])
            except:
                pass
            item['tag'] = [channel] +tags

            item['category'] ={"channel": channel, "child_channel":'', "topic": [], "tag": item['tag'], "keyword": [],
                 "region": ''}

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
            item['release_time'] = publish_time
            item['janesi_time'] = janesi_time
            item['scan'] = Util.random_number()
            item['like'] = 0
            item['share'] = 0
            item['play'] = Util.random_number()
            item['forward'] = 0
            item['collect'] = 0
            item['upload_file_flag'] = 'true'
            item['platform'] = 'toutiao'
            item['author_id'] = None
            check = Util.check_item(item)
            if check == 1:
                return
            if item['body'] == '':
                return
            else:
                yield item

        except:
            print('toutiao   error parse html (解析失败) -------------  ')
            return


