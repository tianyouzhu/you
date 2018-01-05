# wangqiushi (wang.qiushi@yottabyte.cn)
# 2015/01/07
# Copyright 2015 Yottabyte
# file description : url.py
__author__ = 'wangqiushi; yangguang;'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.config.resources import ConfigResource

version_api = Api(api_name='v0')
version_api.register(ConfigResource())

urlpatterns = patterns('yottaweb.apps.config.views',
    (r'^configs/$', 'configs'),
    (r'^configs/new/$', 'configs_new'),
    (r'^configs/new/steps/([\d\w_\-]+)/$', 'configs_steps'),
    (r'^configs/helper/$', 'configs_helper'),
    (r'^configs/(\d+)/$', 'configs_update'),
    (r'^api/', include(version_api.urls)),
)