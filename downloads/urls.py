__author__ = 'wangqiushi; yangguang;'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.downloads.resources import DownloadsResource

version_api = Api(api_name='v0')
version_api.register(DownloadsResource())

urlpatterns = patterns('yottaweb.apps.downloads.views',
    (r'^download/$', 'download'),
    (r'^api/', include(version_api.urls))
)
