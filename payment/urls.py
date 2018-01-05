__author__ = 'zhaixiaoyu;'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.payment.resources import PaymentResource

version_api = Api(api_name='v0')
version_api.register(PaymentResource())

urlpatterns = patterns('yottaweb.apps.payment.views',
                       (r'^payments/$', 'payments'),
                       (r'^payments/new/$', 'new'),
                       (r'^payments/([\w\d_]+)/$', 'update'),
                       (r'^payments/usage/([\w\d_]+)/$', 'usage'),
                       (r'^api/', include(version_api.urls)),
)
