# wangqiushi (wang.qiushi@yottabyte.cn)
# 2014/07/22
# Copyright 2014 Yottabyte
# file description : urls.py
__author__ = 'wangqiushi;'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.savedsearch.resources import SavedSearchResource

version_api = Api(api_name='v0')
version_api.register(SavedSearchResource())

urlpatterns = patterns('yottaweb.apps.savedsearch.views',
    (r'^api/', include(version_api.urls)),
)