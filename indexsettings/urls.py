from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.indexsettings.resources import IndexsettingsResource

version_api = Api(api_name='v0')
version_api.register(IndexsettingsResource())

urlpatterns = patterns('yottaweb.apps.indexsettings.views',
    (r'^indexsettings/indexinfo/$', 'indexinfo'),
    (r'^indexsettings/indexinfo/new/$', 'create_index_info'),
    (r'^indexsettings/indexinfo/([\w\d_]+)/$', 'update_index_info'),
    (r'^indexsettings/indexmatchrule/$', 'indexmatchrule'),
    (r'^indexsettings/indexmatchrule/new/$', 'create_index_match_rule'),
    (r'^indexsettings/indexmatchrule/([\w\d_]+)/$', 'update_index_match_rule'),
    (r'^api/', include(version_api.urls))
)
