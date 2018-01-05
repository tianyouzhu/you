from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.security.resources import SecurityResource

version_api = Api(api_name='v0')
version_api.register(SecurityResource())

urlpatterns = patterns('yottaweb.apps.security.views',
    (r'^security/$', 'overview'),
    (r'^security/overview/$', 'overview'),
    (r'^security/attack_details/$', 'attack_details'),
    (r'^security/config/$', 'config'),
    (r'^api/', include(version_api.urls))
)