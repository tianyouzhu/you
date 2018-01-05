# wangqiushi (@yottabyte.cn)
# 2016/09/01
# Copyright 2015 Yottabyte
# file description : urls.py.
__author__ = 'wangqiushi'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.schedule.resources import ScheduleResource

version_api = Api(api_name='v0')
version_api.register(ScheduleResource())

urlpatterns = patterns('yottaweb.apps.schedule.views',
                       (r'^schedule/$', 'schedules'),
                       (r'^schedule/([\w\d_]+)/$', 'schedule_content'),
                       (r'^schedule/update/([\w\d_]+)/$', 'schedule_update'),
                       (r'^schedule/([\w\d_]+)/([\d]{10})/$', 'schedule_detail'),
                       (r'^api/', include(version_api.urls)),
)
