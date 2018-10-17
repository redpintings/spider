# -*- coding: utf-8 -*-
# @Author  : 杨星星
# @Email   : yangshilong_liu@163.com

import datetime
import hashlib
import random
import re

import time
import requests
from lxml.html.clean import Cleaner
import jieba.posseg as pseg
import logging

from News_scrapy import settings
import jieba.analyse

class Util():

    PLACEHOLDERIMAGE = 'http://yun.janesi.com/janesi-solian/solian-2.1/background/backgroundImg.png" data-echo="{}"'

    @classmethod
    def to_md5(self, target):
        if isinstance(target, str):
            jiansi_time = str(time.strftime('%Y-%m',time.localtime(time.time())))
            target_md5 = hashlib.md5((target + jiansi_time).encode(encoding='UTF-8')).hexdigest()
            return str(target_md5)
        else:
            return None

    @classmethod
    def local_time(self):
        format_time = "%Y-%m-%d %H:%M:%S"
        cur_time = datetime.datetime.now().strftime(format_time)
        data_time = datetime.datetime.strptime(cur_time, format_time)
        return str(data_time)

    @classmethod
    def replace_style(self, origin_content):

        if origin_content:
            if isinstance(origin_content, str):
                # 过滤掉style 样式
                content = re.sub(r'style="(.*?)"', '', origin_content)
                # 内容里的跳转链接不可点击
                content = re.sub(r'target="_blank"', '', content)
                content = re.sub(r'width="(.*?)"','',content)
                content = re.sub(r'height="(.*?)"','',content)
                content = re.sub(r'align="center"','',content)
                content = re.sub(r'img_height="(.*?)"','',content)
                content = re.sub(r'img_width="(.*?)"','',content)
                content = content.replace('href=', '')
                # content = re.sub('data-original', 'src', content)
                if 'sizes=' in content:
                    content = re.sub('sizes=".*"','',content)
                return content
            else:
                return None
        else:
            return None


    # body  lazy loading  exclusive use
    @classmethod
    def generate_pic_time(self, target_url, oss_type=None,placeholderimg=PLACEHOLDERIMAGE):
        date = datetime.date.today()
        date = str(date).replace('-', '')

        if isinstance(target_url, str):
            pic_name = target_url.split('/')[-1]
            if "."in pic_name:
                if oss_type:
                    pic_name = 'news/' + date  + '/' + str(pic_name)
                else:
                    pic_name = settings.WEBSITE +'news/'+date+'/'+str(pic_name)
                    pic_name = placeholderimg.format(pic_name)
            else:
                if oss_type:
                    pic_name = 'news/' + date  + '/' + str(pic_name) + ".jpg"
                else:
                    pic_name = settings.WEBSITE+'news/' + date  + '/' + str(pic_name) + ".jpg"
                    pic_name = placeholderimg.format(pic_name)
            return pic_name
        else:
            return None


    #  image and  tencent cos  exclusive use
    @classmethod
    def generate_images_pic(self, target_url, oss_type=None):
        date = datetime.date.today()
        date = str(date).replace('-', '')

        if isinstance(target_url, str):
            pic_name = target_url.split('/')[-1]
            if "." in pic_name:
                if oss_type:
                    pic_name = 'news/' + date + '/' + str(pic_name)
                else:
                    pic_name = settings.WEBSITE +'news/' + date + '/' + str(pic_name)
            else:
                if oss_type:
                    pic_name = 'news/' + date + '/' + str(pic_name) + ".jpg"
                else:
                    pic_name = settings.WEBSITE +'news/' + date + '/' + str(pic_name) + ".jpg"
            return pic_name
        else:
            return None

    # 腾讯新闻专用
    @classmethod
    def generate_pic_time_qq(self, target_url, oss_type=None):
        date = datetime.date.today()
        date = str(date).replace('-', '')
        if isinstance(target_url, str):
            pic_name_end = target_url.split('/')[-1]
            pic_name_second = target_url.split('/')[-2]
            if "." in pic_name_end:
                pic_name = settings.WEBSITE + 'news/' + date + '/' + str(pic_name_end)
            elif oss_type:
                pic_name = 'news/' + date + '/' + pic_name_second + '.jpg'
            else:
                pic_name = settings.WEBSITE + 'news/' + date + '/' + str(pic_name_end) + '.jpg'
            return pic_name
        else:
            return None

    @classmethod
    def generate_pic_time_qq_lazy(self, target_url, oss_type=None, placeholderimg=PLACEHOLDERIMAGE):
        date = datetime.date.today()
        date = str(date).replace('-', '')
        if isinstance(target_url, str):
            pic_name_end = target_url.split('/')[-1]
            pic_name_second = target_url.split('/')[-2]
            if "." in pic_name_end:
                pic_name = settings.WEBSITE + 'news/' + date + '/' + str(pic_name_second)
            elif oss_type:
                pic_name = 'news/' + date + '/' + str(pic_name_second) + '.jpg'
            else:
                pic_name = settings.WEBSITE + 'news/' + date + '/' + str(pic_name_second) + '.jpg'
                pic_name = placeholderimg.format(pic_name)
            return pic_name

        else:
            return None


    # 一点资讯专用修改名称
    @classmethod
    def generate_pic_time_yd(self, target_url, oss_type=None):
        date = datetime.date.today()
        date = str(date).replace('-', '')
        if isinstance(target_url, str):
            pic_name = target_url.split('/')[-1].replace('.','').replace('?','').replace("=",'')
            if oss_type:
                pic_name = 'news/' + date + '/' + str(pic_name) + '.jpg'
            else:
                pic_name = settings.WEBSITE +'news/' + date + '/' + str(pic_name)
            return pic_name
        else:
            return None

    #  一点咨询的专用懒记载
    @classmethod
    def generate_pic_time_yidian_lazy(self, target_url, oss_type=None,placeholderimg=PLACEHOLDERIMAGE):
        date = datetime.date.today()
        date = str(date).replace('-', '')

        if isinstance(target_url, str):
            pic_name = target_url.split('/')[-1].replace('.','').replace('?','').replace("=",'')
            if "."in pic_name:
                if oss_type:
                    pic_name = 'news/' + date  + '/' + str(pic_name)
                else:
                    pic_name = settings.WEBSITE +'news/'+ date +'/'+str(pic_name)
                    pic_name = placeholderimg.format(pic_name)
            else:
                if oss_type:
                    pic_name = 'news/' + date  + '/' + str(pic_name) + ".jpg"
                else:
                    pic_name = settings.WEBSITE +'news/' + date  + '/' + str(pic_name) + ".jpg"
                    pic_name = placeholderimg.format(pic_name)
            return pic_name
        else:
            return None


    @classmethod
    def generate_pic_time_pengpai(self, target_url, oss_type=None):
        date = datetime.date.today()
        date = str(date).replace('-', '')
        if isinstance(target_url, str):
            pic_name = target_url.split('/')[-1]
            wb_name = '.jpg'
            if "." in pic_name:
                wb_name = pic_name
            if oss_type:
                pic_name = 'news/' + date + '/' +  wb_name
            else:
                pic_name = settings.WEBSITE+'news/' + date + '/' + wb_name
            return pic_name
        else:
            return None

    @classmethod
    def generate_pic_time_pengpai_lazy(self, target_url, oss_type=None,placeholderimg=PLACEHOLDERIMAGE):
        date = datetime.date.today()
        date = str(date).replace('-', '')
        if isinstance(target_url, str):
            fir_name = target_url.split('//')[-1]
            pic_name = fir_name.replace('.','').replace('/','')
            # 截取倒数第40位到结尾
            if len(pic_name) >= 40:
                pic_name = 'SUPERLAZYSUB'+pic_name[-40:]
            else:
                pic_name = 'SUPERLAZYSUB' + pic_name
            wb_name = '.jpg'
            if "." in fir_name:
                wb_name = '.'+str(fir_name).split('.')[-1]  #  .gif   .jpg

            if oss_type:
                pic_name = 'news/' + date + '/' + str(pic_name) + wb_name
            else:
                pic_name = settings.WEBSITE+'news/' + date + '/' + str(pic_name) + wb_name
                pic_name = placeholderimg.format(pic_name)
            return pic_name

        else:
            return None

    # 除去不必要的标签
    @classmethod
    def remove_impurity(self, content):

        cleaner = Cleaner(scripts=True, annoying_tags=True, remove_unknown_tags=True, style=True,
                          links=True, page_structure=False, safe_attrs_only=False, )
        html = cleaner.clean_html(content)
        return html


    # 造假随机阅读数
    @classmethod
    def random_number(self):
        return random.randint(10000, 15000)

    @classmethod
    def check_item(self, item):
        right = 0
        loser = 1


        if isinstance(item['item_id'], str) \
            and isinstance(item['title'], str) \
            and isinstance(item['item_type'], str)\
            and isinstance(item['create_type'], str) \
            and isinstance(item['source'], str) \
            and isinstance(item['original_url'], str) \
            and isinstance(item['body'], str) \
            and isinstance(item['name'], str) \
            and isinstance(item['channel'], str) \
            and isinstance(item['tag'], list)\
            and isinstance(item['scan'], int) \
            and isinstance(item['like'], int)\
            and isinstance(item['share'], int) \
            and isinstance(item['play'], int) \
            and isinstance(item['forward'], int)\
            and isinstance(item['collect'], int)\
            and isinstance(item['release_time'], str)\
            and isinstance(item['janesi_time'], str)\
            and isinstance(item['images'], list) \
            and isinstance(item['videos'], list)\
            and isinstance(item['audios'], list) \
            and isinstance(item['copyright'], str) \
            and isinstance(item['platform'], str) \
            and isinstance(item['avatar'], str)\
            and isinstance(item['type'], int) \
            and isinstance(item["category"], dict)\
            and isinstance(item['janesi_time'],str):
            # and isinstance(item['author'], dict):

            return right
        else:
            logging.info('----check--item---not---pass-----')
            return loser

    # 检查 body
    @classmethod
    def check_body(self,body):
        if not body:
            logging.info('------body----empty----error----')
            return
        if len(body) < 200:
            logging.info('------body---length----error-----')
            return
        if body:
            logging.info('------body -----is------right-----')

    # 对body进行分词 提取名词,作为tag  如果对 body进行分词请开启jieba并行模式
    @classmethod
    def get_tags_by_jieba(self, body):
        res = re.compile("\<.*?\>")
        bodys = res.sub('', body)

        allowps = ['n', 'nr', 'ns', 'nt', 'nz']
        jieba.analyse.set_stop_words('/home/admin/janesi-spider/ETL/stop_words')
        key_word = jieba.analyse.extract_tags(bodys, topK=5, allowPOS=allowps,withWeight=False)
        tag = key_word
        return tag

    # 对title进行分词作为标签
    @classmethod
    def tag_by_jieba_title(self,title):

        words = pseg.cut(title)
        tag = []
        for w in words:
            if 'n' in w.flag and len(w.word) > 1:
                tag.append(w.word)
        logging.info('-----cut-  title--right----')
        return tag


    #  根据状态码检查视频链接是否可用
    @classmethod
    def send_request(self,video_url):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        }
        response_info = requests.get(url=video_url,headers=header)
        code = response_info.status_code
        return code