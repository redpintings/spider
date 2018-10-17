#encoding=utf-8
import re
import scrapy
from bs4 import BeautifulSoup
from scrapy_redis.spiders import RedisSpider

from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem


class Bite8Spider(scrapy.Spider):
    name = 'bite8'
    allowed_domains = ['www.8btc.com']
    # start_urls = ['http://www.8btc.com/blockchain']
    redis_key = 'btc8:start_urls'

    def parse(self, response):
        for page in range(0,10):
            url = 'http://www.8btc.com/blockchain/page/{}'.format(page)
            yield scrapy.Request(url=url,callback=self.parse)

        soup = BeautifulSoup(response.body, 'lxml')
        main_node = soup.find_all('div', class_='item clearfix hidden-xs')
        for node in main_node:
            # print(node)
            title_link = node.find('a')['href']
            if title_link:
                yield scrapy.Request(title_link, callback=self.parse_detail)

    def parse_detail(self,response):
        item = NewsItem()

        soup = BeautifulSoup(response.body,'lxml')
        uinfo = soup.find('div',class_='single-crumbs clearfix').find_all('span',class_='')
        title = soup.find('div',class_='article-title').find('h1').get_text()
        item['title'] = title
        print('---------------少时诵诗书-------------  ',title)
        author = uinfo[0].get_text()
        item['name'] = author if None else ''
        relase_time = uinfo[1].get_text()
        item['release_time'] = relase_time if None else ''
        channel = '区块链'
        content = soup.find('div',class_='article-content')

        try:
            iframe = re.findall('<iframe(.*?)</iframe>',str(content))
            print('iframe ==== ',iframe)
            if iframe:
                strreplace = '<iframe'+str(iframe)+'</iframe>'
                print('strreplace ',strreplace)
                content = str(content).replace(strreplace,content)
            else:
                print('adsfffffffffffffffffffffffffff')
        except:
            pass

        content = str(content)
        content = Util.remove_impurity(content)
        content = Util.replace_style(content)

        image_urls = re.findall('<img.*src="(.*?)"',str(content))
        target_image_urls = []
        for v_image in image_urls:
            t_image = Util.generate_pic_time_pengpai_lazy(v_image)
            content = content.replace(v_image, t_image)
            v_image = 'SUPERLAZYSUB' + response.urljoin(v_image)
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
        item['channel'] = channel
        item['tag'] =['区块链']
        item_id = Util.to_md5(item['title'])

        item['item_id'] = item_id
        item['item_type'] = 'ARTICLE'
        # 原创还是转载，
        item['create_type'] = ''
        item['source'] = '巴比特'
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
        item['category'] = {"channel": item['channel'], "child_channel": '', "topic": [], "tag": item['tag'], "keyword": [],
                            "region": ''}

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
        item['platform'] = 'btc8'
        if content:
            check = Util.check_item(item)
            print('--------------  btc8  --------  ', check)
            if check == 1:
                return
            yield item
            # print(item)
        else:
            print('-----------  btc8  parse  error --------')
