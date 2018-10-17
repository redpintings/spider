#! /bin/sh

cd /home/admin/janesi-spider/log
now_time=`date "+%Y-%m-%d-%H:%M:%S"`
echo $now_time>>run_time.txt
time -a -o run_time.txt /home/admin/janesi-spider/Daily_crawler/news_hot_crawl.sh