# -*- coding: utf-8 -*-
# mayangguang (ma.yanguang@yottabyte.cn)
# 2015/03/25
# Copyright 2015 Yottabyte
# file description : security api

from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
import mimetypes
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.utils.encoding import smart_str
from datetime import datetime
import json
import requests
import os
import hashlib
from django.conf import settings
from subprocess import call
from django.http import Http404
from yottaweb.apps.variable.resources import MyVariable
import os
import re
# get es url from yottaweb.ini


try:
    my_var = MyVariable()
    HEKA_PACKAGE_URL =  my_var.get_var('path', 'data_path') + 'heka_update'
    origin = my_var.get_var('heka_agent', 'download_origin')
except Exception, e:
    print e
    HEKA_PACKAGE_URL =  '/data/rizhiyi/yottaweb/heka_update'
    origin = "http://ops.rizhiyi.com"

err_data = ContributeErrorData()


class AgentResource(Resource):
    class Meta:
        resource_name = 'agent'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/agents/$" % self._meta.resource_name,
                self.wrap_view('agent_agents'), name="api_agent_agents"),
            url(r"^(?P<resource_name>%s)/delete_agent/$" % self._meta.resource_name,
                self.wrap_view('delete_agent'), name="api_delete_agent"),
            url(r"^(?P<resource_name>%s)/get_config/$" % self._meta.resource_name,
                self.wrap_view('agent_get_config'), name="api_agent_get_config"),
            url(r"^(?P<resource_name>%s)/add_config/$" % self._meta.resource_name,
                self.wrap_view('agent_add_config'), name="api_agent_add_config"),
            url(r"^(?P<resource_name>%s)/del_config/$" % self._meta.resource_name,
                self.wrap_view('agent_del_config'), name="api_agent_del_config"),
            url(r"^(?P<resource_name>%s)/get_full_config/$" % self._meta.resource_name,
                self.wrap_view('agent_get_full_config'), name="api_agent_get_full_config"),
            url(r"^(?P<resource_name>%s)/modify_full_config/$" % self._meta.resource_name,
                self.wrap_view('agent_modify_full_config'), name="api_agent_modify_full_config"),
            url(r"^(?P<resource_name>%s)/query_heka_status/$" % self._meta.resource_name,
                self.wrap_view('agent_query_heka_status'), name="api_agent_query_heka_status"),
            url(r"^(?P<resource_name>%s)/control_heka/$" % self._meta.resource_name,
                self.wrap_view('agent_control_state'), name="api_agent_control_state"),
            url(r"^(?P<resource_name>%s)/uploadagent/$" % self._meta.resource_name,
                self.wrap_view('upload_agent'), name="api_upload_agent"),
            url(r"^(?P<resource_name>%s)/download/(?P<platform>.+)/(?P<version>.+)/(?P<file_name>.+)$" % self._meta.resource_name,
                self.wrap_view('agent_download'), name="api_agent_download"),
            url(r"^(?P<resource_name>%s)/delete_agent_package/$" % self._meta.resource_name,
                self.wrap_view('delete_agent_package'), name="api_agent_delete_package"),
            url(r"^(?P<resource_name>%s)/get_agent_package/$" % self._meta.resource_name,
                self.wrap_view('get_agent_package'), name="api_get_agent_package"),
            url(r"^(?P<resource_name>%s)/update_agent/$" % self._meta.resource_name,
                self.wrap_view('update_agent'), name="api_update_agent"),

            # the following is newly added for agent add data
            url(r"^(?P<resource_name>%s)/get_ls/$" % self._meta.resource_name,
                self.wrap_view('agent_get_ls'), name="api_agent_get_ls"),

            url(r"^(?P<resource_name>%s)/preview_match_files/$" % self._meta.resource_name,
                self.wrap_view('preview_match_files'), name="api_agent_preview_match_files"),

            url(r"^(?P<resource_name>%s)/preview_split_result/$" % self._meta.resource_name,
                self.wrap_view('preview_split_result'), name="api_agent_preview_split_result"),

            url(r"^(?P<resource_name>%s)/add_heka_config/$" % self._meta.resource_name,
                self.wrap_view('add_heka_config'), name="api_agent_add_heka_config"),

            url(r"^(?P<resource_name>%s)/get_timestamp_config/$" % self._meta.resource_name,
                self.wrap_view('get_timestamp_config'), name="api_agent_get_timestamp_config"),

            url(r"^(?P<resource_name>%s)/preview_timestamp_recognition/$" % self._meta.resource_name,
                self.wrap_view('preview_timestamp_recognition'), name="api_agent_preview_timestamp_recognition"),

            url(r"^(?P<resource_name>%s)/get_heka_config/$" % self._meta.resource_name,
                self.wrap_view('agent_get_heka_config'), name="api_agent_get_heka_config"),

            url(r"^(?P<resource_name>%s)/del_heka_config/$" % self._meta.resource_name,
                self.wrap_view('agent_del_heka_config'), name="api_agent_del_heka_config"),

            url(r"^(?P<resource_name>%s)/modify_heka_config/$" % self._meta.resource_name,
                self.wrap_view('agent_modify_heka_config'), name="api_agent_modify_heka_config"),


            # for server heka
            url(r"^(?P<resource_name>%s)/server_agent_get_config/$" % self._meta.resource_name,
                self.wrap_view('server_agent_get_config'), name="api_server_agent_get_config"),

            url(r"^(?P<resource_name>%s)/server_agent_add_config/$" % self._meta.resource_name,
                self.wrap_view('server_agent_add_config'), name="api_server_agent_add_config"),

            url(r"^(?P<resource_name>%s)/server_agent_modify_config/$" % self._meta.resource_name,
                self.wrap_view('server_agent_modify_config'), name="api_server_agent_modify_config"),

            url(r"^(?P<resource_name>%s)/server_agent_delete_config/$" % self._meta.resource_name,
                self.wrap_view('server_agent_delete_config'), name="api_server_agent_delete_config"),


            # for dbinput

            url(r"^(?P<resource_name>%s)/verify_connection/$" % self._meta.resource_name,
                self.wrap_view('verify_connection'), name="api_agent_verify_connection"),

            url(r"^(?P<resource_name>%s)/add_connection/$" % self._meta.resource_name,
                self.wrap_view('add_connection'), name="api_agent_add_connection"),

            url(r"^(?P<resource_name>%s)/get_connections/$" % self._meta.resource_name,
                self.wrap_view('get_connections'), name="api_agent_get_connections"),

            url(r"^(?P<resource_name>%s)/del_connection/$" % self._meta.resource_name,
                self.wrap_view('del_connection'), name="api_agent_del_connection"),

            url(r"^(?P<resource_name>%s)/get_drivers/$" % self._meta.resource_name,
                self.wrap_view('get_drivers'), name="api_agent_get_drivers"),

            url(r"^(?P<resource_name>%s)/modify_connection/$" % self._meta.resource_name,
                self.wrap_view('modify_connection'), name="api_agent_modify_connection"),

            url(r"^(?P<resource_name>%s)/fetch_record/$" % self._meta.resource_name,
                self.wrap_view('fetch_record'), name="api_agent_fetch_record"),


            # for agent resource groups
            url(r"^(?P<resource_name>%s)/resourcegroup/read/$" % self._meta.resource_name,
                self.wrap_view('agent_rg_read'), name="api_agent_rg_read"),

            url(r"^(?P<resource_name>%s)/resourcegroup/assign/$" % self._meta.resource_name,
                self.wrap_view('agent_rg_assign'), name="api_agent_rg_assign"),

            url(r"^(?P<resource_name>%s)/resourcegroup/canassign/$" % self._meta.resource_name,
                self.wrap_view('agent_can_rg_assign'), name="api_agent_can_rg_assign"),

            url(r"^(?P<resource_name>%s)/assign_resource/$" % self._meta.resource_name,
                self.wrap_view('agent_assign_resource'), name="api_agent_assign_resource"),

            url(r"^(?P<resource_name>%s)/get_group/$" % self._meta.resource_name,
                self.wrap_view('agent_get_resource_group'), name="api_agent_get_resource_group"),

            url(r"^(?P<resource_name>%s)/add_resource_to_group/$" % self._meta.resource_name,
                self.wrap_view('add_resource_to_group'), name="api_add_resource_to_group"),

            url(r"^(?P<resource_name>%s)/remove_resource_from_group/$" % self._meta.resource_name,
                self.wrap_view('remove_resource_from_group'), name="api_remove_resource_from_group"),

        ]

    def agent_get_resource_group(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        try:
            if es_check:
                rg_id = request.GET.get('rg_id')
                param = {
                  #  "token": es_check["t"],
                    "id": rg_id,
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                res = BackendRequest.get_resource_group(param)

                if res['result']:
                    dummy_data["status"] = "1"
                    dummy_data["data"] = res
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
            else:
                data = err_data.build_error({}, "auth error!")
                data["location"] = "/auth/login/"
                dummy_data = data
        except Exception as e:
            print e
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def agent_assign_resource(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        try:
            if es_check:
                version = request.POST.get('rg_id')
                platform = request.POST.get('r_ids')
                param = {
                  #  "token": es_check["t"],
                    "resource_group_id": version,
                    "resource_ids": platform,
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                res = BackendRequest.assign_resource(param)

                if res['result']:
                    dummy_data["status"] = "1"
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
            else:
                data = err_data.build_error({}, "auth error!")
                data["location"] = "/auth/login/"
                dummy_data = data
        except Exception as e:
            print e
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def add_resource_to_group(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        try:
            if es_check:
                ppp = json.loads(request.body)
                group = ppp.get('rg_id')
                ids = ppp.get('r_ids')
                param = {
                  #  "token": es_check["t"],
                    "resource_group_id": group,
                    "resource_ids": ids,
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                res = BackendRequest.add_resource_to_group(param)

                if res['result']:
                    dummy_data["status"] = "1"
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
            else:
                data = err_data.build_error({}, "auth error!")
                data["location"] = "/auth/login/"
                dummy_data = data
        except Exception as e:
            print e
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def remove_resource_from_group(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        try:
            if es_check:
                ppp = json.loads(request.body)
                version = ppp.get('rg_id')
                platform = ppp.get('r_ids')
                param = {
                  #  "token": es_check["t"],
                    "resource_group_id": version,
                    "resource_ids": platform,
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                res = BackendRequest.remove_resource_from_group(param)

                if res['result']:
                    dummy_data["status"] = "1"
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
            else:
                data = err_data.build_error({}, "auth error!")
                data["location"] = "/auth/login/"
                dummy_data = data
        except Exception as e:
            print e
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    @staticmethod
    def rebuild_resource_group_list(data):
        res_list = []
        permit_request = []
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
            permit_request.append({
                "resource_id": final["rg_id"],
                "target": "ResourceGroup",
                "action": "Delete"
            })
            permit_request.append({
                "resource_id": final["rg_id"],
                "target": "ResourceGroup",
                "action": "Update"
            })
        permit_request.append({
            'target': 'RGC_AgentStatus',
            'action': 'Create'
        })
        permit_request.append({
            'target': 'DerelictResource',
            'action': 'Possess'
        })
        return (res_list, permit_request)

    @staticmethod
    def rebuild_resource_group_list2(data):
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

    def agent_rg_read(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {}
            param['action'] = "Read"
            param['category'] = "AgentStatus"
            param['token'] = es_check['t']
            param['operator'] = es_check['u']
            param['target'] = "ResourceGroup"

            res = BackendRequest.permit_list_resource_group(param)
            if res['result']:
                (rg_list, permit_request) = self.rebuild_resource_group_list(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(rg_list)
                dummy_data["agent_rg_list"] = rg_list

                # add can_visit_ungrouped to see if user can see ungrouped option
                param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_param = {
                    'permits': permit_request
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
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def agent_rg_assign(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        resource_id = request.GET.get("resource_id", "")
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {}
            param['action'] = "Assign"
            param['target'] = "AgentStatus"
            param['token'] = es_check['t']
            param['operator'] = es_check['u']

            res = BackendRequest.permit_list_resource_group(param)
            if res['result']:
                data = self.rebuild_resource_group_list2(res['resource_groups'])

                param2 = {
                    'resource_id': resource_id,
                    'category': "AgentStatus",
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                res2 = BackendRequest.list_assigned_resource_group(param2)
                if res2['result']:
                    data2 = self.rebuild_assigned_resource_group_list(res2['resource_groups'])
                    dummy_data["agent_assigned_list"] = data2

                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["agent_assign_list"] = data
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def agent_can_rg_assign(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {}
            param['action'] = "Assign"
            param['target'] = "AgentStatus"
            param['token'] = es_check['t']
            param['operator'] = es_check['u']

            res = BackendRequest.permit_list_resource_group(param)
            if res['result']:
                data = self.rebuild_resource_group_list2(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["agent_assign_list"] = data
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp



    def agent_agents(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        start = request.GET.get('start')
        size = request.GET.get('size')
        orderby = request.GET.get('orderby')
        ip = request.GET.get('ip', "")
        hostname = request.GET.get('hostname', "")
        version = request.GET.get('version', "")
        isfuzzy = request.GET.get('isfuzzy')
        isServerHeka = request.GET.get('is_server_heka', "")
        group = request.GET.get('agent_group_ids', "")
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
               # "token": es_check["t"],
                "size": size,
                "start": start,
                "orderby": orderby,
                "version": version,
                "ip": ip,
                "isfuzzy": isfuzzy,
                'token': es_check['t'],
                'operator': es_check['u']
            }
            if (isServerHeka != ""):
                param["is_server_heka"] = isServerHeka
            if (group != ""):
                param["agent_group_ids"] = group
            if (hostname != ""):
                param["hostname"] = hostname

            res = BackendRequest.get_agent_status(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["total"] = res.get('total')
                dummy_data["data"] = res.get('agent_status')

                ## +00:00 适应新浏览器的接口变化，要是不加在中国就直接是东八区的时间了
                dummy_data["current_time"] = datetime.utcnow().isoformat() + "+00:00"

                permits = self.build_agent_permits(dummy_data["data"])
                param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_param = {
                    'permits': permits
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

    def upload_agent(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            visit_permit = BackendRequest.can_visit({
                "token": es_check['t'],
                "operator": es_check['u'],
                "requestUrl": "agent/upload/"
            })
            if visit_permit['result'] and visit_permit['can_visit']:
                platform = request.POST.get("type")
                version = request.POST.get("version")
                (result, reason) = handle_uploaded_file(request.FILES['file'], platform, version, es_check['t'], es_check['u'])
                if result:
                    dummy_data["status"] = "1"
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = reason
            else:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "You don't have permission to do this operation."
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def agent_download(self, request, **kwargs):
        # only for heka agent to download package use, with no auth procedure.

        self.method_check(request, allowed=['get'])
        file_name = kwargs["file_name"]
        platform = kwargs["platform"]
        version = kwargs["version"]
        file_path = HEKA_PACKAGE_URL + "/" + platform.replace("..", "") + "_" + version.replace("..", "") + "/" + file_name.replace("..", "")
        if not os.path.exists(file_path):
            raise Http404
        file_wrapper = FileWrapper(file(file_path,'rb'))
        file_mimetype, dumpass = mimetypes.guess_type(file_path)
        response = HttpResponse(file_wrapper, content_type=file_mimetype )
        #response['X-Sendfile'] = file_path
        response['Content-Length'] = os.stat(file_path).st_size
        response['Content-Disposition'] = 'attachment; filename="%s"' % smart_str(file_name)
        return response

    def delete_agent_package(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            visit_permit = BackendRequest.can_visit({
                "token": es_check['t'],
                "operator": es_check['u'],
                "requestUrl": "agent/upload/"
            })
            if visit_permit['result'] and visit_permit['can_visit']:
                version = request.POST.get('version')
                platform = request.POST.get('platform')
                param = {
                  #  "token": es_check["t"],
                    "version": version,
                    "platform": platform,
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                res = BackendRequest.delete_agent_package(param)

                if res['result']:
                    dummy_data["status"] = "1"
                    try_to_delete_package_file(platform, version)
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
            else:
                data = err_data.build_error({}, "You don't have permission to do this operation.")
                data["location"] = "/auth/login/"
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def get_agent_package(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            platform = request.GET.get('platform')
            param = {
              #  "token": es_check["t"],
                "platform": platform,
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_agent_package(param)

            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["versions"] = res['versions']
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


    def delete_agent(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        id = request.GET.get('id')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
              #  "token": es_check["t"],
                "id": id,
                'token': es_check['t'],
                'operator': es_check['u']
            }

            res = BackendRequest.delete_agent(param)

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

    def update_agent(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
              #  "token": es_check["t"],
                "ids": request.POST.get('ids'),
                "version": request.POST.get("version"),
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.update_agent(param)
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

    def agent_get_config(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            
            url = make_url_from_proxy(proxy, ip_port, 'getConfig', es_check['u'], es_check['t'])

            try:
                result = requests.get(url)
                if result.status_code == 200:
                    res = result.json()
                    if res['result']:
                        dummy_data["status"] = "1"
                        dummy_data["data"] = res['config']
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["error_type"] = "010"
                        dummy_data["msg"] = res['reason']
                else:
                    data = err_data.build_error({}, "get data error!")
                    dummy_data = data
            except:
                data = err_data.build_error({}, "get data error!")
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def agent_control_state(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        ip_port = request.POST.get('ip_port')
        action = request.POST.get('action')
        proxy = request.POST.get('proxy', '')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'controlHeka', es_check['u'], es_check['t'])

            post_data = {"type": action}
            try:

                result = requests.post(url, data=json.dumps(post_data))
                if result.status_code == 200:
                    res = result.json()

                    if res['result']:
                        dummy_data["status"] = "1"
                        dummy_data["data"] = {}
                        dummy_data["msg"] = ""
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["data"] = None
                        dummy_data["msg"] = res['reason']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = " agent 服务器暂时无法服务."
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        response_data = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        resp = self.create_response(request, response_data)
        return resp

    def agent_add_config(self, request, **kwargs):
        self.method_check(request, allowed=['get', 'post'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        data = request.POST.get('config')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'addConfig', es_check['u'], es_check['t'])

            result = requests.post(url, data=data)
            if result.status_code == 200:
                res = result.json()
                if res['result']:
                    dummy_data["status"] = "1"
                else:
                    dummy_data["status"] = "0"
                    dummy_data["error_type"] = "010"
                    dummy_data["msg"] = res['reason']
            else:
                data = err_data.build_error({}, "get data error!")
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def agent_del_config(self, request, **kwargs):
        self.method_check(request, allowed=['get', 'post'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        data = request.POST.get('config')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'delConfig', es_check['u'], es_check['t'])

            result = requests.delete(url, data=data)
            if result.status_code == 200:
                res = result.json()
                if res['result']:
                    dummy_data["status"] = "1"
                else:
                    dummy_data["status"] = "0"
                    dummy_data["error_type"] = "010"
                    dummy_data["msg"] = res['reason']
            else:
                data = err_data.build_error({}, "get data error!")
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def agent_get_full_config(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'getFullConfig', es_check['u'], es_check['t'])

            result = requests.get(url)
            if result.status_code == 200:
                res = result.json()
                if res['result']:
                    dummy_data["status"] = "1"
                    dummy_data["data"] = res['config']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["error_type"] = "010"
                    dummy_data["msg"] = res['reason']
            else:
                data = err_data.build_error({}, "get data error!")
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def agent_modify_full_config(self, request, **kwargs):
        self.method_check(request, allowed=['get','post'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        config = request.POST.get('config')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'modifyFullConfig', es_check['u'], es_check['t'])

            data = {"config": config}
            result = requests.post(url, data=json.dumps(data))
            if result.status_code == 200:
                res = result.json()
                if res['result']:
                    dummy_data["status"] = "1"
                else:
                    dummy_data["status"] = "0"
                    dummy_data["error_type"] = "010"
                    dummy_data["msg"] = res['reason']
            else:
                data = err_data.build_error({}, "modify data error!")
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def agent_query_heka_status(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'queryHekaStatus', es_check['u'], es_check['t'])

            result = requests.get(url)
            if result.status_code == 200:
                res = result.json()
                if res['result']:
                    dummy_data["status"] = "1"
                    dummy_data["reason"] = res['reason']
                    dummy_data["data"] = res['error_log']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["error_type"] = "010"
                    dummy_data["msg"] = res['reason']
            else:
                data = err_data.build_error({}, "modify data error!")
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


##  for agent add data
    def agent_get_ls(self, request, **kwargs):
        self.method_check(request, allowed=['get'])  # the hekad only use post, so for consistency use post also although violate rest
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        root_dir = request.GET.get('root_dir')
        # dict_path = request.POST.dict() # {'root_dir': "..."}
        post_data = {"root_dir": root_dir}
        dummy_data = {}

        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'ls', es_check['u'], es_check['t'])

            try:
                result = requests.post(url, data=json.dumps(post_data))
                if result.status_code == 200:
                    res = result.json() # returns [dirs, files, reason, result]

                    if res['result']:
                        dummy_data["status"] = "1"
                        dummy_data["data"] = {"dirs": res["dirs"], "files": res["files"]}
                        dummy_data["msg"] = ""
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["data"] = None
                        dummy_data["msg"] = res['reason']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务."
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def preview_match_files(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dic = json.loads(request.body)
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        post_data = {"path": dic.get('path'),
                     "white_list": dic.get('white_list'),
                     "black_list": dic.get('black_list', ""),
                     "oldest_duration": dic.get('oldest_duration'),
                     "limit": int(dic.get('limit'))}

        diff = dic.get("differentiator", "")
        priority = dic.get("priority", "")
        if (diff != "") and (priority != ""):
            post_data["differentiator"] = diff
            post_data["priority"] = priority
            try:
                re.compile(post_data["white_list"])
                regex_right = True
            except:
                regex_right = False
        else:
            regex_right = True

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check and regex_right:

            url = make_url_from_proxy(proxy, ip_port, 'previewMatchFiles', es_check['u'], es_check['t'])

            try:
                result = requests.post(url, data=json.dumps(post_data))
                if result.status_code == 200:
                    res = result.json() # returns [result, reason, files]
                    if res['result']:
                        dummy_data["status"] = "1"
                        dummy_data["data"] = {"files": res["files"]}
                        dummy_data["msg"] = ""
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["data"] = None
                        dummy_data["msg"] = res['reason']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务."
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        elif es_check and (not regex_right):
            dummy_data["status"] = "0"
            dummy_data["msg"] = "white list regex couldn't be compiled, please rewrite it."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def preview_split_result(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')

        post_data = {"path": request.GET.get('path'),
                     "split_regex": request.GET.get('split_regex'),
                     "Charset": request.GET.get('charset')}

        seek = request.GET.get('seek', '')
        if (seek != ''):
            post_data['seek'] = int(seek)


        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'previewSplitResult', es_check['u'], es_check['t'])

            try:
                result = requests.post(url, data=json.dumps(post_data))

                if result.status_code == 200:
                    res = result.json() # returns [result, reason, files]
                    if res['result']:
                        dummy_data["status"] = "1"
                        # events = [e.encode("utf-8") for e in res["events"]]
                        ret_data = {"events": res["events"]}
                        # print "Type of events", type(events[0])
                        if (res.get("seek", "") != ""):
                            # heka 1.7.35.0 or rizhiyi-agent 1.7.30.0 has this param
                            ret_data["seek"] = res.get("seek")
                            ret_data["size"] = res.get("size")

                        dummy_data["data"] = ret_data
                        dummy_data["msg"] = "Success"
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["data"] = None
                        dummy_data["msg"] = res['reason']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务."
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def add_heka_config(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')

        post_data = request.body
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'addHekaConfig', es_check['u'], es_check['t'])

            try:
                result = requests.post(url, data=post_data)

                if result.status_code == 200:
                    res = result.json() # returns [result, reason]
                    if res['result']:
                        dummy_data["status"] = "1"
                        dummy_data["msg"] = ""
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["msg"] = res['reason']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务."
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def get_timestamp_config(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')

        post_data = request.body
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'getTimestampConfig', es_check['u'], es_check['t'])

            try:
                result = requests.post(url, data=post_data)

                if result.status_code == 200:
                    res = result.json() # returns [result, reason]
                    if res['result']:
                        dummy_data["status"] = "1"
                        dummy_data["config"] = {
                            "time_format": res['time_format'],
                            "max_timestamp_lookahead": res['max_timestamp_lookahead'],
                            "time_prefix": res['time_prefix'],
                            "timezone": res['timezone']
                        }
                        dummy_data["msg"] = ""
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["msg"] = res['reason']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务."
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def preview_timestamp_recognition(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')

        post_data = request.body
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'previewTimestampRecognition', es_check['u'], es_check['t'])

            try:
                result = requests.post(url, data=post_data)

                if result.status_code == 200:
                    res = result.json() # returns [result, reason]
                    if res['result']:
                        dummy_data["status"] = "1"
                        dummy_data["log_timestamps"] = res['log_timestamps']
                        dummy_data["timestamps"] = res['timestamps']
                        dummy_data["msg"] = ""
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["msg"] = res['reason']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务."
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def agent_get_heka_config(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'getHekaConfig', es_check['u'], es_check['t'])

            try:
                result = requests.get(url)
                if result.status_code == 200:
                    res = result.json()
                    if res['result']:
                        dummy_data["status"] = "1"
                        dummy_data["data"] = res["Configs"]
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["msg"] = res['reason']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务."
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def agent_del_heka_config(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            try:
                url = make_url_from_proxy(proxy, ip_port, 'delHekaConfig', es_check['u'], es_check['t'])

                result = requests.post(url, data=request.body)
                if result.status_code == 200:
                    res = result.json()
                    if res['result']:
                        dummy_data["status"] = "1"
                        dummy_data["msg"] = ""
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["msg"] = res['reason']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务"
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def agent_modify_heka_config(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            try:

                url = make_url_from_proxy(proxy, ip_port, 'modifyHekaConfig', es_check['u'], es_check['t'])

                result = requests.post(url, data=request.body)
                if result.status_code == 200:
                    res = result.json()
                    if res['result']:
                        dummy_data["status"] = "1"
                        dummy_data["msg"] = ""
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["msg"] = res['reason']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务."
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "check error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


##  for server heka
    def server_agent_get_config(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:

            res = BackendRequest.get_agent_config(dict())
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["msg"] = "Success"
                dummy_data["data"] = {"other_conf": res["other_conf"],}
            else:
                dummy_data["status"] = "0"
                dummy_data["msg"] = res["error"]
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def server_agent_add_config(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = json.loads(request.body)
            res = BackendRequest.add_agent_config(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["msg"] = "Success"
            else:
                dummy_data["status"] = "0"
                dummy_data["msg"] = res["error"]
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def server_agent_modify_config(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = json.loads(request.body)
            res = BackendRequest.modify_agent_config(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["msg"] = "Success"
            else:
                dummy_data["status"] = "0"
                dummy_data["msg"] = res["error"]
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def server_agent_delete_config(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = json.loads(request.body)
            res = BackendRequest.delete_agent_config(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["msg"] = "Success"
            else:
                dummy_data["status"] = "0"
                dummy_data["msg"] = res["error"]
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def verify_connection(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        post_data = request.body
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'verifyConnection', es_check['u'], es_check['t'])

            try:
                result = requests.post(url, data=post_data)

                if result.status_code == 200:
                    res = result.json() # returns [result, reason]
                    if res['result']:
                        dummy_data["status"] = "1"
                        dummy_data["msg"] = "Success"
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["msg"] = res['reason']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务."
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def add_connection(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        post_data = request.body
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'addConnection', es_check['u'], es_check['t'])

            try:
                result = requests.post(url, data=post_data)

                if result.status_code == 200:
                    res = result.json() # returns [result, reason]
                    if res['result']:
                        dummy_data["status"] = "1"
                        dummy_data["msg"] = "Success"
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["msg"] = res['reason']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务."
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def get_connections(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'getConnections', es_check['u'], es_check['t'])

            try:
                result = requests.get(url)
                if result.status_code == 200:
                    res = result.json()
                    if len(res) >= 0:
                        dummy_data["status"] = "1"
                        dummy_data["data"] = res
                        dummy_data["msg"] = "Success"
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["msg"] = "No idea."
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务."
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp



    def del_connection(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            try:

                url = make_url_from_proxy(proxy, ip_port, 'delConnection', es_check['u'], es_check['t'])

                result = requests.post(url, data=request.body)
                if result.status_code == 200:
                    res = result.json()
                    if res['result']:
                        dummy_data["status"] = "1"
                        dummy_data["msg"] = "Success"
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["msg"] = res['reason']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务"
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def get_drivers(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'getDrivers', es_check['u'], es_check['t'])

            try:
                result = requests.get(url)
                if result.status_code == 200:
                    res = result.json()
                    if len(res) >= 0:
                        dummy_data["status"] = "1"
                        dummy_data["data"] = res
                        dummy_data["msg"] = "Success"
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["msg"] = "No ideas."
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务."
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def modify_connection(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        post_data = request.body
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'modifyConnection', es_check['u'], es_check['t'])

            try:
                result = requests.post(url, data=post_data)

                if result.status_code == 200:
                    res = result.json() # returns [result, reason]
                    if res['result']:
                        dummy_data["status"] = "1"
                        dummy_data["msg"] = "Success"
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["msg"] = res['reason']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务."
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def fetch_record(self, request, **kwargs):
        self.method_check(request, allowed=['get'])  # the hekad only use post, but for consistency use post also although validate rest
        ip_port = request.GET.get('ip_port')
        proxy = request.GET.get('proxy', '')
        connection_name = request.GET.get('connection_name')
        sql_stmt = request.GET.get('sql_stmt')
        # dict_path = request.POST.dict() # {'root_dir': "..."}
        post_data = {"sql_stmt": sql_stmt, "connection_name": connection_name}
        dummy_data = {}

        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:

            url = make_url_from_proxy(proxy, ip_port, 'fetchRecord', es_check['u'], es_check['t'])

            try:
                result = requests.post(url, data=json.dumps(post_data))
                if result.status_code == 200:
                    res = result.json() # returns [dirs, files, reason, result]
                    if res['result']:
                        dummy_data["status"] = "1"
                        dummy_data["data"] = res['records']
                        dummy_data["msg"] = "Success"
                    else:
                        dummy_data["status"] = "0"
                        dummy_data["data"] = None
                        dummy_data["msg"] = res['reason']
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "服务器暂时无法服务."
            except:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "无法访问到" + ip_port + "所在的 Agent."
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "You're not authenticated."
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    @staticmethod
    def build_agent_permits(agents):
        permits = []
        for agent in agents:
            id = int(agent['id'])
            permits.append({
                "resource_id": id,
                "target": "AgentStatus",
                "action": "Update"
            })
            permits.append({
                "resource_id": id,
                "target": "AgentStatus",
                "action": "Delete"
            })
            permits.append({
                "resource_id": id,
                "target": "AgentStatus",
                "action": "Assign"
            })

        permits.append({
            "target": "AgentStatus",
            "action": "Create"
        })
        return permits


def try_to_delete_package_file(platform, version):
    files_path = HEKA_PACKAGE_URL + "/" + platform.replace("..", "") + "_" + version.replace("..", "")
    call(["rm", "-rf", files_path])

def handle_uploaded_file(f, platform, version, token, operator):
    path = HEKA_PACKAGE_URL
    filename = f.name
    if not os.path.exists(path):
        os.mkdir(path)
    absolutePath = path + "/" + filename
    with open(absolutePath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    if (".tar.gz" in filename) and (("linux" in platform) or ("*nix" in platform)):
        ret = call(["tar", "-xvzf", absolutePath, "-C", path])
        if (ret == 0):
            if ("linux" in platform):
                if ("-db" in filename):
                    sourceDirectory = path + "/" +(filename[:-10])
                else:
                    sourceDirectory = path + "/" +(filename[:-7])

                hekadDir = "/bin/hekad"
                hekadDaemonDir = "/bin/hekad-daemon"
            elif ("*nix" in platform):
                sourceDirectory = path + "/rizhiyi-agent"
                hekadDir = "/backup/logstash-forwarder-java-"+version+"-jar-with-dependencies.jar"
                hekadDaemonDir = "/backup/forwarder-daemon-"+version+"-jar-with-dependencies.jar"

            targetDirectory = path + "/" + platform + "_" + version
            call(["rm", absolutePath])
            if not os.path.exists(targetDirectory):
                os.mkdir(targetDirectory)

            ret = call(["cp", sourceDirectory+hekadDir, sourceDirectory+hekadDaemonDir, targetDirectory])
            call(["rm", "-rf", sourceDirectory])
            if (ret == 0):
                return calculate_MD5_and_report_fe(targetDirectory, platform, version, token, operator)
            else:
                return (False, "failed to copy execute file, please try again.")
        else:
            return (False, "Try to unpack package failed, please check the package and try again.")
    elif (".zip" in filename) and ("win" in platform):
        ret = call(["unzip", "-o", absolutePath, "-d", path])
        if (ret == 0):
            sourceDirectory = path+ "/" + (filename[:-4])
            targetDirectory = path + "/" + platform + "_" + version
            call(["rm", absolutePath])
            if not os.path.exists(targetDirectory):
                os.mkdir(targetDirectory)
            ret = call(["cp", sourceDirectory+"/bin/hekad.exe", sourceDirectory+"/bin/hekad-daemon.exe", targetDirectory])
            call(["rm", "-rf", sourceDirectory])
            if (ret == 0):
                return calculate_MD5_and_report_fe(targetDirectory, platform, version, token, operator)

            else:
                return (False, "failed to copy execute file, please try again.")
        else:
            return (False, "Try to unpack package failed, please check the package and try again.")
    else:
        return (False, "Failed to recognize the package type.")


def calculate_MD5_and_report_fe(targetDir, platform, version, token, operator):
    if ("linux" in platform):
        hekad_file = "/hekad"
        hekad_daemon_file = "/hekad-daemon"
    elif ("win" in platform):
        hekad_file = "/hekad.exe"
        hekad_daemon_file = "/hekad-daemon.exe"
    elif ('*nix' in platform):
        hekad_file = "/logstash-forwarder-java-"+version+"-jar-with-dependencies.jar"
        hekad_daemon_file = "/forwarder-daemon-"+version+"-jar-with-dependencies.jar"

    hekad_path = targetDir + hekad_file
    hekad_daemon_path = targetDir + hekad_daemon_file

    with open(hekad_path, "rb") as file_to_check:
        data = file_to_check.read()
        hekad_md5 = hashlib.md5(data).hexdigest()
        hekad_uri = origin + "/api/v0/agent/download/"+platform+"/"+version+hekad_file

    with open(hekad_daemon_path, "rb") as file_to_check:
        data = file_to_check.read()
        hekad_daemon_md5 = hashlib.md5(data).hexdigest()
        hekad_daemon_uri = origin + "/api/v0/agent/download/"+platform+"/"+version+hekad_daemon_file

    param = {
        "version": version,
        "platform": platform,
        "hekad_uri": hekad_uri,
        "hekad_md5": hekad_md5,
        "hekad_daemon_uri": hekad_daemon_uri,
        "hekad_daemon_md5": hekad_daemon_md5,
        "token": token,
        "operator": operator
    }
    res =BackendRequest.add_agent_package(param)

    if res['result']:
        return (True, True)
    else:
        return (False, res['error'])


def make_url_from_proxy(proxy, ip_port, action, operator, token):
    if (proxy == ""):
        url = 'http://' + ip_port + '/' + action
        addition_params = "?operator=" + operator + "&token="+ token
        url = url + addition_params
        return url
    else:
        url = 'http://' + proxy + '/' + action
        arr = ip_port.split(":")
        addition_params = "?operator=" + operator + "&token="+ token + "&ip=" + arr[0] + "&port=" + arr[1]
        url = url + addition_params
        return url




