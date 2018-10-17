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

        }
        mysql_list = {

        }
        redis_list = {

        }
        oss_list = {

        }
        es_list = {

        }
        config_type = {

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

        }
        mysql_list = {

        }
        redis_list = {

        }
        oss_list = {

        }
        es_list = {

        }
        config_type = {

        }
        j_list = {

        }

        return j_list

    @classmethod
    def pro_config(self):

        mongo_list = {

        }
        mysql_list = {

        }
        redis_list = {

        }
        oss_list = {
        }
        es_list = {
        }
        config_type = {
        }
        j_list = {

        }
        return j_list