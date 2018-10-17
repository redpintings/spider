#!/bin/sh
PATH=/home/admin/anaconda3/bin:/home/admin/bin:/home/admin/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
cd /home/admin/janesi-spider/Daily_crawler
python3 push_urls.py
#cd /home/admin/janesi-spider/Daily_crawler/News_data
#time=`date "+%Y-%m-%d-%H:%M:%S"`
#dirname="news_${time}"
#mkdir $dirname
#cd $dirname


#scrapy crawl besttoutiao      > /home/admin/janesi-spider/log/crawler.log 2>&1
#scrapy crawl bobovideo      > /home/admin/janesi-spider/log/crawler.log 2>&1




scrapy crawl egvideo      > /home/admin/janesi-spider/log/crawler.log 2>&1
scrapy crawl zaker     > /home/admin/janesi-spider/log/crawler.log 2>&1

scrapy crawl dftoutiao  > /home/admin/janesi-spider/log/crawler.log 2>&1

scrapy crawl fireball  > /home/admin/janesi-spider/log/crawler.log 2>&1
scrapy crawl yidian  > /home/admin/janesi-spider/log/crawler.log 2>&1

scrapy crawl jiemian         > /home/admin/janesi-spider/log/crawler.log 2>&1


scrapy crawl vmov  > /home/admin/janesi-spider/log/crawler.log 2>&1

scrapy crawl maopu   > /home/admin/janesi-spider/log/crawler.log 2>&1

scrapy crawl pengfu   > /home/admin/janesi-spider/log/crawler.log 2>&1
scrapy crawl qncye   > /home/admin/janesi-spider/log/crawler.log 2>&1

scrapy crawl fenghuangtv > /home/admin/janesi-spider/log/crawler.log 2>&1


scrapy crawl pearvideo > /home/admin/janesi-spider/log/crawler.log 2>&1
scrapy crawl toutiaohouse > /home/admin/janesi-spider/log/crawler.log 2>&1

scrapy crawl toutiao  > /home/admin/janesi-spider/log/crawler.log 2>&1

scrapy crawl budejie  > /home/admin/janesi-spider/log/crawler.log 2>&1
















#pre_dir=/home/admin/janesi-spider/News_data/

#pre_dir=$main_dir/News_data/
#news_dir=${pre_dir}${dirname}
#cd /home/admin/janesi-spider/ETL
#cd $main_dir/ETL
#python auto_embedding_simhash.py --dir $news_dir > /home/admin/janesi-spider/log/auto_embedding_simhash.log 2>&1
#python3 auto_embedding_simhash.py --dir $news_dir > $main_dir/log/auto_embedding_simhash.log 2>&1
#cd /home/admin/janesi-spider/News_statistics
#cd $main_dir/News_statistics
#python news_statistics.py --dir $news_dir > /home/admin/janesi-spider/log/news_count.log 2>&1
#python3 news_statistics.py --dir $news_dir > $main_dir/log/news_count.log 2>&1

#echo $news_dir
