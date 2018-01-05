# wangqiushi (wang.qiushi@yottabyte.cn)
# 2014/11/11
# Copyright 2014 Yottabyte
# file description : urls.py
__author__ = 'wangqiushi;'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.feedback.resources import FeedbackResource

version_api = Api(api_name='v0')
version_api.register(FeedbackResource())

urlpatterns = patterns('yottaweb.apps.feedback.views',
                       (r'^feedback/$', 'feedback'),
                       (r'^api/', include(version_api.urls)),
)