# wangqiushi,mayangguang (wang.qiushi@yottabyte.cn, ma.yangguang@yottabyte.cn)
# 2014/07/30
# Copyright 2014 Yottabyte
# file description : urls.py.
__author__ = 'wangqiushi'
from django.conf.urls import patterns, url, include
from tastypie.api import Api
from yottaweb.apps.account.resources import AccountResource

version_api = Api(api_name='v0')
version_api.register(AccountResource())

urlpatterns = patterns('yottaweb.apps.account.views',
                       (r'^account/users/$', 'users'),
                       (r'^account/usergroups/$', 'usergroups'),
                       (r'^account/usergroups/new/$', 'usergroups_new'),
                       (r'^account/usergroups/([\d\w_]+)/$', 'usergroups_update'),
                       (r'^account/usage/$', 'usage'),
                       (r'^account/users/new/$', 'users_new'),
                       (r'^account/users/([\d\w_]+)/$', 'update'),
                       (r'^account/roles/$', 'roles'),
                       (r'^account/roles/new/$', 'roles_new'),
                       (r'^account/roles/([\d\w_]+)/$', 'roles_update'),
                       (r'^account/roles/assign/([\d\w_]+)/$', 'roles_assign'),
                       (r'^account/roles/copy/([\d\w_]+)/$', 'roles_copy'),
                       (r'^account/resourcegroups/$', 'resourcegroups'),
                       (r'^account/resourcegroups/new/$', 'resourcegroups_new'),
                       (r'^account/resourcegroups/([\d\w_]+)/$', 'resourcegroups_update'),
                       (r'^api/', include(version_api.urls)),
)
