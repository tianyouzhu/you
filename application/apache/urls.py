from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.application.apache.resources import ApacheResource

version_api = Api(api_name='v0')
version_api.register(ApacheResource())

urlpatterns = patterns('yottaweb.apps.application.apache.views',
    (r'^app/apache/$', 'overview'),
    (r'^app/apache/referer/$', 'referer'),
    (r'^app/apache/resource/$', 'resource'),
    (r'^app/apache/visitor/$', 'visitor'),
    (r'^app/apache/service/$', 'service'),
    (r'^api/', include(version_api.urls))
)