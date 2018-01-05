# wangqiushi (@yottabyte.cn)
# 2014/07/24
# Copyright 2014 Yottabyte
# file description : urls.py.
__author__ = 'wangqiushi'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.alert.resources import AlertResource

version_api = Api(api_name='v0')
version_api.register(AlertResource())

urlpatterns = patterns('yottaweb.apps.alert.views',
                       (r'^alerts/$', 'alerts'),
                       (r'^alerts/records/$', 'records'),
                       (r'^alerts/new/$', 'alerts_new'),
                       (r'^alerts/([\w\d_]+)/$', 'update'),
                       (r'^api/', include(version_api.urls)),
)
