#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-04-01 18:41
# @Author  : yangshilong
# @Site    : 
# @File    : spider.py
# @Software: PyCharm
import csv
import hashlib
import json
import time
import redis
import random
import requests
from waimai.Ua_cookie import COOKIE, MeiTuanSpiser
import logging
import pymysql


class WaiMai(object):

    logging = logging.getLogger('mt_spider')

    def __init__(self):
        config = MeiTuanSpiser.mysql_config()
        redis_config = MeiTuanSpiser.redis_config()
        self.conn = pymysql.connect(host=config.get('host'),
                                    port=config.get('port'),
                                    user=config.get('user'),
                                    password=config.get('password'),
                                    db=config.get('db'),
                                    charset='utf8', )
        self.cursor = self.conn.cursor()
        self.pool = redis.ConnectionPool(host=redis_config.get('host'), port=redis_config.get('port'), db=0, )

    @staticmethod
    def get_log():
        """
        Gets a log instance
        :return:
        """
        logger = logging.getLogger("mz_log")

        logger.setLevel("INFO")

        log_name = 'mz_dirty_error.log'
        if not logger.handlers:
            fh = logging.FileHandler(log_name)
            log_format = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s-%(message)s-[%(filename)s:%(lineno)d]")
            fh.setFormatter(log_format)  # setFormatter() selects a Formatter object for this handler to use
            logger.addHandler(fh)
        return logger

    @staticmethod
    def zip_list_data(jw_list):
        """
        made long lat data
        :param jw_list:
        :return:
        """
        r_data = None
        list_lang = []
        list_lat = []
        for i in range(10):
            _lang = jw_list[-2]
            _lat = jw_list[-1]
            if len(_lang) != 6:
                lang = (str(_lang + '0')[0:-1] + str(i) + '0000').replace('.', '')
            else:
                lang = (str(_lang)[0:-1] + str(i) + '0000').replace('.', '')

            list_lang.append(lang)
            if len(_lat) != 5:
                lat = (str(_lat + '0')[0:-1] + str(i) + '0000').replace('.', '')
            else:
                lat = (str(_lat)[0:-1] + str(i) + '0000').replace('.', '')
            list_lat.append(lat)
            city_dt = ''.join(jw_list[0:3])
            r_data = {
                "city": city_dt,
                "data": list(zip(list_lang, list_lat))
            }
        return r_data

    @staticmethod
    def _send_request(index, lat, long):
        url = "http://i.waimai.meituan.com/openh5/homepage/poilist?_={}".format(int(time.time()))
        form_data = {
            "startIndex": "{}".format(index),
            "wm_actual_latitude": "{}".format(lat),
            "wm_actual_longitude": "{}".format(long),
        }
        headers = {
            "Cookie": random.choice(COOKIE)
        }
        response_data = requests.post(url=url, data=form_data, headers=headers)
        print(response_data.status_code)
        if response_data.status_code == 200:
            response_body = response_data.text
            return response_body

    def read_csv(self):
        """
        read csv from city data
        And traverse the detailed longitude and latitude data
        :return:
        """
        try:
            with open('/Users/ysl/py_file/Mtwaimai/Mtwaimai/city_long_lat.csv') as csvfile:
                csv_reader = csv.reader(csvfile)
                for row in csv_reader:
                    csv_city_dt = ''.join(row).split(' ')
                    dict_city_long_lat = self.zip_list_data(csv_city_dt)
                    city_name = dict_city_long_lat.get('city')
                    print('*'*30)
                    print(city_name)
                    for long, lat in dict_city_long_lat.get('data'):
                        for index in range(250):
                            try:
                                response_body = self._send_request(index, lat, long)
                                print(response_body)
                                print('坐标位置', long, lat)
                                for shop_l in self.parse_data(response_body):
                                    self.insert_mysql(city_name=city_name, shop_l=shop_l)
                                    # if insert_flag == 'pass':
                                    #     continue
                            except Exception as f:
                                self.get_log().info('error--{' + str(f) + '}')
                                continue
        except Exception as e:
            self.get_log().info('error-{' + str(e) + '}')

    def insert_mysql(self, city_name, shop_l):
        """
        Insert the data into mysql
        :param city_name:
        :param shop_l:
        :return:
        """
        _id = shop_l.get('mtWmPoiId')
        city_name = city_name
        shop_name = shop_l.get('shopName')
        month_sales = shop_l.get('monthSalesTip')
        shop_pic_url = shop_l.get("picUrl")
        shop_score = shop_l.get("wmPoiScore")
        delivery_time = shop_l.get("deliveryTimeTip")
        start_price = shop_l.get("minPriceTip")
        shipping_send_price = shop_l.get("shippingFeeTip")
        average_price = shop_l.get("averagePriceTip")
        shipping_time_info = shop_l.get("shipping_time")
        distance = shop_l.get("distance")
        address = shop_l.get('address')
        # self.save_data(json.dumps(shop_data) + '\n')
        join_md5_data = str(address + shop_name)
        md5_str = self.to_md5(join_md5_data)
        redis_flag = self.redis_repetition(md5_code=md5_str)
        if not redis_flag:
            data = (
                city_name, shop_name, month_sales, shop_pic_url, shop_score, delivery_time,
                start_price, shipping_send_price,
                average_price, shipping_time_info, distance, address)
            sql = 'insert into shop_data(city_name,shop_name,mouth_sales,shop_pic_url,' \
                  'shop_score,delivery_time,shipping_send_price,shipping_start_price,' \
                  'average_price,time_info,distance,address) values ("%s","%s","%s","%s"' \
                  ',"%s","%s","%s","%s","%s","%s","%s","%s")' % (data)
            self.cursor.execute(sql)
            self.conn.commit()
            print('ok')
        # else:
        #     print('这个是重复数据 丢弃！')
        #     return 'pass'

    def redis_repetition(self, md5_code):
        """
        redis hash
        :param md5_code:
        :return:
        """
        key_name = 'wm_{}'.format(str(time.strftime('%Y-%m', time.localtime(time.time())))[-1])
        r = redis.StrictRedis(connection_pool=self.pool)
        if r.sismember(key_name, str(md5_code)):
            return True
        else:
            r.sadd(key_name, str(md5_code))
            return False

    @staticmethod
    def to_md5(target):
        """
        :param target:
        :return:
        """
        if isinstance(target, str):
            shop_name = str(time.strftime('%Y-%m', time.localtime(time.time())))
            target_md5 = hashlib.md5((target + shop_name).encode(encoding='UTF-8')).hexdigest()
            return str(target_md5)
        else:
            return None

    @staticmethod
    def parse_data(response_body):
        """
        Get json data from source page
        :param response_body:
        :return:
        """
        json_data = json.loads(response_body)
        shop_list = json_data.get('data').get('shopList')
        if not shop_list:
            return
        for shop_l in shop_list:
            yield shop_l

    @staticmethod
    def save_data(content):
        """
        Save the data locally
        :param content:
        :return:
        """
        with open('shop_data.json', 'a') as f:
            print('xxx')
            f.write(content.encode('utf-8').decode('unicode-escape'))
            print('insert ok')

    @staticmethod
    def insert_mysql_bak(self):
        """
        data = (
        city_name, shop_name, month_sales, shop_pic_url, shop_score, delivery_time, start_price, shipping_send_price,
        averagePrice, shipping_time_info, distance, address)
        sql = 'insert into shop_data(city_name,shop_name,mouth_sales,shop_pic_url,shop_score,delivery_time,shipping_send_price,shipping_start_price,average_price,time_info,distance,address) values ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")' % (
            data)
        self.cursor.execute(sql)
        self.conn.commit()
        print('ok')
        """
        return

    def main(self):
        """
        the main code run
        close connection
        :return:
        """
        self.read_csv()
        self.cursor.close()
        self.conn.close()
        self.pool.disconnect()


if __name__ == "__main__":

    w = WaiMai()
    w.main()
