# wangqiushi,mayangguang (wang.qiushi@yottabyte.cn, ma.yangguang@yottabyte.cn)
# 2014/07/30
# Copyright 2014 Yottabyte
# file description : urls.py.
__author__ = 'wangqiushi'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.system.resources import SystemResource

version_api = Api(api_name='v0')
version_api.register(SystemResource())

urlpatterns = patterns('yottaweb.apps.system.views',
                       (r'^system/custom/$', 'custom'),
                       (r'^system/custom/dashboard/$', 'custom_dash'),
                       (r'^system/custom/dashboard/new/$', 'custom_dash_new'),
                       (r'^system/custom/dashboard/([\d\w_]+)/$', 'custom_dash_update'),
                       (r'^system/custom/application/$', 'custom_app'),
                       (r'^system/custom/application/new/$', 'custom_app_new'),
                       (r'^system/custom/application/([\d\w_]+)/$', 'custom_app_update'),
                       (r'^system/custom/theme/$', 'custom_theme'),
                       (r'^system/custom/table/$', 'custom_table'),
                       (r'^system/custom/table/new/$', 'custom_table_new'),
                       (r'^system/custom/table/([\d\w_]+)/$', 'custom_table_update'),
                       (r'^api/', include(version_api.urls)),
                       )
