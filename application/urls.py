from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.application.resources import ApplicationListResource

version_api = Api(api_name='v0')
version_api.register(ApplicationListResource())

urlpatterns = patterns('yottaweb.apps.application.views',
    (r'^app/$', 'overview'),
    (r'^api/', include(version_api.urls))
)
