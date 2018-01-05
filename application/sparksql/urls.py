from django.conf.urls import patterns, include
from tastypie.api import Api
from yottaweb.apps.application.sparksql.resources import SparksqlResource

version_api = Api(api_name='v0')
version_api.register(SparksqlResource())

urlpatterns = patterns('yottaweb.apps.application.sparksql.views',
    (r'^app/sparksql/$', 'index'),
    (r'^app/sparksql/referer/$', 'referer'),
    (r'^app/sparksql/resource/$', 'resource'),
    (r'^app/sparksql/visitor/$', 'visitor'),
    (r'^app/sparksql/service/$', 'service'),
    (r'^api/', include(version_api.urls))
)
