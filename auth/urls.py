__author__ = 'wangqiushi; yangguang;'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.auth.resources import AuthResource

version_api = Api(api_name='v0')
version_api.register(AuthResource())

urlpatterns = patterns('yottaweb.apps.auth.views',
    (r'^auth/register/$', 'auth_register'),
    (r'^auth/register_info/(?P<for_md5>[\w\d_.-]+)/(?P<for_base64>[\w\d_.-=]+)/$', 'auth_register_info'),
    (r'^auth/register/active/(?P<for_md5>[\w\d_.-]+)/(?P<for_base64>[\w\d_.-=]+)/$', 'auth_register_active'),
    (r'^auth/register/agreement/$', 'auth_register_agree'),
    (r'^api/', include(version_api.urls)),
)
