# -*- coding: utf-8 -*-
# wangqiushi (@yottabyte.cn)
# 2014/07/30
# Copyright 2014 Yottabyte
# file description : resources.py.
from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.account import parser
import logging
import json
import time
import datetime
import hashlib
import ConfigParser
import os
import math
import json
import random

__author__ = 'wangqiushi'

logger = logging.getLogger("yottaweb.audit")
err_data = ContributeErrorData()

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    show_fullname = cf.get('custom', 'fullname')
except Exception, e:
    print e
    show_fullname = "yes"


class AccountResource(Resource):
    class Meta:
        resource_name = 'account'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/users/list/$" % self._meta.resource_name,
                self.wrap_view('account_users_list'), name="api_account_users_list"),
            url(r"^(?P<resource_name>%s)/users/list/other/$" % self._meta.resource_name,
                self.wrap_view('account_users_list_other'), name="api_account_users_list"),
            url(r"^(?P<resource_name>%s)/usage/$" % self._meta.resource_name,
                self.wrap_view('account_usage'), name="api_account_usage"),
            url(r"^(?P<resource_name>%s)/licence_info/$" % self._meta.resource_name,
                self.wrap_view('account_licence_info'), name="api_account_licence_info"),
            url(r"^(?P<resource_name>%s)/usage/sourcegroup/(?P<days>\d+)/$" % self._meta.resource_name,
                self.wrap_view('account_usage_sourcegroup'), name="api_account_usage"),
            url(r"^(?P<resource_name>%s)/users/new" % self._meta.resource_name,
                self.wrap_view('account_users_new'), name="api_account_users_new"),
            url(r"^(?P<resource_name>%s)/users/permit/(?P<uid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_users_permit'), name="api_account_users_permit"),
            url(r"^(?P<resource_name>%s)/users/del/(?P<uid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_users_delete'), name="api_account_users_delete"),
            url(r"^(?P<resource_name>%s)/users/filter/$" % self._meta.resource_name,
                self.wrap_view('account_users_filter'), name="api_account_users_filter"),
            url(r"^(?P<resource_name>%s)/users/ungrouped/$" % self._meta.resource_name,
                self.wrap_view('account_users_ungrouped'), name="api_account_users_ungrouped"),
            url(r"^(?P<resource_name>%s)/users/(?P<uid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_users_update'), name="api_account_users_update"),
            url(r"^(?P<resource_name>%s)/users/list/(?P<action>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_users_action'), name="api_account_users_action"),
            url(r"^(?P<resource_name>%s)/users/list/assigned/(?P<rid>[\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_users_assigned'), name="api_account_users_assigned"),
            url(r"^(?P<resource_name>%s)/usergroups/list/$" % self._meta.resource_name,
                self.wrap_view('account_usergroups_list'), name="api_account_usergroups_list"),
            url(r"^(?P<resource_name>%s)/usergroups/list/simple/$" % self._meta.resource_name,
                self.wrap_view('account_usergroups_list_simple'), name="api_account_usergroups_list"),
            url(r"^(?P<resource_name>%s)/usergroups/detail/(?P<uid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_usergroups_detail'), name="api_account_usergroups_detail"),
            url(r"^(?P<resource_name>%s)/usergroups/new/" % self._meta.resource_name,
                self.wrap_view('account_usergroups_new'), name="api_account_usergroups_new"),
            url(r"^(?P<resource_name>%s)/usergroups/(?P<uid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_usergroups_update'), name="api_account_usergroups_update"),
            url(r"^(?P<resource_name>%s)/usergroups/del/(?P<uid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_usergroups_delete'), name="api_account_usergroups_delete"),
            url(r"^(?P<resource_name>%s)/usergroups/role/(?P<uid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_usergroups_role'), name="api_account_usergroups_role"),
            url(r"^(?P<resource_name>%s)/usergroups/member/(?P<uid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_usergroups_member'), name="api_account_usergroups_member"),
            url(r"^(?P<resource_name>%s)/roles/list/$" % self._meta.resource_name,
                self.wrap_view('account_roles_list'), name="api_account_roles_list"),
            url(r"^(?P<resource_name>%s)/roles/new/$" % self._meta.resource_name,
                self.wrap_view('account_roles_new'), name="api_account_roles_new"),
            url(r"^(?P<resource_name>%s)/roles/detail/(?P<rid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_roles_detail'), name="api_account_roles_detail"),
            url(r"^(?P<resource_name>%s)/roles/assign/(?P<rid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_roles_assign'), name="api_account_roles_assign"),
            url(r"^(?P<resource_name>%s)/roles/(?P<rid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_roles_update'), name="api_account_roles_update"),
            url(r"^(?P<resource_name>%s)/roles/del/(?P<rid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_roles_del'), name="api_account_roles_del"),
            url(r"^(?P<resource_name>%s)/resourcegroups/list/$" % self._meta.resource_name,
                self.wrap_view('account_resourcegroups_list'), name="api_account_resourcegroups_list"),
            url(r"^(?P<resource_name>%s)/resourcegroups/list/(?P<rgtype>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_resourcegroups_current_list'), name="api_account_resourcegroups_current_list"),
            url(r"^(?P<resource_name>%s)/resourcegroups/type/$" % self._meta.resource_name,
                self.wrap_view('account_resourcegroups_type'), name="api_account_resourcegroups_type"),
            url(r"^(?P<resource_name>%s)/resourcegroups/detail/(?P<rgid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_resourcegroups_detail'), name="api_account_resourcegroups_detail"),
            url(r"^(?P<resource_name>%s)/resourcegroups/new/$" % self._meta.resource_name,
                self.wrap_view('account_resourcegroups_new'), name="api_account_resourcegroups_new"),
            url(r"^(?P<resource_name>%s)/resourcegroups/verify/$" % self._meta.resource_name,
                self.wrap_view('account_resourcegroups_verify'), name="api_account_resourcegroups_verify"),
            url(r"^(?P<resource_name>%s)/resourcegroups/import/$" % self._meta.resource_name,
                self.wrap_view('account_resourcegroups_import'), name="api_account_resourcegroups_import"),
            url(r"^(?P<resource_name>%s)/resourcegroups/export/$" % self._meta.resource_name,
                self.wrap_view('account_resourcegroups_export'), name="api_account_resourcegroups_export"),
            url(r"^(?P<resource_name>%s)/resourcegroups/(?P<rgid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_resourcegroups_update'), name="api_account_resourcegroups_update"),
            url(r"^(?P<resource_name>%s)/resourcegroups/del/(?P<rgid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('account_resourcegroups_delete'), name="api_account_resourcegroups_delete"),
        ]

    def account_users_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        data = [
            {"user_id": "34859", "username": "wanadr", "email": "wanadr@123.com",
             "roles": "Owner,Admin", "sourcegroup": "", "last_login": "1406689406396", "created": "1406689406396"}
        ]
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_account_list(param)
            if res['result']:
                data = self._rebuild_account_list(res['accounts'], es_check['t'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["user_list"] = data["accounts"]
                param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_param = {
                    'permits': data["permits"]
                }
                permit_res = BackendRequest.batch_permit_can(param, permit_param)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
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

    def account_users_list_other(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_account_list(param)
            if res['result']:
                data = self._rebuild_account_list_other(res['accounts'], es_check['t'], es_check['i'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["user_list"] = data
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

    def account_usage(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_upload_bytes_stat(param)
            if res['result']:
                data = []
                res['stats'].reverse()
                today = datetime.date.today()
                today_timestamp = time.mktime(today.timetuple()) * 1000
                step = 60*60*24*1000
                days = 29
                unit = {
                    "0": "Byte",
                    "1": "KB",
                    "2": "MB",
                    "3": "GB",
                    "4": "TB",
                    "5": "PB"
                }
                max_value = max(res.get("stats", [0]))
                log_value = 0 if max_value == 0 else int(math.log(max_value, 1024))
                log_value = log_value if log_value <= 5 else 5
                cur_unit = unit.get(str(log_value), "PB")

                g = lambda x: x if x == 0 else round((float(x)/math.pow(1024, log_value)), 4)
                for i in res['stats']:
                    #until today
                    data.append([today_timestamp-days * step, g(i)])
                    days -= 1
                dummy_data["status"] = "1"
                dummy_data["data"] = data
                dummy_data["unit"] = cur_unit
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

    def account_licence_info(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_licence_info(param)
            if res['result']:
                license_info = res.get("licenseInfo", {"volume": 0, "usedIndexVolume": 0, "expiredTimestamp": 0})
                unit = {
                    "0": "Byte",
                    "1": "KB",
                    "2": "MB",
                    "3": "GB",
                    "4": "TB",
                    "5": "PB"
                }
                daily_value = license_info.get("volume", 0)
                daily_log_value = 0 if daily_value == 0 else int(math.log(daily_value, 1024))
                daily_log_value = daily_log_value if daily_log_value <= 5 else 5
                daily_unit = unit.get(str(daily_log_value), "PB")


                expired_time = license_info.get("expiredTimestamp", 0)
                expired_time = expired_time / 1000.0
                expired_time = datetime.datetime.fromtimestamp(expired_time).strftime('%Y-%m-%d %H:%M:%S')

                license_info["dailyIndexVolumeFormatted"] = round((float(daily_value)/math.pow(1024, daily_log_value)), 4)
                license_info["dailyUnit"] = daily_unit
                license_info["expiredTime"] = expired_time


                usage_info = res.get("usageInfo", {"2017-04-01": 0})
                usage_values = usage_info.values()
                if len(usage_values) == 0:
                    max_value = 0
                else:
                    max_value = max(usage_values)
                square_times = 0 if max_value == 0 else int(math.log(max_value, 1024))
                square_times = square_times if square_times <= 5 else 5
                cur_unit = unit.get(str(square_times), "PB")

                g = lambda x: x if x == 0 else round((float(x)/math.pow(1024, square_times)), 4)
                for i in usage_info:
                    d = usage_info[i]
                    usage_info[i] = [g(d), d]

                license_info["usageInfo"] = {
                    "unit": cur_unit,
                    "data": usage_info
                }

                licenses = license_info.get("licenses", [])
                for license in licenses:
                    t1 = license["createTimestamp"]
                    t1 = t1 / 1000.0
                    t1 = datetime.datetime.fromtimestamp(t1).strftime('%Y-%m-%d')
                    license["createTime"] = t1

                    t2 = license["expiredTimestamp"]
                    t2 = t2 / 1000.0
                    t2 = datetime.datetime.fromtimestamp(t2).strftime('%Y-%m-%d %H:%M:%S')
                    license["expiredTime"] = t2

                    v = license["volume"]
                    v_v = 0 if v == 0 else int(math.log(v, 1024))
                    v_v = v_v if v_v <= 5 else 5
                    v_u = unit.get(str(v_v), "PB")
                    license["volumeFormatted"] = round((float(v)/math.pow(1024, v_v)), 4)
                    license["unit"] = v_u

                dummy_data["status"] = "1"
                dummy_data["data"] = license_info
            else:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "get account usage error!"
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "auth error!"
            dummy_data["location"] = "/auth/login/"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def account_usage_sourcegroup(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        days = kwargs['days']
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            results = []
            res = BackendRequest.get_source_group({
                "account": es_check['i'],
                "token": es_check["t"],
                "operator": es_check["u"],
                'stat_days': days
            })
            if res['result']:
                for i in res['items']:
                    a_sg = {
                        'total': 0
                    }
                    for (k, v) in i.get("raw_sizes", {}).items():
                        new_key = k.replace('-', '_')
                        a_sg[new_key] = v
                        a_sg['total'] += v
                    # a_sg = i.get("raw_sizes", {})
                    a_sg["name"] = i['name'].encode('utf-8')
                    results.append(a_sg)
            dummy_data["status"] = "1"
            dummy_data["totle"] = len(results)
            dummy_data["list"] = results
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def account_users_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_dict = request.POST
        param = {
            "name": post_dict.get('username', ''),
            "full_name": post_dict.get('fullname', ''),
            "email": post_dict.get('email', ''),
            "phone": post_dict.get('phone', ''),
            "passwd": post_dict.get('password', ''),
            "user_group_ids": post_dict.get('usergroup', '')
        }
        # 如果show_fullname为no, 说明页面上未展示fullname, 为了减小改动, 人为赋予username
        #if show_fullname == "no" and not param.get("full_name", ""):
        #    param["full_name"] = post_dict.get('username', '')
        #if param['user_group_name'] == '':
        #    param['user_group_name'] = 'default'
        param_check = self.__check_param(self, param, request)
        dummy_data = {}
        es_check = True

        if param_check['has_error']:
            data = err_data.build_error({}, "param should not be empty!")
            data["errorType"] = param_check['error_type']
            dummy_data = data
        else:
            # go check login
            my_auth = MyBasicAuthentication()
            es_check = my_auth.is_authenticated(request, **kwargs)

            if es_check:
                param['operator'] = es_check['u']
                param['token'] = es_check['t']
                param['access_type'] = "user"
                param['passwd'] = hashlib.md5(param['passwd']).hexdigest()
                res = BackendRequest.create_account(param)
                to_log = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    "action": "create_user",
                    "user_name": es_check['u'],
                    "user_id": es_check['i'],
                    "domain": es_check['d'],
                    "result": "success"
                }


                # print "###############res ",res
                if res['result']:
                    dummy_data["status"] = "1"
                    dummy_data["location"] = "/account/users/"
                else:
                    to_log["result"] = "error"
                    to_log["msg"] = res.get('error')
                    data = err_data.build_error(res)
                    dummy_data = data
                    dummy_data["errorType"] = "name has been used"
                logger.info(json.dumps(to_log))
            else:
                data = err_data.build_error({}, "auth error!")
                data["location"] = "/auth/login/"
                dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def account_users_update(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_dict = request.POST
        user_id = kwargs['uid']
        dummy_data = {}
        change_password = post_dict.get('changePassword', 'false')
        if change_password == 'false':
            param = {
                "username": post_dict.get('username', ''),
                "fullname": post_dict.get('fullname', ''),
                "email": post_dict.get('email', ''),
                "phone": post_dict.get('phone', ''),
                "user_group_ids": post_dict.get('usergroup', '')
            }
        else:
            param = {
                "username": post_dict.get('username', ''),
                "fullname": post_dict.get('fullname', ''),
                "email": post_dict.get('email', ''),
                "phone": post_dict.get('phone', ''),
                "oldPassword": post_dict.get('oldPassword', ''),
                "newPassword": post_dict.get('newPassword', ''),
                "rePassword": post_dict.get('rePassword', ''),
                "user_group_ids": post_dict.get('usergroup', '')
            }
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            update_param = {
                'id': user_id,
                'name': param['username'],
                'full_name': param['fullname'],
                'operator': es_check['u'],
                'token': es_check['t'],
                'user_group_ids': param["user_group_ids"],
                'email': param['email'],
                'phone': param['phone']
            }
            if 'newPassword' in param:
                update_param['passwd'] = hashlib.md5(param['newPassword']).hexdigest()
            if 'oldPassword' in param:
                update_param['old_passwd'] = hashlib.md5(param['oldPassword']).hexdigest()

            res = BackendRequest.update_account(update_param)

            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "update_user",
                "user_name": es_check['u'],
                "user_id": es_check['i'],
                "domain": es_check['d'],
                "result": "success",
                "target": user_id
            }
            if res['result']:
                dummy_data["status"] = "1"
                if user_id == str(es_check['i']):
                    dummy_data["location"] = "/account/users/" + user_id + "/"
                else:
                    dummy_data["location"] = "/account/users/"
            else:
                to_log["result"] = "error"
                to_log["msg"] = res.get('error')

                data = err_data.build_error(res)
                dummy_data = data
            logger.info(json.dumps(to_log))
        else:
            data = err_data.build_error({}, "auth error!")
            data["errorType"] = "name has been used"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def account_users_permit(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        user_id = kwargs['uid']
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            permits = []
            permits.append({
                "resource_id": int(user_id),
                "target": "Account",
                "action": "Read"
            })
            permits.append({
                "resource_id": int(user_id),
                "target": "Account",
                "action": "Update"
            })
            permits.append({
                "target": "Account",
                "action": "Create"
            })
            permits.append({
                "target": "UserPassword",
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

    def account_users_delete(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        user_id = kwargs['uid']

        # data = filter(lambda x: x["user_id"] != user_id, data)
        dummy_data = {}
        es_check = True
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            delete_param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': user_id
            }
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "delete_user",
                "user_name": es_check['u'],
                "user_id": es_check['i'],
                "domain": es_check['d'],
                "result": "success",
                "target": user_id
            }

            res = BackendRequest.delete_account(delete_param)
            if res['result']:
                list_param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                list_res = BackendRequest.get_account_list(list_param)
                if list_res['result']:
                    data = self._rebuild_account_list(list_res['accounts'], es_check['t'])
                    dummy_data["status"] = "1"
                    dummy_data["total"] = len(data)
                    dummy_data["user_list"] = data["accounts"]
                    param = {
                        'token': es_check['t'],
                        'operator': es_check['u']
                    }
                    permit_param = {
                        'permits': data["permits"]
                    }
                    permit_res = BackendRequest.batch_permit_can(param, permit_param)
                    if permit_res['result']:
                        dummy_data["permit_list"] = permit_res["short_permits"]
                    else:
                        dummy_data["permit_list"] = []
                else:
                    data = err_data.build_error(list_res)
                    dummy_data = data
            else:
                to_log["result"] = "error"
                to_log["msg"] = res.get('error', '')
                data = err_data.build_error(res)
                dummy_data = data
            logger.info(json.dumps(to_log))
        else:
            data = err_data.build_error({}, "auth error!")
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def account_users_action(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'target': "Account"
            }
            if kwargs['action'].lower() == "read":
                param['action'] = "Read"
            elif kwargs['action'].lower() == "assign":
                param['action'] = "Assign"

            res = BackendRequest.permit_list_resource_group(param)
            if res['result']:
                data = self.rebuild_resource_group_list(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["user_rg_list"] = data
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def account_users_assigned(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        rid = kwargs['rid']
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'resource_id': rid,
                'category': "Account",
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.list_assigned_resource_group(param)
            if res['result']:
                data = self.rebuild_resource_group_list(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["user_rg_list"] = data
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def account_usergroups_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_all_user_group(param)
            if res['result']:
                data = res.get('user_groups', [])
                list_data = self._rebuild_group_data(data)
                dummy_data["status"] = "1"
                dummy_data["total"] = len(list_data["groups"])
                dummy_data["group_list"] = list_data["groups"]
                permit_param = {
                    'permits': list_data["permits"]
                }
                permit_res = BackendRequest.batch_permit_can(param, permit_param)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def account_usergroups_list_simple(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_all_user_group(param)
            if res['result']:
                data = res.get('user_group',[])
                list_data = self._rebuild_group_data_simple(data)
                dummy_data["status"] = "1"
                dummy_data["totle"] = len(data)
                dummy_data["group_list"] = list_data
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

    def account_usergroups_detail(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        group_id = kwargs['uid']
        dummy_data = {}
        permits = []
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': group_id
            }
            res = BackendRequest.get_user_group(param)
            if res['result']:
                data = self._build_group_detail(res.get('user_group', {}))
                dummy_data["status"] = "1"
                dummy_data["detail"] = data

                permits.append({
                    "resource_id": int(group_id),
                    "target": "AccountGroup",
                    "action": "Update"
                })
                permit_param = {
                    'permits': permits
                }
                permit_res = BackendRequest.batch_permit_can(param, permit_param)
                if permit_res['result']:
                    dummy_data["permit"] = permit_res["short_permits"]
                else:
                    dummy_data["permit"] = []
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

    def account_usergroups_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_dict = request.POST
        dict_name = post_dict.get('name')
        dict_ids = post_dict.get('role_ids')
        dict_assign_ids = post_dict.get('assign_role_ids')
        dict_uids = post_dict.get('user_ids', '')
        dict_memo = post_dict.get('memo', '')
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'name': dict_name,
                'memo': dict_memo,
                'role_ids': dict_ids,
                'assign_role_ids': dict_assign_ids
            }
            if dict_uids != "":
                param["user_ids"] = dict_uids
            res = BackendRequest.create_user_group(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["id"] = res['id']
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

    def account_usergroups_update(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_dict = request.POST
        group_id = kwargs['uid']
        dict_name = post_dict.get('name')
        dict_memo = post_dict.get('memo', '')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            param = {
                'id': group_id,
                'name': dict_name,
                'memo': dict_memo,
                'operator': es_check['u'],
                'token': es_check['t']
                }
            res = BackendRequest.update_user_group(param)
            if res['result']:
                data = self._build_group_detail(res.get('user_group', {}))
                dummy_data["status"] = "1"
                dummy_data["user_group"] = data
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

    def account_usergroups_delete(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        group_id = kwargs['uid']

        # data = filter(lambda x: x["user_id"] != user_id, data)
        dummy_data = {}
        es_check = True
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            delete_param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': group_id
            }
            res = BackendRequest.delete_user_group(delete_param)
            if res['result']:
                list_param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                list_res = BackendRequest.get_all_user_group(list_param)
                if list_res['result']:
                    data = list_res.get('user_groups', [])
                    list_data = self._rebuild_group_data(data)
                    dummy_data["status"] = "1"
                    dummy_data["total"] = len(list_data["groups"])
                    dummy_data["group_list"] = list_data["groups"]
                    permit_param = {
                        'permits': list_data["permits"]
                    }
                    permit_res = BackendRequest.batch_permit_can(list_param, permit_param)
                    if permit_res['result']:
                        dummy_data["permit_list"] = permit_res["short_permits"]
                    else:
                        dummy_data["permit_list"] = []
                else:
                    data = err_data.build_error(list_res)
                    dummy_data = data
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

    def account_usergroups_role(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        group_id = kwargs['uid']
        post_dict = request.POST
        dict_ids = post_dict.get('ids')
        dummy_data = {}
        es_check = True
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'role_ids': dict_ids,
                'user_group_id': group_id
            }
            res = BackendRequest.assign_role(param)
            if res['result']:
                data = self._build_group_detail(res.get('user_group', []))
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["user_group"] = data
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

    def account_usergroups_member(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        group_id = kwargs['uid']
        post_dict = request.POST
        dict_ids = post_dict.get('ids')
        dummy_data = {}
        es_check = True
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'user_ids': dict_ids,
                'user_group_id': group_id
            }
            res = BackendRequest.assign_user(param)
            if res['result']:
                data = self._build_group_detail(res.get('user_group', []))
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["user_group"] = data
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

    def account_roles_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        data = [{}]
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_role_list(param)
            if res['result']:
                data = self._rebuild_role_list(res['roles'], es_check['t'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["role_list"] = data

                permit_param = {
                    'token': es_check['t'],
                    'operator': es_check['u'],
                    'target': 'Privilege',
                    'action': 'Possess'
                }
                permit_res = BackendRequest.permit_can(permit_param)
                if permit_res['result']:
                    dummy_data["permit_role"] = permit_res['can']
                else:
                    dummy_data["permit_role"] = False
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

    def account_roles_detail(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        rid = kwargs['rid']
        dummy_data = {}
        if rid != '':
            es_check = False
            # go check login
            my_auth = MyBasicAuthentication()
            es_check = my_auth.is_authenticated(request, **kwargs)
            if es_check:
                param = {
                    'token': es_check['t'],
                    'operator': es_check['u'],
                    'id': rid.encode('utf-8')
                }
                res = BackendRequest.get_role(param)
                if res['result']:
                    data = self._build_role_obj(res['role'])
                    dummy_data["role"] = data
                    dummy_data["status"] = "1"
                    dummy_data["location"] = "/account/roles/"
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
            else:
                data = err_data.build_error({}, "auth error!")
                data["location"] = "/auth/login/"
                dummy_data = data
        else:
            data = err_data.build_error({}, "invalid rid!")
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def account_roles_assign(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        rid = kwargs['rid']
        assign_package = {
            'resource': [],
            'non_resource': [],
            'url_resource': []
        }
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            list_param = {
                'format': 'with_resources',
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_permissionmeta_list(list_param)
            if res['result']:
                for name in res['permission_metas']['resource']:
                    single_param = {
                        'token': es_check['t'],
                        'operator': es_check['u'],
                        'category': name.encode('utf-8'),
                        'role_id': rid
                    }
                    res_rg = BackendRequest.privilege_list_resource_group(single_param)
                    if res_rg['result']:
                        assign_data = {
                            'name': name.encode('utf-8'),
                            'titleObj': json.dumps(res['permission_metas']['resource'][name], ensure_ascii=False).encode('utf8'),
                            'updateRowObj': json.dumps(res_rg['update'], ensure_ascii=False).encode('utf8'),
                            'readRowObj': json.dumps(res_rg['read'], ensure_ascii=False).encode('utf8')
                        }
                        assign_package['resource'].append(assign_data)
                    else:
                        data = err_data.build_error(res)
                        dummy_data = data

                for nr_name in res['permission_metas']['non_resource']:
                    nr_assign_data = {
                        'name': nr_name.encode('utf-8'),
                        'nrObj': json.dumps(res['permission_metas']['non_resource'][nr_name], ensure_ascii=False).encode('utf8')
                    }
                    assign_package['non_resource'].append(nr_assign_data)

                for url_name in res['permission_metas']['url_resources']['urls']:
                    url_assign_data = {
                        'name': url_name.encode('utf-8'),
                        'meta_id': res['permission_metas']['url_resources']['url_permission_meta']['id'],
                        'urlObj': json.dumps(res['permission_metas']['url_resources']['urls'][url_name], ensure_ascii=False).encode('utf8')
                    }
                    assign_package['url_resource'].append(url_assign_data)

                dummy_data["status"] = "1"
                dummy_data["total"] = len(assign_package)
                dummy_data["resourcegroup_table"] = assign_package
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

    def account_roles_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_dict = parser.parse(request.POST.urlencode().encode('utf-8'))
        dict_id = post_dict.get('role_id', '')
        dict_name = post_dict.get('rolename', '')
        dict_memo = post_dict.get('memo', '')
        dict_group = True if request.POST.get('followupGroup') == 'true' else False
        dict_prm = post_dict.get("permissions", []).values() if post_dict.get("permissions", []) else post_dict.get("permissions", [])
        dict_selected_groups = post_dict.get("selectedItem", []).values() if post_dict.get("selectedItem", []) else post_dict.get("selectedItem", [])
        dummy_data = {}
        if dict_name != '':
            es_check = False
            # go check login
            my_auth = MyBasicAuthentication()
            es_check = my_auth.is_authenticated(request, **kwargs)
            if es_check:
                param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                data = {
                    'id': 0,
                    'name': dict_name,
                    'memo': dict_memo,
                    'permissions': self._format_new_int_array(dict_prm)
                }
                res = BackendRequest.create_role(param, data)
                if res['result']:
                    dummy_data["status"] = "1"
                    dummy_data["location"] = "/account/roles/"

                    if dict_group:
                        group_name = dict_name
                        groups = []
                        list_param = {
                            'format': 'with_resources',
                            'token': es_check['t'],
                            'operator': es_check['u']
                        }
                        list_res = BackendRequest.get_permissionmeta_list(list_param)
                        if list_res['result']:
                            for name in list_res['permission_metas']['resource']:
                                if name == "Account" or name not in dict_selected_groups:
                                    continue
                                group_param = {
                                    'token': es_check['t'],
                                    'operator': es_check['u'],
                                    'name': group_name,
                                    'category': name.encode('utf-8'),
                                    'memo': dict_memo,
                                    'role_ids': res['role']['id']
                                }
                                group_res = BackendRequest.create_resource_group(group_param)
                                if group_res['result']:
                                    groups.append(group_param)
                        dummy_data["followupGroup"] = groups

                else:
                    data = err_data.build_error(res)
                    dummy_data = data
            else:
                data = err_data.build_error({}, "auth error!")
                data["location"] = "/auth/login/"
                dummy_data = data
        else:
            data = err_data.build_error({}, "invalid dict_name!")
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def account_roles_update(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_dict = parser.parse(request.POST.urlencode().encode('utf-8'))
        dict_id = post_dict.get('role_id', '')
        dict_name = post_dict.get('rolename', '')
        dict_memo = post_dict.get('memo', '')
        dict_prm = post_dict.get("permissions", []).values() if post_dict.get("permissions", []) else post_dict.get("permissions", [])
        dummy_data = {}
        if dict_name != '' and dict_id != '':
            es_check = False
            # go check login
            my_auth = MyBasicAuthentication()
            es_check = my_auth.is_authenticated(request, **kwargs)
            if es_check:
                param = {
                    'id': dict_id,
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                data = {
                    'id': int(dict_id),
                    'name': dict_name,
                    'memo': dict_memo,
                    'permissions': self._format_int_array(dict_prm)
                }
                res = BackendRequest.update_role(param, data)
                if res['result']:
                    dummy_data["status"] = "1"
                    dummy_data["role_update"] = res['role']
                    dummy_data["location"] = "/account/roles/"
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
            else:
                data = err_data.build_error({}, "auth error!")
                data["location"] = "/auth/login/"
                dummy_data = data
        else:
            data = err_data.build_error({}, "invalid dict_name or dict_id!")
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def account_roles_del(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        roleid = kwargs['rid']
        dummy_data = {}
        if roleid:
            es_check = False
            # go check login
            my_auth = MyBasicAuthentication()
            es_check = my_auth.is_authenticated(request, **kwargs)
            if es_check:
                param = {
                    'id': roleid,
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                list_param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                res = BackendRequest.delete_role(param)
                if res['result']:
                    res_list = BackendRequest.get_role_list(list_param)
                    if res_list['result']:
                        data = self._rebuild_role_list(res_list['roles'], es_check['t'])
                        dummy_data["status"] = "1"
                        dummy_data["total"] = len(data)
                        dummy_data["role_list"] = data

                        permit_param = {
                            'token': es_check['t'],
                            'operator': es_check['u'],
                            'target': 'Privilege',
                            'action': 'Possess'
                        }
                        permit_res = BackendRequest.permit_can(permit_param)
                        if permit_res['result']:
                            dummy_data["permit_role"] = permit_res['can']
                        else:
                            dummy_data["permit_role"] = False
                    else:
                        data = err_data.build_error(res_list)
                        dummy_data = data
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
            else:
                data = err_data.build_error({}, "auth error!")
                data["location"] = "/auth/login/"
                dummy_data = data
        else:
            data = err_data.build_error({}, "invalid role id!")
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def account_resourcegroups_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        resourcegroup_list = []
        permit_list = []
        typename_list = []
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            list_param = {
                'format': 'with_resources',
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_permissionmeta_list(list_param)
            if res['result']:
                for name in res['permission_metas']['resource']:
                    if name == "Account":
                        continue
                    else:
                        single_param = {
                            'target': 'ResourceGroup',
                            'action': 'Read',
                            'token': es_check['t'],
                            'operator': es_check['u'],
                            'category': name.encode('utf-8')
                        }
                        res_rg = BackendRequest.permit_list_resource_group(single_param)
                        if res_rg['result']:
                            for item in res_rg['resource_groups']:
                                resource_data = {
                                    'resourcegroup_id': item['id'],
                                    'type': name.encode('utf-8'),
                                    'memo': item['memo'],
                                    'name': item['name']
                                }
                                resourcegroup_list.append(resource_data)

                                permit_list.append({
                                    "resource_id": item['id'],
                                    "target": "ResourceGroup",
                                    "action": "Delete"
                                })
                                permit_list.append({
                                    "resource_id": item['id'],
                                    "target": "ResourceGroup",
                                    "action": "Update"
                                })
                            permit_list.append({
                                "target": "ResourcePackage",
                                "action": "Possess"
                            })
                        else:
                            data = err_data.build_error(res)
                            dummy_data = data

                        # 通过permit_can直接获取哪个ResourceGroup可以新建，最后通过typename_list是否为空
                        # 可得该用户是否显示新建
                        permit_param = {
                            'token': es_check['t'],
                            'operator': es_check['u'],
                            'target': res['permission_metas']['resource'][name][0][0]['target'],
                            'action': res['permission_metas']['resource'][name][0][0]['action']
                        }
                        permit_res = BackendRequest.permit_can(permit_param)
                        if permit_res['result'] and permit_res['can']:
                            typename_list.append(name)

                dummy_data["status"] = "1"
                dummy_data["total"] = len(resourcegroup_list)
                dummy_data["resourcegroup_list"] = resourcegroup_list

                param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_param = {
                    'permits': permit_list
                }
                permit_res = BackendRequest.batch_permit_can(param, permit_param)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                    if typename_list:
                        dummy_data["permit_list"]["ResourceGroup_Create"] = True
                    else:
                        dummy_data["permit_list"]["ResourceGroup_Create"] = False
                else:
                    dummy_data["permit_list"] = []
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

    def account_resourcegroups_current_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        resourcegroup_list = []
        rg_type = kwargs['rgtype']
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            single_param = {
                'target': 'ResourceGroup',
                'action': 'Read',
                'token': es_check['t'],
                'operator': es_check['u'],
                'category': rg_type
            }
            res = BackendRequest.permit_list_resource_group(single_param)
            if res['result']:
                for item in res['groups']:
                    resource_data = {
                        'rg_id': item['id'],
                        'type': rg_type.encode('utf-8'),
                        'memo': item['memo'],
                        'name': item['name'],
                        'rids': item['resource_ids']
                    }
                    resourcegroup_list.append(resource_data)
            else:
                data = err_data.build_error(res)
                dummy_data = data
            dummy_data["status"] = "1"
            dummy_data["total"] = len(resourcegroup_list)
            dummy_data["resourcegroup_list"] = resourcegroup_list
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def account_resourcegroups_type(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        typename_list = []
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            list_param = {
                'format': 'with_resources',
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_permissionmeta_list(list_param)
            if res['result']:
                for name in res['permission_metas']['resource']:
                    if name == "Account":
                        continue
                    else:
                        permit_param = {
                            'token': es_check['t'],
                            'operator': es_check['u'],
                            'target': res['permission_metas']['resource'][name][0][0]['target'],
                            'action': res['permission_metas']['resource'][name][0][0]['action']
                        }
                        permit_res = BackendRequest.permit_can(permit_param)
                        if permit_res['result'] and permit_res['can']:
                            typename_list.append(name)
                dummy_data["status"] = "1"
                dummy_data["total"] = len(typename_list)
                dummy_data["typename_list"] = typename_list
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

    def account_resourcegroups_detail(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        rgid = kwargs['rgid']
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': int(rgid)
            }
            res = BackendRequest.get_resource_group(param)
            if res['result']:
                data = self._build_resource_group_data(res['resource_group'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["rg_detail"] = data
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

    def account_resourcegroups_update(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        rgid = kwargs['rgid']
        post_dict = request.POST
        dict_name = post_dict.get('rgname')
        dict_memo = post_dict.get('memo', '')
        dict_type = post_dict.get('type')
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': int(rgid),
                'name': dict_name,
                'memo': dict_memo
            }
            res = BackendRequest.update_resource_group(param)
            if res['result']:
                data = self._build_resource_group_data(res['resource_group'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["rg_update"] = data
                dummy_data["location"] = "/account/resourcegroups/"
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

    def account_resourcegroups_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_dict = request.POST
        dict_name = post_dict.get('rgname')
        dict_memo = post_dict.get('memo', '')
        dict_type = post_dict.get('type')
        dict_roleids = post_dict.get('roles')
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'name': dict_name,
                'category': dict_type,
                'memo': dict_memo,
                'role_ids': dict_roleids
            }
            res = BackendRequest.create_resource_group(param)
            if res['result']:
                data = self._build_resource_group_data(res['resource_group'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["rg_update"] = data
                dummy_data["location"] = "/account/resourcegroups/"
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

    def account_resourcegroups_delete(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        rgid = kwargs['rgid']
        resourcegroup_list = []
        permit_list = []
        dummy_data = {}
        es_check = False
        # go check login
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': int(rgid)
            }
            res = BackendRequest.delete_resource_group(param)
            if res['result']:
                list_param = {
                    'format': 'with_resources',
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                res = BackendRequest.get_permissionmeta_list(list_param)
                if res['result']:
                    for name in res['permission_metas']['resource']:
                        single_param = {
                            'target': 'ResourceGroup',
                            'action': 'Read',
                            'token': es_check['t'],
                            'operator': es_check['u'],
                            'category': name.encode('utf-8')
                        }
                        res_rg = BackendRequest.permit_list_resource_group(single_param)
                        if res_rg['result']:
                            for item in res_rg['resource_groups']:
                                resource_data = {
                                    'resourcegroup_id': item['id'],
                                    'type': name.encode('utf-8'),
                                    'memo': item['memo'],
                                    'name': item['name']
                                }
                                resourcegroup_list.append(resource_data)

                                permit_list.append({
                                    "resource_id": item['id'],
                                    "target": "ResourceGroup",
                                    "action": "Delete"
                                })
                                permit_list.append({
                                    "resource_id": item['id'],
                                    "target": "ResourceGroup",
                                    "action": "Update"
                                })
                            permit_list.append({
                                "target": "ResourceGroup",
                                "action": "Create"
                            })
                        else:
                            data = err_data.build_error(res)
                            dummy_data = data
                    dummy_data["status"] = "1"
                    dummy_data["total"] = len(resourcegroup_list)
                    dummy_data["resourcegroup_list"] = resourcegroup_list

                    param = {
                        'token': es_check['t'],
                        'operator': es_check['u']
                    }
                    permit_param = {
                        'permits': permit_list
                    }
                    permit_res = BackendRequest.batch_permit_can(param, permit_param)
                    if permit_res['result']:
                        dummy_data["permit_list"] = permit_res["short_permits"]
                    else:
                        dummy_data["permit_list"] = []
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
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

    def account_resourcegroups_verify(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            import_file = request.FILES['file']
            file_content = import_file.read()
            param = {
                'act': 'verify_resource_package',
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.verify_resource_package(param, file_content)
            if res.get('error_code') in [702, 703, 704, 706]:
                dummy_data = {
                    'status': '0',
                    'msg': res.get('error_code')
                }
            elif res['result']:
                dummy_data["status"] = "1"
            else:
                dummy_data["status"] = "0"
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def account_resourcegroups_import(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        role_ids = request.POST.get('role_ids', '')
        name_conflict_strategy = request.POST.get('op_type', '')
        import_file = request.FILES['file']
        file_content = import_file.read()
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            if not name_conflict_strategy:
                param = {
                    'role_ids': role_ids,
                    'name_conflict_strategy': 'replace',
                    'act': 'import_resource_package',
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                res = BackendRequest.import_resource_package(param, file_content)
                if res['result']:
                    res_data = { 'status': '1' }
                    dummy_data = res_data
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
            else:
                param = {
                    'role_ids': role_ids,
                    'name_conflict_strategy': name_conflict_strategy,
                    'act': 'import_resource_package',
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                res = BackendRequest.import_resource_package(param, file_content)
                if res['result']:
                    res_data = { 'status': '1' }
                    dummy_data = res_data
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

    def account_resourcegroups_export(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        req_data = request.POST
        name = req_data.get('name', '')
        resource_group_ids = req_data.get('ids', '')
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'name': name,
                'resource_group_ids': resource_group_ids,
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.export_resource_package(param)
            if res['result']:
                package_path = res.get('package_path', None)
                res_data = { 'status': '1' }
                if package_path:
                    data = open(package_path).read()
                    res_data['data'] = data
                dummy_data = res_data
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

    def account_users_filter(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        req_data = request.POST
        post_data = req_data.get('ids', '')
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'ids': post_data,
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_batch_account(param)
            if res['result']:
                data = self._rebuild_account_list(res['accounts'], es_check['t'])
                dummy_data["status"] = "1"
                dummy_data["totle"] = len(data)
                dummy_data["user_list"] = data["accounts"]
                param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_param = {
                    'permits': data["permits"]
                }
                permit_res = BackendRequest.batch_permit_can(param, permit_param)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
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

    def account_users_ungrouped(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'category': "Account",
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.list_derelict_resource_ids(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["ids"] = res['resource_ids']
            else:
                data = err_data.build_error(res)
                dummy_data = data
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
            final["rgname"] = item.get("name").encode('utf-8')
            final["memo"] = item.get("memo", "").encode('utf-8')
            final["rg_id"] = item.get("id")
            final["resource_ids"] = item.get("resource_ids", [])
            res_list.append(final)
        return res_list

    @staticmethod
    def __check_param(self, param, request):
        """
        This method checks the parameter to find out whether the password is equal to repassword and
        the required field is full-filled.
        :param self:
        :param request:
        :return: 1.has_error:whether the parameter has error. 2.msg:error message. 3.error_code: the code of error
        """
        res = {
            "has_error": False,
            "msg": "",
            "error_type": ""
        }
        # post_dict = dict(request.POST._iteritems())

        has_error = False
        # for k, v in param.iteritems():
        #     if v == "" and k != "sourcegroup" and k != "usergroup":
        #         res['error_type'] = v
        #         has_error = True
        #         break
        if has_error:
            res["msg"] = "parameter required error"
            res["has_error"] = True
            return res
        else:
            res["msg"] = ""
            res["has_error"] = False
            return res

    @staticmethod
    def _rebuild_account_list(origin_list, token):
        # {"user_id": "34859", "username": "wanadr", "email": "wanadr@123.com",
        # "roles": "Owner,Admin", "sourcegroup": "", "last_login": "1406689406396", "created": "1406689406396"}
        target = {
            "accounts": [],
            "permits": []
        }
        accounts = []
        permits = []
        for el in origin_list:
            ugs = []
            ug_info = el.get('user_group_infos', {})
            user_groups = ug_info.get("user_groups", [])
            for item in user_groups:
                ugs.append(item["name"])
            accounts.append({
                "user_id": el.get('id', ""),
                "username": el.get('name', ""),
                "email": el.get('email', ""),
                "roles": el.get('access_type', ""),
                "sourcegroup": el.get('source_groups', ""),
                "usergroup": ",".join(ugs),
                "last_login": el.get('last_login_time', 0) * 1000,
                "created": el.get('create_time', 0) * 1000,
            })
            permits.append({
                "resource_id": int(el.get('id')),
                "target": "Account",
                "action": "Read"
            })
            permits.append({
                "resource_id": int(el.get('id')),
                "target": "Account",
                "action": "Delete"
            })
        permits.append({
            "target": "Account",
            "action": "Create"
        })
        target["accounts"] = accounts
        target["permits"] = permits
        return target

    @staticmethod
    def _rebuild_account_list_other(origin_list, token, user_id):
        final_list = []
        for el in origin_list:
            # if el.get('id', '') == user_id:
            #     continue
            final_list.append({
                "user_id": el.get('id', ""),
                "username": el.get('name', ""),
                "email": el.get('email', ""),
                "roles": el.get('access_type', ""),
            })
        return final_list

    @staticmethod
    def _rebuild_group_data(data):
        target = {
            "groups": [],
            "permits": []
        }
        final_list = []
        permits = []
        for el in data:
            # if el.get('name', '') == "default":
            #     continue
            final_list.append({
                "name": el["name"],
                "id": int(el["id"]),
                "domain_id": int(el["domain_id"]),
                "memo": el["memo"],
                "in_group": el["in_group"],
            })
            permits.append({
                "resource_id": int(el["id"]),
                "target": "AccountGroup",
                "action": "Delete"
            })
            permits.append({
                "resource_id": int(el["id"]),
                "target": "AccountGroup",
                "action": "Update"
            })
            permits.append({
                "resource_id": int(el["id"]),
                "target": "Account",
                "action": "Read"
            })
        permits.append({
            "target": "AccountGroup",
            "action": "Create"
        })
        target["groups"] = final_list
        target["permits"] = permits
        return target

    @staticmethod
    def _rebuild_group_data_simple(data):
        final_list = []
        for el in data:
            if el.get('name', '') == "default":
                continue
            final_list.append({
                "name": el["name"],
                "id": el["id"],
            })
        return final_list

    @staticmethod
    def _build_group_detail(data):
        final = {}
        members = []
        roles = []
        manager_roles = []
        members_arr = data.get("members", [])
        roles_arr = data.get("roles", [])
        managers_arr = data.get("manager_roles", [])
        for item in roles_arr:
            roles.append({
                "role_id": item["id"],
                "rolename": item["name"],
                "memo": item["memo"],
            })
        for item in managers_arr:
            manager_roles.append({
                "role_id": item["id"],
                "rolename": item["name"],
                "memo": item["memo"],
            })
        for item in members_arr:
            members.append({
                "id": item["id"],
                "name": item["name"],
                "email": item["email"],
            })

        final["name"] = data.get("name")
        final["memo"] = data.get("memo")
        final["id"] = int(data.get("id"))
        final["members"] = members
        final["roles"] = roles
        final["manager_roles"] = manager_roles
        return final

    @staticmethod
    def _rebuild_role_list(origin_list, token):
        final_list = []
        for el in origin_list:
            final_list.append({
                "role_id": el.get('id', ""),
                "rolename": el.get('name', ""),
                "memo": el.get('memo', ""),
                "permissions": el.get('permissions', []),
            })
        return final_list

    @staticmethod
    def _format_int_array(origin_array):
        final_array = []
        for item in origin_array:
            if item.get('resource_id') == "0":
                final_array.append({
                    "permission_meta_id": int(item.get('permission_meta_id')),
                    "id": int(item.get('id'))
                })
            else:
                final_array.append({
                    "permission_meta_id": int(item.get('permission_meta_id')),
                    "resource_id": int(item.get('resource_id')),
                    "id": int(item.get('id'))
                })
        return final_array

    @staticmethod
    def _format_new_int_array(origin_array):
        final_array = []
        for item in origin_array:
            if item.get('resource_id') == "0":
                final_array.append({
                    "permission_meta_id": int(item.get('permission_meta_id')),
                    "id": 0
                })
            else:
                final_array.append({
                    "permission_meta_id": int(item.get('permission_meta_id')),
                    "resource_id": int(item.get('resource_id')),
                    "id": 0
                })
        return final_array

    @staticmethod
    def _build_resource_group_data(data):
        final = {}
        final["type"] = data.get("category")
        final["rgname"] = data.get("name")
        final["memo"] = data.get("memo", "")
        final["domain_id"] = data.get("domain_id")
        final["creator_id"] = data.get("creator_id")
        final["rg_id"] = data.get("id")
        return final

    @staticmethod
    def _build_role_obj(data):
        final = {}
        final["rolename"] = data['name'].encode('utf-8')
        final["memo"] = data['memo'].encode('utf-8')
        final["role_id"] = int(data['id'])
        arr = []
        for item in data['permissions']:
            newObj = {}
            newObj["id"] = int(item["id"])
            newObj["target"] = item["target"]
            newObj["permission_meta_id"] = int(item["permission_meta_id"])
            try:
                newObj["resource_id"] = int(item["resource_id"])
            except Exception:
                newObj["resource_id"] = 0
            arr.append(newObj)
        final["permissions"] = arr
        return final
