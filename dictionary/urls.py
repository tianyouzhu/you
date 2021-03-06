__author__ = 'wangqiushi; yangguang;'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.dictionary.resources import DictionaryResource

version_api = Api(api_name='v0')
version_api.register(DictionaryResource())

urlpatterns = patterns('yottaweb.apps.dictionary.views',
    (r'^dictionary/$', 'lists'),
    (r'^api/', include(version_api.urls)),
)