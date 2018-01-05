# -*- coding: utf-8 -*-
# wu.ranbo@yottabyte.cn
# 2014-12-01
# Copyright 2014 Yottabyte
# file description:

from django.conf.urls import patterns, url, include
from yottaweb.apps.subscription import views
from tastypie.api import Api
from yottaweb.apps.subscription.resources import SubscriptionResource

version_api = Api(api_name='v0')
version_api.register(SubscriptionResource())

urlpatterns = patterns('',
                       url(r'^subscription/new$', views.new, name='new'),
                       url(r'^subscription$', views.create, name='create'),
                       (r'^api/', include(version_api.urls)),
                       )
