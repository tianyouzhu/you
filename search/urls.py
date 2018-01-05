# wangqiushi(wang.qiushi@yottabyte.cn), mayangguang(ma.yangguang@yottabyte.cn)
# 14-7-8
# Copyright 2014 Yottabyte
#
# file description : urls for search.

from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.search.resources import SearchResource

version_api = Api(api_name='v0')
version_api.register(SearchResource())

urlpatterns = patterns('yottaweb.apps.search.views',
    (r'^search/$', 'search'),
    (r'^api/', include(version_api.urls))
)