# wangqiushi(wang.qiushi@yottabyte.cn)
# 2015/08/19
# Copyright 2015 Yottabyte
# file description : urls.py.
__author__ = 'wangqiushi'
from django.conf.urls import patterns, url, include

urlpatterns = patterns('yottaweb.apps.docs.views',
                       (r'^docs/([\d\w]+)/$', 'docs'),
)
