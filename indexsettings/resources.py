# -*- coding: utf-8 -*-
# daibin (ma.yanguang@yottabyte.cn)
# 2017/02/22
# Copyright 2016 Yottabyte
# file description : index settings api

from tastypie import fields
from tastypie.resources import Resource
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.basic.resources import ContributeErrorData
import ast
import json
import requests
import os
import ConfigParser
__author__ = 'daibin'
err_data = ContributeErrorData()

class IndexsettingsResource(Resource):
    class Meta:
        resource_name = 'indexsettings'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/get_index_info_list/$" % self._meta.resource_name,
                self.wrap_view('get_index_info_list'), name="api_indexsettings"),
            url(r"^(?P<resource_name>%s)/create_index_info/$" % self._meta.resource_name,
                self.wrap_view('create_index_info'), name="api_indexsettings"),
            url(r"^(?P<resource_name>%s)/update_index_info/(?P<id>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('update_index_info'), name="api_indexsettings"),
            url(r"^(?P<resource_name>%s)/delete_index_info/(?P<id>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('delete_index_info'), name="api_indexsettings"),
            url(r"^(?P<resource_name>%s)/get_index_match_rule_list/$" % self._meta.resource_name,
                self.wrap_view('get_index_match_rule_list'), name="api_indexsettings"),
            url(r"^(?P<resource_name>%s)/create_index_match_rule/$" % self._meta.resource_name,
                self.wrap_view('create_index_match_rule'), name="api_indexsettings"),
            url(r"^(?P<resource_name>%s)/update_index_match_rule/(?P<id>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('update_index_match_rule'), name="api_indexsettings"),
            url(r"^(?P<resource_name>%s)/delete_index_match_rule/(?P<id>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('delete_index_match_rule'), name="api_indexsettings"),
        ]

    def get_index_info_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
            }
            res = BackendRequest.get_index_info_list(param)
            print res
            if res["result"]:
                if res["index_infos"]:
                    dummy_data["status"] = "1"
                    dummy_data["list"] = res["index_infos"]
            else:
                dummy_data = err_data.build_error_new(res)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        response_data = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, response_data)

    def create_index_info(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        req_data = request.POST
        post_data = {
            'name': req_data.get('name', ''),
            'alias': req_data.get('alias', ''),
            'description': req_data.get('description', ''),
            'expired_time': req_data.get('expired_time', ''),
            'rotation_period': req_data.get('rotation_period', ''),
            'disabled': req_data.get('disabled', 'false')
        }
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'name': post_data['name'],
                'alias': post_data['alias'],
                'description': post_data['description'],
                'expired_time': post_data['expired_time'],
                'rotation_period': post_data['rotation_period'],
                'disabled': post_data['disabled']
            }
            res = BackendRequest.create_index_info(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["location"] = "/indexsettings/indexinfo/"
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def update_index_info(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        index_info_id = kwargs['id']
        req_data = request.POST
        post_data = {
            'name': req_data.get('name', ''),
            'alias': req_data.get('alias', ''),
            'description': req_data.get('description', ''),
            'expired_time': req_data.get('expired_time', ''),
            'rotation_period': req_data.get('rotation_period', ''),
            'disabled': req_data.get('disabled', 'false')
        }
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'id': index_info_id,
                'token': es_check['t'],
                'operator': es_check['u'],
                'name': post_data['name'],
                'alias': post_data['alias'],
                'description': post_data['description'],
                'expired_time': post_data['expired_time'],
                'rotation_period': post_data['rotation_period'],
                'disabled': post_data['disabled']
            }
            res = BackendRequest.update_index_info(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["location"] = "/indexsettings/indexinfo/"
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def delete_index_info(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        index_info_id = kwargs['id']

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            res = BackendRequest.delete_index_info({
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': index_info_id
            })
            if res['result']:
                dummy_data["status"] = "1"
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def get_index_match_rule_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
            }
            res_info = BackendRequest.get_index_info_list(param)
            res_index_map = {}
            if res_info['result']:
                if res_info["index_infos"]:
                    res_info_list = res_info["index_infos"]
                    print res_info_list
                    for item in res_info_list:
                        res_index_map[item['id']] = item['name']

            res = BackendRequest.get_index_match_rule_list(param)
            if res["result"]:
                if res["rules"]:
                    dummy_data["status"] = "1"
                    dummy_data["list"] = []
                    for item in res["rules"]:
                        item['index_name'] = res_index_map.get(item['index_id'], '')
                        dummy_data["list"].append(item)
            else:
                dummy_data = err_data.build_error_new(res)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        response_data = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, response_data)

    def create_index_match_rule(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        req_data = request.POST
        post_data = {
            'index_id': req_data.get('index_id', ''),
            'appname': req_data.get('appname', ''),
            'description': req_data.get('description', ''),
            'tag': req_data.get('tag', ''),
            'raw_message_regex': req_data.get('raw_message_regex', '')
        }
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'index_id': req_data.get('index_id', ''),
                'appname': req_data.get('appname', ''),
                'description': req_data.get('description', ''),
                'tag': req_data.get('tag', ''),
                'raw_message_regex': req_data.get('raw_message_regex', '')
            }
            res = BackendRequest.create_index_match_rule(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["location"] = "/indexsettings/indexmatchrule/"
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def update_index_match_rule(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        index_match_rule_id = kwargs['id']
        req_data = request.POST
        post_data = {
            'index_id': req_data.get('index_id', ''),
            'appname': req_data.get('appname', ''),
            'description': req_data.get('description', ''),
            'tag': req_data.get('tag', ''),
            'raw_message_regex': req_data.get('raw_message_regex', '')
        }
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'id': index_match_rule_id,
                'token': es_check['t'],
                'operator': es_check['u'],
                'index_id': post_data['index_id'],
                'appname': post_data['appname'],
                'description': post_data['description'],
                'tag': post_data['tag'],
                'raw_message_regex': post_data['raw_message_regex']
            }
            res = BackendRequest.update_index_match_rule(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["location"] = "/indexsettings/indexmatchrule/"
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def delete_index_match_rule(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        index_match_rule_id = kwargs['id']

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            res = BackendRequest.delete_index_match_rule({
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': index_match_rule_id
            })
            if res['result']:
                dummy_data["status"] = "1"
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp
