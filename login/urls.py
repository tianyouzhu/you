__author__ = 'wangqiushi'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.login.resources import LoginResource

version_api = Api(api_name='v0')
version_api.register(LoginResource())

urlpatterns = patterns('yottaweb.apps.login.views',
    (r'^auth/passwordReset/$', 'auth_reset'),
    (r'^auth/password/(?P<for_md5>[\w\d_.-]+)/(?P<for_base64>[\w\d_.-=]+)/$', 'auth_password'),
    (r'^$', 'login'),
    (r'^auth/$', 'login'),
    (r'^auth/login/$', 'login'),
    (r'^auth/logout/$', 'logout'),
    (r'^api/', include(version_api.urls)),
)