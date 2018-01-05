from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.backup.resources import BackupResource

version_api = Api(api_name='v0')
version_api.register(BackupResource())

urlpatterns = patterns('yottaweb.apps.backup.views',
    (r'^backup/$', 'backup'),
    (r'^api/', include(version_api.urls))
)