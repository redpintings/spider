# -*- coding: utf-8 -*-

import random

import oss2
import requests
from itertools import islice

import time

from News_scrapy import uautil

auth = oss2.Auth('LTAIt1aWL6gEopIk', '8bOHy8aCWnjlyv1JWeVxDdXJ4siVWN')
service = oss2.Service(auth, 'janesi-oss')
bucket = oss2.Bucket(auth, 'http://oss-cn-shanghai.aliyuncs.com', 'janesi-oss')
b_url = 'http://yun.janesi.com/'
count = 0
e_count = 0
e2_count = 0
for b in islice(oss2.ObjectIterator(bucket), 40000):
    url = b.key
    c_url = b_url + url
    count = count +1
    print(c_url,count)
    # if 'news/20180515' in url:
    #     count = count+1
    #     print(c_url,count)
    #     # input = requests.get(c_url, headers={'User-Agent': random.choice(uautil.USER_AGENT_LIST)})
    #     # dataname = str(url).replace('news','newstest')
    #     # result = bucket.put_object(dataname, input)
    #     # if result.status == 200:
    #     #     pass
    #     # else:
    #     #     print('failed =====  ',url)
    # elif 'newstest/20180515' in url:
    #     e2_count = e2_count +1
    #     print(e2_count,c_url)
    # else:
    #     e_count = e_count+1