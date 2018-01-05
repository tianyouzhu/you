# -*- coding: utf-8 -*-
# mayangguang (ma.yanguang@yottabyte.cn)
# 2016/01/20
# Copyright 2016 Yottabyte
# file description :notice api 

from tastypie import fields
from tastypie.resources import Resource
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
import ast
import json
import requests
import os
import ConfigParser


class NoticeResource(Resource):
    class Meta:
        resource_name = 'notice'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/new/$" % self._meta.resource_name,
                self.wrap_view('new'), name="api_new"),
            url(r"^(?P<resource_name>%s)/clear/(?P<notice_id>.+)/$" % self._meta.resource_name,
                self.wrap_view('clear'), name="api_clear"),
            url(r"^(?P<resource_name>%s)/notices/$" % self._meta.resource_name,
                self.wrap_view('notices'), name="api_notices"),
            url(r"^(?P<resource_name>%s)/notice_setting/$" % self._meta.resource_name,
                self.wrap_view('notice_setting'), name="api_notices"),
        ]

    def new(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'act': 'get_unread_notice_list',
                'token': es_check['t'],
                'operator': es_check['u'],
                'account_id': es_check['i'],
            }
            res = BackendRequest.get_notice(param)
            if res['result']:
                dummy_data["status"] = '1'
                dummy_data["data"] =res 
            else:
                dummy_data["status"] = '0'
                dummy_data["msg"] =res.get('error','get new notices error!')
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "auth error!"
            dummy_data["location"] = "/auth/login/"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def notices(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'act': 'get_notice_list',
                'token': es_check['t'],
                'operator': es_check['u'],
                'account_id': es_check['i'],
            }
            res = BackendRequest.get_notice(param)
            if res['result']:
                dummy_data["status"] = '1'
                dummy_data["data"] =res.get('notices') 
            else:
                dummy_data["status"] = '0'
                dummy_data["msg"] =res.get('error','get notices error!')
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "auth error!"
            dummy_data["location"] = "/auth/login/"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def clear(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        notice_id = kwargs['notice_id'].encode('utf-8')
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'act': 'update_notice_state',
                'token': es_check['t'],
                'operator': es_check['u'],
                'account_id': es_check['i'],
                'notice_ids': notice_id,
            }
            print "######################clear param: ",param
            res = BackendRequest.get_notice(param)
            if res['result']:
                dummy_data["status"] = '1'
            else:
                dummy_data["status"] = '0'
                dummy_data["msg"] =res.get('error','clear notices error!')
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "auth error!"
            dummy_data["location"] = "/auth/login/"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def notice_setting(self, request, **kwargs):
        self.method_check(request, allowed=['get','post'])
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            real_path = os.getcwd() + '/config'
            if request.method == 'GET':
                try:
                    cf = ConfigParser.ConfigParser()
                    cf.read(real_path + "/yottaweb.ini")

                    enable = True if cf.get('notice', 'enable') == 'true' else False
                    frequency = max(int(cf.get('notice', 'frequency')),1)
                    data = {
                            'enable':enable,
                            'frequency':frequency,    
                            }
                    dummy_data["status"] = '1'
                    dummy_data["data"] =data 
                except Exception, e:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "get error!"

            elif request.method == 'POST':
                enable = request.POST.get('enable')
                frequency = request.POST.get('frequency')

                try:
                    config = ConfigParser.RawConfigParser()
                    config.read(real_path + "/yottaweb.ini")
                    config.set('notice', 'enable', enable)
                    config.set('notice', 'frequency', frequency)
                    with open(real_path + "/yottaweb.ini", 'wb') as configfile:
                        config.write(configfile)

                    dummy_data["status"] = '1'

                except Exception, e:
                    dummy_data["status"] = '0'
                    dummy_data["msg"] = "get error!"
                 
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "auth error!"
            dummy_data["location"] = "/auth/login/"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp
