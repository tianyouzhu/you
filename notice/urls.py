from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.notice.resources import NoticeResource

version_api = Api(api_name='v0')
version_api.register(NoticeResource())

urlpatterns = patterns('yottaweb.apps.notice.views',
    (r'^notice/$', 'list'),
    # (r'^notice/setting/$', 'setting'),
    (r'^api/', include(version_api.urls))
)
