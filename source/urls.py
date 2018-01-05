__author__ = 'wangqiushi; yangguang;'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.source.resources import SourceResource

version_api = Api(api_name='v0')
version_api.register(SourceResource())

urlpatterns = patterns('yottaweb.apps.source.views',
    (r'^sources/input/agent/$', 'source_input_agent'),
    (r'^sources/input/serverheka/$', 'source_input_server_heka'),
    (r'^sources/input/example/$', 'source_input_example'),
    (r'^sources/input/os/$', 'source_input_os'),
    (r'^sources/input/ssa/$', 'source_input_ssa'),
    (r'^sources/detail/$', 'source_detail'),
    (r'^sources/input/([\d\w_.-]+)/$', 'source_input_linux'),
    (r'^sources/sourcegroups/$', 'source_sourcegroups'),
    (r'^sources/sourcegroups/new/$', 'source_sourcegroups_new'),
    (r'^sources/sourcegroups/([\d\w_.-]+)/$', 'source_sourcegroups_update'),
    (r'^api/', include(version_api.urls)),
)
