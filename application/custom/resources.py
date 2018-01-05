# -*- coding: utf-8 -*-
# wangqiushi (wang.qiushi@yottabyte.cn)
# 2015/11/21
# Copyright 2015 Yottabyte
# file description : application custom api

from tastypie import fields
from tastypie.resources import Resource
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.variable.resources import MyVariable
import ast
import json
import requests
import ConfigParser
import os
import re

err_data = ContributeErrorData()


class CustomResource(Resource):
    class Meta:
        resource_name = 'custom'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^application/(?P<resource_name>%s)/(?P<sid>[\w\d]+)/steps/$" % (self._meta.resource_name), self.wrap_view('steps'), name="api_step"),
            url(r"^application/(?P<resource_name>%s)/search/$" % (self._meta.resource_name),
                self.wrap_view('search'), name="api_search"),
            url(r"^application/(?P<resource_name>%s)/field/$" % (self._meta.resource_name),
                self.wrap_view('field'), name="api_field"),
            url(r"^application/(?P<resource_name>%s)/newfield/$" % (self._meta.resource_name),
                self.wrap_view('new_field'), name="api_field"),
            url(r"^application/(?P<resource_name>%s)/table/info/(?P<sid>[\w\d]+)/$" % (self._meta.resource_name), self.wrap_view('table_info'), name="api_step"),
        ]

    def steps(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        sid = kwargs.get('sid')

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            info = {}
            try:
                my_var = MyVariable()
                data_path = my_var.get_var('path', 'data_path')
                config_path = data_path + "custom"
                real_file = config_path + '/apps.json'
                with open(real_file, 'r') as f:
                    config = json.load(f)
                apps = config["apps"]
                for item in apps:
                    if item["id"] == sid:
                        info = item
            except Exception, e:
                print e
                info = {}
            dummy_data["status"] = "1"
            dummy_data["name"] = info.get("name", "")
            dummy_data["auto_search"] = info.get("auto_search", "no")
            dummy_data["sumSection"] = info.get("sumSection", {})
            dummy_data["steps"] = info.get("content", [])
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def table_info(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        sid = kwargs.get('sid')

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            info = {}
            try:
                my_var = MyVariable()
                data_path = my_var.get_var('path', 'data_path')
                config_path = data_path + "custom"
                real_file = config_path + '/tables.json'
                with open(real_file, 'r') as f:
                    config = json.load(f)
                tables = config["tables"]
                for item in tables:
                    if item["id"] == sid:
                        info = item
            except Exception, e:
                print e
                info = {}
            dummy_data["status"] = "1"
            dummy_data["table"] = info.get("content", {})
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        dummy_data = {}
        req_data = request.GET
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            group_id = req_data.get("group_id", "")
            if group_id:
                param = {
                    "jid": group_id,
                    "category": "events",
                    "token": es_check["t"],
                    "operator": es_check["u"],
                    "owner_name": es_check["u"],
                    "owner_id": es_check["i"],
                    "sid": req_data.get("sid", ""),
                    "size": req_data["size"],
                    "usetable": "true",
                    "page": int(req_data["page"]) - 1
                }
            else:
                param = {
                    "query": req_data["query"],
                    "token": es_check["t"],
                    "operator": es_check["u"],
                    "owner_name": es_check["u"],
                    "owner_id": es_check["i"],
                    "time_range": "-1d,now" if req_data["time_range"] == "," else req_data["time_range"],
                    "order": req_data.get("order", "desc"),
                    "size": req_data.get("size", 20),
                    "page": int(req_data.get("page", 1)) - 1,
                    "filter_field": req_data.get("filters", ""),
                    "field": req_data.get("field", ""),
                    # "source_group": "0811test"
                    "source_group": req_data.get("sourcegroup", "all")
                }
            res = BackendRequest.search(param)
            if res["rc"] == 0:
                _type, rst, hits = self._build_events_new(res)
                data = {
                    "status": 1,
                    "total": res["result"]["sheets"].get("total", 0),
                    "page": int(req_data.get("page", 1)) - 1,
                    "size": req_data.get("size", 20),
                    "type": _type,
                    "sid": req_data.get("sid", ""),
                    "group_id": res.get("groups_id", ""),
                    "search_timerange": str(res["result"].get("starttime", "")) + "," + str(
                            res["result"].get("endtime", "")),
                    "table": {
                        "head": res["result"]["sheets"].get("_field_infos_", []),
                        "body": rst,
                        "total": res["result"]["sheets"].get("total", 0)
                    }
                }
                if req_data.get("needParamRtn", "no") == "yes":
                    data["search_param"] = req_data
                dummy_data = data
                dummy_data["status"] = "1"
            else:
                dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""))
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def _build_events_new(self, res, with_status="no"):
        type = res["result"].get("type", "stats").lower() if with_status == "no" else "query"
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
                rst.append(item)
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

    def field(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        dummy_data = {}
        req_data = request.GET
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            res = BackendRequest.search({
                "query": req_data["query"],
                "token": es_check["t"],
                "operator": es_check["u"],
                "owner_name": es_check["u"],
                "owner_id": es_check["i"],
                "time_range": "-1d,now" if req_data["time_range"] == "," else req_data["time_range"],
                "order": req_data.get("order", "desc"),
                "size": req_data.get("size", 20),
                "page": int(req_data.get("page", 1)) - 1,
                "filter_field": req_data.get("filters", ""),
                "with_trend": "false",
                "category": "fields",
                "field": req_data.get("field", ""),
                "source_group": req_data.get("sourcegroup", "all")
            })
            if res["result"]:
                data = {
                    "status": "1",
                    "list": []
                }
                for i in res["buckets"]:
                    if not i["key"] in data["list"]:
                        data["list"].append(i["key"])
            else:
                data = {
                    "status": "0",
                    "msg": "search error"
                }
            dummy_data = data
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "auth check error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        result = bundle
        resp = self.create_response(request, result)
        return resp

    def new_field(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        dummy_data = {}
        req_data = request.GET
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            res = BackendRequest.search({
                "query": req_data["query"] + " | top 100 " + req_data.get("field", ""),
                "token": es_check["t"],
                "operator": es_check["u"],
                "owner_name": es_check["u"],
                "owner_id": es_check["i"],
                "time_range": "-1d,now" if req_data["time_range"] == "," else req_data["time_range"],
                "order": req_data.get("order", "desc"),
                "size": req_data.get("size", 20),
                "page": int(req_data.get("page", 1)) - 1,
                "filter_field": req_data.get("filters", ""),
                "field": req_data.get("field", ""),
                # "source_group": "0811test"
                "source_group": req_data.get("sourcegroup", "all")
            })
            if res["rc"] == 0:
                data = {
                    "status": "1",
                    "index": req_data.get("index", 0),
                    "list": []
                }
                for item in res["result"]["sheets"].get("rows", []):
                    data["list"].append(item[req_data.get("field", "")])
            else:
                data = {
                    "status": "0",
                    "msg": "search error"
                }
            dummy_data = data
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "auth check error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        result = bundle
        resp = self.create_response(request, result)
        return resp

    def _build_body(self, res):
        type = res["type"].lower()
        if type == "stats":
            return res["stats"]
        elif type == "query":
            return res["hits"]
        elif type == "transaction":
            return res["groups"]

    def _build_events(self, logs):
        result = []
        for i in logs:
            source = i.get("_source", {})
            _fields = {}
            for (k, v) in source.items():
                _fields[k] = v
            # a_event["_tmp_fields"] = tmp_fields
            row = self.multiToOne(_fields)
            result.append(row)
        return result

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


    def multiToOne(self, fl, parent=""):
        # convert dict which likes {"a":{"b":1}} to {"a.b":1}
        result = {}
        for (k,v) in fl.items():
            to_next = parent+"."+k if parent else k
            if isinstance(v, dict):
                result.update(self.multiToOne(v, to_next))
            else:
                result[to_next] = v
        return result
