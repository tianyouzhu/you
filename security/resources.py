# -*- coding: utf-8 -*-
# mayangguang (ma.yanguang@yottabyte.cn)
# 2015/03/25
# Copyright 2015 Yottabyte
# file description : security api

from tastypie import fields
from tastypie.resources import Resource
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
import ast
import json

# We need a generic object to shove data in/get data from.
# Riak generally just tosses around dictionaries, so we'll lightly
# wrap that.
class RiakObject(object):
    def __init__(self, initial=None):
        self.__dict__['_data'] = {}

        if hasattr(initial, 'items'):
            self.__dict__['_data'] = initial

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data


class SecurityResource(Resource):
    class Meta:
        resource_name = 'security'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            # url(r"^(?P<resource_name>%s)/$" % (self._meta.resource_name),
            #     self.wrap_view('dashboard'),
            #     name="api_dashboard"),

        ]

    # def dashboard(self, request, **kwargs):
    #     self.method_check(request, allowed=['get', 'post'])
    #     # print '############request.method', request.method
    #     dummy_data = {}
    #     my_auth = MyBasicAuthentication()
    #     es_check = my_auth.is_authenticated(request, **kwargs)
    #     if es_check:
    #         if request.method == 'GET':
    #             dummy_data = self.get_dashboard_data(es_check)
    #         else:
    #             dummy_data = self.update_dashboard_data(request, es_check)
    #     else:
    #         dummy_data["status"] = "0"
    #         dummy_data["msg"] = "get alert error!"
    #
    #     bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
    #     response_data = bundle
    #     resp = self.create_response(request, response_data)
    #     return resp


