# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import time
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver

from News_scrapy.settings_bak import USER_AGENT_LIST as user_list
import random
import requests
from News_scrapy import uautil
import logging

class UserAgentMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    def process_request(self, request, spider):
        """给每一个请求换一个user_agent"""
        if "xw.qq.com" in request.url:
            user_agent = random.choice(uautil.USER_AGENT_M)
        elif "is.snssdk.com/api/news/" in request.url:
            user_agent = random.choice(uautil.USER_AGENT_M)
        else:
            user_agent = random.choice(uautil.USER_AGENT_LIST)
        request.headers["User_Agent"] = user_agent

class ProxyMiddleware(object):
    """给每一个请求换一个ip代理"""

    def process_request(self, request, spider):
        try:
            PROXY_POOL_URL = 'http://api.ip.data5u.com/dynamic/get.html?order=ceb48be0f517bf1ade7aaaae008d890f&sep=3'
            response = requests.get(url=PROXY_POOL_URL)
            if response.status_code == 200:
                proxy = response.text.strip()
                print('-------in----use---proxy------: http://',proxy)
                request.meta['proxy'] = "http://" + proxy

        except Exception as e :
            print("-----Error:---Proxy---ERROR-----", e)

class PhantomJSMiddleware(object):
    @classmethod
    def process_request(cls, request, spider):
        if 'PhantomJS_V1' in request.meta:
            driver = webdriver.PhantomJS()
            try:
                driver.get(request.url)
                print('current_url0 >>>>', driver.current_url)
                time.sleep(1)
                page = 1
                content = ''
                while page < 10:
                    # 找到点击刷新按钮
                    refresh_btn = driver.find_element_by_xpath('//*[@id="pageletIndexHeader"]/div[1]/div[1]/a[2]')
                    refresh_btn.click()
                    time.sleep(random.uniform(2, 4))
                    page += 1
                    current_content = driver.page_source.encode('utf-8').decode('utf-8')
                    content = content + str(current_content) + '666666666'
                driver.quit()
            except Exception as e:
                driver.quit()
                pass

            return HtmlResponse(request.url, encoding='utf-8', body=content, request=request,)

        elif 'PhantomJS_V2' in request.meta:
            driver = webdriver.PhantomJS()
            try:
                driver.get(request.url)
                print('current_url1 >>>>', driver.current_url)
                time.sleep(1)
                content = driver.page_source.encode('utf-8')
                driver.quit()
            except Exception as e:
                driver.quit()

            return HtmlResponse(request.url, encoding='utf-8', body=content, request=request, )
