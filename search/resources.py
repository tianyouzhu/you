# -*- coding: utf-8 -*-
# wangqiushi (wang.qiushi@yottabyte.cn)
# wu.ranbo (wu.ranbo@yottabyte.cn)
# 2014/07/22
# Copyright 2014 Yottabyte
# file description : resources.py
from tastypie import fields
from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.variable.resources import MyVariable
from yottaweb.apps.search.models import History

import os
import json
import ast
import re
import time
import logging
import csv
import ConfigParser
import random
import uuid
import sys
import math
import copy
from sets import Set

audit_logger = logging.getLogger('yottaweb.audit')
_logger = logging.getLogger('django.request')

__author__ = 'wangqiushi'
err_data = ContributeErrorData()

sys.setrecursionlimit(100000)


class SearchResource(Resource):
    sid = fields.CharField(attribute='sid')
    source = fields.DictField(attribute='source')

    class Meta:
        resource_name = 'search'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/new/$" % self._meta.resource_name, self.wrap_view('_search'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/history/$" % self._meta.resource_name, self.wrap_view('_search_history'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/logtail/$" % self._meta.resource_name, self.wrap_view('_search_logtail'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/submit/$" % self._meta.resource_name, self.wrap_view('_search_submit'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/submit/download/$" % self._meta.resource_name, self.wrap_view('_search_download_submit'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/submit/offlinetask/$" % self._meta.resource_name, self.wrap_view('_search_offlinetask_submit'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/fetch/$" % self._meta.resource_name, self.wrap_view('_search_fetch'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/fetch/paged/$" % self._meta.resource_name, self.wrap_view('_search_fetch_paged'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/fetch/cancel/$" % self._meta.resource_name, self.wrap_view('_search_cancel'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/fetch/pause/$" % self._meta.resource_name, self.wrap_view('_search_pause'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/fetch/resume/$" % self._meta.resource_name, self.wrap_view('_search_resume'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/fetch/heartbeat/$" % self._meta.resource_name, self.wrap_view('_search_heartbeat'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/fetch/fields/$" % self._meta.resource_name, self.wrap_view('_search_top_fields'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/fetch/allfields/$" % self._meta.resource_name, self.wrap_view('_search_all_fields'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/fetch/stats/$" % self._meta.resource_name, self.wrap_view('_search_stats'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/fetch/stats/events/$" % self._meta.resource_name, self.wrap_view('_search_stats_events'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/onlyfields/$" % self._meta.resource_name, self.wrap_view('_only_fields'),
                name="api_only_fields"),
            url(r"^(?P<resource_name>%s)/onlytimeline/$" % self._meta.resource_name, self.wrap_view('_only_timeline'),
                name="api_only_timeline"),
            url(r"^(?P<resource_name>%s)/fields/$" % self._meta.resource_name, self.wrap_view('_fields'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/fields/search/$" % self._meta.resource_name, self.wrap_view('_fields_search'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/events/$" % self._meta.resource_name, self.wrap_view('_events'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/events/table/$" % self._meta.resource_name, self.wrap_view('_events_table'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/sheets/$" % self._meta.resource_name, self.wrap_view('_sheets'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/new/grid/$" % self._meta.resource_name, self.wrap_view('_events_grid'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/action/$" % self._meta.resource_name, self.wrap_view('_search_action'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/statis/$" % self._meta.resource_name, self.wrap_view('_search_statis'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/newstatis/$" % self._meta.resource_name, self.wrap_view('_search_newstatis'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/drilldown/query/$" % self._meta.resource_name, self.wrap_view('_search_drilldown_query'),
                name="api_search"),
            url(r"^(?P<resource_name>%s)/statis/eventscount/$" % self._meta.resource_name,
                self.wrap_view('_search_events_count'), name="api_search"),
            url(r"^(?P<resource_name>%s)/statis/fieldcategory/$" % self._meta.resource_name,
                self.wrap_view('_search_field_category'), name="api_search"),
            url(r"^(?P<resource_name>%s)/statis/fieldvalue/$" % self._meta.resource_name,
                self.wrap_view('_search_field_value'), name="api_search"),
            url(r"^(?P<resource_name>%s)/statis/fieldpercent/$" % self._meta.resource_name,
                self.wrap_view('_search_field_percent'), name="api_search"),
            url(r"^(?P<resource_name>%s)/statis/multi/$" % self._meta.resource_name,
                self.wrap_view('_search_field_multi'), name="api_search"),
            url(r"^(?P<resource_name>%s)/download/$" % self._meta.resource_name,
                self.wrap_view('_search_download'), name="api_search"),
            url(r"^(?P<resource_name>%s)/events/table/download/$" % self._meta.resource_name,
                self.wrap_view('_search_spl_download'), name="api_search"),
            url(r"^(?P<resource_name>%s)/context/$" % self._meta.resource_name,
                self.wrap_view('_search_context'), name="api_search"),
            url(r"^(?P<resource_name>%s)/permit/batch/$" % self._meta.resource_name,
                self.wrap_view('search_permit_batch'), name="api_search")
        ]

    def _search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            resdata = self._get_search(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_history(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        dummy_data = {}
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            req_data = request.GET
            query_data = self._get_history(auth_result, req_data.get('size', 20), **kwargs)
            if not query_data:
                data = err_data.build_error({}, "Get history error!")
                dummy_data = data
            else:
                dummy_data = {
                    "list": query_data,
                    "status": "1"
                }
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _get_history(self, auth_result, size, **kwargs):
        token = auth_result["t"]
        user_id = auth_result["i"]
        try:
            history_list_origin = History.objects.filter(user_id=user_id, token=token).order_by('-id')[:size]
            history_list = [item.query for item in history_list_origin]
            # history_list = list(history_list)
        except Exception:
            return False
        return history_list

    def _add_history(self, user_id, token, query):
        try:
            history_list_origin = History.objects.filter(user_id=user_id, token=token)
            history_list = [item.query for item in history_list_origin]
            if not query in history_list:
                if len(history_list) >= 100:
                    history_list = History.objects.filter(user_id=user_id, token=token)[len(history_list)-100:100]
                    _id = history_list[0].id
                    History.objects.filter(user_id=user_id, token=token, id__lt=_id).delete()
                history = History(user_id=user_id, token=token, query=query)
                history.save()
        except Exception, e:
            _logger.error("Add search history error!", e)

    def _sheets(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            is_param = self.checkParam(request, **kwargs)
            req_data = request.GET
            param = {
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "filter_field": is_param["filters"],
                "field": req_data.get("field", ""),
                "source_group": is_param["source_group"],
                "size": is_param.get("size", 20)
            }
            queryfilters = req_data.get("queryfilters")
            if queryfilters:
                param["queryfilters"] = queryfilters
            res = BackendRequest.search(param)
            try:
                if res["rc"] == 0:
                    if res["result"]["sheets"]:
                        type, rst, hits = self._build_events_new(res)
                        dummy_data["table"] = {
                            "head": res["result"]["sheets"].get("_field_infos_", []),
                            "body": rst,
                            "total": res["result"]["sheets"].get("total", 0)
                        }
                    dummy_data["status"] = "1"
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""))
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                _logger.error("search error:", e)
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_stats(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            req_data = request.GET
            sid = req_data.get('sid', '')
            param = {
                "sid": sid,
                "category": "sheets",
                "token": auth_result["t"],
                "owner_id": auth_result["i"],
                "operator": auth_result["u"],
                "page": 0,
                "size": req_data["size"]
            }
            res = BackendRequest.search_preview(param)
            try:
                if res["rc"] == 0:
                    stats_param = {
                        "showType": req_data.get("showType", ""),
                        "cur_ByField": req_data.get("cur_ByField", ""),
                        "cur_ByFields": req_data.get("cur_ByFields", ""),
                        "cur_YField": req_data.get("cur_YField", ""),
                        "cur_YFields": req_data.get("cur_YFields", ""),
                        "cur_XField": req_data.get("cur_XField", ""),
                        "cur_FromField": req_data.get("cur_FromField", ""),
                        "cur_ToField": req_data.get("cur_ToField", ""),
                        "cur_FromLongitudeField": req_data.get("cur_FromLongitudeField", ""),
                        "cur_FromLatitudeField": req_data.get("cur_FromLatitudeField", ""),
                        "cur_ToLongitudeField": req_data.get("cur_ToLongitudeField", ""),
                        "cur_ToLatitudeField": req_data.get("cur_ToLatitudeField", ""),
                        "cur_WeightField": req_data.get("cur_WeightField", ""),
                        "cur_LowerField": req_data.get("cur_LowerField", ""),
                        "cur_UpperField": req_data.get("cur_UpperField", ""),
                        "cur_OutlierField": req_data.get("cur_OutlierField", "")
                    }
                    if res["result"]["sheets"]:
                        type, rst, hits = self._build_events_new(res)
                        stats_result = self._build_stats_new(rst, stats_param)
                    else:
                        stats_result = {}
                    dummy_data["uniq"] = stats_result
                    dummy_data["status"] = "1"
                    dummy_data["job_status"] = res["job_status"]
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                _logger.error("search error:", e)
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_logtail(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            is_param = self.checkParam(request, **kwargs)
            req_data = request.GET
            param = {
                "query": is_param["query"],
                "token": auth_result["t"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "operator": auth_result["u"],
                "interval": req_data.get("interval", ""),
                "order": is_param["order"],
                "size": is_param["size"],
                "sid": is_param.get("sid", ""),
                "page": int(is_param["page"]) - 1,
                "filter_field": is_param["filters"],
                "category": "events",
                "field": req_data.get("field", ""),
                "usetable": "true",
                "source_group": is_param["source_group"],
            }
            res = BackendRequest.search_logtail(param)
            try:
                if res["rc"] == 0:
                    self._add_history(auth_result["i"], auth_result["t"], is_param["query"])
                    dummy_data["status"] = "1"
                    dummy_data["sid"] = res.get("sid", "default")
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                _logger.error("search error:", e)
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_submit(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            is_param = self.checkParam(request, **kwargs)
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "submit",
                "module": "search",
                "user_name": auth_result["u"],
                "user_id": auth_result["i"],
                "domain": auth_result["d"],
                "query": is_param["query"],
                "result": "success"
            }
            req_data = request.GET
            param = {
                "query": is_param["query"],
                "token": auth_result["t"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "operator": auth_result["u"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "size": is_param["size"],
                "sid": is_param.get("sid", ""),
                "page": int(is_param["page"]) - 1,
                "filter_field": is_param["filters"],
                "category": "search",
                "task_name": "search_task_" + time.strftime("%Y%m%d%H%M%S", time.localtime()),
                "field": req_data.get("field", ""),
                "usetable": "true",
                "extra_info": "",
                "source_group": is_param["source_group"],
            }
            _saved_param = {
                "query": is_param["query"],
                "time_range": param["time_range"],
                "filter_field": param["filter_field"],
                "source_group": param["source_group"]
            }
            param["extra_info"] = json.dumps(_saved_param)
            queryfilters = req_data.get("queryfilters")
            if queryfilters:
                param["queryfilters"] = queryfilters
            res = BackendRequest.search_submit(param)
            try:
                if res["rc"] == 0:
                    self._add_history(auth_result["i"], auth_result["t"], is_param["query"])
                    dummy_data["status"] = "1"
                    dummy_data["sid"] = res.get("sid", "default")
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
                    to_log["result"] = "error"
                    to_log["msg"] = res.get("error", "")
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                _logger.error("search error:", e)
                to_log["result"] = "error"
                to_log["msg"] = e
            audit_logger.info(json.dumps(to_log))
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_download_submit(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            is_param = self.checkParam(request, **kwargs)
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "download",
                "module": "search",
                "user_name": auth_result["u"],
                "user_id": auth_result["i"],
                "domain": auth_result["d"],
                "query": is_param["query"],
                "result": "success"
            }
            req_data = request.GET
            print req_data
            param = {
                "query": is_param["query"],
                "token": auth_result["t"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "operator": auth_result["u"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "filter_field": is_param["filters"],
                "source_group": is_param["source_group"],
                "category": "download",
                "task_name": req_data["file_name"],
                "file_name": req_data["file_name"],
                "file_format": req_data["file_format"],
                "max_events": req_data.get("max_events", ""),
                "max_file_size": req_data.get("max_file_size", "")
            }
            queryfilters = req_data.get("queryfilters")
            if queryfilters:
                param["queryfilters"] = queryfilters
            res = BackendRequest.search_download_submit(param)
            try:
                if res["rc"] == 0:
                    dummy_data["status"] = "1"
                    dummy_data["sid"] = res.get("sid", "default")
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
                    to_log["result"] = "error"
                    to_log["msg"] = res.get("error", "")
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                _logger.error("search error:", e)
                to_log["result"] = "error"
                to_log["msg"] = e
            audit_logger.info(json.dumps(to_log))
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_offlinetask_submit(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            post_data = request.POST
            param = {
                "token": auth_result["t"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "operator": auth_result["u"],
                "sid": post_data["sid"],
                "task_name": post_data["task_name"]
            }
            res = BackendRequest.search_offlinetask_submit(param)
            try:
                if res["rc"] == 0:
                    dummy_data["status"] = "1"
                    dummy_data["sid"] = res.get("sid", "default")
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                _logger.error("search error:", e)
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        response_data = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, response_data)

    def _search_fetch(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            req_data = request.GET
            sid = req_data.get('sid', '')
            category = req_data.get('category', '')
            params = {
                "sid": sid,
                "category": category,
                "token": auth_result["t"],
                "owner_id": auth_result["i"],
                "operator": auth_result["u"],
                "page": int(req_data.get("page", 1)) - 1,
                "size": req_data["size"]
            }
            if req_data.get("version", "0"):
                params["version"] = req_data.get("version", "0")
            res = BackendRequest.search_preview(params)
            try:
                if res["rc"] == 0:
                    if res["type"] == "logtail":
                        res["type"] = "query"
                        res["logtail"] = "yes"
                    else:
                        res["logtail"] = "no"
                    if "fields" in category:
                        rtn_fields = self._build_fields_new(res["result"].get("fields", []))
                        res["result"]["fields"] = rtn_fields
                    if "sheets" in category and res["result"]["sheets"]:
                        type, rst, hits = self._build_events_new(res)
                        res["result"]["table"] = {
                            "head": res["result"]["sheets"].get("_field_infos_", []),
                            "body": rst,
                            "time_range": str(res["result"]["timeline"].get("start_ts", 0)) +","+str(res["result"]["timeline"].get("end_ts", 0)),
                            "total": res["result"]["sheets"].get("total", 0),
                            "version": res["result"]["sheets"].get("version", 0),
                            "page": req_data.get("page", 1),
                            "size": params["size"]
                        }
                    dummy_data["status"] = "1"
                    dummy_data["data"] = res
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                _logger.error(e)
            dummy_data["sid"] = sid
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_fetch_paged(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            req_data = request.GET
            sid = req_data.get('sid', '')
            params = {
                "sid": sid,
                "category": req_data.get('category', 'sheets'),
                "token": auth_result["t"],
                "owner_id": auth_result["i"],
                "operator": auth_result["u"],
                "page": int(req_data.get("page", 1)) - 1,
                "size": req_data["size"]
            }
            res = BackendRequest.search_preview(params)
            try:
                if res["rc"] == 0:
                    if res["type"] == "logtail":
                        res["type"] = "query"
                        res["logtail"] = "yes"
                    else:
                        res["logtail"] = "no"
                    if res["result"]["sheets"]:
                        type, rst, hits = self._build_events_new(res)
                        res["result"]["table"] = {
                            "head": res["result"]["sheets"].get("_field_infos_", []),
                            "body": rst,
                            "version": res["result"]["sheets"].get("version", 0),
                            "total": res["result"]["sheets"]["total"],
                            "size": params["size"]
                        }
                    dummy_data["status"] = "1"
                    dummy_data["data"] = res
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                _logger.error("search error:", e)
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_stats_events(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            req_data = request.GET
            sid = req_data.get('sid', '')
            params = {
                "sid": sid,
                "category": req_data.get('category', 'sheets'),
                "token": auth_result["t"],
                "owner_id": auth_result["i"],
                "operator": auth_result["u"],
                "page": int(req_data.get("page", 1)) - 1,
                "size": req_data["size"]
            }
            res = BackendRequest.search_stats_events(params)
            try:
                if res["rc"] == 0:
                    if res["result"]["sheets"]:
                        type, rst, hits = self._build_events_new(res, "yes")
                        res["result"]["table"] = {
                            "head": res["result"]["sheets"].get("_field_infos_", []),
                            "body": rst,
                            "total": res["result"]["sheets"]["total"],
                            "size": params["size"]
                        }
                    dummy_data["status"] = "1"
                    dummy_data["data"] = res
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                _logger.error("search error:", e)
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_cancel(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            req_data = request.GET
            sid = req_data.get('sid', '')
            params = {
                "sid": sid,
                "token": auth_result["t"],
                "operator": auth_result["u"],
            }
            res = BackendRequest.search_kill(params)
            try:
                if res["rc"] == 0:
                    dummy_data["status"] = "1"
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                _logger.error("search error:", e)
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_pause(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            req_data = request.GET
            sid = req_data.get('sid', '')
            params = {
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "sid": sid
            }
            res = BackendRequest.search_pause(params)
            try:
                if res["rc"] == 0:
                    dummy_data["status"] = "1"
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                _logger.error("search error:", e)
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_resume(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            req_data = request.GET
            sid = req_data.get('sid', '')
            params = {
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "sid": sid
            }
            res = BackendRequest.search_recover(params)
            try:
                if res["rc"] == 0:
                    dummy_data["status"] = "1"
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                _logger.error("search error:", e)
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_heartbeat(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            req_data = request.GET
            sid = req_data.get('sid', '')
            params = {
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "sid": sid
            }
            res = BackendRequest.search_heartbeat(params)
            try:
                if res["rc"] == 0:
                    dummy_data["status"] = "1"
                    dummy_data["sid"] = sid
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
                    dummy_data["sid"] = sid
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                dummy_data["sid"] = sid
                _logger.error("search error:", e)
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_top_fields(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            req_data = request.GET
            sid = req_data.get('sid', '')
            type = req_data.get('type', "fields")
            params = {
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "field": req_data.get('field', ""),
                "size": 50,
                "sid": sid
            }
            res = BackendRequest.search_topfields(params)
            try:
                if res["rc"] == 0:
                    dummy_data["status"] = "1"
                    dummy_data["list"] = []
                    for i in res["topk"]:
                        if type == "fields":
                            dummy_data["list"].append({
                                "name": i["value"],
                                "count": i["count"]
                            })
                        else:
                            dummy_data["list"].append([i["to"], i["doc_count"]])

                    dummy_data["total"] = len(dummy_data["list"])
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                _logger.error("search error:", e)
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_all_fields(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            is_param = self.checkParam(request, **kwargs)
            req_data = request.GET
            param = {
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "filter_field": is_param["filters"],
                "size": 1000,
                "page": 0,
                "field": req_data.get("field", ""),
                "source_group": is_param["source_group"],
            }
            res = BackendRequest.search(param)
            try:
                if res["rc"] == 0:
                    if res["result"]["sheets"]:
                        dummy_data["list"] = []
                        heads = []
                        for a_head in res["result"]["sheets"]["_field_infos_"]:
                            heads.append(a_head["name"])
                        for item in res["result"]["sheets"]["rows"]:
                            dummy_data["list"].append({
                                "name": item.get(heads[0], ""),
                                "count": item.get(heads[1], 0),
                                "percent": item.get(heads[2], 0)
                            })
                    dummy_data["status"] = "1"
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                _logger.error("search error:", e)
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_drilldown_query(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            req_data = request.GET
            param = {
                "pipe_command": req_data["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "filters": req_data["filters"],
                "type": req_data["type"]
            }
            if req_data["type"] == "drill_down":
                res = BackendRequest.drill_down(param)
            else:
                res = BackendRequest.drill_down_filter(param)
            try:
                if res["rc"] == 0:
                    dummy_data["query"] = res["pipe_command"]
                    dummy_data["status"] = "1"
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
                _logger.error("search error:", e)
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _only_fields(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            resdata = self._get_only_fields(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _only_timeline(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            resdata = self._get_only_timeline(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _fields(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            resdata = self._get_fields(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _events(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            resdata = self._get_events(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _events_table(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            resdata = self._get_events_table(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _fields_search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            resdata = self._get_fields_search(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _events_grid(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            resdata = self._get_grid_events(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_action(self, request, **kwargs):
        self.method_check(request, allowed=['get', 'post'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        rtn_data = {
            'curIndex': 0,
            'tabs': []
        }
        if auth_result:
            if request.method == "POST":
                req_data = request.POST
                post_data = req_data.get('content', '')
                res = BackendRequest.add_account_action({
                    "token": auth_result["t"],
                    "id": auth_result["i"],
                    "operator": auth_result["u"],
                    "category": "search"
                }, post_data)
                if res["result"]:
                    dummy_data["status"] = "1"
                else:
                    dummy_data["status"] = "0"
            else:
                default_tab = [{
                    'info': {
                        'savedsearch_id': "",
                        'title': '%E9%BB%98%E8%AE%A4',
                        'active': True,
                        'new': False  # be True for every new request
                    },
                    'search': {
                        'query': "*",
                        'time_range': "-1d,now",
                        'order': "desc",
                        'size': "20",
                        'page': "1",
                        'sourcegroup': "all",
                        'sourcegroupCn': "",
                        'type': "timeline",
                        'filters': []
                    },
                    'timeline': {},
                    'fields': {},
                    'view': {
                        'curView': 'events',
                        'events': {},
                        'grid': {},
                        'charts': {
                            'curChart': 'line',
                            'line': {
                                'dataSeries': [],
                                'type': 'line'
                            },
                            'bar': {
                                'dataSeries': [],
                                'type': 'bar'
                            },
                            'pie': {
                                'dataSeries': [],
                                'type': 'pie'
                            }
                        }
                    },
                    'data': {
                        'events': [],
                        'fields': {'all': [], 'num': [], 'ot': []},
                        'timeline': [
                            [0, 0]
                        ]
                    }
                }]
                res = BackendRequest.get_account_action({
                    "token": auth_result["t"],
                    "id": auth_result["i"],
                    "operator": auth_result["u"],
                    "category": "search"
                })
                if res["result"]:
                    try:
                        res_data = json.loads(ast.literal_eval(res["content"]))
                    except Exception, e:
                        print e
                        res_data = {}
                    rtn_data["curIndex"] = res_data.get("curIndex", 0)
                    rtn_data["tabs"] = res_data.get("tabs", default_tab)
                    rtn_data["searchHistories"] = res_data.get("searchHistories", [])
                    dummy_data["status"] = "1"
                    dummy_data["data"] = rtn_data
                else:
                    # if res["error"].encode('utf-8') == "action category is not existed":
                    rtn_data["tabs"] = default_tab
                    dummy_data["status"] = "1"
                    dummy_data["data"] = rtn_data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def checkParam(self, request, **kwargs):
        req_data = request.GET
        sg = req_data.get('sourcegroup', 'all')
        post_data = {
            "query": req_data.get('query', '*'),
            "time_range": "-1d,now" if req_data.get('time_range', '') == "" else req_data['time_range'],
            "order": req_data.get('order', 'desc'),
            "size": req_data.get('size', '20'),
            "page": req_data.get('page', '1'),
            "type": req_data.get('type', 'timeline'),
            "sid": req_data.get('sid', ""),
            "filters": req_data.get('filters', ''),
            "exist_fields": req_data.get('exist_fields', ''),
            "source_group": sg
        }
        # query = kwargs['query']
        # time_range = kwargs['time_range']
        # order = kwargs['order']
        # size  = kwargs['size']
        return post_data

    def _get_search(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        audit_logger = logging.getLogger('yottaweb.audit')
        to_log = dict.copy(is_param)
        to_log["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        to_log["action"] = "search"
        to_log["user_name"] = auth_result["u"]
        to_log["user_id"] = auth_result["i"]
        audit_logger.info(json.dumps(to_log))
        if is_param:
            res = BackendRequest.search({
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "size": is_param["size"],
                "page": int(is_param["page"]) - 1,
                "filter_field": is_param["filters"],
                "category": is_param["type"],
                "source_group": is_param["source_group"]
            })
            if res["result"]:
                if "groups" in res:
                    _timeline = {'event_counts': res.get('event_counts', {})}
                    _fields = res.get('index_fields', {})
                    _groups = res.get('groups', [])
                    _stats = res.get("stats", [])
                    _with_stats = 'yes' if "stats" in res and res["stats"] else 'no'
                    data = {
                        "status": 1,
                        "total": res.get("total", 0),
                        "page": int(res.get("page", 0)),
                        "size": res.get("size", 20),
                        "group_id": res.get("groups_id", ""),
                        "type": "trans",
                        "with_stats": _with_stats,
                        "events": self._build_groups(_groups) if _groups else [],
                        "timeline": self._build_time_line(_timeline) if _timeline else {"time_line": []},
                        "fields": self._build_fields(_fields) if _fields else {},
                        "stats": self._build_stats(_stats) if _stats else []
                    }
                else:
                    _fields = res.get('index_fields', {})
                    _stats = res.get("stats", [])
                    _with_stats = 'yes' if "stats" in res and res["stats"] else 'no'
                    if _with_stats == "yes":
                        _timeline = {'event_counts': res.get('event_counts', {})}
                        _events = res['hits'].get('hits', [])
                        total = res['hits']["total"]

                    else:
                        _timeline = res.get('aggs', {})
                        _events = res.get('events', [])
                        total = res["total"]

                    data = {
                        "status": 1,
                        "total": total,
                        "page": int(res.get("page", 1)),
                        "size": res.get("size", 20),
                        "type": "search",
                        "search_timerange": str(res.get("start_timestamp", "")) + "," + str(res.get("end_timestamp", "")),
                        "with_stats": _with_stats,
                        "events": self._build_events(_events) if _events else [],
                        "timeline": self._build_time_line(_timeline) if _timeline else {"time_line": []},
                        "fields": self._build_fields(_fields) if _fields else {},
                        "stats": self._build_stats(_stats) if _stats else []
                    }
            else:
                if res["error_code"] == 522:
                    data = {
                        "status": 1,
                        "total": 0,
                        "page": 1,
                        "size": 20,
                        "type": "search",
                        "events": [],
                        "timeline": {"time_line": []},
                        "fields": {}
                    }
                else:
                    data = err_data.build_error(res)
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
            # path = os.path.dirname(os.path.realpath(__file__))
            # json_data = open(path + '/search.json')
            # data = json.load(json_data)
            # dummy_data = data
            # bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            # result = bundle
            # json_data.close()
            # time.sleep(2)
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        return result

    def _get_only_fields(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        if is_param:
            res = BackendRequest.search({
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "sid": is_param.get("sid", ""),
                "size": is_param["size"],
                "page": int(is_param["page"]) - 1,
                "filter_field": is_param["filters"],
                "category": "only_fields_outline",
                "usetable": "true",
                "source_group": is_param["source_group"]
            })
            if res["result"]:
                rtn_type = "group" if res.get('disabled', False) else "search"
                _fields = res.get('index_fields', {})
                _with_stats = 'yes' if "stats" in res and res["stats"] else 'no'
                data = {
                    "status": 1,
                    "type": rtn_type,
                    "sid": res.get("sid", ""),
                    "with_stats": _with_stats,
                    "fields": self._build_fields(_fields) if _fields else {}
                }
            else:
                if res["error_code"] == 522:
                    data = {
                        "status": 1,
                        "total": 0,
                        "page": 1,
                        "size": 20,
                        "sid": is_param.get("sid", ""),
                        "type": "search",
                        "events": [],
                        "timeline": {"time_line": []},
                        "fields": {}
                    }
                else:
                    data = err_data.build_error(res)
                    data["sid"] = is_param.get("sid", "")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        return result

    def _get_only_timeline(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        audit_logger = logging.getLogger('yottaweb.audit')
        to_log = dict.copy(is_param)
        to_log["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        to_log["action"] = "search"
        to_log["user_name"] = auth_result["u"]
        to_log["user_id"] = auth_result["i"]
        to_log["domain"] = auth_result["d"]
        audit_logger.info(json.dumps(to_log))
        if is_param:
            res = BackendRequest.search({
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "size": is_param["size"],
                "sid": is_param.get("sid", ""),
                "page": int(is_param["page"]) - 1,
                "filter_field": is_param["filters"],
                "category": "only_timeline",
                "usetable": "true",
                "source_group": is_param["source_group"]
            })
            if res["result"]:
                if "groups" in res:
                    _timeline = {'event_counts': res.get('event_counts', {})}
                    _fields = res.get('index_fields', {})
                    _groups = res.get('groups', [])
                    _stats = res.get("stats", [])
                    _with_stats = 'yes' if "stats" in res and res["stats"] else 'no'
                    data = {
                        "status": 1,
                        "total": res.get("total", 0),
                        "group_id": res.get("groups_id", ""),
                        "sid": res.get("sid", ""),
                        "type": "trans",
                        "with_stats": _with_stats,
                        "timeline": self._build_time_line(_timeline) if _timeline else {"time_line": []},
                        "stats": self._build_stats(_stats) if _stats else []
                    }

                else:
                    _fields = res.get('index_fields', {})
                    _stats = res.get("stats", [])
                    _with_stats = 'yes' if "stats" in res and res["stats"] else 'no'
                    if _with_stats == "yes":
                        _timeline = {'event_counts': res.get('event_counts', {})}
                        _events = res['hits'].get('hits', [])
                        total = res['hits']["total"]

                    else:
                        _timeline = res.get('aggs', {})
                        total = res["total"]

                    data = {
                        "status": 1,
                        "total": total,
                        "type": "search",
                        "with_stats": _with_stats,
                        "sid": res.get("sid", ""),
                        "timeline": self._build_time_line(_timeline) if _timeline else {"time_line": []},
                        "stats": self._build_stats(_stats) if _stats else []
                    }
            else:
                if res["error_code"] == 522:
                    data = {
                        "status": 1,
                        "total": 0,
                        "page": 1,
                        "size": 20,
                        "sid": is_param.get("sid", ""),
                        "type": "search",
                        "events": [],
                        "timeline": {"time_line": []},
                        "fields": {}
                    }
                else:
                    data = err_data.build_error(res)
                    data["sid"] = is_param.get("sid", "")

            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        return result

    def _get_fields(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        try:
            cf = ConfigParser.ConfigParser()
            real_path = os.getcwd() + '/config'
            cf.read(real_path + "/yottaweb.ini")
            config_size = cf.get('custom', 'field_value_num')
        except Exception, e:
            print e
            config_size = 1000

        if is_param:
            search_param = {
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "page": int(is_param["page"]) - 1,
                "filter_field": is_param["filters"],
                "with_trend": "false",
                "category": is_param["type"],
                "field": req_data.get("field", ""),
                # "source_group": "0811test"
                "source_group": is_param["source_group"]
            }
            if req_data.get("all", ""):
                search_param["size"] = config_size
            else:
                search_param["size"] = is_param["size"]

            res = BackendRequest.search(search_param)
            if res["result"]:
                data = {
                    "status": 1,
                    "count": search_param["size"],
                    "total": 0,
                    "list": []
                }
                for i in res["buckets"]:
                    if is_param["type"] == "fields":
                        data["list"].append({
                            "name": i["key"],
                            "count": i["doc_count"]
                        })
                    else:
                        data["list"].append([i["to"], i["doc_count"]])
                data["total"] = len(data["list"])
            else:
                data = err_data.build_error(res)
        else:
            data = err_data.build_error({}, "parameter is wrong")
        dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        result = bundle
        return result

    def _get_events(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        if is_param:
            group_id = req_data.get("groupId", "")
            if group_id:
                param = {
                    "jid": group_id,
                    "category": "events",
                    "token": auth_result["t"],
                    "operator": auth_result["u"],
                    "owner_name": auth_result["u"],
                    "owner_id": auth_result["i"],
                    "sid": is_param.get("sid", ""),
                    "size": is_param["size"],
                    "usetable": "false",
                    "page": int(is_param["page"]) - 1
                }
            else:
                param = {
                    "query": is_param["query"],
                    "token": auth_result["t"],
                    "operator": auth_result["u"],
                    "owner_name": auth_result["u"],
                    "owner_id": auth_result["i"],
                    "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                    "order": is_param["order"],
                    "size": is_param["size"],
                    "sid": is_param.get("sid", ""),
                    "page": int(is_param["page"]) - 1,
                    "filter_field": is_param["filters"],
                    "category": "events",
                    "field": req_data.get("field", ""),
                    "usetable": "false",
                    # "source_group": "0811test"
                    "source_group": is_param["source_group"],
                }
                queryfilters = req_data.get("queryfilters")
                if queryfilters:
                    param["queryfilters"] = queryfilters

            if is_param["exist_fields"]:
                param["exist_fields"] = is_param["exist_fields"]
            res = BackendRequest.search(param)
            if res["result"]:
                if "groups" in res:
                    _groups = res.get('groups', [])
                    data = {
                        "status": 1,
                        "total": res["total"],
                        "page": int(res["page"]),
                        "size": res["size"],
                        "sid": res.get("sid", ""),
                        "group_id": res.get("groups_id", ""),
                        "type": "trans",
                        "events": self._build_groups(_groups) if _groups else []
                    }

                else:
                    _stats = res.get("stats", [])
                    _with_stats = 'yes' if "stats" in res and res["stats"] else 'no'
                    if _with_stats == "yes":
                        _events = res['hits'].get('hits', [])
                        total = res['hits']["total"]
                    elif "hits" in res:
                        _events = res['hits'].get('hits', [])
                        total = res['hits']["total"]
                    else:
                        _events = res.get('events', [])
                        total = res["total"]

                    data = {
                        "status": 1,
                        "total": total,
                        "page": int(res.get("page", 1)),
                        "size": res.get("size", 20),
                        "type": "search",
                        "with_stats": _with_stats,
                        "sid": res.get("sid", ""),
                        "search_timerange": str(res.get("start_timestamp", "")) + "," + str(
                            res.get("end_timestamp", "")),
                        "events": self._build_events(_events) if _events else [],
                        "stats": self._build_stats(_stats) if _stats else []
                    }
            else:
                data = {
                    "status": 0,
                    "msg": "search error"
                }
                if res["error_code"] == 522:
                    data = {
                        "status": 1,
                        "total": 0,
                        "page": 1,
                        "size": 20,
                        "type": "search",
                        "sid": is_param.get("sid", ""),
                        "events": [],
                        "timeline": {"time_line": []},
                        "fields": {}
                    }
                else:
                    data = err_data.build_error(res)
                    data["sid"] = is_param.get("sid", "")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        return result

    def _get_events_table(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        if is_param:
            group_id = req_data.get("groupId", "")
            if group_id:
                param = {
                    "jid": group_id,
                    "category": "events",
                    "token": auth_result["t"],
                    "operator": auth_result["u"],
                    "owner_name": auth_result["u"],
                    "owner_id": auth_result["i"],
                    "sid": is_param.get("sid", ""),
                    "size": is_param["size"],
                    "usetable": "true",
                    "page": int(is_param["page"]) - 1
                }
            else:
                param = {
                    "query": is_param["query"],
                    "token": auth_result["t"],
                    "operator": auth_result["u"],
                    "owner_name": auth_result["u"],
                    "owner_id": auth_result["i"],
                    "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                    "order": is_param["order"],
                    "size": is_param["size"],
                    "sid": is_param.get("sid", ""),
                    "page": int(is_param["page"]) - 1,
                    "filter_field": is_param["filters"],
                    "category": "events",
                    "field": req_data.get("field", ""),
                    "usetable": "true",
                    # "source_group": "0811test"
                    "source_group": is_param["source_group"],
                }
                queryfilters = req_data.get("queryfilters")
                if queryfilters:
                    param["queryfilters"] = queryfilters
            if is_param["exist_fields"]:
                param["exist_fields"] = is_param["exist_fields"]
            res = BackendRequest.search(param)
            if res["result"]:
                search_type, body, hits = self._build_body(res)
                data = {
                    "status": 1,
                    "total": res["total"],
                    "page": int(res.get("page", 0)),
                    "size": res.get("size", 10),
                    "searchType": search_type,
                    "sid": res.get("sid", ""),
                    "group_id": res.get("groups_id", ""),
                    "search_timerange": str(res.get("start_timestamp", "")) + "," + str(
                            res.get("end_timestamp", "")),
                    "table": {
                        "head": res.get("_field_infos_", []),
                        "body": body
                    }
                }
                if hits:
                    data["hits"] = hits
            else:
                data = {
                    "status": 0,
                    "msg": "search error"
                }
                if res["error_code"] == 522:
                    data = {
                        "status": 1,
                        "total": 0,
                        "page": 1,
                        "size": 20,
                        "searchType": "query",
                        "sid": is_param.get("sid", ""),
                        "table": {
                            "head": [],
                            "body": []
                        },
                        "timeline": {"time_line": []},
                        "fields": {}
                    }
                else:
                    data = err_data.build_error(res)
                    data["sid"] = is_param.get("sid", "")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        return result

    def _build_events_new(self, res, with_status="no"):
        type = res.get("type", "stats").lower() if with_status == "no" else "query"
        hits = {}
        if type == "stats":
            body = []
            data = {
                "status": 1,
                "table": {
                    "head": hits.get("_field_infos_", []),
                    "body": body
                }
            }

            return type, res["result"]["sheets"]["rows"], data
        elif type == "query":
            rst = []
            for item in res["result"]["sheets"]["rows"]:
                a_event = item
                tokens = item.get("_tokens", [])
                hlight = item.get("_highlight", {"raw_message": ""})
                high_light = hlight["raw_message"]
                hl = re.findall(r'<em>(.*?)</em>', high_light)
                # tokens = sorted(tokens, key=len, reverse=True)
                raw_msg = item.get("raw_message", "")
                # if len(tokens) > 500 and len(hl) > 0:
                    # 如果tokens数量大于500并且存在高亮内容，需要提取高亮内容在前端展现，添加的target参数中find设置为False以保证不当做正常的token去处理
                target = []
                if high_light:
                    _hl_arr_segement = high_light.split("<em>")
                    for segement in _hl_arr_segement:
                        print segement.split("</em>")
                        if len(segement.split("</em>")) == 2:
                            _seg_content_arr = segement.split("</em>")
                            target.append({
                                "s": _seg_content_arr[0],
                                "hover": False,
                                "highlight": True,
                                "find": False
                            })
                            target.append({
                                "s": _seg_content_arr[1],
                                "hover": False,
                                "highlight": False,
                                "find": False
                            })
                        else:
                            target.append({
                                "s": segement,
                                "hover": False,
                                "highlight": False,
                                "find": False
                            })
                else:
                    target.append({
                        "s": item.get('raw_message', ''),
                        "hover": False,
                        "highlight": False,
                        "find": False
                    })
                # else:
                #     ori = [{
                #         "s": raw_msg,
                #         "find": False
                #     }]
                #     target = self.contribute(tokens, ori, hl)
                a_event["_cus_raw"] = {
                    "segment_tree": target
                }
                a_event["context_id"] = str(a_event.get("context_id", '0'))
                if "_tokens" in a_event:
                    del a_event["_tokens"]
                if "_highlight" in a_event:
                    del a_event["_highlight"]
                rst.append(a_event)
            return type, rst, hits
        elif type == "transaction":
            result = []
            heads = res.get("_field_infos_", [])
            for group in res["result"]["sheets"]["rows"]:
                source = group.get("source", [])
                events = []
                cus_fields = {}
                group_fields = {}
                new_group = group
                key_timestamp = group.get("min_timestamp", 0)
                if "_cache_id_" in new_group:
                    del new_group["_cache_id_"]
                if "_id_" in new_group:
                    del new_group["_id_"]
                if "source" in new_group:
                    del new_group["source"]
                if "max_timestamp" in new_group:
                    del new_group["max_timestamp"]
                if "min_timestamp" in new_group:
                    del new_group["min_timestamp"]

                new_group["hostname"] = []
                new_group["appname"] = []
                new_group["logtype"] = []
                new_group["tag"] = []
                # for a_head in heads:
                #     if not a_head["name"] == "source" and not a_head.get("groupby", False):
                #         group_fields[a_head["name"]] = group[a_head["name"]] if isinstance(group[a_head["name"]],
                #                                                                            list) else [
                #             group[a_head["name"]]]
                #         del new_group[a_head["name"]]
                for event in source:
                    event["context_id"] = str(event.get("context_id", '0'))
                    events.append(event["raw_message"])
                    new_group["hostname"].append(event.get("hostname", ""))
                    new_group["appname"].append(event.get("appname", ""))
                    new_group["logtype"].append(event.get("logtype", ""))
                    event["tag"] = event["tag"] if isinstance(event["tag"], list) else [event["tag"]]
                    new_group["tag"] = list(set(new_group["tag"] + event["tag"]))
                    # if event.get("security", {}):
                    #     own_fields["security"] = {}
                    #     own_fields["security"] = self.merge_dict(own_fields["security"], event.get("security", {}))
                    cus_fields = self.merge_dict(cus_fields, event)
                    if "hostname" in cus_fields:
                        del cus_fields["hostname"]
                    if "appname" in cus_fields:
                        del cus_fields["appname"]
                    if "logtype" in cus_fields:
                        del cus_fields["logtype"]
                    if "tag" in cus_fields:
                        del cus_fields["tag"]
                    del cus_fields["raw_message"]

                new_group["hostname"] = list(set(new_group["hostname"]))
                new_group["appname"] = list(set(new_group["appname"]))
                new_group["logtype"] = list(set(new_group["logtype"]))

                new_group["events"] = events
                new_group["timestamp"] = key_timestamp
                new_group["fields"] = cus_fields
                new_group["group_fields"] = group_fields
                result.append(new_group)
            return type, result, hits

    def _build_stats_new(self, section, param):
        chartType = param.get("showType", "")
        uniq = {}
        if chartType == "multiaxis" or chartType == "line" or chartType == "area" or chartType == "scatter" or chartType == "column":
            tmp_uniq = {}
            try:
                x = param["cur_XField"]
                yFields = param["cur_YFields"].split(",")
                byFields = param["cur_ByFields"].split(",") if param["cur_ByFields"] else []

                if len(byFields) == 0:
                    for item in yFields:
                        uniq[item] = []
                    for one in section:
                        for item in yFields:
                            uniq[item].append([one[x], one.get(item)])
                else:
                    for i in range(len(yFields)):
                        uniq[yFields[i]] = {}
                        tmp_uniq[yFields[i]] = {}
                    for one in section:
                        for k in range(len(yFields)):
                            new_key = ""
                            temp_new_key = str(one[x])
                            try:
                                for a_b in byFields:
                                    new_key = str(one[a_b]) if new_key == "" else str(new_key) +"_" + str(one[a_b])
                                    temp_new_key += "_" + str(one[a_b])
                                if not new_key in uniq[yFields[k]]:
                                    uniq[yFields[k]][new_key] = []
                                if not temp_new_key in tmp_uniq[yFields[k]]:
                                    tmp_uniq[yFields[k]][temp_new_key] = one.get(yFields[k])
                                else:
                                    if tmp_uniq[yFields[k]][temp_new_key] == None:
                                        tmp_uniq[yFields[k]][temp_new_key] = one.get(yFields[k])
                                    else:
                                        if one.get(yFields[k]) != None:
                                            tmp_uniq[yFields[k]][temp_new_key] += one.get(yFields[k])
                                uniq[yFields[k]][new_key].append([one[x], tmp_uniq[yFields[k]][temp_new_key]])
                            except Exception, e:
                                print e
            except Exception, e:
                print e

        elif chartType == "pie":
            try:
                x = param["cur_XField"]
                uniq[x] = []
                for one in section:
                    new_key = ""
                    try:
                        for a_b in param["cur_ByFields"].split(","):
                            new_key = str(one[a_b]) if new_key == "" else str(new_key) +"_" + str(one[a_b])
                        uniq[x].append({"name":new_key, "value":one[x]})
                    except Exception, e:
                        print e
            except Exception, e:
                print e
        elif chartType == "bar":
            try:
                x = param["cur_XField"]
                uniq[x] = []
                for one in section:
                    new_key = ""
                    try:
                        for a_b in param["cur_ByFields"].split(","):
                            new_key = str(one[a_b]) if new_key == "" else str(new_key) +"_" + str(one[a_b])
                        uniq[x].append({"name":new_key, "value":one[x]})
                    except Exception, e:
                        print e
            except Exception, e:
                print e
        elif chartType == "wordcloud":
            try:
                x = param["cur_XField"]
                byField = param["cur_ByField"]
                uniq = []
                for one in section:
                    uniq.append({"name":one[byField], "value":one[x]})
            except Exception, e:
                print e
        elif chartType == "heatmap":
            try:
                x = param["cur_XField"]
                byField = param["cur_ByField"]
                uniq = []
                for one in section:
                    uniq.append({"name":one[byField], "value":one[x]})
            except Exception, e:
                print e
        elif chartType == "rangeline":
            averages = []
            outliers = []
            uppers = []
            lowers = []
            try:
                x = param["cur_XField"]
                average = param["cur_YField"]
                outlier = param["cur_OutlierField"]
                upper = param["cur_UpperField"]
                lower = param["cur_LowerField"]
                base = 0
                for one in section:
                    averages.append([one[x], one[average]])
                    # if one.get(outlier) != None:
                    outliers.append([one[x], one[outlier]])
                    if one.get(upper) != None and one.get(lower) != None:
                        uppers.append([one[x], one[upper]-one[lower]])
                        lowers.append([one[x], one[lower]])
                    else:
                        uppers.append([one[x], one[upper]])
                        lowers.append([one[x], one[lower]])
                    if one.get(lower) != None:
                        if base > one[lower]:
                            base = one[lower];
                    if one.get(outlier) != None:
                        if base > one[outlier]:
                            base = one[outlier];
                base = -base;
                base = math.ceil(base)

            except Exception, e:
                print e
            uniq = {
                "averages": averages,
                "outliers": outliers,
                "uppers": uppers,
                "lowers": lowers,
                "base": base
            }
        elif chartType == "attackmap":
            nodes = []
            links = []
            try:
                fromField = param["cur_FromField"]
                fromLongitudeField = param["cur_FromLongitudeField"]
                fromLatitudeField = param["cur_FromLatitudeField"]
                toField = param["cur_ToField"]
                toLongitudeField = param["cur_ToLongitudeField"]
                toLatitudeField = param["cur_ToLatitudeField"]
                weightField = param["cur_WeightField"]
                tmp_set = Set()
                tmp_obj = {}
                _max = 0
                _min = 0
                for one in section:
                    tmp_set.add(one[fromField])
                    tmp_set.add(one[toField])
                    if one[fromField] in tmp_obj:
                        tmp_obj[one[fromField]]['value'] += one[weightField]
                    else:
                        tmp_obj[one[fromField]] = copy.copy(one)
                        tmp_obj[one[fromField]]['value'] = one[weightField]
                        tmp_obj[one[fromField]]['type'] = 'from'
                    if one[toField] in tmp_obj:
                        tmp_obj[one[toField]]['value'] += one[weightField]
                    else:
                        tmp_obj[one[toField]] = copy.copy(one)
                        tmp_obj[one[toField]]['value'] = one[weightField]
                        tmp_obj[one[toField]]['type'] = 'to'

                    _max = tmp_obj[one[fromField]]['value'] if _max < tmp_obj[one[fromField]]['value'] else _max
                    _max = tmp_obj[one[toField]]['value'] if _max < tmp_obj[one[toField]]['value'] else _max
                    # _min = tmp_obj[one[fromField]] if _min > tmp_obj[one[fromField]] else _min
                    links.append({'fromName': one[fromField], 'toName': one[toField], 'coords': [[one[fromLongitudeField], one[fromLatitudeField]], [one[toLongitudeField], one[toLatitudeField]]]})
                    # links.append({'target': one[fromField], 'source': one[toField], 'weight': one[weightField]})
                tmp_nodes = list(tmp_set)
                for item in tmp_nodes:
                    _size = math.floor(((tmp_obj[item]['value']-_min)* 5)/float(_max-_min) + 1)
                    if tmp_obj[item]['type'] == 'from':
                        nodeValue = [tmp_obj[item][fromLongitudeField], tmp_obj[item][fromLatitudeField], tmp_obj[item]['value']]
                    else:
                        nodeValue = [tmp_obj[item][toLongitudeField], tmp_obj[item][toLatitudeField], tmp_obj[item]['value']]
                    nodes.append({'name': item, 'value': nodeValue, 'symbolSize': _size})
            except Exception, e:
                print e
            uniq = {
                "citys": nodes,
                "moveLines": links
            }
        elif chartType == "chord" or chartType == "sankey" or chartType == "force":
            nodes = []
            links = []
            try:
                fromField = param["cur_FromField"]
                toField = param["cur_ToField"]
                weightField = param["cur_WeightField"]
                tmp_set = Set()
                tmp_obj = {}
                _max = 0
                _min = 0
                for one in section:
                    tmp_set.add(one[fromField])
                    tmp_set.add(one[toField])
                    if one[fromField] in tmp_obj:
                        tmp_obj[one[fromField]] = tmp_obj[one[fromField]] + one[weightField]
                    else:
                        tmp_obj[one[fromField]] = one[weightField]
                    if one[toField] in tmp_obj:
                        tmp_obj[one[toField]] = tmp_obj[one[toField]] + one[weightField]
                    else:
                        tmp_obj[one[toField]] = one[weightField]

                    _max = tmp_obj[one[fromField]] if _max < tmp_obj[one[fromField]] else _max
                    _max = tmp_obj[one[toField]] if _max < tmp_obj[one[toField]] else _max
                    # _min = tmp_obj[one[fromField]] if _min > tmp_obj[one[fromField]] else _min
                    links.append({'source': one[fromField], 'target': one[toField], 'value': one[weightField]})
                    # links.append({'target': one[fromField], 'source': one[toField], 'weight': one[weightField]})
                tmp_nodes = list(tmp_set)
                category = 0
                categories = []
                for item in tmp_nodes:
                    _size = math.floor(((tmp_obj[item]-_min)* 45)/float(_max-_min) + 5)
                    nodes.append({'name': item, 'value': tmp_obj[item], 'symbolSize': _size, 'category': category, 'label': {
                        "normal": {
                            "show": _size > 5
                        }
                    }})
                    categories.append({'name': category})
                    category += 1
            except Exception, e:
                print e
            uniq = {
                "nodes": nodes,
                "links": links,
                "categories": categories
            }
        return uniq

    def _build_body(self, res):
        type = res["type"].lower()
        hits = {}
        if type == "stats":
            hits = res.get("hits", {})
            body = []
            if hits:
                for item in hits["hits"]:
                    a_event = item
                    tokens = item.get("_tokens", [])
                    hlight = item.get("_highlight", {"raw_message": ""})
                    high_light = hlight["raw_message"]
                    hl = re.findall(r'<em>(.*?)</em>', high_light)
                    # tokens = sorted(tokens, key=len, reverse=True)
                    raw_msg = item.get("raw_message", "")
                    ori = [{
                        "s": raw_msg,
                        "find": False
                    }]
                    target = self.contribute(tokens, ori, hl)
                    a_event["_cus_raw"] = {
                        "segment_tree": target
                    }
                    if "_tokens" in a_event:
                        del a_event["_tokens"]
                    if "_highlight" in a_event:
                        del a_event["_highlight"]
                    body.append(a_event)
            else:
                body = []
            data = {
                "status": 1,
                "total": hits.get("total", 0),
                "page": int(hits.get("page", 0)),
                "size": hits.get("size", 10),
                "table": {
                    "head": hits.get("_field_infos_", []),
                    "body": body
                }
            }

            return type, res["stats"], data
        elif type == "query":
            rst = []
            for item in res["hits"]:
                a_event = item
                tokens = item.get("_tokens", [])
                hlight = item.get("_highlight", {"raw_message": ""})
                high_light = hlight["raw_message"]
                hl = re.findall(r'<em>(.*?)</em>', high_light)
                # tokens = sorted(tokens, key=len, reverse=True)
                raw_msg = item.get("raw_message", "")
                ori = [{
                    "s": raw_msg,
                    "find": False
                }]
                target = self.contribute(tokens, ori, hl)
                a_event["_cus_raw"] = {
                    "segment_tree": target
                }
                if "_tokens" in a_event:
                    del a_event["_tokens"]
                if "_highlight" in a_event:
                    del a_event["_highlight"]
                rst.append(a_event)
            return type, rst, hits
        elif type == "transaction":
            result = []
            heads = res["_field_infos_"]
            for group in res["groups"]:
                source = group.get("source", [])
                events = []
                cus_fields = {}
                group_fields = {}
                new_group = group
                key_timestamp = group.get("min_timestamp", 0)
                if "_cache_id_" in new_group:
                    del new_group["_cache_id_"]
                if "_id_" in new_group:
                    del new_group["_id_"]
                if "source" in new_group:
                    del new_group["source"]
                if "max_timestamp" in new_group:
                    del new_group["max_timestamp"]
                if "min_timestamp" in new_group:
                    del new_group["min_timestamp"]

                new_group["hostname"] = []
                new_group["appname"] = []
                new_group["logtype"] = []
                new_group["tag"] = []
                for a_head in heads:
                    if not a_head["name"] == "source" and not a_head.get("groupby", False):
                        group_fields[a_head["name"]] = group[a_head["name"]] if isinstance(group[a_head["name"]],
                                                                                           list) else [
                            group[a_head["name"]]]
                        del new_group[a_head["name"]]
                for event in source:
                    events.append(event["raw_message"])
                    new_group["hostname"].append(event.get("hostname", ""))
                    new_group["appname"].append(event.get("appname", ""))
                    new_group["logtype"].append(event.get("logtype", ""))
                    event["tag"] = event["tag"] if isinstance(event["tag"], list) else [event["tag"]]
                    new_group["tag"] = list(set(new_group["tag"] + event["tag"]))
                    # if event.get("security", {}):
                    #     own_fields["security"] = {}
                    #     own_fields["security"] = self.merge_dict(own_fields["security"], event.get("security", {}))
                    cus_fields = self.merge_dict(cus_fields, event)
                    if "hostname" in cus_fields:
                        del cus_fields["hostname"]
                    if "appname" in cus_fields:
                        del cus_fields["appname"]
                    if "logtype" in cus_fields:
                        del cus_fields["logtype"]
                    if "tag" in cus_fields:
                        del cus_fields["tag"]
                    del cus_fields["raw_message"]

                new_group["hostname"] = list(set(new_group["hostname"]))
                new_group["appname"] = list(set(new_group["appname"]))
                new_group["logtype"] = list(set(new_group["logtype"]))

                new_group["events"] = events
                new_group["timestamp"] = key_timestamp
                new_group["fields"] = cus_fields
                new_group["group_fields"] = group_fields
                result.append(new_group)
            return type, result, hits

    def _build_body_simple(self, res):
        type = res["type"].lower()
        hits = {}
        if type == "stats":
            hits = res.get("hits", {})
            body = []
            data = {
                "status": 1,
                "total": hits.get("total", 0),
                "page": int(hits.get("page", 0)),
                "size": hits.get("size", 10),
                "table": {
                    "head": hits.get("_field_infos_", []),
                    "body": body
                }
            }

            return type, res["stats"], data
        elif type == "query":
            rst = []
            for item in res["hits"]:
                a_event = item
                rst.append(a_event)
            return type, rst, hits
        elif type == "transaction":
            result = []
            heads = res["_field_infos_"]
            for group in res["groups"]:
                source = group.get("source", [])
                events = []
                cus_fields = {}
                group_fields = {}
                new_group = group
                key_timestamp = group.get("min_timestamp", 0)
                if "_cache_id_" in new_group:
                    del new_group["_cache_id_"]
                if "_id_" in new_group:
                    del new_group["_id_"]
                if "source" in new_group:
                    del new_group["source"]
                if "max_timestamp" in new_group:
                    del new_group["max_timestamp"]
                if "min_timestamp" in new_group:
                    del new_group["min_timestamp"]

                new_group["hostname"] = []
                new_group["appname"] = []
                new_group["logtype"] = []
                new_group["tag"] = []
                for a_head in heads:
                    if not a_head["name"] == "source" and not a_head.get("groupby", False):
                        group_fields[a_head["name"]] = group[a_head["name"]] if isinstance(group[a_head["name"]],
                                                                                           list) else [
                            group[a_head["name"]]]
                        del new_group[a_head["name"]]
                for event in source:
                    events.append(event["raw_message"])
                    new_group["hostname"].append(event.get("hostname", ""))
                    new_group["appname"].append(event.get("appname", ""))
                    new_group["logtype"].append(event.get("logtype", ""))
                    event["tag"] = event["tag"] if isinstance(event["tag"], list) else [event["tag"]]
                    new_group["tag"] = list(set(new_group["tag"] + event["tag"]))
                    # if event.get("security", {}):
                    #     own_fields["security"] = {}
                    #     own_fields["security"] = self.merge_dict(own_fields["security"], event.get("security", {}))
                    cus_fields = self.merge_dict(cus_fields, event)
                    if "hostname" in cus_fields:
                        del cus_fields["hostname"]
                    if "appname" in cus_fields:
                        del cus_fields["appname"]
                    if "logtype" in cus_fields:
                        del cus_fields["logtype"]
                    if "tag" in cus_fields:
                        del cus_fields["tag"]
                    del cus_fields["raw_message"]

                new_group["hostname"] = list(set(new_group["hostname"]))
                new_group["appname"] = list(set(new_group["appname"]))
                new_group["logtype"] = list(set(new_group["logtype"]))

                new_group["events"] = events
                new_group["timestamp"] = key_timestamp
                new_group["fields"] = cus_fields
                new_group["group_fields"] = group_fields
                result.append(new_group)
            return type, result, hits

    def _get_fields_search(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        try:
            cf = ConfigParser.ConfigParser()
            real_path = os.getcwd() + '/config'
            cf.read(real_path + "/yottaweb.ini")
            config_size = cf.get('custom', 'field_value_num')
        except Exception, e:
            print e
            config_size = 1000

        if is_param:
            param = {
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "page": int(is_param["page"]) - 1,
                "filter_field": is_param["filters"],
                "field_query": "*"+req_data.get("field_query", "")+"*",
                "search_field": req_data.get("search_field", ""),
                # "source_group": "0811test"
                "source_group": is_param["source_group"]
            }
            if req_data.get("all", ""):
                param["size"] = config_size
            else:
                param["size"] = is_param["size"]

            res = BackendRequest.field_search(param)
            if res["rc"] == 0:
                data = {
                    "status": '1',
                    "list": []
                }
                for i in res["result"]["sheets"]["rows"][0]["top_values"]:
                    data["list"].append({
                        "name": i[0],
                        "count": i[1]
                    })
            else:
                data = err_data.build_error(res)
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        return result

    def _search_statis(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            resdata = self._get_statis(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _search_events_count(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            res_data = self._get_events_count(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            res_data = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, res_data)

    def _get_events_count(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        if is_param:
            res = BackendRequest.search({
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "size": is_param["size"],
                "page": int(is_param["page"]) - 1,
                "filter_field": is_param["filters"],
                "category": "new_stat",
                "stat_field": req_data.get("field", ""),
                "stat_method": req_data.get("method", ""),
                "source_group": is_param["source_group"]
            })
            if res["result"]:
                stat_method = req_data.get("method", "")
                value_key = 'value' if stat_method == 'cardinality' else 'doc_count'
                data = {
                    "status": 1,
                    "start_time": res["buckets"][0]["from"],
                    "end_time": res["buckets"][len(res["buckets"]) - 1]["to"],
                    "list": []
                }
                span_arr = []
                for b_index,bucket in enumerate(res["buckets"]):
                    span_arr.append(bucket["to"] - bucket["from"])
                    if b_index != len(res["buckets"]) - 1:
                        data["list"].append([int(bucket["to"]), bucket.get(value_key, 0)])
                    else:
                        data["list"].append([int(res["buckets"][0]["to"] + (max(span_arr) * (len(res["buckets"]) - 1))), bucket.get(value_key, 0)])
                data["range"] = max(span_arr)
            else:
                data = err_data.build_error(res)
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        return result

    def _search_field_category(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            res_data = self._get_field_category(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            res_data = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, res_data)

    def _get_field_category(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        if is_param:
            res = BackendRequest.search({
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "size": is_param["size"],
                "page": int(is_param["page"]) - 1,
                "filter_field": is_param["filters"],
                "category": "new_stat",
                "stat_field": req_data.get("field", ""),
                "stat_method": req_data.get("method", ""),
                "topn": req_data.get("topn", 5),
                "with_trend": req_data.get("trend", "false"),
                "source_group": is_param["source_group"]
            })
            if res["result"]:
                data = {
                    "status": 1,
                    "list": []
                }
                for i in res["buckets"]:
                    if req_data.get("trend") == "false":
                        data["list"].append({
                            "name": i["key"],
                            "count": i["doc_count"]
                        })
                    else:
                        val = {
                            "name": i["key"],
                            "arr": []
                        }
                        for bucket in i["buckets"]:
                            val["arr"].append([int(bucket["to"]), bucket["doc_count"] or 0])
                        data["list"].append(val)
            else:
                data = err_data.build_error(res)
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        return result

    def _search_field_value(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            res_data = self._get_field_value(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            res_data = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, res_data)

    def _get_field_value(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        if is_param:
            res = BackendRequest.search({
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "size": is_param["size"],
                "page": int(is_param["page"]) - 1,
                "filter_field": is_param["filters"],
                "category": "new_stat",
                "source_group": is_param["source_group"],
                "stat_field": req_data.get("stat_field", ""),
                "stat_method": req_data.get("stat_method", ""),
                "stat_split_field_topn": 5,
                "stat_split_field": req_data.get("stat_split_field", "")
            })
            if res["result"]:
                stat_method = req_data.get("stat_method", "")
                data = {
                    "status": 1,
                    "data": []
                }
                for result in res["buckets"]:
                    val = {
                        "start_time": result["buckets"][0]["from"],
                        "end_time": result["buckets"][len(result["buckets"]) - 1]["to"],
                        "name": result["key"],
                        "arr": []
                    }
                    span_arr = []
                    for b_index,bucket in enumerate(result["buckets"]):
                        span_arr.append(bucket["to"] - bucket["from"])
                        if stat_method in ['sum', 'avg', 'max', 'min']:
                            if b_index != len(result["buckets"]) - 1:
                                val["arr"].append([int(bucket["to"]), bucket.get("value", 0)])
                            else:
                                val["arr"].append([int(result["buckets"][0]["to"] + (max(span_arr) * (len(result["buckets"]) - 1) )), bucket.get("value"), 0])
                    val["range"] = max(span_arr)
                    data["data"].append(val)
            else:
                data = err_data.build_error(res)
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        return result

    def _search_field_percent(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            res_data = self._get_field_percent(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            res_data = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, res_data)

    def _get_field_percent(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        if is_param:
            res = BackendRequest.search({
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "size": is_param["size"],
                "page": int(is_param["page"]) - 1,
                "filter_field": is_param["filters"],
                "category": "new_stat",
                "stat_field": req_data.get("stat_field", ""),
                "stat_method": req_data.get("stat_method", ""),
                "stat_values": req_data.get("percents", ""),
                "source_group": is_param["source_group"]
            })
            if res["result"]:
                data = {
                    "status": 1,
                    "list": []
                }
                if req_data.get("stat_method", "") == "percentiles":
                    for (k, v) in res["values"].items():
                        data["list"].append({
                            "percent": float(k),
                            "value": float('%.3f' % v)
                        })
                    data["list"] = sorted(data["list"], key=lambda x: x["percent"])
                else:
                    if res["values"]:
                        for (k, v) in res["values"].items():
                            data["list"].append(v)
                    else:
                        data = err_data.build_error(res)
            else:
                data = err_data.build_error(res)
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        return result

    def _search_field_multi(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            res_data = self._get_multi_level(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            res_data = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, res_data)

    def _get_multi_level(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        step = req_data.get('stat_step', '')
        post_data = {
            "query": {}
        }
        need_other = False
        need_timeline = False
        if step and step == 'step1':
            post_data["query"] = {
                "step1": {
                    "terms": {
                        "field": req_data.get('stat_field', ''),
                        "size": int(req_data.get('stat_top', '5'))
                    }
                }
            }
            # if req_data.get('stat_chartType', ''):
            #     if req_data.get('stat_other', 'false')
            need_other = True if req_data.get('stat_other', False) and req_data.get('stat_other', False) != 'false' else False
            if req_data.get('stat_chartType', '') and need_other:
                post_data["query"]['missing_result'] = {
                    "missing": {
                        "field": req_data.get('stat_field', '')
                    }
                }
            if req_data.get('stat_chartType', '') and req_data.get('stat_split', ''):
                need_timeline = True
                post_data["query"]["step1"]['group'] = {
                    "timeline_result": {
                        "timeline": {
                            "period": req_data.get('stat_split', '')
                        }
                    }}
            # if req_data.get('stat_chartType')
        elif step and step == "step2":
            ori_statis_type = req_data.get('stat_method', 'count')
            mid_statis_type = "stats" if ori_statis_type in ["sum", "max", "min", "avg"] else ori_statis_type
            final_stats_type = "terms" if mid_statis_type == "count" else mid_statis_type
            post_data["query"] = {
                "step2": {
                    final_stats_type: {
                        "field": req_data.get('stat_split_field', '')
                    }
                }
            }
            need_other = True if req_data.get('stat_other', False) and req_data.get('stat_other',
                                                                                    False) != 'false' else False
            if req_data.get('stat_chartType', '') and need_other:
                post_data["query"]['missing_result'] = {
                    "missing": {
                        "field": req_data.get('stat_split_field', '')
                    }
                }
            if req_data.get('stat_chartType', '') and req_data.get('stat_split', ''):
                need_timeline = True
                if final_stats_type == 'stats' or final_stats_type == "cardinality":
                    post_data["query"] = {
                        "step2": {
                            "timeline": {
                                "period": req_data.get('stat_split', '')
                            },
                            "group": {
                                "timeline_result": {
                                    final_stats_type: {
                                        "field": req_data.get('stat_split_field', '')
                                    }
                                }
                            }

                        }
                    }
                else:
                    post_data["query"]["step2"]['group'] = {
                        "timeline_result": {
                            "timeline": {
                                "period": req_data.get('stat_split', '')
                            }
                        }
                    }
        elif step and step == "step3":
            ori_statis_type = req_data.get('stat_method', 'count')
            mid_statis_type = "stats" if ori_statis_type in ["sum", "max", "min", "avg"] else ori_statis_type
            final_stats_type = "terms" if mid_statis_type == "count" else mid_statis_type
            post_data["query"] = {
                "step3": {
                    final_stats_type: {
                        "field": req_data.get('stat_split_field', '')
                    }
                }
            }
            need_other = True if req_data.get('stat_other', False) and req_data.get('stat_other',
                                                                                    False) != 'false' else False
            if req_data.get('stat_chartType', '') and need_other:
                post_data["query"]['missing_result'] = {
                    "missing": {
                        "field": req_data.get('stat_split_field', '')
                    }
                }
            if req_data.get('stat_chartType', '') and req_data.get('stat_split', ''):
                need_timeline = True
                if final_stats_type == 'stats' or final_stats_type == "cardinality":
                    post_data["query"] = {
                        "step3": {
                            "timeline": {
                                "period": req_data.get('stat_split', '')
                            },
                            "group": {
                                "timeline_result": {
                                    final_stats_type: {
                                        "field": req_data.get('stat_split_field', '')
                                    }
                                }
                            }

                        }
                    }
                else:
                    post_data["query"]["step3"]['group'] = {
                        "timeline_result": {
                            "timeline": {
                                "period": req_data.get('stat_split', '')
                            }
                        }
                    }

        if is_param:
            res = BackendRequest.multi_search({
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "size": is_param["size"],
                "page": int(is_param["page"]) - 1,
                "filter_field": is_param["filters"],
                "source_group": is_param["source_group"],
                "category": "api_stat"

            }, post_data)
            print post_data
            if res["result"]:
                data = {
                    "status": 1,
                    "list": []
                }
                if step == 'step1':
                    if not need_timeline:
                        total = res['total']
                        in_use = 0
                        for i in res["data"][step]["buckets"]:
                            data["list"].append({
                                "name": i['key'],
                                "count": i['doc_count']
                            })
                            in_use += i['doc_count']
                        if need_other:
                            missing = res['data']['missing_result']['doc_count']

                            data["list"].append({
                                "name": 'other',
                                "count": total - missing - in_use
                            })
                    else:
                        for result in res['data'][step]["buckets"]:
                            val = {
                                "start_time": result["timeline_result"]["buckets"][0]["from"],
                                "end_time": result["timeline_result"]["buckets"][len(result["timeline_result"]["buckets"]) - 1]["to"],
                                "name": result["key"],
                                "arr": []
                            }
                            span_arr = []
                            for b_index, bucket in enumerate(result["timeline_result"]["buckets"]):
                                span_arr.append(bucket["to"] - bucket["from"])

                                if b_index != len(result["timeline_result"]["buckets"]) - 1:
                                    val["arr"].append([int(bucket["to"]), bucket.get("doc_count", 0)])
                                else:
                                    val["arr"].append(
                                        [int(result["timeline_result"]["buckets"][0]["to"] + (max(span_arr) * (len(result[
                                            "timeline_result"]["buckets"]) - 1) )),
                                         bucket.get("doc_count"), 0])
                            val["range"] = max(span_arr)
                            data["list"].append(val)
                elif step == 'step2':
                    if not need_timeline:
                        stat_key = "buckets" if req_data.get('stat_method', 'count') == "count" else req_data.get(
                            'stat_method', 'count')
                        stat_key = "value" if stat_key == "cardinality" else stat_key


                        total = res['total']
                        in_use = 0

                        try:
                            if req_data.get('stat_method', 'count') == "count":
                                for p in res["data"][step]["buckets"]:
                                    data["list"].append({
                                        "name": p['key'],
                                        "count": p['doc_count'],
                                        "stats_method": req_data.get('stat_method', 'count'),
                                        "stats": p['doc_count']
                                    })
                                    in_use += p['doc_count']
                            else:
                                data["list"].append({
                                    "name": req_data.get('stat_field', ''),
                                    "count": res["data"][step][stat_key],
                                    "stats_method": req_data.get('stat_method', 'count'),
                                    "stats": res["data"][step][stat_key] if not req_data.get('stat_method',
                                    'count') == 'avg' else float('%.2f' % res["data"][step][stat_key])
                                })
                            if need_other:
                                missing = res['data']['missing_result']['doc_count']

                                data["list"].append({
                                    "name": 'other',
                                    "count": total - missing - in_use
                                })
                        except:
                            data = err_data.build_error(res)
                    else:
                        if req_data.get('stat_method', 'count') == "count":
                            for result in res['data'][step]["buckets"]:
                                val = {
                                    "start_time": result["timeline_result"]["buckets"][0]["from"],
                                    "end_time":
                                        result["timeline_result"]["buckets"][len(result["timeline_result"]["buckets"]) - 1][
                                            "to"],
                                    "name": result["key"],
                                    "arr": []
                                }
                                span_arr = []
                                for b_index, bucket in enumerate(result["timeline_result"]["buckets"]):
                                    span_arr.append(bucket["to"] - bucket["from"])

                                    if b_index != len(result["timeline_result"]["buckets"]) - 1:
                                        val["arr"].append([int(bucket["to"]), bucket.get("doc_count", 0)])
                                    else:
                                        val["arr"].append(
                                            [int(result["timeline_result"]["buckets"][0]["to"] + (
                                                max(span_arr) * (len(result[
                                                "timeline_result"]["buckets"]) - 1) )),
                                             bucket.get("doc_count"), 0])
                                val["range"] = max(span_arr)
                                data["list"].append(val)
                        else:
                            result = res['data'][step]
                            stat_key = req_data.get('stat_method', 'count')
                            stat_key = "value" if req_data.get('stat_method', 'count') == "cardinality" else stat_key
                            val = {
                                "start_time": result["buckets"][0]["from"],
                                "end_time":result["buckets"][len(result["buckets"]) - 1]["to"],
                                "name": req_data.get('stat_field', ''),
                                "arr": []
                            }
                            span_arr = []
                            for b_index, bucket in enumerate(result["buckets"]):
                                span_arr.append(bucket["to"] - bucket["from"])

                                if b_index != len(result["buckets"]) - 1:
                                    val["arr"].append([int(bucket["to"]), bucket["timeline_result"].get(stat_key, 0)])
                                else:
                                    val["arr"].append(
                                        [int(result["buckets"][0]["to"] + (max(span_arr) * (len(result["buckets"]) - 1) )),
                                         bucket["timeline_result"].get(stat_key, 0),0])
                            val["range"] = max(span_arr)
                            data["list"].append(val)
                elif step == 'step3':
                    if not need_timeline:
                        stat_key = "buckets" if req_data.get('stat_method', 'count') == "count" else req_data.get(
                            'stat_method', 'count')
                        stat_key = "value" if stat_key == "cardinality" else stat_key

                        total = res['total']
                        in_use = 0

                        try:
                            if req_data.get('stat_method', 'count') == "count":
                                for p in res["data"][step]["buckets"]:
                                    data["list"].append({
                                        "name": p['key'],
                                        "count": p['doc_count'],
                                        "stats_method": req_data.get('stat_method', 'count'),
                                        "stats": p['doc_count']
                                    })
                                    in_use += p['doc_count']
                            else:
                                data["list"].append({
                                    "name": req_data.get('stat_field', ''),
                                    "count": res["data"][step][stat_key],
                                    "stats_method": req_data.get('stat_method', 'count'),
                                    "stats": res["data"][step][stat_key] if not req_data.get('stat_method',
                                    'count') == 'avg' else float('%.2f' % res["data"][step][stat_key])
                                })
                            if need_other:
                                missing = res['data']['missing_result']['doc_count']

                                data["list"].append({
                                    "name": 'other',
                                    "count": total - missing - in_use
                                })
                        except:
                            data = err_data.build_error(res)
                    else:
                        if req_data.get('stat_method', 'count') == "count":
                            for result in res['data'][step]["buckets"]:
                                val = {
                                    "start_time": result["timeline_result"]["buckets"][0]["from"],
                                    "end_time":
                                        result["timeline_result"]["buckets"][
                                            len(result["timeline_result"]["buckets"]) - 1][
                                            "to"],
                                    "name": result["key"],
                                    "arr": []
                                }
                                span_arr = []
                                for b_index, bucket in enumerate(result["timeline_result"]["buckets"]):
                                    span_arr.append(bucket["to"] - bucket["from"])

                                    if b_index != len(result["timeline_result"]["buckets"]) - 1:
                                        val["arr"].append([int(bucket["to"]), bucket.get("doc_count", 0)])
                                    else:
                                        val["arr"].append(
                                            [int(result["timeline_result"]["buckets"][0]["to"] + (
                                                max(span_arr) * (len(result[
                                                    "timeline_result"]["buckets"]) - 1) )),
                                             bucket.get("doc_count"), 0])
                                val["range"] = max(span_arr)
                                data["list"].append(val)
                        else:
                            result = res['data'][step]
                            stat_key = req_data.get('stat_method', 'count');
                            stat_key = "value" if req_data.get('stat_method', 'count') == "cardinality" else stat_key
                            val = {
                                "start_time": result["buckets"][0]["from"],
                                "end_time": result["buckets"][len(result["buckets"]) - 1]["to"],
                                "name": req_data.get('stat_field', ''),
                                "arr": []
                            }
                            span_arr = []
                            for b_index, bucket in enumerate(result["buckets"]):
                                span_arr.append(bucket["to"] - bucket["from"])

                                if b_index != len(result["buckets"]) - 1:
                                    val["arr"].append([int(bucket["to"]), bucket["timeline_result"].get(stat_key, 0)])
                                else:
                                    val["arr"].append(
                                        [int(result["buckets"][0]["to"] + (
                                            max(span_arr) * (len(result["buckets"]) - 1) )),
                                         bucket["timeline_result"].get(stat_key, 0), 0])
                            val["range"] = max(span_arr)
                            data["list"].append(val)

            else:
                data = err_data.build_error(res)
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        return result

    def _get_statis(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        if is_param:
            res = BackendRequest.search({
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "size": is_param["size"],
                "page": int(is_param["page"]) - 1,
                "filter_field": is_param["filters"],
                "category": is_param["type"],
                "field": req_data.get("field", ""),
                "source_group": is_param["source_group"],
                "stat_field": req_data.get("stat_field", ""),
                "stat_method": req_data.get("stat_method", ""),
                "stat_split_field": req_data.get("stat_split_field", "")
            })
            if res["result"]:
                stat_method = req_data.get("stat_method", "")
                data = {
                    "status": 1,
                    "data": []
                }
                for result in res["buckets"]:
                    val = {
                        "name": result["key"],
                        "arr": []
                    }
                    for bucket in result["result"]["buckets"]:
                        if stat_method == 'sum':
                            val["arr"].append([bucket["to"], bucket["sum_result"]["value"] or 0])
                        if stat_method == 'avg':
                            val["arr"].append([bucket["to"], bucket["avg_result"]["value"] or 0])
                        if stat_method == 'max':
                            val["arr"].append([bucket["to"], bucket["max_result"]["value"] or 0])
                        if stat_method == 'min':
                            val["arr"].append([bucket["to"], bucket["min_result"]["value"] or 0])
                    data["data"].append(val)
                    # print "#########################data:", data["data"]
            else:
                data = err_data.build_error(res)
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        return result

    def _search_newstatis(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            # print '###################request.GET: ',request.GET
            if request.GET['visType'] == 'SJSFDTJ_TIME' or request.GET['visType'] == 'SJSFDTJ_VALUE':
                resdata = self._get_newstatis_SJSFDTJ(request, auth_result, **kwargs)
            elif request.GET['visType'] == 'ZFT_TIME' or request.GET['visType'] == 'ZFT_VALUE':
                resdata = self._get_newstatis_ZFT(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _get_newstatis_SJSFDTJ(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        if is_param:
            res = BackendRequest.search({
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "size": is_param["size"],
                "page": int(is_param["page"]) - 1,
                "filter_field": is_param["filters"],
                "source_group": is_param["source_group"],

                "category": req_data.get("category","range"),
                "stat_field": req_data.get("stat_field", ""),
                "stat_method": req_data.get("stat_method", ""),
                "stat_ranges": req_data.get("stat_ranges", ""),
            })
            # print '#####################res: ',res
            if res["result"]:
                data = {
                    "status": 1,
                    "data": res.get('buckets',[])
                }
            else:
                data = err_data.build_error(res)
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        return result

    def _get_newstatis_ZFT(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        if is_param:
            res = BackendRequest.search({
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "size": is_param["size"],
                "page": int(is_param["page"]) - 1,
                "filter_field": is_param["filters"],
                "source_group": is_param["source_group"],

                "category": req_data.get("category","range"),
                "stat_field": req_data.get("stat_field", ""),
                "stat_method": req_data.get("stat_method", ""),
                "stat_interval": req_data.get("stat_interval", ""),
            })
            # print '#####################res: ',res
            if res["result"]:
                data = {
                    "status": 1,
                    "data": res.get('buckets',[])
                }
            else:
                data = err_data.build_error(res)
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        return result

    def _get_grid_events(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        page = int(is_param["page"]) - 1
        if is_param:
            param = {
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "size": is_param["size"],
                "page": page,
                "filter_field": is_param["filters"],
                "category": is_param["type"],
                "exist_fields": is_param["exist_fields"],
                "field": req_data.get("field", ""),
                # "source_group": "0811test"
                "source_group": is_param["source_group"]
            }
            res = BackendRequest.search(param)
            if res["result"]:
                _events = res.get('events', [])
                data = {
                    "status": 1,
                    "events": self._build_events(_events) if _events else []
                }
            else:
                data = err_data.build_error(res)
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            result = bundle
        return result

    def _search_download(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            resdata = self._get_search_download(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _get_search_download(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        col = req_data.get("cols", [])
        raw_message_only = req_data.get("only", "no")
        if is_param:
            group_id = req_data.get("groupId", "")
            if group_id:
                param = {
                    "jid": group_id,
                    "category": is_param["type"],
                    "token": auth_result["t"],
                    "operator": auth_result["u"],
                    "owner_name": auth_result["u"],
                    "owner_id": auth_result["i"],
                    "size": 1000,
                    "page": 0
                }
            else:
                param = {
                    "query": is_param["query"],
                    "token": auth_result["t"],
                    "operator": auth_result["u"],
                    "owner_name": auth_result["u"],
                    "owner_id": auth_result["i"],
                    "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                    "order": is_param["order"],
                    "size": 10000,
                    "page": 0,
                    "filter_field": is_param["filters"],
                    "category": is_param["type"],
                    "field": req_data.get("field", ""),
                    # "source_group": "0811test"
                    "source_group": is_param["source_group"]
                }
            res = BackendRequest.search(param)
            if res["result"]:
                if "groups" in res:
                    _groups = res.get('groups', [])
                    evs = {
                        "status": 1,
                        "total": res["total"],
                        "page": int(res["page"]),
                        "size": res["size"],
                        "type": "trans",
                        "events": self._build_csv_groups(_groups) if _groups else []
                    }

                else:
                    _with_stats = 'yes' if "stats" in res else 'no'
                    if _with_stats == "yes":
                        _events = res['hits'].get('hits', [])
                        total = res['hits']["total"]

                    else:
                        _events = res.get('events', [])
                        total = res["total"]

                    evs = {
                        "status": 1,
                        "total": total,
                        "page": int(res.get("page", 1)),
                        "size": res.get("size", 20),
                        "type": "search",
                        "events": self._build_csv_events(_events) if _events else []
                    }
                file_name = self._build_csv(col, evs["events"], evs["type"], auth_result["d"], auth_result["u"],
                                            raw_message_only)
                data = {
                    "status": 1,
                    "fileName": file_name
                }
            else:
                data = err_data.build_error(res)
            dummy_data = data
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        result = bundle
        return result

    def _search_spl_download(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        if auth_result:
            resdata = self._get_search_spl_download(request, auth_result, **kwargs)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _get_search_spl_download(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        col = req_data.get("cols", [])
        raw_message_only = req_data.get("only", "no")
        if is_param:
            param = {
                "query": is_param["query"],
                "token": auth_result["t"],
                "operator": auth_result["u"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "size": 10000,
                "page": 0,
                "filter_field": is_param["filters"],
                "field": req_data.get("field", ""),
                "category": "events",
                "usetable": "true",
                # "source_group": "0811test"
                "source_group": is_param["source_group"]
            }
            res = BackendRequest.search(param)
            if res["result"]:
                search_type, body, hits = self._build_body_simple(res)
                evs = {
                    "table": {
                        "head": res.get("_field_infos_", []),
                        "body": body
                    }
                }
                columns = req_data.get("columns", "")
                file_name = self._build_table_csv(evs["table"], auth_result["d"], auth_result["u"], columns)
                data = {
                    "status": 1,
                    "fileName": file_name
                }
            else:
                data = err_data.build_error(res)
            dummy_data = data
        else:
            data = err_data.build_error({}, "parameter is wrong")
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        result = bundle
        return result

    def _search_context(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        auth_res = True
        if auth_result:
            resdata = self._get_search_context(request, auth_result, **kwargs)
        else:
            dummy_data = {
                "status": "0",
                "redirect": "/auth/login/"
            }
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def _get_search_context(self, request, auth_result, **kwargs):
        is_param = self.checkParam(request, **kwargs)
        req_data = request.GET
        col = req_data.get("cols", [])
        raw_message_only = req_data.get("only", "no")
        if is_param:
            param = {
                "query": is_param["query"],
                "operator": auth_result["u"],
                "token": auth_result["t"],
                "time_range": "-1d,now" if is_param["time_range"] == "," else is_param["time_range"],
                "order": is_param["order"],
                "size": is_param["size"],
                "page": 0,
                "filter_field": is_param["filters"],
                "field": req_data.get("field", ""),
                "search_query": req_data.get("searchQuery", ""),
                "source_group": is_param["source_group"]
            }
            res = BackendRequest.context_search(param)
            if res["rc"] == 0:
                if "groups" in res:
                    _groups = res.get('groups', [])
                    data = {
                        "status": '1',
                        "total": res["total"],
                        "page": int(res["page"]),
                        "size": res["size"],
                        "type": "trans",
                        "events": self._build_csv_groups(_groups) if _groups else []
                    }

                else:
                    # _events = res['hits'].get('hits', [])
                    results = res.get('result', {})
                    _events = results.get('sheets', [])
                    data = {
                        "status": '1',
                        "type": "search",
                        "events": self._build_context_events(_events) if _events else []
                    }
            else:
                data = {
                    "status": 0,
                    "msg": "search error"
                }
            dummy_data = data
        else:
            data = {
                "status": 0,
                "msg": "search error"
            }
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        result = bundle
        return result

    def _build_context_events(self, events):
        rst = []
        rows = events.get("rows", [])
        for item in rows:
            rst.append({
                "context_id": str(item.get("context_id", '0')),
                "raw_message": item.get("raw_message", ""),
            })
        return rst

    def _build_csv(self, col, events, type, domain, user, raw_only):
        if raw_only == "yes":
            new_col = ["raw_message"]
        else:
            new_col = col.split(',') if col else []
        rows = []
        for row in events:
            a_row = []
            for a in new_col:
                val = row.get(a, "")
                new_val = ",".join([str(el) for el in val]) if isinstance(val, list) else val
                val = new_val.encode('utf-8') if isinstance(new_val, str) else new_val
                if a == "timestamp":
                    str_t = str(val)
                    if len(str_t) > 10 and len(str_t) == 13:
                        m_s = str_t[-3:]
                        r_s = str_t[:-3]
                        val = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(r_s))) + '.' + str(m_s)
                a_row.append(val)
            rows.append(a_row)
        root_path = os.getcwd()
        my_var = MyVariable()
        data_path = my_var.get_var('path', 'data_path')
        tmp_path = data_path + "yottaweb_tmp/" + domain + "/" + user + "/"
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        # remove old file first
        for old_file in os.listdir(tmp_path):
            target_file = os.path.join(tmp_path, old_file)
            if os.path.isfile(target_file):
                os.remove(target_file)
        # write new csv file
        name = 'rizhiyi_' + user.encode("utf-8") + '_' + time.strftime('%Y%m%d%H%M%S', time.localtime())
        file_name = str(name) + ".csv"
        file_path = tmp_path + file_name
        f = open(file_path, "wb+")
        # write bom to resolve unreadable chinese problem
        f.write("\xEF\xBB\xBF")
        writer = csv.writer(f)
        writer.writerow(new_col)
        for line in rows:
            writer.writerow(line)
        return file_name

    def _build_table_csv(self, table, domain, user, columns):
        _col = []
        rows = []
        columns_arr = columns.split(",")
        print columns_arr
        for head in table["head"]:
            _col.append(head["name"])
        new_col = []
        for custom_column in columns_arr:
            if columns_arr and custom_column in _col:
                new_col.append(custom_column)
        new_col = new_col if new_col else _col
        for row in table["body"]:
            a_row = []
            for a in new_col:
                val = row.get(a, "")
                new_val = ",".join([str(el) for el in val]) if isinstance(val, list) else val
                val = new_val.encode('utf-8') if isinstance(new_val, str) else new_val
                if a == "timestamp":
                    str_t = str(val)
                    if len(str_t) > 10 and len(str_t) == 13:
                        m_s = str_t[-3:]
                        r_s = str_t[:-3]
                        val = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(r_s))) + '.' + str(m_s)
                a_row.append(val)
            rows.append(a_row)

        my_var = MyVariable()
        data_path = my_var.get_var('path', 'data_path')
        tmp_path = data_path + "yottaweb_tmp/" + domain + "/" + user + "/"
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        # remove old file first
        for old_file in os.listdir(tmp_path):
            target_file = os.path.join(tmp_path, old_file)
            if os.path.isfile(target_file):
                os.remove(target_file)
        # write new csv file
        name = 'rizhiyi_search_' + user.encode("utf-8") + '_' + time.strftime('%Y%m%d%H%M%S', time.localtime())
        file_name = str(name) + ".csv"
        file_path = tmp_path + file_name
        f = open(file_path, "wb+")
        # write bom to resolve unreadable chinese problem
        f.write("\xEF\xBB\xBF")
        writer = csv.writer(f)
        writer.writerow(new_col)
        for line in rows:
            writer.writerow(line)
        return file_name

    def _build_events(self, logs):
        result = []
        for i in logs:
            tokens = i.get("tokens", [])
            source = i.get("_source", {})
            tmp_fields = i.get("fields", {})
            a_event = {}
            _fields = {}
            _static_fields = {}
            for (k, v) in source.items():
                if k == "hostname" or k == "timestamp" or k == "tag" or \
                        k == "raw_message" or k == "appname" or k == "logtype" or k == "security":
                    _fields[k] = v
                else:
                    _static_fields[k] = v
                    _fields[k] = v
            a_event["_tmp_fields"] = tmp_fields

            a_event["_cus_fields"] = _fields
            a_event["_static_fields"] = _static_fields
            hlight = i.get("highlight", {"raw_message": [""]})
            high_light = hlight["raw_message"][0]
            hl = re.findall(r'<em>(.*?)</em>', high_light)
            # tokens = sorted(tokens, key=len, reverse=True)
            raw_msg = source.get("raw_message", "")
            ori = [{
                       "s": raw_msg,
                       "find": False
                   }]
            target = self.contribute(tokens, ori, hl)
            a_event["_cus_raw"] = {
                # "tokens": tokens,
                "segment_tree": target
            }
            result.append(a_event)
        return result

    def _build_csv_events(self, logs):
        result = []
        for i in logs:
            tokens = i.get("tokens", [])
            source = i.get("_source", {})
            tmp_fields = i.get("fields", {})
            a_event = {}
            _fields = {}
            _static_fields = {}

            _fields = self._multi_to_one(source, "")
            # a_event["_tmp_fields"] = tmp_fields

            # a_event["_cus_fields"] = _fields
            # raw_msg = source.get("raw_message", "")

            result.append(_fields)
        return result

    def _multi_to_one(self, obj, parent):
        rst = {}
        for (k, v) in obj.items():
            new_k = parent + "." + k if parent else k
            if v and isinstance(v, dict):
                y = self._multi_to_one(v, new_k)
                rst = dict(rst, **y)
            else:
                rst[new_k] = v
        return rst

    def _build_csv_groups(self, groups):
        result = []
        for group in groups:
            source = group.get("source", [])
            events = []
            cus_fields = {}
            own_fields = {
                "hostname": [],
                "appname": [],
                "logtype": [],
                "tag": []
            }
            key_field = group.get("fields", {})
            key_timestamp = group.get("min_timestamp", 0)
            for event in source:
                events.append(event["raw_message"])
                own_fields["hostname"].append(event.get("hostname", ""))
                own_fields["appname"].append(event.get("appname", ""))
                own_fields["logtype"].append(event.get("logtype", ""))
                if event.get("security", {}):
                    own_fields["security"] = {}
                    own_fields["security"] = self.merge_dict(own_fields["security"], event.get("security", {}))
                own_fields["tag"] = list(set(own_fields["tag"]+event["tag"]))
                cus_fields = self.merge_dict(cus_fields, event)
                del cus_fields["hostname"]
                if "appname" in cus_fields:
                    del cus_fields["appname"]
                if "logtype" in cus_fields:
                    del cus_fields["logtype"]
                if "tag" in cus_fields:
                    del cus_fields["tag"]
                if "security" in cus_fields:
                    del cus_fields["security"]
                del cus_fields["timestamp"]
                del cus_fields["raw_message"]
            own_fields["hostname"] = list(set(own_fields["hostname"]))
            own_fields["appname"] = list(set(own_fields["appname"]))
            final_fields = dict(own_fields, **cus_fields)
            result.append(final_fields)
        rtn = []
        for i in result:
            _fields = self._multi_to_one(i, "")
            rtn.append(_fields)
        return rtn

    def _build_groups(self, groups):
        result = []
        for group in groups:
            source = group.get("source", [])
            events = []
            cus_fields = {}
            own_fields = {
                "hostname": [],
                "appname": [],
                "logtype": [],
                "tag": []
            }
            key_field = group.get("fields", {})
            key_timestamp = group.get("min_timestamp", 0)
            for event in source:
                event["context_id"] = str(event["context_id"]) if event["context_id"] else ""
                events.append(event["raw_message"])
                own_fields["hostname"].append(event.get("hostname", ""))
                own_fields["appname"].append(event.get("appname", ""))
                own_fields["logtype"].append(event.get("logtype", ""))
                if event.get("security", {}):
                    own_fields["security"] = {}
                    own_fields["security"] = self.merge_dict(own_fields["security"], event.get("security", {}))
                own_fields["tag"] = list(set(own_fields["tag"] + event["tag"]))
                cus_fields = self.merge_dict(cus_fields, event)
                if "hostname" in cus_fields:
                    del cus_fields["hostname"]
                if "appname" in cus_fields:
                    del cus_fields["appname"]
                if "logtype" in cus_fields:
                    del cus_fields["logtype"]
                if "tag" in cus_fields:
                    del cus_fields["tag"]
                if "security" in cus_fields:
                    del cus_fields["security"]
                del cus_fields["timestamp"]
                del cus_fields["raw_message"]
            own_fields["hostname"] = list(set(own_fields["hostname"]))
            own_fields["appname"] = list(set(own_fields["appname"]))
            own_fields["logtype"] = list(set(own_fields["logtype"]))
            result.append({
                "events": events,
                "key_field": key_field,
                "key_timestamp": key_timestamp,
                "own_fields": own_fields,
                "cus_fields": cus_fields
            })
        return result

    def _build_stats(self, stats):
        is_bucket = False
        for l in stats:
            if "bucket" in l:
                is_bucket = True
                break
        if len(stats) > 0 and is_bucket:
            result = {
                "heads": [],
                "by": [],
                "x_arr": [],
                "y_arr": [],
                "list": [],
                "method": "bucket",
                "method_cnt": 1
            }
            row_one = stats[0]

            result["x_arr"] = row_one["bucket"]

            tmp_heads = []
            if "fields" in row_one:
                tmp_heads.append("fields")
                bucket_field = row_one["bucket"][0]
                for (k, v) in row_one["fields"].items():
                    result["heads"].append(k)
                    if not k == bucket_field:
                        result["by"].append(k)
            if "eval" in row_one:
                tmp_heads.append("eval")
                for (k, v) in row_one["eval"].items():
                    result["heads"].append(k)
                    result["y_arr"].append(k)
            for (method, value) in row_one.items():
                if not method == "eval" and not method == "fields" and not method == "bucket":
                    tmp_heads.append(method)
                    if "as_field" in value:
                        result["heads"].append(value["as_field"])
                        result["y_arr"].append(value["as_field"])
                    else:
                        result["heads"].append(method)
                        result["y_arr"].append(method)

            # print result["heads"]
            for item in stats:
                val = {}
                for key in tmp_heads:
                    if key == "eval" or key == "fields":
                        for (k, v) in item[key].items():
                            val[k] = v
                    else:
                        if "as_field" in item[key]:
                            val[item[key]["as_field"]] = item[key]["value"]
                        else:
                            val[key] = item[key]["value"]
                result["list"].append(val)

        else:
            result = {
                "method_cnt": 0,
                "list": []
            }
            for row in stats:
                col = {
                    "fields": {},
                    "content": []
                }
                if "fields" in row:
                    col["fields"] = row["fields"]
                    # for (k, v) in row["fields"].items():
                    #     col.append({
                    #         k: v
                    #     })
                    del row["fields"]
                if "eval" in row:
                    col["eval"] = row["eval"]
                    del row["eval"]
                method_cnt = 0
                for (method, value) in row.items():
                    val = {
                        "method": "",
                        "field": "",
                        "alias": "",
                        "values": []
                    }
                    a_val = []
                    m = re.search("(^.+)\((.*)\)$", method)
                    sub_method = m.group(1)
                    field = m.group(2)
                    alias = value.get("as_field", "")
                    if sub_method in ["max", "min", "avg", "count", "sum", "distinct_count", "dc"]:
                        if alias:
                            method = alias
                        a_val.append({
                            method: value.get("value", "")
                        })

                    if sub_method == 'extended_stat'  or sub_method == 'es' or sub_method == 'extend_stat':
                        a_val.append({"count": value["count"]})
                        a_val.append({"max": value["max"]})
                        a_val.append({"min": value["min"]})
                        a_val.append({"sum": value["sum"]})
                        a_val.append({"avg": float('%.3f' % value["avg"])})
                        a_val.append({"variance": float('%.3f' % value["variance"])})
                        a_val.append({"sum_of_squares": float(value["sum_of_squares"])})
                        a_val.append({"std_deviation": float('%.3f' % value["std_deviation"])})

                    if sub_method == "percentiles"  or sub_method == 'pct':
                        for (m, n) in value["values"].items():
                            a_val.append({
                                m: n
                            })
                        a_val = sorted(a_val, key=lambda x: float(x.keys()[0]))
                    if sub_method == "percentile_ranks" or sub_method == 'pct_ranks':
                        for (m, n) in value["values"].items():
                            a_val.append({
                                m: float('%.3f' % n)
                            })
                        a_val = sorted(a_val, key=lambda x: float(x.keys()[0]))
                    if sub_method == "date_histogram" or sub_method == 'dhg':
                        for k in value["buckets"]:
                            a_val.append({
                                k["key"]: k["doc_count"]
                            })
                    if sub_method == "top":
                        # cus_count = 0
                        for k in value["buckets"]:
                            a_val.append({
                                k["key"]: k["doc_count"]
                            })
                            # cus_count = cus_count + k["doc_count"]
                        other = value.get("other", 0)

                        if other:
                            a_val.append({
                                "other": int(other)
                            })

                    if sub_method == "histogram"  or sub_method == 'hg':
                        for k in value["buckets"]:
                            a_val.append({
                                "doc_count": k["doc_count"],
                                "from": k["key"],
                                "to": k["key"] + value["interval"]
                            })
                    if sub_method == "range" or sub_method == 'range_bucket' or sub_method == 'rb':
                        for k in value["buckets"]:
                            a_val.append(k)

                    val["field"] = field
                    val["method"] = sub_method
                    val["alias"] = alias if alias else method
                    val["values"] = a_val
                    method_cnt += 1
                    col["content"].append(val)
                result['method_cnt'] = method_cnt
                result["list"].append(col)
        return result

    def _build_time_line(self, tl):
        time_line = []
        buckets = []
        event_counts = tl.get('event_counts', {})
        if event_counts:
            buckets = event_counts.get('buckets', [])
        span_arr = []# 起终点所在的区间一定小于正当的子段时间宽度，求max方式可避免所有异常情况
        for index, i in enumerate(buckets):
            span_arr.append(i["to"] - i["from"])
            if index != len(buckets) - 1:
                time_line.append([i["to"], i["doc_count"]])
            else:
                time_line.append([buckets[0]["to"] + (max(span_arr) * (len(buckets) - 1)), i["doc_count"]])
        rtn_data = {
            "start_time": buckets[0]["from"],
            "end_time": buckets[len(buckets) - 1]["to"],
            "range": max(span_arr),
            "time_line": time_line
        }
        return rtn_data

    def _build_fields_new(self, fl):
        res = {
            "all": [],
            "num": [],
            "ot": [],
            "json": {}
        }
        _tmp_field = []
        for item in fl:
            if item["type"] == "long" or item["type"] == "int" or item["type"] == "double" :
                res["num"].append(item["name"])
            else:
                if item["name"] == "logtype" or item["name"] == "tag" or item["name"] == "appname" or item["name"] == "hostname":
                    res["ot"].insert(0, item["name"])
                elif item["name"] == "raw_message":
                    pass
                else:
                    res["ot"].append(item["name"])
            if item["name"] == "logtype" or item["name"] == "tag" or item["name"] == "appname" or item["name"] == "hostname":
                res["all"].insert(0, item["name"]+":"+item["type"])
                _tmp_field.insert(0, item["name"]+":"+item["type"])
            elif item["name"] == "raw_message":
                pass
            else:
                res["all"].append(item["name"]+":"+item["type"])
                _tmp_field.append(item["name"]+":"+item["type"])
        res['json']['General'] = {}
        for v in _tmp_field:
            current_level = res['json']
            vc = v.split('.')
            if len(vc) == 1:
                res['json']['General'][v] = {}
            else:
                for part in vc:
                    if part not in current_level:
                        current_level[part] = {}
                    current_level = current_level[part]
        if 'appname:string' in res['json']:
            res['json']['General']['appname:string'] = res['json'].pop('appname:string')
        if 'hostname:string' in res['json']:
            res['json']['General']['hostname:string'] = res['json'].pop('hostname:string')
        if 'logtype:string' in res['json']:
            res['json']['General']['logtype:string'] = res['json'].pop('logtype:string')
        if 'tag:string' in res['json']:
            res['json']['General']['tag:string'] = res['json'].pop('tag:string')
        res['tree'] = self.generateTree(res['json'])
        return res

    def generateTree(self, _in_obj):
        _tmp_list = []
        if 'General' in _in_obj:
            item = 'General'
            _item_arr = item.split(':')
            _tmp_item = {
                "type": _item_arr[-1] if len(_item_arr) > 1 else 'string',
                "label": ':'.join(_item_arr[:-1]) if len(_item_arr) > 1 else item
            }
            if _in_obj[item] and not 'children' in _tmp_item:
                _tmp_item['children'] = []
            if _in_obj[item]:
                _tmp_item['children'] = self.generateTree(_in_obj[item])
            _tmp_list.append(_tmp_item)
        for item in _in_obj:
            if item != 'General':
                _item_arr = item.split(':')
                _tmp_item = {
                    "type": _item_arr[-1] if len(_item_arr) > 1 else 'string',
                    "label": ':'.join(_item_arr[:-1]) if len(_item_arr) > 1 else item
                }
                if _in_obj[item] and not 'children' in _tmp_item:
                    _tmp_item['children'] = []
                if _in_obj[item]:
                    _tmp_item['children'] = self.generateTree(_in_obj[item])
                _tmp_list.append(_tmp_item)
        return _tmp_list



    def _build_fields(self, fl):
        res = {
            "all": [],
            "num": [],
            "ot": [],
            "json": {}
        }
        if fl.count("log_type:string") > 0:
            fl.remove("log_type:string")
            fl.insert(0, "log_type:string")
        if fl.count("logtype:string") > 0:
            fl.remove("logtype:string")
            fl.insert(0, "logtype:string")
        if fl.count("tag:string") > 0:
            fl.remove("tag:string")
            fl.insert(0, "tag:string")
        if fl.count("appname:string") > 0:
            fl.remove("appname:string")
            fl.insert(0, "appname:string")
        if fl.count("hostname:string") > 0:
            fl.remove("hostname:string")
            fl.insert(0, "hostname:string")
        if fl.count("raw_message:string") > 0:
            fl.remove("raw_message:string")
        if fl.count("timestamp:long") > 0:
            fl.remove("timestamp:long")
        temp = []
        for item in fl:
            ai = item.split(':')
            # if ai[0] in res["num"]:
            #     continue
            # if ai[0] in res["ot"]:
            #     del res["ot"][res["ot"].index(ai[0])]
            #     try:
            #         del res["all"][res["all"].index(ai[0]+":string")]
            #         del temp[temp.index(ai[0] + ":string")]
            #     except Exception, e:
            #         logger = logging.getLogger("django.request")
            #         logger.info("field error: %s", item)

            if ai[1] == "long" or ai[1] == "double":
                res["num"].append(ai[0])
            else:
                res["ot"].append(ai[0])
            res["all"].append(item)
            temp.append(item)
        for v in temp:
            current_level = res['json']
            vc = v.split('.')
            for part in vc:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
        res['json']['overview'] = {}
        if 'appname:string' in res['json']:
            res['json']['overview']['appname'] = res['json'].pop('appname:string')
        if 'hostname:string' in res['json']:
            res['json']['overview']['hostname'] = res['json'].pop('hostname:string')
        if 'logtype:string' in res['json']:
            res['json']['overview']['logtype'] = res['json'].pop('logtype:string')
        if 'tag:string' in res['json']:
            res['json']['overview']['tag'] = res['json'].pop('tag:string')

            # if sv[0] not in res['json'].keys:
            #     res['json'][sv[0]] = {}
            # if len(sv) > 2:


        # for item in fl:
        # if item == 'hostname'
        # res.append(item)
        # print fl
        # result = {}
        # for (k, v) in fl.items():
        # if isinstance(v, dict):
        #         for (a, b) in v.items():
        #             result[k+"."+a] = b
        #     else:
        #         result[k] = v
        # _fields = result

        return res

    def is_string(self, anobj):
        return isinstance(anobj, basestring)

    def is_num(self, value):
        try:
            value + 1
        except TypeError:
            return False
        else:
            return True

    def merge_dict(self, d1, d2):
        for k, v2 in d2.items():
            v1 = d1.get(k, [])
            v1 = [v1] if isinstance(v1, basestring) or isinstance(v1, int)  or isinstance(v1, long) else v1
            v2 = [v2] if isinstance(v2, basestring) or isinstance(v2, int)  or isinstance(v2, long) else v2
            if v1 and isinstance(v1, dict) and isinstance(v2, dict):
                d1[k] = self.merge_dict(v1, v2)
            elif v1 and isinstance(v1, list) and isinstance(v2, list):
                d1[k] = list(set(v1 + v2))
            elif v2:
                d1[k] = v2
        return d1

    def contribute_old(self, tokens, sor, hl):
        result = []
        find = False
        if len(tokens) > 500:
            return sor
        for i in sor:
            if not i["find"] and len(tokens) > 0 and re.search(tokens[0], i["s"], re.IGNORECASE):
                a_str = i["s"]
                m = re.search(tokens[0], i["s"], re.IGNORECASE)
                start = m.start()
                lens = len(tokens[0])
                st = a_str[0:start]
                cr = a_str[start:(start + lens)]
                ed = a_str[(start + lens):len(a_str)]
                if len(st) != 0:
                    result.append({
                        "s": st,
                        "find": False
                    })
                if len(cr) != 0:
                    result.append({
                        "s": cr,
                        "find": True,
                        "highlight": cr in hl
                    })
                if len(ed) != 0:
                    result.append({
                        "s": ed,
                        "find": False
                    })
                find = True
            else:
                result.append(i)
        if len(tokens) > 1:
            del tokens[0]
            result = self.contribute(tokens, result, hl)
        return result

    def contribute(self, tokens, sor, hl):
        result = sor
        find = False
        if len(tokens) > 500:
            return sor
        for token in tokens:
            a_str = result[-1]["s"]
            m = re.search(token, a_str, re.IGNORECASE)
            if m:
                start = m.start()
                lens = len(token)
                st = a_str[0:start]
                cr = a_str[start:(start + lens)]
                ed = a_str[(start + lens):len(a_str)]
                result.pop(-1)
                if len(st) != 0:
                    result.append({
                        "s": st,
                        "hover": True,
                        "find": False
                    })
                if len(cr) != 0:
                    result.append({
                        "s": cr,
                        "hover": True,
                        "find": True,
                        "highlight": cr in hl
                    })
                if len(ed) != 0:
                    result.append({
                        "s": ed,
                        "hover": True,
                        "find": False
                    })
        return result

    def search_permit_batch(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            permits = []
            permits.append({
                "target": "Download",
                "action": "Possess"
            })
            permits.append({
                "target": "Alert",
                "action": "Create"
            })
            permits.append({
                "target": "Pivot",
                "action": "Possess"
            })

            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            permit_param = {
                'permits': permits
            }
            permit_res = BackendRequest.batch_permit_can(param, permit_param)
            if permit_res['result']:
                permit_list = permit_res["short_permits"]
            else:
                permit_list = []
            dummy_data["status"] = "1"
            dummy_data["permit_list"] = permit_list
        else:
            data = err_data.build_error({}, "auth error!")
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp
