#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-03-29 18:51
# @Author  : yangshilong
# @Site    : 
# @File    : Ua_cookie.py
# @Software: PyCharm
import redis

USER_AGNET = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
]

COOKIE = [

]


class MeiTuanSpiser(object):

    @staticmethod
    def process_cookie(cookie):
        """
        cookie test
        :param cookie:
        :return:
        """
        list_dt = cookie.split(';')
        cookie_dict = {}
        for item in list_dt:
            if item and '=' in item:
                print(item.strip().split('='))
                key = item.strip().split('=')[0]
                value = item.strip().split('=')[1]
                cookie_dict[key] = value
        return cookie_dict

    @staticmethod
    def mysql_config():
        """
        mysql config
        :return:
        """
        test = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "mysql",
            "db": "waimai",
        }
        return test

    @staticmethod
    def redis_config():
        redis_config = {
            'host': '127.0.0.1',
            'port': 6379,
            'db': 0,
        }
        return redis_config




