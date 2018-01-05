# wangqiushi,mayangguang (wang.qiushi@yottabyte.cn, ma.yangguang@yottabyte.cn)
# 2014/07/30
# Copyright 2014 Yottabyte
# file description : urls.py.
__author__ = 'wangqiushi'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.report.resources import ReportResource

version_api = Api(api_name='v0')
version_api.register(ReportResource())

urlpatterns = patterns('yottaweb.apps.report.views',
                       (r'^reports/$', 'reports'),
                       (r'^reports/new/$', 'reports_new'),
                       (r'^reports/list/$', 'reports_list'),
                       (r'^reports/([\w\d_]+)/$', 'report_update'),
                       (r'^api/', include(version_api.urls)),
)
