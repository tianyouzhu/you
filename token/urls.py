__author__ = 'wangqiushi; yangguang;'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.token.resources import TokenResource

version_api = Api(api_name='v0')
version_api.register(TokenResource())

urlpatterns = patterns('yottaweb.apps.token.views',
    (r'^tokens/$', 'tokens'),
    (r'^api/', include(version_api.urls)),
)