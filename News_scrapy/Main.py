# -*- coding: utf-8 -*-
# @Time    : 2018/1/6 14:51
# @Author  : 蛇崽
# @Email   : 643435675@QQ.com
# @File    : Main.py(命令行入口)

# 导入scrapy命令方法

from scrapy.cmdline import execute
import sys
import os

# 给python解释器，添加模块新路径，
# 将main.py 文件所在目录添加到python解释器中
sys.path.append(os.path.join(os.getcwd()))

# targetLine = 'zixun'
targetLine = 'xiachufang'
# targetLine = 'douguo'
targetLine = 'qiqusp'
targetLine = 'lingshitx'
targetLine = 'cnsoftnews'
targetLine = 'zaker'
# targetLine = 'jiemian'
# targetLine = 'qncye'
targetLine = 'fangtianxia'
targetLine = 'thepaper'
# targetLine = 'budejie'
targetLine = 'wangyi3g'
# targetLine = 'WeChat'
# targetLine = 'budejie'
targetLine = 'besttoutiao2'
targetLine = 'atoutiaoqualityvideo'
targetLine = 'adouban_spider'
targetLine = 'agonggong_spider'
execute(['scrapy', 'crawl', targetLine])

