__author__ = 'wangqiushi; yangguang;'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.usage.resources import UsageResource

version_api = Api(api_name='v0')
version_api.register(UsageResource())

urlpatterns = patterns('yottaweb.apps.usage.views',
    (r'^usage/$', 'usage'),
    (r'^api/', include(version_api.urls)),
)