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
from yottaweb.apps.basic.resources import ContributeErrorData
import ast
import json
import requests
import os
import ConfigParser
import logging
import time

logger = logging.getLogger("django.request")

err_data = ContributeErrorData()

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    BACKUP_HOST_list = cf.get('backup', 'host').split(",")
except Exception, e:
    BACKUP_HOST_list = ['http://localhost']
# for test
# BACKUP_HOST = 'http://192.168.1.82:10000'

BACKUP_HOST = BACKUP_HOST_list[0]
TRY_COUNT = 0

def choose_backup_host(count):
    global BACKUP_HOST
    global BACKUP_HOST_list
    logger.info("start check backup_host : %s !", BACKUP_HOST)
    _url = BACKUP_HOST + '/appnames/get'
    try:
        result = requests.get(_url, timeout=30.000)
        # print "result.status_code: ", result.status_code
    except Exception, e:
        logger.info("choose_backup_host error: %s !", BACKUP_HOST)
        BACKUP_HOST_list.remove(BACKUP_HOST)
        BACKUP_HOST_list.append(BACKUP_HOST)
        BACKUP_HOST = BACKUP_HOST_list[0]
        logger.info("choose_backup_host change to: %s !", BACKUP_HOST)
        if count < len(BACKUP_HOST_list):
            count = count + 1
            choose_backup_host(count)

choose_backup_host(0)

class BackupResource(Resource):
    class Meta:
        resource_name = 'backup'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/auto_backup/$" % self._meta.resource_name,
                self.wrap_view('auto_backup'), name="api_auto_backup"),
            url(r"^(?P<resource_name>%s)/strategy/list/$" % self._meta.resource_name,
                self.wrap_view('strategy_list'), name="api_auto_backup"),
            url(r"^(?P<resource_name>%s)/strategy/new/$" % self._meta.resource_name,
                self.wrap_view('strategy_new'), name="api_auto_backup"),
            url(r"^(?P<resource_name>%s)/strategy/del/$" % self._meta.resource_name,
                self.wrap_view('strategy_del'), name="api_auto_backup"),
            url(r"^(?P<resource_name>%s)/recoverable/list/$" % self._meta.resource_name,
                self.wrap_view('recoverable_list'), name="api_auto_backup"),
            url(r"^(?P<resource_name>%s)/recoverable/submit/$" % self._meta.resource_name,
                self.wrap_view('recoverable_submit'), name="api_auto_backup"),
            url(r"^(?P<resource_name>%s)/recoverable/stop/$" % self._meta.resource_name,
                self.wrap_view('recoverable_stop'), name="api_auto_backup"),
            url(r"^(?P<resource_name>%s)/manual_backup/$" % self._meta.resource_name,
                self.wrap_view('manual_backup'), name="api_manual_backup"),
            url(r"^(?P<resource_name>%s)/manual_restore/$" % self._meta.resource_name,
                self.wrap_view('manual_restore'), name="api_manual_restore"),
            url(r"^(?P<resource_name>%s)/list/$" % self._meta.resource_name,
                self.wrap_view('list'), name="api_list"),
            url(r"^(?P<resource_name>%s)/set_bandwidth/$" % self._meta.resource_name,
                self.wrap_view('set_bandwidth'), name="api_set_bandwidth"),
            url(r"^(?P<resource_name>%s)/get_setting/$" % self._meta.resource_name,
                self.wrap_view('get_setting'), name="api_get_setting"),
            url(r"^(?P<resource_name>%s)/get_appname/$" % self._meta.resource_name,
                self.wrap_view('get_appname'), name="api_get_appname"),
            url(r"^(?P<resource_name>%s)/get_backup_strategy/$" % self._meta.resource_name,
                self.wrap_view('get_backup_strategy'), name="api_get_backup_strategy"),
            url(r"^(?P<resource_name>%s)/get_ttls/$" % self._meta.resource_name,
                self.wrap_view('get_ttls'), name="api_get_ttls"),
            url(r"^(?P<resource_name>%s)/get_ttl_bk_times/$" % self._meta.resource_name,
                self.wrap_view('get_ttl_bk_times'), name="api_get_ttl_bk_times"),
            url(r"^(?P<resource_name>%s)/update_ttls/$" % self._meta.resource_name,
                self.wrap_view('update_ttls'), name="api_update_ttls"),


        ]

    def auto_backup(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        index = request.POST.get('index')
        exclude = request.POST.get('exception')
        ttl = request.POST.get('ttl')
        start = request.POST.get('start')

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            url = BACKUP_HOST + '/auto'
            # print "###############url: ", url
            data = {
                "backup": {
                    "index": json.loads(index),
                    "exclude": json.loads(exclude),
                    "ttl": int(ttl),
                    "start": int(start),
                }
            }
            data = json.dumps(data)
            # print "###############data: ", data

            result = requests.post(url, data=data)
            # print "result.status_code: ", result.status_code
            if result.status_code == 200:
                res = result.json()
                # print "res: ", res
                if res['result']:
                    dummy_data["status"] = 1
                else:
                    dummy_data = err_data.build_error(res)
            else:
                dummy_data = err_data.build_error({}, "auto backup request error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def strategy_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            _url = BACKUP_HOST + '/appnames/get'
            try:
                result = requests.get(_url, timeout=120.000)
                logger.info("get_backup_appnames result: %s", result.url)
                # print "result.status_code: ", result.status_code
                if result.status_code == 200:
                    res = result.json()
                    logger.info("get_backup_appnames result: %s", res)
                    # print "res: ", res
                    if res['rc'] == 0:
                        dummy_data["status"] = "1"
                        dummy_data["lists"] = res.get("appnames", [])
                    else:
                        dummy_data = err_data.build_error(res)
                else:
                    logger.info("get_backup_appnames error")
                    dummy_data = err_data.build_error({}, "get_backup_appnames error!")
            except Exception, e:
                logger.info("get_backup_appnames error!")
                dummy_data = err_data.build_error({}, "auto backup request error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            choose_backup_host(0)
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def strategy_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_data = request.POST
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            _url = BACKUP_HOST + '/appnames/add?appnames=' + post_data.get("appname", "")
            try:
                result = requests.post(_url, timeout=120.000)
                logger.info("add_backup_appname: %s", result.url)
                # print "result.status_code: ", result.status_code
                if result.status_code == 200:
                    res = result.json()
                    logger.info("add_backup_appnames result: %s", res)
                    # print "res: ", res
                    if res['rc'] == 0:
                        _list_url = BACKUP_HOST + '/appnames/get'
                        _list_result = requests.get(_list_url, timeout=120.000)
                        dummy_data["status"] = "1"
                        if _list_result.status_code == 200:
                            _list_res = _list_result.json()
                            dummy_data["lists"] = _list_res.get("appnames", [])
                        else:
                            dummy_data["lists"] = []
                    else:
                        dummy_data = err_data.build_error({}, res.get("error", "add_backup_appnames error!"))
                else:
                    logger.info("add_backup_appnames error")
                    dummy_data = err_data.build_error({}, "add_backup_appnames error!")
            except Exception, e:
                logger.info("add_backup_appnames error!")
                dummy_data = err_data.build_error({}, "add backup request error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            choose_backup_host(0)
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def strategy_del(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_data = request.POST
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            _url = BACKUP_HOST + '/appnames/delete?appnames=' + post_data.get("appname", "")
            try:
                result = requests.delete(_url, timeout=120.000)
                logger.info("delete_backup_appname: %s", result.url)
                # print "result.status_code: ", result.status_code
                if result.status_code == 200:
                    res = result.json()
                    logger.info("delete_backup_appnames result: %s", res)
                    # print "res: ", res
                    if res['rc'] == 0:
                        _list_url = BACKUP_HOST + '/appnames/get'
                        _list_result = requests.get(_list_url, timeout=120.000)
                        dummy_data["status"] = "1"
                        if _list_result.status_code == 200:
                            _list_res = _list_result.json()
                            dummy_data["lists"] = _list_res.get("appnames", [])
                        else:
                            dummy_data["lists"] = []
                    else:
                        dummy_data = err_data.build_error({}, res.get("error", "delete_backup_appnames error!"))
                else:
                    logger.info("delete_backup_appnames error")
                    dummy_data = err_data.build_error({}, "delete_backup_appnames error!")
            except Exception, e:
                logger.info("delete_backup_appnames error!")
                dummy_data = err_data.build_error({}, "delete backup request error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            choose_backup_host(0)
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def recoverable_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        get_data = request.GET
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            _url = BACKUP_HOST + '/recoverables/get'
            try:
                params = {
                    "startdate": get_data.get("from"),
                    "enddate": get_data.get("to")
                }
                result = requests.get(_url, params=dict(params), timeout=120.000)
                logger.info("get_recoverables: %s", result.url)
                if result.status_code == 200:
                    res = result.json()
                    logger.info("get_recoverables result: %s", res)
                    # print "res: ", res
                    if res['rc'] == 0:
                        dummy_data["status"] = "1"
                        dummy_data["lists"] = res.get("recoverables", [])
                    else:
                        dummy_data = err_data.build_error(res)
                else:
                    logger.info("get_recoverables error")
                    dummy_data = err_data.build_error({}, "get_recoverables error!")
            except Exception, e:
                logger.info("get_recoverables error!")
                dummy_data = err_data.build_error({}, "auto backup request error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def recoverable_submit(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_data = request.POST
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            _url = BACKUP_HOST + '/recoverables/submit?appname=' + post_data.get("appname", "") + "&date="+post_data.get("date", "")
            try:
                result = requests.post(_url, timeout=120.000)
                logger.info("submit_backup_appname: %s", result.url)
                # print "result.status_code: ", result.status_code
                if result.status_code == 200:
                    res = result.json()
                    logger.info("submit_backup_appname result: %s", res)
                    # print "res: ", res
                    if res['rc'] == 0:
                        _list_url = BACKUP_HOST + '/recoverables/get'
                        params = {
                            "startdate": post_data.get("from"),
                            "enddate": post_data.get("to")
                        }
                        _list_result = requests.get(_list_url, params=dict(params), timeout=120.000)
                        logger.info("get_recoverables: %s", _list_result.url)
                        if _list_result.status_code == 200:
                            _list_res = _list_result.json()
                            logger.info("get_recoverables result: %s", _list_res)
                            # print "res: ", res
                            if _list_res['rc'] == 0:
                                dummy_data["lists"] = _list_res.get("recoverables", [])
                            else:
                                dummy_data["lists"] = []
                        dummy_data["status"] = "1"
                    else:
                        dummy_data = err_data.build_error({}, res.get("error", "submit_backup_appname error!"))
                else:
                    logger.info("submit_backup_appname error")
                    dummy_data = err_data.build_error({}, "submit_backup_appname error!")
            except Exception, e:
                logger.info("submit_backup_appname error!")
                dummy_data = err_data.build_error({}, "add backup request error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def recoverable_stop(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_data = request.POST
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            _url = BACKUP_HOST + '/recoverables/stop?appname=' + post_data.get("appname", "") + "&date="+post_data.get("date", "")
            try:
                result = requests.delete(_url, timeout=120.000)
                logger.info("stop_recover: %s", result.url)
                if result.status_code == 200:
                    res = result.json()
                    logger.info("stop_recover result: %s", res)
                    if res['rc'] == 0:
                        _list_url = BACKUP_HOST + '/recoverables/get'
                        params = {
                            "startdate": post_data.get("from"),
                            "enddate": post_data.get("to")
                        }
                        _list_result = requests.get(_list_url, params=dict(params), timeout=120.000)
                        if _list_result.status_code == 200:
                            _list_res = _list_result.json()
                            logger.info("get_recoverables result: %s", _list_res)
                            if _list_res['rc'] == 0:
                                dummy_data["lists"] = _list_res.get("recoverables", [])
                            else:
                                dummy_data["lists"] = []
                        dummy_data["status"] = "1"
                    else:
                        dummy_data = err_data.build_error({}, res.get("error", "stop_recover error!"))
                else:
                    logger.info("stop_recover error")
                    dummy_data = err_data.build_error({}, "stop_recover error!")
            except Exception, e:
                logger.info("stop_recover error!")
                dummy_data = err_data.build_error({}, "stop_recover error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def manual_backup(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        pattern = request.POST.get('pattern')
        types = request.POST.get('types')

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            url = BACKUP_HOST + '/backup'
            # print "###############url: ", url
            data = {
                "index": {
                    "pattern": pattern,
                    "types": types
                }
            }
            data = json.dumps(data)

            # print "##########backup data: ",data
            result = requests.post(url, data=data)
            # print "result.status_code: ", result.status_code
            if result.status_code == 200:
                res = result.json()
                # print "########################res: ", res
                if res['result']:
                    dummy_data["status"] = 1
                    dummy_data["message"] = res.get('message') or ''
                else:
                    dummy_data = err_data.build_error(res)
            else:
                dummy_data = err_data.build_error({}, "backup request error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def manual_restore(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        pattern = request.POST.get('pattern')
        types = request.POST.get('types')

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            url = BACKUP_HOST + '/restore'
            # print "###############url: ", url
            data = {
                "index": {
                    "pattern": pattern,
                    "types": types
                }
            }
            # print "############### restore query data: ", data
            data = json.dumps(data)

            result = requests.post(url, data=data)
            # print "result.status_code: ", result.status_code
            if result.status_code == 200:
                res = result.json()
                # print "res: ", res
                if res['result']:
                    dummy_data["status"] = 1
                    dummy_data["message"] = res.get('message') or ''
                else:
                    dummy_data = err_data.build_error(res)
            else:
                dummy_data = err_data.build_error({}, "restore request error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        search = request.GET.get('search')
        page = request.GET.get('page')
        limit = request.GET.get('limit')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            url = BACKUP_HOST + '/query/indextype?action=query&condition=%s&pageno=%s&limit=%s'%(search,page,limit)
            try:
                result = requests.get(url)
            except Exception, e:
                result = None
            if result and result.status_code == 200:
                res = result.json()
                # print "res: ", res
                if res['result']:
                    dummy_data["status"] = 1
                    dummy_data["data"] = res.get('match')
                    dummy_data["total"] = res.get('total')
                else:
                    dummy_data = err_data.build_error(res)
            else:
                dummy_data["status"] = 0
                dummy_data["msg"] = "get request error!"
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def set_bandwidth(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        max = request.POST.get('max')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            url = BACKUP_HOST + '/setting'
            # print "###############url: ", url
            data = {
                "speed": {
                    "max": max,
                }
            }
            # print "###############data: ", data
            data = json.dumps(data)

            result = requests.post(url, data=data)
            # print "result.status_code: ", result.status_code
            if result.status_code == 200:
                res = result.json()
                # print "res: ", res
                if res['result']:
                    dummy_data["status"] = 1
                else:
                    dummy_data = err_data.build_error(res)
            else:
                dummy_data = err_data.build_error({},  "backup request error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def get_setting(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            url = BACKUP_HOST + '/setting'
            # print "###############url: ", url
            result = requests.get(url)
            # print "result.status_code: ", result.status_code
            if result.status_code == 200:
                res = result.json()
                # print "################ 260 res: ", res
                if not res.get('result'):
                    dummy_data["status"] = 1
                    dummy_data["data"] = res
                else:
                    dummy_data = err_data.build_error(res)
            else:
                dummy_data = err_data.build_error({}, "setting request error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def get_appname(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        pattern = request.GET.get('pattern')
        # print "############### pattern: ", pattern

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            url = BACKUP_HOST + '/appname/' + pattern
            # print "############### get_appname: ", url
            result = requests.get(url)
            # print "result.status_code: ", result.status_code
            if result.status_code == 200:
                res = result.json()
                # print "################ 260 res: ", res
                if res.get('result'):
                    dummy_data["status"] = 1
                    dummy_data["data"] = res.get('appname')
                else:
                    dummy_data = err_data.build_error(res)
            else:
                dummy_data = err_data.build_error({}, "setting request error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def get_backup_strategy(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            url = BACKUP_HOST + '/auto'
            # print "###############url: ", url

            result = requests.get(url)
            # print "result.status_code: ", result.status_code
            if result.status_code == 200:
                res = result.json()
                # print "res: ", res
                data = {
                        "status":1,
                        "data":res
                        }
                dummy_data = data
            else:
                dummy_data = err_data.build_error({}, "get backup strategy error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def get_ttls(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_appname_ttl(param)
            # print "#################get_appname_ttl: ",res
            if res["result"]:
                data = {
                        "status":1,
                        "data":res.get('appnameTTL',[])
                        }
                dummy_data = data
            else:
                dummy_data = err_data.build_error({}, "get appname ttls bk times error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def get_ttl_bk_times(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_ttl_bk_times(param)
            # print "#################get_ttl_bk_times: ",res
            if res["result"]:
                data = {
                        "status":1,
                        "data":res.get('ttl',[])
                        }
                dummy_data = data
            else:
                dummy_data = err_data.build_error({}, "get appname ttls bk times error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def update_ttls(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        ttls = json.loads(request.POST.get('ttls'))
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            tmpList = []
            ttls.pop()
            for ttl in ttls:
                tmpStr = str(ttl.get('pattern','')) + ':' + str(ttl.get('ttl',''))
                tmpList.append(tmpStr)
            ttl = ",".join(tmpList)
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'ttl':ttl
            }
            # print "#################update_ttls param: ",param
            res = BackendRequest.update_ttls(param)
            # print "#################update_ttls: ",res
            if res["result"]:
                data = {
                        "status":1,
                        }
                dummy_data = data
            else:
                dummy_data = err_data.build_error({}, "update_ttls error!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp
