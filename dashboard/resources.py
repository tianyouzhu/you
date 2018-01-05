# -*- coding: utf-8 -*-
# wangqiushi (wang.qiushi@yottabyte.cn) mayangguang (ma.yanguang@yottabyte.cn)
# wu.ranbo (wu.ranbo@yottabyte.cn)
# 2014/08/03
# Copyright 2014 Yottabyte
# file description : dashboard api

from tastypie import fields
from tastypie.resources import Resource
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.variable.resources import MyVariable
from yottaweb.apps.utils.resources import MyUtils
import ast
import json
import os
import re
import datetime
import logging
import time

err_data = ContributeErrorData()
audit_logger = logging.getLogger("yottaweb.audit")


class DashboardResource(Resource):
    class Meta:
        resource_name = 'dashboard'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/group/new/$" % (self._meta.resource_name),
                self.wrap_view('create_dashboard_group'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/group/update/$" % (self._meta.resource_name),
                self.wrap_view('update_dashboard_group'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/group/del/$" % (self._meta.resource_name),
                self.wrap_view('delete_dashboard_group'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/group/(?P<dg_id>.+)/$" % (self._meta.resource_name),
                self.wrap_view('dashboard'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/allevents/(?P<search_time_range>.+)/$" % (self._meta.resource_name),
                self.wrap_view('dashboard_allevents'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/savedsearches/$" % (self._meta.resource_name),
                self.wrap_view('dashboard_savedsearches'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/alerts/(?P<search_time_range>[\d]+)/$" % (self._meta.resource_name),
                self.wrap_view('dashboard_alerts'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/topvalues/fields/(?P<search_time_range>.+)/$" % (self._meta.resource_name),
                self.wrap_view('dashboard_topvalues_fields'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/topvalues/(?P<field>.+)/(?P<search_time_range>[\d]+)/$" % (
                self._meta.resource_name),
                self.wrap_view('dashboard_topvalues'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/trendslist/$" % (self._meta.resource_name),
                self.wrap_view('dashboard_trendslist'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/trends/new$" % (self._meta.resource_name),
                self.wrap_view('dashboard_trends_new'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/trends/update/(?P<trend_id>.+)/$" % (self._meta.resource_name),
                self.wrap_view('dashboard_trends_update'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/trends/(?P<trend_id>.+)/$" % (self._meta.resource_name),
                self.wrap_view('dashboard_trends'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/get_custom_config/$" % (self._meta.resource_name),
                self.wrap_view('get_custom_config'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/get_custom_config/(?P<ccid>.+)/$" % (self._meta.resource_name),
                self.wrap_view('get_given_custom_config'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/update_custom_config/$" % (self._meta.resource_name),
                self.wrap_view('update_custom_config'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/groups/$" % (self._meta.resource_name),
                self.wrap_view('get_all_dashboard_group'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/simplifiedgroups/$" % self._meta.resource_name,
                self.wrap_view('get_all_simplified_dashboards'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/tab/new/$" % (self._meta.resource_name),
                self.wrap_view('create_dashboard_tab'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/tab/update/$" % (self._meta.resource_name),
                self.wrap_view('update_dashboard_tab'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/tab/move/$" % (self._meta.resource_name),
                self.wrap_view('move_dashboard_tab'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/resourcegroup/filter/$" % self._meta.resource_name,
                self.wrap_view('filter_dashboard_rg'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/resourcegroup/filter/trend/$" % self._meta.resource_name,
                self.wrap_view('filter_trend_rg'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/resourcegroup/list/assigned/(?P<target>[\w_.-]+)/(?P<rid>[\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('assigned_dashboard_rg'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/resourcegroup/list/(?P<action>[\w_.-]+)/(?P<category>[\w_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('action_dashboard_rg'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/resourcegroup/ungrouped/(?P<target>[\w_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('ungrouped_rg'),
                name="api_dashboard"),
            url(r"^(?P<resource_name>%s)/permit/batch/(?P<did>.+)/$" % self._meta.resource_name,
                self.wrap_view('permit_batch'), name="api_dashboard")
        ]

    def dashboard(self, request, **kwargs):
        self.method_check(request, allowed=['get', 'post'])
        dashboard_group_id = kwargs.get("dg_id", "")
        # print '############request.method', request.method
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check and dashboard_group_id:
            if request.method == 'GET':
                dummy_data = self.get_dashboard_data(es_check, dashboard_group_id)
            else:
                dummy_data = self.update_dashboard_data(request, es_check)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def get_dashboard_data(self, es_check, dashboard_group_id):
        dummy_data = {}
        defaultData = {
            'curIndex': '0',
            'name': 'default',
            'tabOrder': '',
            'tabs': [
                {
                    'info': {
                        'title': '',
                        'active': True
                    },
                    'refresh': {
                        'time': 0,
                        'on': False,
                        'lastUpdate': '00:00'
                    },
                    'gridster': None,
                    'widgets': [
                        {
                            'type': 'allevents',
                            'name': 'All Events',
                            'id': 'id001',
                            'col': 1,
                            'row': 1,
                            'sizex': 2,
                            'sizey': 1,
                            'searchTimeRange': 24
                        },
                        {
                            'type': 'savedsearches',
                            'name': 'Saved Searches',
                            'id': 'id002',
                            'col': 1,
                            'row': 2,
                            'sizex': 1,
                            'sizey': 1
                        },
                        {
                            'type': 'alerts',
                            'name': 'Alerts',
                            'id': 'id003',
                            'col': 2,
                            'row': 2,
                            'sizex': 1,
                            'sizey': 1,
                            'searchTimeRange': 24
                        },
                        {
                            'type': 'topvalues',
                            'name': 'Top Values',
                            'id': 'id004',
                            'col': 1,
                            'row': 3,
                            'sizex': 1,
                            'sizey': 1,
                            'searchTimeRange': 24
                        }
                    ],
                },
            ]
        }
        param = {
            'operator': es_check['u'],
            'token': es_check['t'],
            'id': dashboard_group_id
        }
        res = BackendRequest.get_dashboard_group(param)

        if res["result"]:
            try:
                tmp_data = {
                    'curIndex': '0',
                    'name': '',
                    'tabs': []
                }
                for item in res["dashboard_group"]["dashboard_infos"]:
                    _id =  item.get("id", "")
                    _content = json.loads(ast.literal_eval(item["content"]))
                    if not (_content.get("info", "") and _content["info"].get("id", "")):
                        _content["info"]["id"] = _id
                    tmp_data["tabs"].append(_content)
                    # tmp_data["tabs"].append(json.loads(item["content"]))
                # data = json.loads(ast.literal_eval(res["dashboard_tab_infos"]))
                data = tmp_data
                name = res["dashboard_group"].get("name", "")
                owner_id = res["dashboard_group"].get("owner_id", "")
                sequences = res["dashboard_group"].get("sequences", "")
                # print '#################data: ', data
            except Exception, e:
                print e
                data = {}
                name = ""
                # data = defaultData
            dummy_data["status"] = "1"
            dummy_data["data"] = data
            dummy_data["name"] = name
            dummy_data["owner_id"] = owner_id
            dummy_data["tabOrder"] = sequences
        elif res['error'] == 'action category is not existed':
            data = defaultData
            dummy_data["status"] = "1"
            dummy_data["data"] = data
        else:
            dummy_data = err_data.build_error(res)

        return dummy_data

    def update_dashboard_data(self, request, es_check):
        dummy_data = {}
        contents = request.POST.get('contents')
        param = {
            'act': 'add_account_action',
            'token': es_check['t'],
            'id': es_check['i'],
            'category': 'dashboard',

        }
        res = BackendRequest.add_account_action(param, contents)
        if res['result']:
            dummy_data["status"] = "1"
            dummy_data["data"] = 'update success!'
        else:
            dummy_data = err_data.build_error(res)

        return dummy_data

    def dashboard_savedsearches(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            params = {
                "token": auth_result["t"],
                'operator': auth_result['u']
            }
            data = BackendRequest.get_all_saved_search(params)
            # print "###################data: ",data
            if data['result']:
                items = [x for x in data['items'] if x['anonymous'] == False]
                data['items'] = items
                dummy_data["status"] = "1"
                dummy_data["data"] = data
            else:
                dummy_data = err_data.build_error(data)
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def dashboard_allevents(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            data, res = self.get_data(request, auth_result, 'only_timeline', **kwargs)
            if data:
                dummy_data["status"] = "1"
                dummy_data["data"] = data.get("buckets")
                dummy_data["total"] = data.get("total")
            else:
                dummy_data = err_data.build_error(res)
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def get_data(self, request, auth_result, type, **kwargs):
        search_time_range = kwargs['search_time_range']
        time_range = search_time_range
        if search_time_range == '24':
            time_range = "-1d,now"
        with_trend = 'false'
        print type
        if type == 'chart':
            category = type
        elif type == 'only_fields_outline':
            category = type
        else:
            category = 'only_timeline'

        field = kwargs.get('field', '')
        if field:
            category = 'fields'
            with_trend = 'true'

        params = {
            "token": auth_result["t"],
            "owner_id": auth_result["i"],
            "query": "*",
            "time_range": time_range,
            "order": 'desc',
            "size": '50',
            "page": '0',
            "field": field,
            "category": category,
            "filters": '',
            "source_group": 'all',
            "with_trend": with_trend
        }
        res = BackendRequest.search(params)
        # print '==============================params:', params
        # print '===============================res:', res
        if res["result"]:
            if type == 'only_timeline':
                _timeline = res.get('aggs', {})
                data = {
                    "buckets": self._build_time_line(_timeline) if _timeline else [],
                    "total": res.get("total", 0)
                }
            elif type == 'only_fields_outline':
                _fields = res.get('index_fields', {})
                data = {
                    "status": 1,
                    "sid": res.get("sid", ""),
                    "fields": self._build_fields(_fields) if _fields else {}
                }
            elif type == 'fields':
                if field:
                    data = []
                    for value in res['buckets']:
                        serie = {
                            "key": value["key"],
                            "doc_count": value["doc_count"]
                        }
                        if value.get("event_counts", {}):
                            serie["arr"] = []
                            for bucket in value["event_counts"]["buckets"]:
                                serie["arr"].append([bucket["to"], bucket["doc_count"]])
                        data.append(serie)
                else:
                    data = res.get('index_fields', {})
                    if data.count("log_type:string") > 0:
                        data.remove("log_type:string")
                        data.insert(0, "log_type:string")
                    if data.count("logtype:string") > 0:
                        data.remove("logtype:string")
                        data.insert(0, "logtype:string")
                    if data.count("tag:string") > 0:
                        data.remove("tag:string")
                        data.insert(0, "tag:string")
                    if data.count("appname:string") > 0:
                        data.remove("appname:string")
                        data.insert(0, "appname:string")
                    if data.count("hostname:string") > 0:
                        data.remove("hostname:string")
                        data.insert(0, "hostname:string")
                    if data.count("raw_message:string") > 0:
                        data.remove("raw_message:string")
                    if data.count("timestamp:long") > 0:
                        data.remove("timestamp:long")
                    # data = [val.split(':')[0] for val in data]
            return data, res
        return False, res

    # TODO(wu.ranbo@yottabyte.cn): Bad! copy code from apps/search/resources.py
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

    def dashboard_alerts(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        search_time_range = kwargs['search_time_range']
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            params = {
                "token": auth_result["t"],
                "operator": auth_result["u"]
            }
            data = BackendRequest.get_all_alert(params)
            if data:
                dummy_data["status"] = "1"
                dummy_data["data"] = data
            else:
                dummy_data = err_data.build_error(data)
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def dashboard_topvalues_fields(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            data, res = self.get_data(request, auth_result, 'only_fields_outline', **kwargs)
            if data:
                dummy_data["status"] = "1"
                dummy_data["data"] = data
            else:
                dummy_data = err_data.build_error(res)
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def dashboard_topvalues(self, request, **kwargs):
        my_auth = MyBasicAuthentication()
        auth_result = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if auth_result:
            data, res = self.get_data(request, auth_result, 'fields', **kwargs)
            if data or data == []:
                dummy_data["status"] = "1"
                dummy_data["data"] = data
            else:
                dummy_data = err_data.build_error(res)
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            resdata = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, resdata)

    def dashboard_trendslist(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_all_trends(param)
            if res['result']:
                rtn = []
                permits = []
                for item in res.get('trends', []):
                    el = {}
                    el["name"] = item["name"]
                    el["id"] = item["id"]
                    el["resource_groups"] = item["resource_groups"]
                    rtn.append(el)

                    permits.append({
                        "resource_id": int(item["id"]),
                        "target": "Trend",
                        "action": "Update"
                    })
                    permits.append({
                        "resource_id": int(item["id"]),
                        "target": "Trend",
                        "action": "Delete"
                    })
                permits.append({
                    "target": "DerelictResource",
                    "action": "Possess"
                })
                dummy_data["status"] = "1"
                dummy_data["data"] = rtn

                permit_data = {
                    'permits': permits
                }
                permit_res = BackendRequest.batch_permit_can(param, permit_data)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
            else:
                dummy_data = err_data.build_error(res)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def dashboard_trends_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        # save the trend and with trend id
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            content = request.POST.get('content')
            name = request.POST.get('name').encode('utf-8')
            ids = request.POST.get('ids', "")
            # print "#############333name: ",name
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'name': name,
                'resource_group_ids': ids
            }
            res = BackendRequest.create_trend(param, content)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["data"] = 'add trend success!'
            else:
                dummy_data = err_data.build_error(res)
                dummy_data["trendId"] = res.get("id", "")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            dummy_data["trendId"] = ""

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def dashboard_trends(self, request, **kwargs):
        self.method_check(request, allowed=['get', 'delete'])
        dummy_data = {}
        trend_id = kwargs['trend_id'].encode('utf-8')
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            if len(trend_id) > 10:
                new_res = BackendRequest.convert_id({
                    "trend_id": trend_id,
                    "token": es_check["t"],
                    "operator": es_check["u"]
                })
                if new_res["result"]:
                    new_id = new_res["id"]
                else:
                    new_id = trend_id
            else:
                new_id = trend_id
            if request.method == 'GET':
                dummy_data = self.get_trend(es_check, new_id)
            elif request.method == 'DELETE':
                dummy_data = self.delete_trend(es_check, new_id)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def dashboard_trends_update(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        trend_id = kwargs['trend_id'].encode('utf-8')
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            if request.method == 'POST':
                post_dict = request.POST
                name = post_dict.get('name', '')
                content = post_dict.get("content", "")
                ids = post_dict.get("resource_group_ids", "")
                dummy_data = self.update_trend(es_check, trend_id, name, ids, content)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def updateOldTrend(self, content):
        my_utils = MyUtils()
        type = content.get("visType")
        if type == "SJJSTJ":
            series = content.get('series')
            fields = []
            for item in series:
                fields.append({
                    'name': item["name"],
                    'chartType': item["type"],
                    'isUnique': item["isUnique"]
                })
            content["fields"] = fields
            content["chartCount"] = len(series)
            content["chartType"] = 'line'
            del content["series"]
            fromToDate = my_utils.getFromToDate(content.get("time_range"))
            span = my_utils.getSpan(int(fromToDate["toDate"]) - int(fromToDate["fromDate"]))
            content["range"] = my_utils.getUnixTimeInterval(span)
            obj = {
                "span": span,
                "fields": fields
            }
        elif type == "SJSFDTJ_TIME":
            stat_ranges = content.get('stat_ranges')
            timeranges = stat_ranges.split(',')
            times = []
            for item in timeranges:
                fromTo = item.split(':')
                fromDate = datetime.datetime.fromtimestamp(int(fromTo[0])/1000.0).strftime('%Y-%m-%d:%H:%M:%S')
                toDate = datetime.datetime.fromtimestamp(int(fromTo[1])/1000.0).strftime('%Y-%m-%d:%H:%M:%S')
                times.append({
                    "from": fromDate,
                    "to": toDate
                })
            field = content.get('stat_field')
            statisType = content.get("stat_method")
            obj = {
                "field": field,
                "statisType": statisType,
                "times": times
            }
        elif type == "SJSFDTJ_VALUE":
            stat_ranges = content.get('stat_ranges')
            valueranges = stat_ranges.split(',')
            values = []
            for item in valueranges:
                fromTo = item.split(':')
                fromValue = fromTo[0]
                toValue = fromTo[1]
                values.append({
                    "from": fromValue,
                    "to": toValue
                })
            field = content.get('stat_field')
            statisType = content.get("stat_method")
            obj = {
                "field": field,
                "values": values
            }
        elif type == "ZFT_TIME":
            stat_interval = content.get('stat_interval')
            intervalWithUnit = my_utils.convertNumericRangeToStringRange(stat_interval)
            interval=intervalWithUnit[:-1]
            unit=intervalWithUnit[-1]
            obj = {
                "interval": interval,
                "unit": unit
            }
        elif type == "ZFT_VALUE":
            field = content.get('stat_field')
            interval = content.get("stat_interval")
            obj = {
                "field": field,
                "interval": interval
            }
        elif type == "ZDFLTJ":
            field = content.get('field').split(':')[0]
            content['field'] = field
            trend = content.get('trend')
            if trend == 'false':
                top = content.get('topn')
                content['type'] = 'data'
                obj = {
                    "type": "data",
                    "field": field,
                    "top": top
                }
            else:
                content['type'] = 'graph'
                fromToDate = my_utils.getFromToDate(content.get("time_range"))
                span = my_utils.getSpan(int(fromToDate["toDate"]) - int(fromToDate["fromDate"]))
                selected = content.get("filters").split('|-$!|')
                options = []
                for item in selected:
                    options.append(item.split(':')[1][1:-1])
                content['options'] = options
                obj = {
                    "type": "graph",
                    "field": field,
                    "span": span
                }
        elif type == "ZDSZTJ":
            fromToDate = my_utils.getFromToDate(content.get("time_range"))
            span = my_utils.getSpan(int(fromToDate["toDate"]) - int(fromToDate["fromDate"]))
            content["range"] = my_utils.getUnixTimeInterval(span)
            statisType = content.get("stat_method")
            yAxis = content.get("stat_field")
            field = content.get("stat_split_field").split(":")[0]
            content['field'] = field
            content['type'] = 'timeline'
            content['chartType'] = 'line'
            obj = {
                "span": span,
                "statisType": statisType,
                "yAxis": yAxis,
                "field": field
            }
        elif type == "LJBFB":
            field = content.get("stat_field")
            stat_method = content.get('stat_method')
            if stat_method == "percentiles":
                reverse = 'false'
            elif stat_method == "percentile_ranks":
                reverse = 'true'
            percents = content.get('percents')
            if reverse == 'true':
                content['type'] = 'one'
                content['reverse'] = True
                content['reValue'] = percents
                obj = {
                    "reverse": reverse,
                    "field": field,
                    "reValue": percents
                }
            else:
                content['type'] = 'timeline'
                content['reverse'] = False
                obj = {
                    "reverse": reverse,
                    "field": field,
                    "percents": percents
                }
        elif type == "DJTJ":
            stat_step = content.get("stat_step")
            if stat_step == "step1":
                stat_field = content.get("stat_field").split(':')[0]
                chartType = content.get("stat_chartType")
                stat_top = content.get("stat_top")
                content['chartType'] = chartType
                content['stat_field'] = stat_field
                content['type'] = 'timeline'
                content['step'] = stat_step
                if chartType == 'pie' or chartType == 'bar':
                    obj = {
                        "step": stat_step,
                        "chartType": chartType,
                        "step1_field": stat_field
                    }
                else:
                    stat_split = content.get("stat_split")
                    match = re.match(r"([0-9]+)([a-z]+)", stat_split, re.I)
                    if match:
                        items = match.groups()
                        interval = items[0]
                        unit = items[1][0]
                    obj = {
                        "step": stat_step,
                        "chartType": chartType,
                        "step1_field": stat_field,
                        "interval": interval,
                        "unit": unit,
                        "stat_top":stat_top
                    }
            elif stat_step == "step2" or stat_step == "step3":
                stat_field = content.get("stat_split_field").split(':')[0]
                chartType = content.get("stat_chartType")
                content['chartType'] = chartType
                content['stat_field'] = stat_field
                content['type'] = 'timeline'
                content['step'] = stat_step
                if chartType == 'pie' or chartType == 'bar':
                    obj = {
                        "step": stat_step,
                        "chartType": chartType,
                        "step_field": stat_field
                    }
                else:
                    stat_method = content.get("stat_method")
                    stat_split = content.get("stat_split")
                    match = re.match(r"([0-9]+)([a-z]+)", stat_split, re.I)
                    if match:
                        items = match.groups()
                        interval = items[0]
                        unit = items[1][0]
                    obj = {
                        "step": stat_step,
                        "chartType": chartType,
                        "step_field": stat_field,
                        "interval": interval,
                        "unit": unit,
                        "statisType":stat_method
                    }

        elif type == "DLFB":
            field = content.get("field").split(":")[0]
            content['field'] = field
            mapType = content.get('mapType')
            size = content.get('size')
            if mapType == 'world':
                fromValue = 'map_country'
            elif mapType == 'china':
                fromValue = 'map_province'
            else:
                fromValue = 'map_city'
            content['from'] = fromValue
            obj = {
                "type": mapType,
                "field": field,
                "top": size
            }

        out_query = content.get("query")
        query = my_utils.generateSPLQuery(type, obj)
        content["query"] = out_query + " " + query
        content["isNew"] = 'true'
        return content

    def get_trend(self, es_check, trend_id):
        dummy_data = {}
        param = {
            'token': es_check['t'],
            'operator': es_check['u'],
            'id': trend_id
        }

        res = BackendRequest.get_trend(param)
        my_utils = MyUtils()
        if res['result']:
            content = json.loads(ast.literal_eval(res["trend"]["content"]))
            if content.get('isNew') != 'true' and content.get('visType') != 'STATS_NEW':
                name = res["trend"]["name"]
                ids = content.get('ids')
                content = self.updateOldTrend(content)
                self.update_trend(es_check, trend_id, name, ids, json.dumps(content))

            dummy_data["status"] = "1"
            dummy_data["data"] = content
            dummy_data["trend_id"] = trend_id
        else:
            dummy_data = err_data.build_error(res)

        return dummy_data

    def delete_trend(self, es_check, trend_id):
        dummy_data = {}
        param = {
            'token': es_check['t'],
            'operator': es_check['u'],
            'id': trend_id
        }
        res = BackendRequest.delete_trend(param)
        if res['result']:
            dummy_data["status"] = "1"
            dummy_data["data"] = 'trend delete success!'
        else:
            dummy_data = err_data.build_error(res)

        return dummy_data

    def update_trend(self, es_check, trend_id, name, ids, content):
        dummy_data = {}
        param = {
            'token': es_check['t'],
            'operator': es_check['u'],
            'id': trend_id,
            'name': name,
            'resource_group_ids': ids
        }
        if content:
            post_data = content
        else:
            post_data = ""
        res = BackendRequest.update_trend(param, post_data)
        if res['result']:
            dummy_data["status"] = "1"
            dummy_data["data"] = 'trend update success!'
        else:
            dummy_data = err_data.build_error(res)
        #
        # dummy_data["status"] = "1"
        # dummy_data["data"] = 'trend delete success!'
        return dummy_data


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
            if ai[0] in res["num"]:
                continue
            if ai[0] in res["ot"]:
                del res["ot"][res["ot"].index(ai[0])]
                try:
                    del res["all"][res["all"].index(ai[0]+":string")]
                    del temp[temp.index(ai[0] + ":string")]
                except Exception, e:
                    logger = logging.getLogger("django.request")
                    logger.info("field error: %s", item)

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
            if v1 and isinstance(v1, dict) and isinstance(v2, dict):
                d1[k] = self.merge_dict(v1, v2)
            elif v1 and isinstance(v1, list) and isinstance(v2, list):
                d1[k] = list(set(v1 + v2))
            elif v2:
                d1[k] = v2
        return d1

    def get_custom_config(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            # get json
            file_path_name = config_path + '/dashboard.json'
            print "file_path_name: ",file_path_name
            try:
                with open(file_path_name) as data_file:
                    data = json.load(data_file)
                dummy_data["status"] = "1"
                dummy_data["data"] = data
                print "##############data: ",data
            except:
                dummy_data["status"] = "1"
                dummy_data["data"] = []
                # dummy_data = err_data.build_error({}, "Get custom dashboard config failed!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def get_given_custom_config(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        custom_config_id = kwargs['ccid'].encode('utf-8')
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            # get json
            file_path_name = config_path + '/dashboard.json'
            print "file_path_name: ",file_path_name
            try:
                with open(file_path_name) as data_file:
                    data = json.load(data_file)

                for custom_config in data:
                    if custom_config_id == custom_config.get('custom_config_id', ''):
                        dummy_data["data"] = custom_config
                        break

                dummy_data["status"] = "1"
                print "##############data: ",data
            except:
                dummy_data["status"] = "0"
                dummy_data["data"] = []
                # dummy_data = err_data.build_error({}, "Get custom dashboard config failed!")
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def update_custom_config(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        # print "###########request.POST: ",request.POST
        data = json.loads(request.POST.get('customConfigWidgets'))
        # print "###########data: ",data
        # return
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            file_path_name = config_path + '/dashboard.json'
            try:
                with open(file_path_name,'w') as data_file:
                   json.dump(data, data_file)
                dummy_data["status"] = "1"
            except:
                dummy_data = err_data.build_error({})

        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def get_all_dashboard_group(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            permits = []
            param = {
                'token': es_check['t'],
                'id': es_check['i'],
                'operator': es_check['u'],
            }
            res = BackendRequest.get_all_dashboard_group(param)
            if res["result"]:
                data = res["dashboard_groups"]
                dummy_data["status"] = "1"

                for el in data:
                    self.filter_dashboard_data(el)

                list_data = self.build_group_list(data, es_check["i"])
                dummy_data["groups"] = list_data['dashs']
                permits = list_data['permits']

                permit_param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_data = {
                    'permits': permits
                }
                permit_res = BackendRequest.batch_permit_can(permit_param, permit_data)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
            else:
                dummy_data = err_data.build_error(res)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def get_all_simplified_dashboards(self, request, **kwargs):
        '''
          Get and return a simplified version of all dashboards data without permission data
        '''
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'id': es_check['i'],
                'operator': es_check['u'],
            }
            res = BackendRequest.get_all_dashboard_group(param)
            if res["result"]:
                data = res["dashboard_groups"]
                dummy_data["status"] = "1"

                for el in data:
                    if 'dashboard_infos' in el and type(el['dashboard_infos']) is list:
                        tabs = [];
                        for i in el['dashboard_infos']:
                            _content = json.loads(ast.literal_eval(i["content"]))
                            tabs.append({
                                'id': _content['info'].get("id", ""),
                                'name': _content['info'].get("title", ""),
                                'active': _content['info'].get("active", ""),
                                'show': _content.get("show", "false")
                            })
                        el['tabs'] = tabs
                        del el['dashboard_infos']
                    if 'sequences' in el:
                        el['tabOrder'] = el['sequences']
                        del el['sequences']
                    del el['owner_id']
                    del el['owner_name']
                    del el['default_display']

                dummy_data["groups"] = data
            else:
                dummy_data = err_data.build_error(res)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def create_dashboard_group(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        post_data = request.POST
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            permits = []
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'name': post_data.get("name", ""),
                'resource_group_ids': post_data.get("resource_group_ids")
            }
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "create",
                "module": "dashboard group",
                "user_name": es_check["u"],
                "user_id": es_check["i"],
                "domain": es_check["d"],
                "target": post_data.get("name", ""),
                "result": "success"
            }
            res = BackendRequest.create_dashboard_group(param)
            if res["result"]:
                list_param = {
                    'token': es_check['t'],
                    'id': es_check['i'],
                    'operator': es_check['u'],
                }
                list_res = BackendRequest.get_all_dashboard_group(list_param)
                if res["result"]:
                    data = list_res["dashboard_groups"]
                    dummy_data["status"] = "1"

                    for el in data:
                        self.filter_dashboard_data(el)

                    list_data = self.build_group_list(data, es_check["i"])
                    dummy_data["groups"] = list_data['dashs']
                    permits = list_data['permits']

                    permit_param = {
                        'token': es_check['t'],
                        'operator': es_check['u']
                    }
                    permit_data = {
                        'permits': permits
                    }
                    permit_res = BackendRequest.batch_permit_can(permit_param, permit_data)
                    if permit_res['result']:
                        dummy_data["permit_list"] = permit_res["short_permits"]
                    else:
                        dummy_data["permit_list"] = []
                else:
                    dummy_data = err_data.build_error({}, "Get dashboard group list error!")
            else:
                dummy_data = err_data.build_error(res)
                to_log["result"] = "error"
                to_log["msg"] = res.get("error", "")
            audit_logger.info(json.dumps(to_log))
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def delete_dashboard_group(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        post_data = request.POST
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': post_data.get("groupId", "")
            }
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "delete",
                "module": "dashboard group",
                "user_name": es_check["u"],
                "user_id": es_check["i"],
                "domain": es_check["d"],
                "target": post_data.get("groupId", ""),
                "result": "success"
            }
            res = BackendRequest.delete_dashboard_group(param)
            if res["result"]:
                list_param = {
                    'token': es_check['t'],
                    'operator': es_check['u'],
                }
                list_res = BackendRequest.get_all_dashboard_group(list_param)
                if res["result"]:
                    data = list_res["dashboard_groups"]
                    dummy_data["status"] = "1"

                    for el in data:
                        self.filter_dashboard_data(el)

                    list_data = self.build_group_list(data, es_check["i"])
                    dummy_data["groups"] = list_data['dashs']
                    permits = list_data['permits']

                    permit_param = {
                        'token': es_check['t'],
                        'operator': es_check['u']
                    }
                    permit_data = {
                        'permits': permits
                    }
                    permit_res = BackendRequest.batch_permit_can(permit_param, permit_data)
                    if permit_res['result']:
                        dummy_data["permit_list"] = permit_res["short_permits"]
                    else:
                        dummy_data["permit_list"] = []
                else:
                    dummy_data = err_data.build_error({}, "Get dashboard group list error!")
            else:
                dummy_data = err_data.build_error(res)
                to_log["result"] = "error"
                to_log["msg"] = res.get("error", "")
            audit_logger.info(json.dumps(to_log))
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def update_dashboard_group(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        post_data = request.POST
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': post_data.get("groupId", ""),
                'resource_group_ids': post_data.get("rgids"),
                'assign': "1",
                'clear': "0"
            }
            if "name" in post_data:
                param['name'] = post_data.get("name")
            if "default_display" in post_data:
                param['default_display'] = post_data.get("default_display", "0")
            if "tabIds" in post_data:
                param['assign'] = "0"
                if post_data.get("tabIds", ""):
                    param['new_dashboard_ids'] = post_data.get("tabIds", "")
                else:
                    param['clear'] = "1"
            if "sequences" in post_data:
                param['sequences'] = post_data.get("sequences")
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "update",
                "module": "dashboard group",
                "user_name": es_check["u"],
                "user_id": es_check["i"],
                "domain": es_check["d"],
                "target": post_data.get("name", ""),
                "result": "success"
            }
            res = BackendRequest.update_dashboard_group(param)
            if res["result"]:
                permits = []
                list_param = {
                    'token': es_check['t'],
                    'id': es_check['i'],
                    'operator': es_check['u'],
                }
                list_res = BackendRequest.get_all_dashboard_group(list_param)
                if res["result"]:
                    data = list_res["dashboard_groups"]
                    dummy_data["status"] = "1"

                    for el in data:
                        if 'dashboard_infos' in el and type(el['dashboard_infos']) is list:
                            tabs = [];
                            tab_names = [];
                            for i in el['dashboard_infos']:
                                if i['name']:
                                    tab_names.append(i['name'])
                                _content = json.loads(ast.literal_eval(i["content"]))
                                tabs.append({
                                    'id': _content['info'].get("id", ""),
                                    'name': _content['info'].get("title", ""),
                                    'active': _content['info'].get("active", ""),
                                    'show': _content.get("show", "false")
                                })
                            el['tab_names'] = tab_names;
                            el['tabs'] = tabs
                            del el['dashboard_infos']
                        if 'sequences' in el:
                            el['tabOrder'] = el['sequences']
                            del el['sequences']

                    list_data = self.build_group_list(data, es_check["i"])
                    dummy_data["groups"] = list_data['dashs']
                    permits = list_data['permits']

                    permit_param = {
                        'token': es_check['t'],
                        'operator': es_check['u']
                    }
                    permit_data = {
                        'permits': permits
                    }
                    permit_res = BackendRequest.batch_permit_can(permit_param, permit_data)
                    if permit_res['result']:
                        dummy_data["permit_list"] = permit_res["short_permits"]
                    else:
                        dummy_data["permit_list"] = []
                else:
                    dummy_data = err_data.build_error({}, "Get dashboard group list error!")
            else:
                dummy_data = err_data.build_error(res)
                to_log["result"] = "error"
                to_log["msg"] = res.get("error", "")
            audit_logger.info(json.dumps(to_log))
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def create_dashboard_tab(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        post_data = request.POST
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'name': post_data.get("name", ""),
                'content': post_data.get("content", ""),
                'dashboard_group_id': post_data.get("groupId"),
                'resource_group_ids': post_data.get('rgids', "")
            }
            res = BackendRequest.create_dashboard_tab(param)
            if res["result"]:
                if post_data.get("groupId", ""):
                    assign_param = {
                        "id": post_data.get("groupId"),
                        'token': es_check['t'],
                        'operator': es_check['u'],
                        'new_dashboard_ids': res["id"],
                        'assign': "1",
                        'clear': "0",
                        'resource_group_ids': post_data.get('rgids', "")
                    }
                    assign_res = BackendRequest.update_dashboard_group(assign_param)
                    if assign_res["result"]:
                        dummy_data["status"] = "1"
                        dummy_data["tabId"] = res["id"]
                    else:
                        dummy_data = err_data.build_error(res)
                else:
                    dummy_data["status"] = "1"
                    dummy_data["tabId"] = res["id"]
            else:
                if res.get("error_code", "") == 0:
                    # tab name duplication
                    dummy_data["status"] = "0"
                    dummy_data["error_code"] = "0"
                else:
                    dummy_data = err_data.build_error(res)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def update_dashboard_tab(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        post_data = request.POST
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': post_data.get("id", ""),
                'name': post_data.get("name", ""),
                'content': post_data.get("content", ""),
                'resource_group_ids': post_data.get('rgids', "")
            }
            # if post_data.get("newName", ""):
            #     param["new_name"] = post_data.get("newName", "")
            res = BackendRequest.update_dashboard_tab(param)
            if res["result"]:
                dummy_data["status"] = "1"
            else:
                dummy_data = err_data.build_error(res)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def move_dashboard_tab(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        post_data = request.POST
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            assign_param = {
                "id": post_data.get("groupId"),
                'token': es_check['t'],
                'operator': es_check['u'],
                'new_dashboard_ids': post_data.get("tabId"),
                'assign': "1",
                'clear': "0",
                'resource_group_ids': post_data.get('rgids')
            }
            if post_data.get("fromId", ""):
                assign_param["from_id"] = post_data.get("fromId", "")
            assign_res = BackendRequest.update_dashboard_group(assign_param)
            if assign_res["result"]:
                dummy_data["status"] = "1"
            else:
                dummy_data = err_data.build_error(assign_res)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def build_group_list(self, data, user_id):
        target = {
            'dashs': [],
            'permits': []
        }
        rtn = []
        permits = []
        for item in data:
            if "dashboard_names" in item:
                item["tab_names"] = item["dashboard_names"]
                del item["dashboard_names"]
            if "sequences" in item:
                item["tabOrder"] = item["sequences"]
                del item["sequences"]
            if not (item["name"] == "default" and not int(item["owner_id"]) == int(user_id)):
                rgnames = []
                rgnames_short = []
                idx = 0
                if len(item["resource_groups"]) == 1:
                    item["rgnames"] = item["resource_groups"][0]["name"]
                    item["rgnames_short"] = item["resource_groups"][0]["name"]
                elif len(item["resource_groups"]) <= 3:
                    for rgs in item["resource_groups"]:
                        rgnames.append(rgs["name"])
                        rgnames_short.append(rgs["name"])
                    item["rgnames"] = ", ".join(rgnames)
                    item["rgnames_short"] = ", ".join(rgnames_short)
                else:
                    idx = 0
                    for rgs in item["resource_groups"]:
                        rgnames.append(rgs["name"])
                        if idx < 3:
                            rgnames_short.append(rgs["name"])
                        elif idx == 3:
                            rgnames_short.append("...")
                    item["rgnames"] = ", ".join(rgnames)
                    item["rgnames_short"] = ", ".join(rgnames_short)
                rtn.append(item)
            permits.append({
                "resource_id": int(item['id']),
                "target": "DashBoardGroup",
                "action": "Update"
            })
            permits.append({
                "resource_id": int(item['id']),
                "target": "DashBoardGroup",
                "action": "Delete"
            })
            permits.append({
                "resource_id": int(item['id']),
                "target": "DashBoardGroup",
                "action": "Assign"
            })
        permits.append({
            "target": "DashBoardGroup",
            "action": "Create"
        })
        permits.append({
            "target": "DerelictResource",
            "action": "Possess"
        })
        target['dashs'] = rtn
        target['permits'] = permits
        return target

    def filter_dashboard_rg(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        req_data = request.POST
        post_data = req_data.get('ids', '')
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            permits = []
            param = {
                'ids': post_data,
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_batch_dashboard_group(param)
            if res['result']:
                data = res['dashboard_groups']
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                list_data = self.build_group_list(data, es_check["i"])
                dummy_data["groups"] = list_data['dashs']
                permits = list_data['permits']

                permit_param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_data = {
                    'permits': permits
                }
                permit_res = BackendRequest.batch_permit_can(permit_param, permit_data)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
            else:
                dummy_data["status"] = 0
                dummy_data["msg"] = res.get('error', 'get dashboards history error!')
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def filter_trend_rg(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        req_data = request.POST
        ids = req_data.get('ids', '')
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'ids': ids,
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_batch_trend(param)
            if res['result']:
                data = self.build_widget_group_list(res['trends'], es_check['t'], es_check['u'])
                dummy_data["status"] = "1"
                dummy_data["data"] = data['trends']

                permit_param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_data = {
                    'permits': data['permits']
                }
                permit_res = BackendRequest.batch_permit_can(permit_param, permit_data)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
            else:
                dummy_data["status"] = 0
                dummy_data["msg"] = res.get('error', 'get dashboards history error!')
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def action_dashboard_rg(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if kwargs['category'].lower() == "dashboardgroup":
            category = "DashBoardGroup"
        elif kwargs['category'] == "trend":
            category = "Trend"
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {}
            if (kwargs['action'].lower() == "read"):
                param['action'] = "Read"
                param['category'] = category
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = "ResourceGroup"
            elif (kwargs['action'].lower() == "assign"):
                param['action'] = "Assign"
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = category

            res = BackendRequest.permit_list_resource_group(param)
            if res['result']:
                data = self.rebuild_resource_group_list(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["rg_list"] = data
            else:
                dummy_data["status"] = 0
                dummy_data["msg"] = res.get('error', 'get dashboards permit_list_resource_group error!')
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def assigned_dashboard_rg(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if kwargs['target'].lower() == "dashboardgroup":
            target = "DashBoardGroup"
        elif kwargs['target'].lower() == "trend":
            target = "Trend"
        rid = kwargs['rid']
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'resource_id': rid,
                'category': target,
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.list_assigned_resource_group(param)
            if res['result']:
                data = self.rebuild_resource_group_list(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["rg_list"] = data
            else:
                dummy_data["status"] = 0
                dummy_data["msg"] = res.get('error', 'get dashboards list_assigned_resource_group error!')
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def permit_batch(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        dashboard_id = kwargs['did'].encode('utf-8')
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            permits = []
            permits.append({
                "target": "Download",
                "action": "Possess"
            })
            permits.append({
                "resource_id": int(dashboard_id),
                "target": "DashBoardGroup",
                "action": "Update"
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

    def ungrouped_rg(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        target = kwargs['target']
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'category': target,
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.list_derelict_resource_ids(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["ids"] = res['resource_ids']
            else:
                dummy_data["status"] = 0
                dummy_data["msg"] = res.get('error', 'get dashboards ungrouped rg error!')
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    @staticmethod
    def filter_dashboard_data(el):
        if 'dashboard_infos' in el and type(el['dashboard_infos']) is list:
            tabs = [];
            tab_names = [];
            for i in el['dashboard_infos']:
                if i['name']:
                    tab_names.append(i['name'])
                _content = json.loads(ast.literal_eval(i["content"]))
                tabs.append({
                    'id': _content['info'].get("id", ""),
                    'name': _content['info'].get("title", ""),
                    'active': _content['info'].get("active", ""),
                    'show': _content.get("show", "false")
                })
            el['tab_names'] = tab_names;
            el['tabs'] = tabs
            del el['dashboard_infos']
        if 'sequences' in el:
            el['tabOrder'] = el['sequences']
            del el['sequences']


    @staticmethod
    def rebuild_resource_group_list(data):
        res_list = []
        for item in data:
            final = {}
            final["type"] = item.get("category").encode('utf-8')
            final["rgname"] = item.get("name").encode('utf-8')
            final["memo"] = item.get("memo", "").encode('utf-8')
            final["domain_id"] = item.get("domain_id")
            final["creator_id"] = item.get("creator_id")
            final["rg_id"] = item.get("id")
            final["resource_ids"] = item.get("resource_ids", [])
            res_list.append(final)
        return res_list

    @staticmethod
    def build_widget_group_list(data, token, operator):
        target = {
            'trends': [],
            'permits': []
        }
        res_list = []
        permits = []
        for item in data:
            final = {}
            final["name"] = item.get("name").encode('utf-8')
            ids = []
            for el in item["resource_groups"]:
                ids.append(str(el["id"]))
            final["ids"] = ",".join(ids)
            trend_id = item.get("id").encode('utf-8')
            if len(trend_id) > 10:
                new_res = BackendRequest.convert_id({
                    "trend_id": trend_id,
                    "token": token,
                    "operator": operator
                })
                if new_res["result"]:
                    new_id = new_res["id"]
                else:
                    new_id = trend_id
            else:
                new_id = trend_id
            final["trendId"] = new_id
            final["type"] = "trend"
            res_list.append(final)

            permits.append({
                "resource_id": int(new_id),
                "target": "Trend",
                "action": "Update"
            })
            permits.append({
                "resource_id": int(new_id),
                "target": "Trend",
                "action": "Delete"
            })
        permits.append({
            "target": "DerelictResource",
            "action": "Possess"
        })
        target['trends'] = res_list
        target['permits'] = permits
        return target
