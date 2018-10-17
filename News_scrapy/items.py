# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join




class NewsItem(scrapy.Item):

    _id=scrapy.Field()    # mongo索引
    channel_id = scrapy.Field()
    image_num = scrapy.Field()
    item_id = scrapy.Field()
    title = scrapy.Field()
    item_type = scrapy.Field()
    create_type = scrapy.Field()          # 是原创还是转发
    source = scrapy.Field()
    original_url = scrapy.Field()
    author = scrapy.Field()
    category = scrapy.Field()              # 类型image_url
    body = scrapy.Field()
    images = scrapy.Field()
    videos = scrapy.Field()
    audios = scrapy.Field()
    copyright = scrapy.Field()  # 版权
    release_time = scrapy.Field()
    janesi_time = scrapy.Field()
    scan = scrapy.Field()  # 阅读数
    like = scrapy.Field()  # 喜欢
    share = scrapy.Field()  # 分享
    play = scrapy.Field()  # 播放次数
    forward = scrapy.Field()  # 转发次数
    collect = scrapy.Field()  # 收藏数
    image_urls = scrapy.Field()
    cut_url = scrapy.Field()
    duration = scrapy.Field()
    size = scrapy.Field()
    # 上传至cos的flag
    images_success = scrapy.Field()

    tag = scrapy.Field()
    channel = scrapy.Field()
    child_channel = scrapy.Field()
    topic = scrapy.Field()
    keyword = scrapy.Field()
    region = scrapy.Field()
    comment = scrapy.Field()

    name = scrapy.Field()
    author_id = scrapy.Field()
    avatar = scrapy.Field()
    type = scrapy.Field()
    fans_count = scrapy.Field()
    scan_count = scrapy.Field()
    collect_count = scrapy.Field()
    is_delete = scrapy.Field()
    gmt_create =scrapy.Field()
    gmt_modified = scrapy.Field()
    platform = scrapy.Field()
    upload_file_flag = scrapy.Field()

class NewsLoader(ItemLoader):
    default_item_class = NewsItem
    default_input_processor = MapCompose(lambda s: s.strip())
    default_output_processor = TakeFirst()
    description_out = Join()