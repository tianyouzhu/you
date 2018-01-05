# -*- coding:utf-8 -*-
from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.variable.resources import MyVariable
import os
import time
import csv

__author__ = 'wangqiushi, mayangguang'
err_data = ContributeErrorData()


class SourceResource(Resource):
    # Just like a Django ``Form`` or ``Model``, we're defining all the
    # fields we're going to handle with the API here.

    class Meta:
        resource_name = 'sources'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/input/linux/verification$" % self._meta.resource_name,
                self.wrap_view('input_linux_verification'), name="api_input_linux_verification"),
            url(r"^(?P<resource_name>%s)/detail/(?P<type>(appname|sourcegroup))/$" % self._meta.resource_name,
                self.wrap_view('get_detail'), name="api_get_detail"),
            url(r"^(?P<resource_name>%s)/detail/download/(?P<type>(appname|sourcegroup))/$" % self._meta.resource_name,
                self.wrap_view('get_detail_download'), name="api_get_detail"),
            url(r"^(?P<resource_name>%s)/sourcegroups/list/$" % self._meta.resource_name,
                self.wrap_view('sourcegroups_list'), name="api_sourcegroups_new"),
            url(r"^(?P<resource_name>%s)/sourcegroups/list/simple/$" % self._meta.resource_name,
                self.wrap_view('sourcegroups_list_simple'), name="api_sourcegroups_new"),
            url(r"^(?P<resource_name>%s)/sourcegroups/new$" % self._meta.resource_name,
                self.wrap_view('sourcegroups_new'), name="api_sourcegroups_new"),
            url(r"^(?P<resource_name>%s)/sourcegroups/resourcegroup/filter/$" % self._meta.resource_name,
                self.wrap_view('reourcegroup_filter'), name="api_sourcegroups_rg_filter"),
            url(r"^(?P<resource_name>%s)/sourcegroups/resourcegroup/ungrouped/$" % self._meta.resource_name,
                self.wrap_view('reourcegroup_ungrouped'), name="api_sourcegroups_rg_ungrouped"),
            url(r"^(?P<resource_name>%s)/sourcegroups/resourcegroup/list/assigned/(?P<sgid>[\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('get_resourcegroup_assigned_list'), name="api_get_resourcegroup_assigned_list"),
            url(r"^(?P<resource_name>%s)/sourcegroups/resourcegroup/list/(?P<action>[\w_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('get_resourcegroup_list'), name="api_get_resourcegroup_list"),
            url(r"^(?P<resource_name>%s)/sourcegroups/(?P<sgid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('sourcegroups_update'), name="api_sourcegroups_update"),
            url(r"^(?P<resource_name>%s)/sourcegroups/del/(?P<sgid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('sourcegroups_delete'), name="api_sourcegroups_new"),
            url(r"^(?P<resource_name>%s)/upload_volum_info/$" % self._meta.resource_name,
                self.wrap_view('upload_volum_info'), name="api_sourcegroups_new"),


        ]

    def input_linux_verification(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        # username = request.POST['username']
        # password = request.POST['password']
        if True:
            dumyData = {
                'status': '1',
                'msg': 'Success from server !',
            }

            bundle = self.build_bundle(
                obj=dumyData, data=dumyData, request=request)
            resData = bundle
            resp = self.create_response(request, resData)
            return resp
        else:
            dumyData = {
                'status': '0',
                'msg': 'Not success from server !',
            }

            bundle = self.build_bundle(
                obj=dumyData, data=dumyData, request=request)
            resData = bundle
            resp = self.create_response(request, resData)
            return resp

    def get_detail(self, request, **kwargs):
        self.method_check(request, allowed=["get"])
        dummy_data = {}
        type = kwargs["type"]
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            sg_param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            if type == "sourcegroup":
                sg_res = BackendRequest.get_source_group_related_infos(sg_param)
            else:
                sg_param["base"] = "appname"
                sg_res = BackendRequest.get_source_group_related_infos(sg_param)
            if sg_res['result']:
                # todo
                to_res = []
                if type == "appname":
                    sg_res_arr = [] if not sg_res.get("items", []) else sg_res.get("items")
                    if isinstance(sg_res_arr, list):
                        for item in sg_res_arr:
                            for (k, v) in item.items():
                                to_res.append({
                                    "name": k,
                                    "infos": v
                                })
                    else:
                        for (k, v) in sg_res_arr.items():
                            to_res.append({
                                "name": k,
                                "infos": v
                            })
                else:
                    sg_res_arr = [] if not sg_res.get("items", []) else sg_res.get("items")
                    to_res = sg_res_arr
                dummy_data["status"] = "1"
                dummy_data["list"] = to_res
            else:
                dummy_data = err_data.build_error(sg_res)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def get_detail_download(self, request, **kwargs):
        self.method_check(request, allowed=["get"])
        dummy_data = {}
        type = kwargs["type"]
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            sg_param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            if type == "sourcegroup":
                sg_res = BackendRequest.get_source_group_related_infos(sg_param)
            else:
                sg_param["base"] = "appname"
                sg_res = BackendRequest.get_source_group_related_infos(sg_param)
            if sg_res['result']:
                # todo
                to_res = []
                if type == "appname":
                    sg_res_arr = [] if not sg_res.get("items", []) else sg_res.get("items")
                    if isinstance(sg_res_arr, list):
                        for item in sg_res_arr:
                            for (k, v) in item.items():
                                to_res.append({
                                    "name": k,
                                    "infos": v
                                })
                    else:
                        for (k, v) in sg_res_arr.items():
                            to_res.append({
                                "name": k,
                                "infos": v
                            })
                else:
                    sg_res_arr = [] if not sg_res.get("items", []) else sg_res.get("items")
                    to_res = sg_res_arr
                dummy_data["status"] = "1"
                dummy_data["filename"] = self._build_csv(type, to_res, es_check["d"], es_check["u"])
            else:
                dummy_data = err_data.build_error(sg_res)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def _build_csv(self, type, data, domain, user):
        if type == "sourcegroup":
            heads = ["sourcegroup", "appname", "hostname"]
        else:
            heads = ["appname", "sourcegroup", "hostname"]
        rows = []
        for item in data:
            if item.get("infos", {}):
                for (k, v) in item["infos"].items():
                    if v:
                        for hostname in v:
                            rows.append([item["name"], k, hostname])
                    else:
                        rows.append([item["name"], k, ""])
                # todo
            else:
                rows.append([item["name"], "", ""])

        root_path = os.getcwd()
        my_var = MyVariable()
        data_path = my_var.get_var('path', 'data_path')
        tmp_path = data_path + "yottaweb_tmp/" + domain + "/" + user + "/"
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        # remove old file first
        name = 'log_resource_' + domain + "_" + user.encode("utf-8")
        file_name = str(name) + ".csv"
        file_path = tmp_path + file_name
        if os.path.isfile(file_path):
            os.remove(file_path)
        f = open(file_path, "wb+")
        # write bom to resolve unreadable chinese problem
        f.write("\xEF\xBB\xBF")
        writer = csv.writer(f)
        writer.writerow(heads)
        for line in rows:
            writer.writerow(line)
        return file_name

    def sourcegroups_list(self, request, **kwargs):
        '''
        {"sourcegroup_id": "11", "sGroup": "Moroni", "description": "afdds", "contents": "fff",
             "created": "wangqiushi", "activity": [12, 23, 12, 14, 53, 24, 45, 2, 4, 5, 3, 55], "restricted": "aa",
             "edit": "false"}
        :param request:
        :param kwargs:
        :return:
        '''
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            source_group = []
            permits = []
            res = BackendRequest.get_source_group({
                "token": es_check["t"],
                'operator': es_check['u']
            })
            if res['result']:
                for i in res['items']:
                    group_list = filter(lambda x: not x == '' and x is not None, i.get('user_groups', []))
                    source_group.append({
                        'sourcegroup_id': i['id'].encode('utf-8'),
                        'sGroup': i['name'].encode('utf-8'),
                        "description": i.get('description', "").encode('utf-8'),
                        "activity": [],
                        "created": i.get('owner_name', "").encode('utf-8'),
                        "edit": i.get('edit', "false").encode('utf-8'),
                        "contents": i.get('contents', "").encode('utf-8'),
                        "restricted": ','.join(group_list)
                    })
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "SourceGroup",
                        "action": "Update"
                    })
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "SourceGroup",
                        "action": "Delete"
                    })
                permits.append({
                    "target": "SourceGroup",
                    "action": "Create"
                })
                permits.append({
                    "target": "DerelictResource",
                    "action": "Possess"
                })
                dummy_data["status"] = "1"
                dummy_data["totle"] = len(source_group)
                dummy_data["list"] = source_group
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
                dummy_data = err_data.build_error(res)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def sourcegroups_list_simple(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        data = [
            {"id": "11", "name": "Moroni"},
            {"id": "12", "name": "测试"},
            {"id": "13", "name": "dd"},
            {"id": "14", "name": "bb"}
        ]
        dummy_data = {}
        if es_check:
            res = BackendRequest.get_source_group({
                "token": es_check["t"],
                'operator': es_check['u']
            })
            source_group = []
            if res['result']:
                for i in res['items']:
                    source_group.append({
                        'id': i['id'].encode('utf-8'),
                        'name': i['name'].encode('utf-8')
                    })
            else:
                dummy_data = err_data.build_error(res)
            dummy_data["status"] = "1"
            dummy_data["totle"] = len(source_group)
            dummy_data["list"] = source_group

        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def sourcegroups_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        req_data = request.POST
        # username = request.POST['username']
        # password = request.POST['password']
        post_data = {
            'name': req_data.get('name', ''),
            'description': req_data.get('desc', ''),
            'resource_group_ids': req_data.get('resource_group_ids', "")
        }

        if req_data.get('host', '') != '':
            post_data['hostname'] = req_data.get('host', '')
        if req_data.get('application', '') != '':
            post_data['appname'] = req_data.get('application', '')
        if req_data.get('tag', '') != '':
            post_data['tag'] = req_data.get('tag', '')

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            post_data["token"] = es_check["t"]
            post_data["owner_id"] = es_check["i"]
            post_data['operator'] = es_check['u']
            res = BackendRequest.create_source_group(post_data)
            if res["result"]:
                dummy_data["status"] = "1"
                dummy_data["location"] = "/sources/sourcegroups/"
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

    def sourcegroups_update(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        source_group_id = kwargs["sgid"]
        req_data = request.POST
        # username = request.POST['username']
        # password = request.POST['password']
        post_data = {
            'id': source_group_id,
            'name': req_data.get('name', ''),
            'description': req_data.get('desc', ''),
            'hostname': req_data.get('host', ''),
            'appname': req_data.get('application', ''),
            'tag': req_data.get('tag', ''),
            'resource_group_ids': req_data.get('resource_group_ids', "")
        }
        # if req_data.get('host', '') != '':
        # post_data['hostname'] = req_data.get('host', '')
        # if req_data.get('application', '') != '':
        # post_data['appname'] = req_data.get('application', '')
        # if req_data.get('tag', '') != '':
        # post_data['tag'] = req_data.get('tag', '')

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            post_data["token"] = es_check["t"]
            post_data['operator'] = es_check['u']
            res = BackendRequest.update_source_group(post_data)
            if res["result"]:
                dummy_data["status"] = "1"
                dummy_data["location"] = "/sources/sourcegroups/"
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

    def sourcegroups_delete(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        source_group_id = kwargs["sgid"]

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            res = BackendRequest.delete_source_group({
                "token": es_check["t"],
                "id": source_group_id,
                'operator': es_check['u']
            })
            if res["result"]:
                res_list = BackendRequest.get_source_group({
                    "token": es_check["t"],
                    "id": source_group_id,
                    'operator': es_check['u']
                })
                source_group = []
                if res_list['result']:
                    for i in res_list['items']:
                        group_list = filter(lambda x: not x == '' and x is not None, i.get('user_groups', []))
                        source_group.append({
                            'sourcegroup_id': i['id'].encode('utf-8'),
                            'sGroup': i['name'].encode('utf-8'),
                            "description": i.get('description', "").encode('utf-8'),
                            "activity": [],
                            "created": i.get('owner_name', "").encode('utf-8'),
                            "edit": i.get('edit', "false").encode('utf-8'),
                            "contents": i.get('contents', "").encode('utf-8'),
                            "restricted": ','.join(group_list)
                        })
                dummy_data["status"] = "1"
                dummy_data["totle"] = len(source_group)
                dummy_data["list"] = source_group
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

    def upload_volum_info(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        # print "################upload_volum_info: "
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            dummy_data = BackendRequest.get_upload_status({
                "token": es_check["t"],
                'operator': es_check['u']
            })
            # print "################upload_volum_info: ",dummy_data
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
                param['category'] = "SourceGroup"
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = "ResourceGroup"
            elif kwargs['action'].lower() == "assign":
                param['action'] = "Assign"
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = "SourceGroup"

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
        sg_id = kwargs.get('sgid', "")
        dummy_data = {}

        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'resource_id': sg_id,
                'category': "SourceGroup"
            }

            res = BackendRequest.list_assigned_resource_group(param)

            if res['result']:
                data = self.rebuild_resource_group_list(res['resource_groups'])
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


    def reourcegroup_filter(self, request, **kwargs):
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

            res = BackendRequest.get_batch_sourcegroup(param)

            if res['result']:
                data = self.rebuild_sourcegroup_list(res['source_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["list"] = data

                permits = []
                for i in res['source_groups']:
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "SourceGroup",
                        "action": "Update"
                    })
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "SourceGroup",
                        "action": "Delete"
                    })
                permits.append({
                    "target": "SourceGroup",
                    "action": "Create"
                })
                permits.append({
                    "target": "DerelictResource",
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

    def reourcegroup_ungrouped(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'category': "SourceGroup",
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
    def rebuild_sourcegroup_list(data):
        res_list = []
        for i in data:
            res_list.append({
                'sourcegroup_id': i['id'].encode('utf-8'),
                'sGroup': i['name'].encode('utf-8'),
                "description": i.get('description', "").encode('utf-8'),
                "activity": [],
                "created": i.get('owner_name', "").encode('utf-8'),
                "edit": i.get('edit', "false").encode('utf-8'),
                "contents": i.get('contents', "").encode('utf-8'),
                "restricted": ','.join(i.get('user_groups', []))
            })
        return res_list


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
    def check_with_sourcegroup(login):
        with_sg = 'no'
        sg_param = {
            'account': login['i'],
            'token': login['t'],
            'operator': login['u']
        }
        sg_res = BackendRequest.get_source_group(sg_param)
        if sg_res['result']:
            item = sg_res.get('items', [])
            if item:
                with_sg = 'yes'
        return with_sg