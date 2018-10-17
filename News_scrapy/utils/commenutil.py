# -*- coding: utf-8 -*-
# @Time    : 2018/5/21 16:45
# @Author  : 蛇崽
# @Email   : 643435675@QQ.com
# @File    : commenutil.py(部分不必要写的item filed)
import base64
import random

import binascii
import requests

from News_scrapy.MyUtils import Util
from News_scrapy.items import NewsItem


class ItemFiledUtil():

    def getNeedlessFiled(self,item):
        if isinstance(item,NewsItem):
            janesi_time = Util.local_time()
            item['create_type'] = ''
            item['avatar'] = ''
            item['type'] = 0
            item['fans_count'] = 0
            item['scan_count'] = 0
            item['collect_count'] = 0
            item['is_delete'] = '0'
            item['gmt_create'] = janesi_time
            item['gmt_modified'] = janesi_time

            item['child_channel'] = ''
            item['topic'] = []
            item['keyword'] = []
            item['region'] = ''
            item["videos"] = []
            item["audios"] = []
            item['videos'] = []
            item['audios'] = []
            item['copyright'] = ''
            item['scan'] = Util.random_number()
            item['like'] = 0
            item['share'] = 0
            item['play'] = Util.random_number()
            item['forward'] = 0
            item['collect'] = 0
            item['upload_file_flag'] = 'true'
            item['category'] = {"channel": item['channel'],
                                "child_channel": '',
                                "topic": [],
                                "tag": item['tag'],
                                "keyword": [],
                                "region": ''}

            return item
        else:
            print('error --- itemutil')
            return None

class CommenUtil():

    @classmethod
    def get_video_url(self,video_id):
        # video_id = '1eed074a19f54eb5bb36ce33b31c221d'
        r = str(random.random())[2:]
        r_1 = ('/video/urls/v/1/toutiao/mp4/' + str(video_id) + '?r=' + r)
        r_bin = r_1.encode('utf-8')
        s = binascii.crc32(r_bin)
        s = self.right_shift(val=s,n=0)
        url = 'https://ib.365yg.com' + r_1 + '&s=' + str(s)
        return url

        ##获取右移后的数据
    @classmethod
    def right_shift(self,val, n):
        return val >> n if val >= 0 else (val + 0x100000000) >> n

    @classmethod
    def get_url_real_url(self,url):  # 获取真实视频地址
        res = requests.get(url,
                           headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'},
                           verify=False)
        url_json = res.json()
        videolist = url_json['data']['video_list']
        keys = list(videolist.keys())
        videoinfo = videolist[keys[-1:][0]]
        url = base64.b64decode(videoinfo['main_url']).decode('utf-8')

        ret = {'video_url': url, 'video_type': videoinfo['vtype'], 'video_def': videoinfo['definition'], }
        return ret