# -*- coding: utf-8 -*-

import json

import pymongo

# 用户名密码是可选的，非必须的，如果没有设置用户名密码则默认没有
# 端口号默认为 27017
# client = pymongo.MongoClient("mongodb://mongouser:ESOaqDU4upr3@172.17.0.9:27017/news")
#
# # 假设我的数据库下叫test，test下有个collection名字为conference
# # 可以通过以下方式获取名字为conference的collection
# db = client["test"]
# stb = db.conference

client = pymongo.MongoClient(host='118.25.0.170')
client.admin.authenticate('janesi_all', 'janesi_all')
db = client['news']  # 获得数据库的句柄
coll = db['article']  # 获得collection的句柄
# print('================')
# client = pymongo.MongoClient("mongodb://janesi_all:janesi_all@118.25.0.170:27017/news")
#
# # 假设我的数据库下叫test，test下有个collection名字为conference
# # 可以通过以下方式获取名字为conference的collection
# db = client["news"]
# stb = db['article']
# print(stb)

print('-------------------')
# find()用于查找conference下的所有数据
