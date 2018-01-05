from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.application.custom.resources import CustomResource

version_api = Api(api_name='v0')
version_api.register(CustomResource())

urlpatterns = patterns('yottaweb.apps.application.custom.views',
    (r'^app/custom/([\w\d]+)/$', 'overview'),
    (r'^app/table/([\w\d]+)/$', 'table'),
    (r'^api/', include(version_api.urls))
)