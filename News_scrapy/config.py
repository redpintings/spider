# -*- coding: utf-8 -*-


class serviceConfig():

    @classmethod
    def settings(self,default):
        if default == 'dev':
            print('dev env -------- ')
            return self.dev_config()
        elif default == 'test':
            print('test env ------- ')
            return self.test_config()
        elif default == 'pro':
            print('pro  env -------  ')
            return self.pro_config()
        else:
            print(' default env ------ ',default,type(default))

    @classmethod
    def dev_config(self):

        mongo_list = {
            'MONGO_URL': '118.25.0.190',
            'MONGO_HOST': '118.25.0.190',
            'MONGO_USER': '',
            'MONGO_PWD': '',
            'MONGO_PORT': 27017,
            'MONGO_DB': 'news',
            'MONGO_COLL': 'article',
        }
        mysql_list = {
            'MYSQL_HOST':'118.25.0.190',
            'MYSQL_DBNAME':'janesi-center',
            'MYSQL_USER':'janesi_all',
            'MYSQL_PASSWD':'MyLBdwW13I83sygn',
            'MYSQL_PORT':3306
        }
        redis_list = {
            'REDIS_HOST':'118.25.0.190',
            'REDIS_PWD':'MyLBdwW13I83sygn',
        }
        oss_list = {
            'OSS_ENDPOINT':'http://oss-cn-shanghai.aliyuncs.com',
            'OSS_BUCKETNAME': 'janesi-oss-test',
        }
        es_list = {
            'ES_URL':'http://118.25.10.151',
            'ES_AUTH':'TYPE_DEV'
        }
        config_type = {
            'CONFIG_TYPE':'TYPE_DEV',
            'WEBSITE':'//yun2.janesi.net/'
        }
        j_list = {
            'mysql_list':mysql_list,
            'mongo_list':mongo_list,
            'redis_list':redis_list,
            'oss_list':oss_list,
            'es_list':es_list,
            'config_type':config_type,
        }
        return j_list

    @classmethod
    def test_config(self):

        mongo_list = {
            'MONGO_URL': '118.25.0.170',
            'MONGO_HOST': '118.25.0.170',
            'MONGO_USER': 'janesi_all',
            'MONGO_PWD': 'janesi_all',
            'MONGO_PORT': 27017,
            'MONGO_DB': 'news',
            'MONGO_COLL': 'article',
        }
        mysql_list = {
            'MYSQL_HOST':'118.25.0.170',
            'MYSQL_DBNAME':'janesi-center',
            'MYSQL_USER':'janesi_all',
            'MYSQL_PASSWD':'MyLBdwW13I83sygn',
            'MYSQL_PORT':3306,
            'MYSQL_ID_DB':'janesi-center'
        }
        redis_list = {
            'REDIS_HOST':'118.25.0.170',
            'REDIS_PORT':6379,
            'REDIS_PWD':'MyLBdwW13I83sygn',
        }
        oss_list = {
            'OSS_ENDPOINT': 'http://oss-cn-shanghai.aliyuncs.com',
            'OSS_BUCKETNAME':'janesi-oss-test',
        }
        es_list = {
            'ES_URL':'http://118.25.0.170:9200/',
            'ES_AUTH':'TYPE_TEST'
        }
        config_type = {
            'CONFIG_TYPE': 'TYPE_TEST',
            'WEBSITE': '//yun2.janesi.net/'
        }
        j_list = {
            'mysql_list':mysql_list,
            'mongo_list':mongo_list,
            'redis_list':redis_list,
            'oss_list':oss_list,
            'es_list':es_list,
            'config_type':config_type,
        }

        return j_list

    @classmethod
    def pro_config(self):

        mongo_list = {
            'MONGO_URL': 'dds-uf68b60d58b761c41.mongodb.rds.aliyuncs.com',
            'MONGO_HOST': 'dds-uf68b60d58b761c41.mongodb.rds.aliyuncs.com',
            'MONGO_USER': 'root',
            'MONGO_PWD': 'ESOaqDU4upr3',
            'MONGO_PORT': 3717,
            'MONGO_DB': 'news',
            'MONGO_COLL': 'article',
        }
        mysql_list = {
            # 'MYSQL_HOST':'sh-cdb-1ridb5ju.sql.tencentcdb.com',
            'MYSQL_HOST':'rm-uf6e44npwucqc06ip.mysql.rds.aliyuncs.com',
            'MYSQL_DBNAME':'janesi-center',
            'MYSQL_USER':'janesi_all',
            'MYSQL_PASSWD':'MyLBdwW13I83sygn',
            'MYSQL_PORT':3306,
            'MYSQL_ID_DB': 'janesi-center'
        }
        redis_list = {
            'REDIS_HOST':'r-uf602bb89862b934.redis.rds.aliyuncs.com',
            'REDIS_PORT':6379,
            'REDIS_PWD':'AL4pCIZDGIIn',
        }
        oss_list = {
            'OSS_ENDPOINT': 'http://oss-cn-shanghai-internal.aliyuncs.com',
            'OSS_BUCKETNAME':'janesi-oss',
        }
        es_list = {
            'ES_URL':'es-cn-mp90jhkbl0003q4fw.elasticsearch.aliyuncs.com',
            'ES_AUTH':'TYPE_PRO'
        }
        config_type = {
            'CONFIG_TYPE': 'TYPE_PRO',
            'WEBSITE': '//yun.janesi.com/'
        }
        j_list = {
            'mysql_list':mysql_list,
            'mongo_list':mongo_list,
            'redis_list':redis_list,
            'oss_list':oss_list,
            'es_list':es_list,
            'config_type':config_type,
        }
        return j_list