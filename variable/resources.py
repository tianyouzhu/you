# wangqiushi (wang.qiushi@yottabyte.cn)
# 2016/03/09
# Copyright 2014-2016 Yottabyte
# file description : resources.py
__author__ = 'wangqiushi'

import logging
import ConfigParser
import os

# get es url from yottaweb.ini
cf = ConfigParser.ConfigParser()
conf_file = os.getcwd() + '/config/yottaweb.ini'
try:
    cf.read(conf_file)
    yottaweb_path = cf.get("path", "data_path")
except Exception, e:
    print e
    yottaweb_path = "/data/rizhiyi/yottaweb/"

if not os.path.exists(yottaweb_path):
    os.makedirs(yottaweb_path)

custom_path = yottaweb_path + "custom/"
if not os.path.exists(custom_path):
    os.makedirs(custom_path)

HEKA_PACKAGE_URL = 'heka_update/'
heka_path = yottaweb_path + HEKA_PACKAGE_URL
if not os.path.exists(heka_path):
    os.makedirs(heka_path)


log = logging.getLogger('django.request')


class MyVariable():

    def get_var(self, segment="", key="", **kwargs):
        if not segment or not key:
            return ""
        try:
            val = cf.get(segment, key)
        except Exception, e:
            log.error("Get variable[%s]-[%s] error!" % (segment, key))
            if segment == "path" and (key == "data_path" or key == "report_path"):
                val = "/data/rizhiyi/yottaweb/"
            else:
                val = ""
        return val

