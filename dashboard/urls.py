__author__ = 'wangqiushi'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.dashboard.resources import DashboardResource

version_api = Api(api_name='v0')
version_api.register(DashboardResource())

urlpatterns = patterns('yottaweb.apps.dashboard.views',
                       (r'^dashboard/$', 'dashboard_group'),
                       (r'^dashboard/login/(.+)/(.+)/(.+)/$', 'dashboard_group_login'),
                       (r'^dashboard/(?P<did>[\w\d_]+)/(?P<tid>[\w\d_]+)/$', 'dashboard_detail'),
                       (r'^api/', include(version_api.urls))
                       )
