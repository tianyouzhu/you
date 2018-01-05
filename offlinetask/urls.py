__author__ = 'wangqiushi; bindai;'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.offlinetask.resources import OfflinetaskResource

version_api = Api(api_name='v0')
version_api.register(OfflinetaskResource())

urlpatterns = patterns('yottaweb.apps.offlinetask.views',
    (r'^offlinetask/$', 'offlinetask'),
    (r'^api/', include(version_api.urls))
)
