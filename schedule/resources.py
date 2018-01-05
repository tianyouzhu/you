# wangqiushi (@yottabyte.cn)
# 2015/09/01
# Copyright 2015 Yottabyte
# file description : resources.py.
from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.config import parser
import urllib
import json
import re
import time
import datetime
import urllib2
import logging
__author__ = 'wangqiushi'
err_data = ContributeErrorData()
audit_logger = logging.getLogger("yottaweb.audit")


class ScheduleResource(Resource):

    class Meta:
        resource_name = 'schedule'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/lists/$" % self._meta.resource_name,
                self.wrap_view('schedule_list'), name="api_schedule_list"),
            url(r"^(?P<resource_name>%s)/lists/(?P<sid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('schedule_list_content'), name="api_schedule_list"),
            url(r"^(?P<resource_name>%s)/new" % self._meta.resource_name,
                self.wrap_view('schedule_new'), name="api_schedule_new"),
            url(r"^(?P<resource_name>%s)/detail/(?P<sid>[\w\d_.-]+)/(?P<stp>[\d]{10})/$" % self._meta.resource_name,
                self.wrap_view('schedule_detail'), name="api_schedule_detail"),
            url(r"^(?P<resource_name>%s)/update/(?P<sid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('schedule_update'), name="api_schedule_update"),
            url(r"^(?P<resource_name>%s)/del/(?P<sid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('schedule_delete'), name="api_schedule_delete"),
            url(r"^(?P<resource_name>%s)/enable/(?P<sid>[\w\d_.-]+)/(?P<enable>[\w]{1})/$" % self._meta.resource_name,
                self.wrap_view('schedule_enable'), name="api_schedule_enable"),
            url(r"^(?P<resource_name>%s)/resourcegroup/filter/$" % self._meta.resource_name,
                self.wrap_view('resourcegroup_filter'), name="api_sourcegroups_rg_filter"),
            url(r"^(?P<resource_name>%s)/resourcegroup/ungrouped/$" % self._meta.resource_name,
                self.wrap_view('resourcegroup_ungrouped'), name="api_sourcegroups_rg_ungrouped"),
            url(r"^(?P<resource_name>%s)/resourcegroup/list/assigned/(?P<sid>[\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('get_resourcegroup_assigned_list'), name="api_get_resourcegroup_assigned_list"),
            url(r"^(?P<resource_name>%s)/resourcegroup/list/(?P<action>[\w_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('get_resourcegroup_list'), name="api_get_resourcegroup_list"),
        ]

    def schedule_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
            }
            res = BackendRequest.get_all_saved_schedule(param)
            if res['result']:
                data = self.rebuild_schedule_list(res['item'])
                dummy_data["status"] = "1"
                dummy_data["totle"] = len(data)
                dummy_data["list"] = data["schedules"]
                permit_param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_data = {
                    'permits': data["permits"]
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

    def schedule_list_content(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        schedule_id = kwargs['sid']
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': schedule_id
            }
            res = BackendRequest.get_saved_schedule(param)
            if res['result']:
                schedule_info = res.get('saved_schedule', {})
                data = schedule_info.get('item', [])
                req_param_arr = schedule_info.get("request", "").split("&")
                req_param = {}
                for item in req_param_arr:
                    k, v = item.split("=")
                    req_param[k] = v
                req_param["query"] = req_param.get("query", "").replace("+", " ")
                dummy_data["status"] = "1"
                dummy_data["req_param"] = req_param
                dummy_data["totle"] = len(data)
                dummy_data["schedule_info"] = {
                    "name": schedule_info.get("name", "").encode('utf-8'),
                    "description": schedule_info.get("description", "").encode('utf-8'),
                    "start_trigger_time": schedule_info.get("start_trigger_time", ""),
                    "check_interval": schedule_info.get("check_interval", ""),
                    "crontab": schedule_info.get("crontab", "0"),
                    "enabled": schedule_info.get("enabled", False),
                    "derelict": schedule_info.get("derelict", False)
                }
                dummy_data["vis_type"] = schedule_info.get('vis_type', "")
                dummy_data["chart_type"] = schedule_info.get('chart_type', "")
                dummy_data["list"] = data
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

    def schedule_detail(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        schedule_id = kwargs['sid']
        schedule_ts = kwargs['stp']
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            pre_param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': schedule_id
            }
            pre_res = BackendRequest.get_saved_schedule(pre_param)
            schedule_info = pre_res.get('saved_schedule', {})
            vis_type = schedule_info.get('vis_type', "")
            chart_type = schedule_info.get('chart_type', "")
            request_param = schedule_info.get('request', "")
            request_arr = request_param.split("&")
            pre_param = {}
            for item in request_arr:
                key, value = item.split("=")
                pre_param[key] = value
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': schedule_id,
                'timestamps': schedule_ts
            }
            res = BackendRequest.get_schedule_result(param)
            if res['result']:
                schedule_info = res.get("item", [])
                if schedule_info:
                    schedule_detail = json.loads(schedule_info[0].get("run_result", ""))
                else:
                    schedule_detail = ""
                res_data = self.build_detail(vis_type, request_param, schedule_detail)
                dummy_data["status"] = "1"
                dummy_data["vis_type"] = vis_type
                dummy_data["chart_type"] = chart_type
                dummy_data["time_range"] = pre_param["time_range"]
                dummy_data["cur_ts"] = schedule_ts
                dummy_data["data"] = res_data
                dummy_data["usetable"] = pre_param.get("usetable", "false")
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

    def schedule_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_data = request.POST
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            request_url, post_parameters, request_method, vis_type, chart_type = self.build_param(es_check, post_data)
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'name': post_data.get('schedule_name', ""),
                'post_parameters': post_parameters,
                'request': request_url,
                'vis_type': vis_type,
                'chart_type': chart_type,
                'request_method': request_method,
                'check_interval': int(post_data.get('frequency')),
                'crontab': post_data.get('crontab', "0"),
                'description': post_data.get('schedule_description', ""),
                'start_trigger_time': post_data.get('start_trigger_time', ""),
                'resource_group_ids': post_data.get('ids', ""),
                'enabled': 'no' if post_data['enabled'] != 'true' else 'yes'
            }
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "create",
                "module": "schedule",
                "user_name": es_check["u"],
                "user_id": es_check["i"],
                "domain": es_check["d"],
                "target": post_data.get('schedule_name', ""),
                "result": "success"
            }
            if vis_type == "STATS_NEW":
                param["category"] = "1"
            res = BackendRequest.create_schedule(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["location"] = "/alerts/"
            else:
                if res.get("error_code", "") == 7:
                    dummy_data = {
                        'error_type': "110"
                    }
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

    def schedule_update(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_data = request.POST
        _post_data = parser.parse(request.POST.urlencode().encode('utf-8'))
        post_param = _post_data.get("post_parameters", {})

        schedule_id = kwargs['sid']
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': schedule_id,
                'name': post_data.get('schedule_name', ""),
                'description': post_data.get('schedule_description', ""),
                'post_parameters': json.dumps(post_param),
                'request': urllib.urlencode(post_param),
                'check_interval': int(post_data.get('frequency')),
                'crontab': post_data.get('crontab', "0"),
                'start_trigger_time': post_data.get('start_trigger_time', ""),
                'resource_group_ids': post_data.get('resource_group_ids', ""),
                'enabled': 'no' if post_data['enabled'] != 'true' else 'yes'
            }
            print param
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "update",
                "module": "schedule",
                "user_name": es_check["u"],
                "user_id": es_check["i"],
                "domain": es_check["d"],
                "target": post_data.get('schedule_name', ""),
                "result": "success"
            }
            res = BackendRequest.update_schedule(param)
            if res['result']:
                dummy_data["status"] = "1"
            else:
                if res.get("error_code", "") == 7:
                    dummy_data = {
                        'error_type': "110"
                    }
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

    def schedule_delete(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        schedule_id = kwargs['sid']

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            res = BackendRequest.delete_saved_schedule({
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': schedule_id
            })
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "delete",
                "module": "schedule",
                "user_name": es_check["u"],
                "user_id": es_check["i"],
                "domain": es_check["d"],
                "target": schedule_id,
                "result": "success"
            }
            if res['result']:
                list_res = BackendRequest.get_all_saved_schedule({
                    'token': es_check['t'],
                    'operator': es_check['u'],
                })
                if list_res['result']:
                    data = self.rebuild_schedule_list(list_res['item'])
                    dummy_data["status"] = "1"
                    dummy_data["totle"] = len(data)
                    dummy_data["list"] = data["schedules"]
                else:
                    dummy_data["status"] = "1"
                    dummy_data["totle"] = 0
                    dummy_data["list"] = []
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

    def schedule_enable(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        schedule_id = kwargs['sid']
        schedule_enabled = int(kwargs['enable'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'id': schedule_id,
                'token': es_check['t'],
                'operator': es_check['u']
            }
            if schedule_enabled == 1:
                # enabled ==> disbaled
                res = BackendRequest.disable_schedule(param)
            else:
                # disabled ==> enabled
                res = BackendRequest.enable_schedule(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["enabled"] = res.get("saved_schedule", {}).get("enabled", False)
                dummy_data["msg"] = "enable/disable successfully"
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


    def get_resourcegroup_list(self, request, **kwargs):
        """Get a list of available resource groups in aspect of current user.
        """

        self.method_check(request, allowed=['get'])
        dummy_data = {}

        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            # 'action' specifies what action is performed: Read, Assign
            # 'target' specifies what module is requesting
            param = {}
            if kwargs['action'].lower() == "read":
                param['action'] = "Read"
                param['category'] = "SavedSchedule"
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = "ResourceGroup"
            elif kwargs['action'].lower() == "assign":
                param['action'] = "Assign"
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = "SavedSchedule"

            res = BackendRequest.permit_list_resource_group(param)

            if res['result']:
                data = self.rebuild_resource_group_list(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["list"] = data
            else:
                dummy_data['status'] = 0
                dummy_data['msg'] = res.get('error', "Unknow server error")
        else:
            dummy_data['status'] = 0
            dummy_data['msg'] = "auth failed/error"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)

        return resp


    def get_resourcegroup_assigned_list(self, request, **kwargs):
        """
        """

        self.method_check(request, allowed=['get'])
        sid = kwargs.get('sid', "")
        dummy_data = {}

        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'resource_id': sid,
                'category': "SavedSchedule"
            }

            res = BackendRequest.list_assigned_resource_group(param)

            if res['result']:
                data = self.rebuild_assigned_resource_group_list(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["list"] = data
            else:
                dummy_data["status"] = 0
                dummy_data["msg"] = res.get('error', 'get source group history error!')
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def resourcegroup_filter(self, request, **kwargs):
        """
        """

        self.method_check(request, allowed=['post'])

        req_data = request.POST
        ids = req_data.get('ids', "")
        dummy_data = {}

        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'ids': ids
            }

            res = BackendRequest.get_batch_saved_schedule(param)

            if res['result']:
                data = self.rebuild_schedule_list(res['saved_schedules'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["list"] = data["schedules"]
                permit_param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_data = {
                    'permits': data["permits"]
                }
                permit_res = BackendRequest.batch_permit_can(permit_param, permit_data)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
            else:
                dummy_data['status'] = 0
                dummy_data['msg'] = res.get('error', "Unknow server error")
        else:
            dummy_data['status'] = 0
            dummy_data['msg'] = "auth failed/error"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)

        return resp

    def resourcegroup_ungrouped(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'category': 'SavedSchedule',
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.list_derelict_resource_ids(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["ids"] = res['resource_ids']
            else:
                dummy_data['status'] = 0
                dummy_data['msg'] = res.get('error', "Unknow server error")
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

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
    def rebuild_assigned_resource_group_list(data):
        res_list = []
        for item in data:
            final = {}
            final["type"] = item.get("category").encode('utf-8')
            final["rgname"] = item.get("name").encode('utf-8')
            final["memo"] = item.get("memo", "").encode('utf-8')
            final["domain_id"] = item.get("domain_id")
            final["creator_id"] = item.get("creator_id")
            final["rg_id"] = item.get("id")
            res_list.append(final)
        return res_list


    @staticmethod
    def rebuild_schedule_list(origin):
        target = {
            "schedules": [],
            "permits": []
        }
        schedules = []
        permits = []
        for i in origin:
            schedules.append({
                "schedule_id": i['id'],
                "description": i.get("description", ""),
                "schedule_owner": i["owner_name"],
                "schedule_name": i["name"],
                "lastrun": i.get("last_run_timestamp", 0),
                "frequency": i.get("check_interval", "5"),
                "crontab": i.get("crontab", "0"),
                "enabled": i.get("enabled", False),
                "derelict": i.get("derelict", False)
            })
            permits.append({
                "resource_id": int(i['id']),
                "target": "SavedSchedule",
                "action": "Update"
            })
            permits.append({
                "resource_id": int(i['id']),
                "target": "SavedSchedule",
                "action": "Delete"
            })
        permits.append({
            "target": "SavedSchedule",
            "action": "Create"
        })
        permits.append({
            "target": "DerelictResource",
            "action": "Possess"
        })
        target["schedules"] = schedules
        target["permits"] = permits
        return target

    @staticmethod
    def build_param(auth_result, post_data):
        vis_type = post_data.get("visType", "")
        chart_type = post_data.get("chartType", "")
        param = {}
        to_post = {}
        method = "GET"
        if vis_type == "SJJSTJ":
            chartCount = int(post_data["chartCount"])
            i = 0
            fields = []
            while (i < chartCount):
                name = 'fields[' + str(i) + '][name]'
                chartType = 'fields[' + str(i) + '][chartType]'
                isUnique = 'fields[' + str(i) + '][isUnique]'
                fields.append({
                    'name': str(post_data[name]),
                    'chartType': str(post_data[chartType]),
                    'isUnique': str(post_data[isUnique])
                })
                i = i + 1
            param = {
                "act": "search",
                "query": post_data["query"],
                "token": auth_result["t"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if post_data["time_range"] == "," else post_data["time_range"],
                "order": post_data.get("order", 'desc'),
                "size": post_data.get("size", 20000),
                "page": int(post_data.get('page', 1)) - 1,
                "filter_field": post_data.get("filters", ""),
                "category": "events",
                "usetable": "true",
                "stat_fields": fields,
                "stat_method": post_data.get("method", ""),
                "source_group": post_data.get('sourcegroupCn', '') if post_data.get('sourcegroup', 'all') != 'all' else post_data.get('sourcegroup', 'all'),
                "range": post_data.get("range", "")
            }
        elif vis_type == "SJSFDTJ_TIME" or vis_type == "SJSFDTJ_VALUE":
            param = {
                "act": "search",
                "query": post_data["query"],
                "token": auth_result["t"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if post_data["time_range"] == "," else post_data["time_range"],
                "order": post_data.get("order", 'desc'),
                "size": post_data.get("size", 20000),
                "page": int(post_data.get('page', 1)) - 1,
                "filter_field": post_data.get("filters", ""),
                "source_group": post_data.get('sourcegroupCn', '') if post_data.get('sourcegroup', 'all') != 'all' else post_data.get('sourcegroup', 'all'),
                "category": "events",
                "usetable": "true",
                "stat_field": post_data.get("stat_field", ""),
                "stat_method": post_data.get("stat_method", ""),
                "stat_ranges": post_data.get("stat_ranges", ""),
            }
        elif vis_type == "ZFT_TIME" or vis_type == "ZFT_VALUE":
            param = {
                "act": "search",
                "query": post_data["query"],
                "token": auth_result["t"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if post_data["time_range"] == "," else post_data["time_range"],
                "order": post_data.get("order", 'desc'),
                "size": post_data.get("size", 20000),
                "page": int(post_data.get('page', 1)) - 1,
                "filter_field": post_data.get("filters", ""),
                "source_group": post_data.get('sourcegroupCn', '') if post_data.get('sourcegroup', 'all') != 'all' else post_data.get('sourcegroup', 'all'),
                "category": "events",
                "usetable": "true",
                "stat_field": post_data.get("stat_field", ""),
                "stat_method": post_data.get("stat_method", ""),
                "stat_interval": post_data.get("stat_interval", ""),
            }
        elif vis_type == "ZDFLTJ":
            param = {
                "act": "search",
                "query": post_data["query"],
                "token": auth_result["t"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if post_data["time_range"] == "," else post_data["time_range"],
                "order": post_data.get("order", 'desc'),
                "size": post_data.get("size", 20000),
                "page": int(post_data.get('page', 1)) - 1,
                "filter_field": post_data.get("filters", ""),
                "category": "events",
                "usetable": "true",
                "stat_field": post_data.get("field", ""),
                "stat_method": post_data.get("method", ""),
                "topn": post_data.get("topn", 5),
                "with_trend": post_data.get("trend", "false"),
                "source_group": post_data.get('sourcegroupCn', '') if post_data.get('sourcegroup', 'all') != 'all' else post_data.get('sourcegroup', 'all')
            }
        elif vis_type == "ZDSZTJ":
            param = {
                "act": "search",
                "query": post_data["query"],
                "token": auth_result["t"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if post_data["time_range"] == "," else post_data["time_range"],
                "order": post_data.get("order", 'desc'),
                "size": post_data.get("size", 20000),
                "page": int(post_data.get('page', 1)) - 1,
                "filter_field": post_data.get("filters", ""),
                "category": "events",
                "usetable": "true",
                "source_group": post_data.get('sourcegroupCn', '') if post_data.get('sourcegroup', 'all') != 'all' else post_data.get('sourcegroup', 'all'),
                "stat_field": post_data.get("stat_field", ""),
                "stat_method": post_data.get("stat_method", ""),
                "stat_split_field_topn": 5,
                "stat_split_field": post_data.get("stat_split_field", ""),
                "range": post_data.get("range", "")
            }
        elif vis_type == "LJBFB":
            param = {
                "act": "search",
                "query": post_data["query"],
                "token": auth_result["t"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if post_data["time_range"] == "," else post_data["time_range"],
                "order": post_data.get("order", 'desc'),
                "size": post_data.get("size", 20000),
                "page": int(post_data.get('page', 1)) - 1,
                "filter_field": post_data.get("filters", ""),
                "category": "events",
                "usetable": "true",
                "stat_field": post_data.get("stat_field", ""),
                "stat_field_org": post_data.get("stat_field_org", ""),
                "stat_method": post_data.get("stat_method", ""),
                "stat_values": post_data.get("percents", ""),
                "source_group": post_data.get('sourcegroupCn', '') if post_data.get('sourcegroup', 'all') != 'all' else post_data.get('sourcegroup', 'all')
            }
        elif vis_type == "DJTJ":
            method = "POST"
            step = post_data.get('stat_step', '')
            to_post = {
                "query": {}
            }
            need_other = False
            need_timeline = False
            if step and step == 'step1':
                to_post["query"] = {
                    "step1": {
                        "terms": {
                            "field": post_data.get('stat_field', ''),
                            "size": int(post_data.get('stat_top', '5'))
                        }
                    }
                }
                # if req_data.get('stat_chartType', ''):
                #     if req_data.get('stat_other', 'false')
                need_other = True if post_data.get('stat_other', False) and post_data.get('stat_other', False) != 'false' else False
                if post_data.get('stat_chartType', '') and need_other:
                    to_post["query"]['missing_result'] = {
                        "missing": {
                            "field": post_data.get('stat_field', '')
                        }
                    }
                if post_data.get('stat_chartType', '') and post_data.get('stat_split', ''):
                    need_timeline = True
                    to_post["query"]["step1"]['group'] = {
                        "timeline_result": {
                            "timeline": {
                                "period": post_data.get('stat_split', '')
                            }
                        }}
                # if req_data.get('stat_chartType')
            elif step and step == "step2":
                ori_statis_type = post_data.get('stat_method', 'count')
                mid_statis_type = "stats" if ori_statis_type in ["sum", "max", "min", "avg"] else ori_statis_type
                final_stats_type = "terms" if mid_statis_type == "count" else mid_statis_type
                to_post["query"] = {
                    "step2": {
                        final_stats_type: {
                            "field": post_data.get('stat_split_field', '')
                        }
                    }
                }
                need_other = True if post_data.get('stat_other', False) and post_data.get('stat_other', False) != 'false' else False
                if post_data.get('stat_chartType', '') and need_other:
                    to_post["query"]['missing_result'] = {
                        "missing": {
                            "field": post_data.get('stat_split_field', '')
                        }
                    }
                if post_data.get('stat_chartType', '') and post_data.get('stat_split', ''):
                    need_timeline = True
                    if final_stats_type == 'stats' or final_stats_type == "cardinality":
                        to_post["query"] = {
                            "step2": {
                                "timeline": {
                                    "period": post_data.get('stat_split', '')
                                },
                                "group": {
                                    "timeline_result": {
                                        final_stats_type: {
                                            "field": post_data.get('stat_split_field', '')
                                        }
                                    }
                                }

                            }
                        }
                    else:
                        to_post["query"]["step2"]['group'] = {
                            "timeline_result": {
                                "timeline": {
                                    "period": post_data.get('stat_split', '')
                                }
                            }
                        }
            elif step and step == "step3":
                ori_statis_type = post_data.get('stat_method', 'count')
                mid_statis_type = "stats" if ori_statis_type in ["sum", "max", "min", "avg"] else ori_statis_type
                final_stats_type = "terms" if mid_statis_type == "count" else mid_statis_type
                to_post["query"] = {
                    "step3": {
                        final_stats_type: {
                            "field": post_data.get('stat_split_field', '')
                        }
                    }
                }
                need_other = True if post_data.get('stat_other', False) and post_data.get('stat_other', False) != 'false' else False
                if post_data.get('stat_chartType', '') and need_other:
                    to_post["query"]['missing_result'] = {
                        "missing": {
                            "field": post_data.get('stat_split_field', '')
                        }
                    }
                if post_data.get('stat_chartType', '') and post_data.get('stat_split', ''):
                    need_timeline = True
                    if final_stats_type == 'stats' or final_stats_type == "cardinality":
                        to_post["query"] = {
                            "step3": {
                                "timeline": {
                                    "period": post_data.get('stat_split', '')
                                },
                                "group": {
                                    "timeline_result": {
                                        final_stats_type: {
                                            "field": post_data.get('stat_split_field', '')
                                        }
                                    }
                                }

                            }
                        }
                    else:
                        to_post["query"]["step3"]['group'] = {
                            "timeline_result": {
                                "timeline": {
                                    "period": post_data.get('stat_split', '')
                                }
                            }
                        }
            param = {
                "act": "search",
                "query": post_data["query"],
                "token": auth_result["t"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if post_data["time_range"] == "," else post_data["time_range"],
                "order": post_data.get("order", 'desc'),
                "size": post_data.get("size", 20000),
                "page": int(post_data.get('page', 1)) - 1,
                "stat_chartType": post_data.get("stat_chartType", ""),
                "stat_field": post_data.get("stat_field", ""),
                "stat_split_field": post_data.get("stat_split_field", ""),
                "stat_split": post_data.get("stat_split", ""),
                "stat_step": post_data.get("stat_step"),
                "stat_method": post_data.get("stat_method"),
                "filter_field": post_data.get("filters", ""),
                "source_group": post_data.get('sourcegroupCn', '') if post_data.get('sourcegroup', 'all') != 'all' else post_data.get('sourcegroup', 'all'),
                "category": "events",
                "usetable": "true",
                "stat_top": post_data.get("stat_top", ""),
                "range": post_data.get("range", "")
            }
        elif vis_type == "STATS":
            param = {
                "act": "search",
                "query": post_data["query"],
                "token": auth_result["t"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if post_data["time_range"] == "," else post_data["time_range"],
                "order": post_data.get("order", 'desc'),
                "size": 1,
                "page": int(post_data.get('page', 1)) - 1,
                "page": int(post_data["page"]) - 1,
                "filter_field": post_data.get("filters", ""),
                "category": "events",
                "field": post_data.get("field", ""),
                "source_group": post_data.get('sourcegroupCn', '') if post_data.get('sourcegroup', 'all') != 'all' else post_data.get('sourcegroup', 'all')
            }
        elif vis_type == "STATS_NEW":
            param = {
                "act": "search",
                "query": post_data["query"],
                "token": auth_result["t"],
                "owner_name": auth_result["u"],
                "owner_id": auth_result["i"],
                "time_range": "-1d,now" if post_data["time_range"] == "," else post_data["time_range"],
                "order": post_data.get("order", 'desc'),
                "size": post_data.get("size", 20000),
                "page": int(post_data.get('page', 1)) - 1,
                "sid": post_data.get("sid", ""),
                "filter_field": post_data.get("filters", ""),
                "category": "events",
                "usetable": "true",
                "field": post_data.get("field", ""),
                "xField": post_data.get("xField", ""),
                "yField": post_data.get("yField", ""),
                "yFields": post_data.get("yFields", ""),
                "yCharts": post_data.get("yCharts", ""),
                "fromField": post_data.get("fromField", ""),
                "toField": post_data.get("toField", ""),
                "fromLongitudeField": post_data.get("fromLongitudeField", ""),
                "fromLatitudeField": post_data.get("fromLatitudeField", ""),
                "toLongitudeField": post_data.get("toLongitudeField", ""),
                "toLatitudeField": post_data.get("toLatitudeField", ""),
                "weightField": post_data.get("weightField", ""),
                "outlierField": post_data.get("outlierField", ""),
                "upperField": post_data.get("upperField", ""),
                "lowerField": post_data.get("lowerField", ""),
                "cur_ByField": post_data.get("cur_ByField", ""),
                "cur_ByFields": post_data.get("cur_ByFields", ""),
                "defaultColor": post_data.get("defaultColor", ""),
                "colorValues": post_data.get("colorValues", ""),
                "source_group": post_data.get('sourcegroupCn', '') if post_data.get('sourcegroup', 'all') != 'all' else post_data.get('sourcegroup', 'all')
            }
        p = urllib.urlencode(param)
        body = json.dumps(to_post)
        return (p, body, method, vis_type, chart_type)

    def convertToOldResultFormat(self, data):
        result = data["result"]
        return {
            "total": result["sheets"]["total"],
            "type": result["type"] if "type" in result else data['type'],
            "start_timestamp": result["starttime"],
            "end_timestamp": result["endtime"],
            "_field_infos_": result["sheets"]["_field_infos_"],
            "stats": result["sheets"]["rows"]
        }

    def build_detail(self, vis_type, request_param, res_data):
        params = {}
        request_arr = request_param.split("&")
        for item in request_arr:
            key, value = item.split("=")
            params[key] = value
        if vis_type == "SJJSTJ":
            if params.get("usetable") == "true":
                res_data = self.convertToOldResultFormat(res_data)
                stat_fields = urllib.unquote(params.get("stat_fields"))
                stat_fields = stat_fields.replace("+", "").replace("'", '"')
                fields = json.loads(stat_fields)
                param = {}
                param["fields"] = fields
                return {
                    "data": res_data,
                    "param": param,
                    "search_timerange": str(res_data.get("start_timestamp", "")) + "," + str(res_data.get("end_timestamp", ""))
                }
            else:
                stat_method = params.get("stat_method", "")
                value_key = 'value' if stat_method == 'cardinality' else 'doc_count'
                data = {
                    "stat_field": params.get("stat_field", ""),
                    "status": 1,
                    "start_time": res_data["buckets"][0]["from"],
                    "end_time": res_data["buckets"][len(res_data["buckets"]) - 1]["to"],
                    "list": []
                }
                span_arr = []
                for b_index, bucket in enumerate(res_data["buckets"]):
                    span_arr.append(bucket["to"] - bucket["from"])
                    if b_index != len(res_data["buckets"]) - 1:
                        data["list"].append([int(bucket["to"]), bucket.get(value_key, 0)])
                    else:
                        data["list"].append([int(res_data["buckets"][0]["to"] + (max(span_arr) * (len(res_data["buckets"]) - 1))), bucket.get(value_key, 0)])
                data["range"] = max(span_arr)
                data["search_timerange"] = str(res_data.get("start_timestamp", "")) + "," + str(res_data.get("end_timestamp", ""))
                return data
        elif vis_type == "SJSFDTJ_TIME" or vis_type == "SJSFDTJ_VALUE":
            if params.get("usetable") == "true":
                res_data = self.convertToOldResultFormat(res_data)
                return {
                    "data": res_data,
                    "param": {},
                    "search_timerange": str(res_data.get("start_timestamp", "")) + "," + str(res_data.get("end_timestamp", ""))
                }
            else:
                data = {
                    "status": 1,
                    "data": res_data.get('buckets', [])
                }
                data["search_timerange"] = str(res_data.get("start_timestamp", "")) + "," + str(res_data.get("end_timestamp", ""))
                return data
        elif vis_type == "ZFT_TIME" or vis_type == "ZFT_VALUE":
            if params.get("usetable") == "true":
                res_data = self.convertToOldResultFormat(res_data)
                param = {}
                param["interval"] = params.get('stat_interval')
                return {
                    "data": res_data,
                    "param": param,
                    "search_timerange": str(res_data.get("start_timestamp", "")) + "," + str(res_data.get("end_timestamp", ""))
                }
            else:
                data = {
                    "status": 1,
                    "data": res_data.get('buckets', [])
                }
                data["search_timerange"] = str(res_data.get("start_timestamp", "")) + "," + str(res_data.get("end_timestamp", ""))
                return data
        elif vis_type == "ZDFLTJ":
            if params.get("usetable") == "true":
                res_data = self.convertToOldResultFormat(res_data)
                param = {}
                param["field"] = params["stat_field"]
                param["type"] = "data" if params["with_trend"] == 'false' else "graph"
                return {
                    "data": res_data,
                    "param": param,
                    "search_timerange": str(res_data.get("start_timestamp", "")) + "," + str(res_data.get("end_timestamp", ""))
                }
            else:
                data = {
                    "status": 1,
                    "list": []
                }
                for i in res_data["buckets"]:
                    if params.get("trend") == "false":
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
                data["search_timerange"] = str(res_data.get("start_timestamp", "")) + "," + str(res_data.get("end_timestamp", ""))
                return data
        elif vis_type == "ZDSZTJ":
            if params.get("usetable") == "true":
                res_data = self.convertToOldResultFormat(res_data)
                param = {}
                param["field"] = params.get("stat_split_field").split("%3A")[0]
                param["range"] = params.get("range")
                param["start_time"] = res_data["start_timestamp"]
                param["end_time"] = res_data["end_timestamp"]
                return {
                    "data": res_data,
                    "param": param,
                    "search_timerange": str(res_data.get("start_timestamp", "")) + "," + str(res_data.get("end_timestamp", ""))
                }
            else:
                data = {
                    "status": 1,
                    "data": []
                }
                stat_method = params.get("stat_method", "")
                for result in res_data["buckets"]:
                    val = {
                        "start_time": result["buckets"][0]["from"],
                        "end_time": result["buckets"][len(result["buckets"]) - 1]["to"],
                        "name": result["key"],
                        "arr": []
                    }
                    span_arr = []
                    for b_index, bucket in enumerate(result["buckets"]):
                        span_arr.append(bucket["to"] - bucket["from"])
                        if stat_method in ['sum', 'avg', 'max', 'min']:
                            if b_index != len(result["buckets"]) - 1:
                                val["arr"].append([int(bucket["to"]), bucket.get("value", 0)])
                            else:
                                val["arr"].append(
                                    [int(result["buckets"][0]["to"] + (max(span_arr) * (len(result["buckets"]) - 1))),
                                     bucket.get("value"), 0])
                    val["range"] = max(span_arr)
                    data["data"].append(val)
                data["search_timerange"] = str(res_data.get("start_timestamp", "")) + "," + str(res_data.get("end_timestamp", ""))
                return data
        elif vis_type == "LJBFB":
            if params.get("usetable") == "true":
                res_data = self.convertToOldResultFormat(res_data)
                param = {}
                param["field"] = params.get("stat_field")
                param["reverse"] = False if params["stat_method"] == "percentiles" else True
                if param["reverse"]:
                    param["reValue"] = params.get("stat_values", 0)
                else:
                    param["percents"] = ','.join(params.get("stat_values", "").split("%2C"))
                    param["stat_field_org"] = params.get("stat_field_org", "").replace("%3A", ":")
                return {
                    "data": res_data,
                    "param": param,
                    "search_timerange": str(res_data.get("start_timestamp", "")) + "," + str(res_data.get("end_timestamp", ""))
                }
            else:
                data = {
                    "status": 1,
                    "list": []
                }
                if params.get("stat_method", "") == "percentiles":
                    for (k, v) in res_data["values"].items():
                        data["list"].append({
                            "percent": float(k),
                            "value": float('%.3f' % v)
                        })
                    data["list"] = sorted(data["list"], key=lambda x: x["percent"])
                else:
                    if res_data["values"]:
                        for (k, v) in res_data["values"].items():
                            data["list"].append(v)
                    else:
                        data = {
                            "status": 0,
                            "msg": "search error"
                        }
                data["search_timerange"] = str(res_data.get("start_timestamp", "")) + "," + str(res_data.get("end_timestamp", ""))
                return data
        elif vis_type == "DJTJ":
            step = params.get('stat_step', '')
            if  params.get("usetable") == "true":
                res_data = self.convertToOldResultFormat(res_data)
                param = {}
                param["stat_field"] = params.get("stat_field")
                param["stat_chartType"] = params.get("stat_chartType")
                param["range"] = params.get("range")
                param["start_time"] = res_data["start_timestamp"]
                param["end_time"] = res_data["end_timestamp"]
                return {
                    "data": res_data,
                    "param": param,
                    "search_timerange": str(res_data.get("start_timestamp", "")) + "," + str(res_data.get("end_timestamp", ""))
                }
            else:
                data = {
                    "status": 1,
                    "list": []
                }
                need_other = False
                need_timeline = False
                if step == 'step1':
                    if params.get('stat_chartType', '') and params.get('stat_split', ''):
                        need_timeline = True
                    need_other = True if params.get('stat_other', False) and params.get('stat_other', False) != 'false' else False
                    if not need_timeline:
                        total = res_data['total']
                        in_use = 0
                        for i in res_data["data"][step]["buckets"]:
                            data["list"].append({
                                "name": i['key'],
                                "count": i['doc_count']
                            })
                            in_use += i['doc_count']
                        if need_other:
                            missing = res_data['data']['missing_result']['doc_count']

                            data["list"].append({
                                "name": 'other',
                                "count": total - missing - in_use
                            })
                    else:
                        for result in res_data['data'][step]["buckets"]:
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
                                        [int(result["timeline_result"]["buckets"][0]["to"] + (max(span_arr) * (len(result["timeline_result"]["buckets"]) - 1))),
                                         bucket.get("doc_count"), 0])
                            val["range"] = max(span_arr)
                            data["list"].append(val)
                elif step == 'step2':
                    ori_statis_type = params.get('stat_method', 'count')
                    mid_statis_type = "stats" if ori_statis_type in ["sum", "max", "min", "avg"] else ori_statis_type
                    final_stats_type = "terms" if mid_statis_type == "count" else mid_statis_type
                    need_other = True if params.get('stat_other', False) and params.get('stat_other', False) != 'false' else False

                    if params.get('stat_chartType', '') and params.get('stat_split', ''):
                        need_timeline = True

                    if not need_timeline:
                        stat_key = "buckets" if params.get('stat_method', 'count') == "count" else params.get(
                            'stat_method', 'count')
                        stat_key = "value" if stat_key == "cardinality" else stat_key

                        total = res_data['total']
                        in_use = 0

                        try:
                            if params.get('stat_method', 'count') == "count":
                                for p in res_data["data"][step]["buckets"]:
                                    data["list"].append({
                                        "name": p['key'],
                                        "count": p['doc_count'],
                                        "stats_method": params.get('stat_method', 'count'),
                                        "stats": p['doc_count']
                                    })
                                    in_use += p['doc_count']
                            else:
                                data["list"].append({
                                    "name": params.get('stat_field', ''),
                                    "count": res_data["data"][step][stat_key],
                                    "stats_method": params.get('stat_method', 'count'),
                                    "stats": res_data["data"][step][stat_key] if not params.get('stat_method', 'count') == 'avg' else float(
                                        '%.2f' % res_data["data"][step][stat_key])
                                })
                            if need_other:
                                missing = res_data['data']['missing_result']['doc_count']

                                data["list"].append({
                                    "name": 'other',
                                    "count": total - missing - in_use
                                })
                        except Exception, e:
                            data = {
                                "status": 0,
                                "msg": "search error"
                            }
                    else:
                        if params.get('stat_method', 'count') == "count":
                            for result in res_data['data'][step]["buckets"]:
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
                                                                         "timeline_result"]["buckets"]) - 1))),
                                             bucket.get("doc_count"), 0])
                                val["range"] = max(span_arr)
                                data["list"].append(val)
                        else:
                            result = res_data['data'][step]
                            stat_key = params.get('stat_method', 'count')
                            stat_key = "value" if params.get('stat_method', 'count') == "cardinality" else stat_key
                            val = {
                                "start_time": result["buckets"][0]["from"],
                                "end_time": result["buckets"][len(result["buckets"]) - 1]["to"],
                                "name": params.get('stat_field', ''),
                                "arr": []
                            }
                            span_arr = []
                            for b_index, bucket in enumerate(result["buckets"]):
                                span_arr.append(bucket["to"] - bucket["from"])

                                if b_index != len(result["buckets"]) - 1:
                                    val["arr"].append([int(bucket["to"]), bucket["timeline_result"].get(stat_key, 0)])
                                else:
                                    val["arr"].append(
                                        [int(result["buckets"][0]["to"] + (max(span_arr) * (len(result["buckets"]) - 1))),
                                         bucket["timeline_result"].get(stat_key, 0), 0])
                            val["range"] = max(span_arr)
                            data["list"].append(val)
                elif step == 'step3':
                    need_other = True if params.get('stat_other', False) and params.get('stat_other', False) != 'false' else False
                    if params.get('stat_chartType', '') and params.get('stat_split', ''):
                        need_timeline = True

                    if not need_timeline:
                        stat_key = "buckets" if params.get('stat_method', 'count') == "count" else params.get(
                            'stat_method', 'count')
                        stat_key = "value" if stat_key == "cardinality" else stat_key

                        total = res_data['total']
                        in_use = 0

                        try:
                            if params.get('stat_method', 'count') == "count":
                                for p in res_data["data"][step]["buckets"]:
                                    data["list"].append({
                                        "name": p['key'],
                                        "count": p['doc_count'],
                                        "stats_method": params.get('stat_method', 'count'),
                                        "stats": p['doc_count']
                                    })
                                    in_use += p['doc_count']
                            else:
                                data["list"].append({
                                    "name": params.get('stat_field', ''),
                                    "count": res_data["data"][step][stat_key],
                                    "stats_method": params.get('stat_method', 'count'),
                                    "stats": res_data["data"][step][stat_key] if not params.get('stat_method', 'count') == 'avg' else float(
                                        '%.2f' % res_data["data"][step][stat_key])
                                })
                            if need_other:
                                missing = res_data['data']['missing_res_datault']['doc_count']

                                data["list"].append({
                                    "name": 'other',
                                    "count": total - missing - in_use
                                })
                        except:
                            data = {
                                "status": 0,
                                "msg": "search error"
                            }
                    else:
                        if params.get('stat_method', 'count') == "count":
                            for result in res_data['data'][step]["buckets"]:
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
                                                                         "timeline_result"]["buckets"]) - 1))),
                                             bucket.get("doc_count"), 0])
                                val["range"] = max(span_arr)
                                data["list"].append(val)
                        else:
                            result = res_data['data'][step]
                            stat_key = params.get('stat_method', 'count')
                            stat_key = "value" if params.get('stat_method', 'count') == "cardinality" else stat_key
                            val = {
                                "start_time": result["buckets"][0]["from"],
                                "end_time": result["buckets"][len(result["buckets"]) - 1]["to"],
                                "name": params.get('stat_field', ''),
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
                                            max(span_arr) * (len(result["buckets"]) - 1))),
                                         bucket["timeline_result"].get(stat_key, 0), 0])
                            val["range"] = max(span_arr)
                            data["list"].append(val)
                data["search_timerange"] = str(res_data.get("start_timestamp", "")) + "," + str(res_data.get("end_timestamp", ""))
                return data
        elif vis_type == "STATS":
            _stats = res_data.get("stats", [])
            _with_stats = 'yes' if "stats" in res_data else 'no'
            if _with_stats == "yes":
                _events = res_data['hits'].get('hits', [])
                total = res_data['hits']["total"]
            else:
                _events = res_data.get('events', [])
                total = res_data["total"]
            data = {
                "status": 1,
                "total": total,
                "page": int(res_data.get("page", 1)),
                "size": res_data.get("size", 20),
                "type": "search",
                "with_stats": _with_stats,
                "sid": res_data.get("sid", ""),
                "search_timerange": str(res_data.get("start_timestamp", "")) + "," + str(
                    res_data.get("end_timestamp", "")),
                "stats": _build_stats(_stats) if _stats else []
            }
            return data
        elif vis_type == "STATS_NEW":
            res_data = self.convertToOldResultFormat(res_data)
            data = {
                "status": 1,
                "total": res_data["total"],
                "type": res_data["type"].lower(),
                "search_timerange": str(res_data.get("start_timestamp", "")) + "," + str(
                    res_data.get("end_timestamp", "")),
                "table": {
                    "head": res_data.get("_field_infos_", []),
                    "body": res_data.get("stats", [])
                },
                "_info": {
                    "xField": params.get("xField"),
                    "yField": params.get("yField"),
                    "fromField": params.get("fromField"),
                    "toField": params.get("toField"),
                    "weightField": params.get("weightField"),
                    "fromLongitudeField": params.get("fromLongitudeField"),
                    "fromLatitudeField": params.get("fromLatitudeField"),
                    "toLongitudeField": params.get("toLongitudeField"),
                    "toLatitudeField": params.get("toLatitudeField"),
                    "outlierField": params.get("outlierField"),
                    "upperField": params.get("upperField"),
                    "lowerField": params.get("lowerField"),
                    "defaultColor": params.get("defaultColor"),
                    "colorValues": params.get("colorValues"),
                    "cur_ByField": params.get("cur_ByField"),
                    "cur_ByFields": params.get("cur_ByFields"),
                    "yFields": params.get("yFields"),
                    "yCharts": params.get("yCharts")
                }
            }
            return data


def _build_stats(stats):
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

                if sub_method == 'extended_stat' or sub_method == 'es' or sub_method == 'extend_stat':
                    a_val.append({"count": value["count"]})
                    a_val.append({"max": value["max"]})
                    a_val.append({"min": value["min"]})
                    a_val.append({"sum": value["sum"]})
                    a_val.append({"avg": float('%.3f' % value["avg"])})
                    a_val.append({"variance": float('%.3f' % value["variance"])})
                    a_val.append({"sum_of_squares": float(value["sum_of_squares"])})
                    a_val.append({"std_deviation": float('%.3f' % value["std_deviation"])})

                if sub_method == "percentiles" or sub_method == 'pct':
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
                    other = value.get("other", 0)
                    for k in value["buckets"]:
                        a_val.append({
                            k["key"]: k["doc_count"]
                        })
                    if other:
                        a_val.append({
                            "other": other
                        })

                if sub_method == "histogram" or sub_method == 'hg':
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
