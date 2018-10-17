#!/bin/sh
PATH=/home/admin/anaconda3/bin:/home/admin/bin:/home/admin/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
cd /home/admin/janesi-spider/Daily_crawler
python3 push_hot_urls.py
#cd /home/admin/janesi-spider/Daily_crawler/News_data
#time=`date "+%Y-%m-%d-%H:%M:%S"`
#dirname="news_${time}"
#mkdir $dirname
#cd $dirname

#scrapy crawl thepaper > /home/admin/janesi-spider/log/hot_crawler.log 2>&1
#scrapy crawl huanqiuhot > /home/admin/janesi-spider/log/hot_crawler.log 2>&1

#scrapy crawl wangyi3g > /home/admin/janesi-spider/log/hot_crawler.log 2>&1
#scrapy crawl toutiaoquality > /home/admin/janesi-spider/log/hot_crawler.log 2>&1
#scrapy crawl atoutiaoqualityvideo > /home/admin/janesi-spider/log/hot_crawler.log 2>&1
scrapy crawl tencentregion > /home/admin/janesi-spider/log/hot_crawler.log 2>&1
scrapy crawl toutiao_regions > /home/admin/janesi-spider/log/hot_crawler.log 2>&1
