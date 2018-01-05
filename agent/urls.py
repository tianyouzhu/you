from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.agent.resources import AgentResource

version_api = Api(api_name='v0')
version_api.register(AgentResource())

urlpatterns = patterns('yottaweb.apps.agent.views',
    #(r'^agent/$', 'list'),
    (r'^agent/batchupdate/$', 'batch_update_config'),
    (r'^agent/steps/([\d\w_\-]+)/$', 'agent_steps'),
    (r'^agent/([\d\.\:]+)/$', 'config'),
    (r'^agent/([\d\.\:]+)/adddata/$', 'agent_add_data'),
    (r'^agent/serverheka/adddata/$', 'serverheka_add_data'),
    (r'^api/', include(version_api.urls))
)
