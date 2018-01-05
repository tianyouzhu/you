# wangqiushi (@yottabyte.cn)
# 2014/07/30
# Copyright 2014 Yottabyte
# file description : resources.py.
from tastypie.resources import Resource
from django.http import HttpResponse
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.variable.resources import MyVariable
from django.core.servers.basehttp import FileWrapper
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin, String
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.textlabels import Label
from reportlab.platypus.tables import Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from . import build_report
from . import build_stats as _build_stats
from . import build_stats_new as _build_stats_new
from reportlab.graphics.samples.excelcolors import *
from yottaweb.apps.utils.resources import MyUtils
import base64
import logging
import ConfigParser
import pymysql
import string
import json
import time
import datetime
import os
import ast
import traceback

__author__ = 'wangqiushi'
err_data = ContributeErrorData()
audit_logger = logging.getLogger("yottaweb.audit")
re_logger = logging.getLogger("django.request")

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    database = cf.get('db', 'fe_name')
    user = cf.get('db', 'user')
    pwd = cf.get('db', 'password')
    host = cf.get('db', 'host')
except Exception, e:
    print e
    database = "root"
    user = "root"
    pwd = "123456"
    host = "127.0.0.1"


class ReportResource(Resource):
    class Meta:
        resource_name = 'report'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/test/$" % self._meta.resource_name,
                self.wrap_view('report_test'), name="api_report_test"),
            url(r"^(?P<resource_name>%s)/list/$" % self._meta.resource_name,
                self.wrap_view('report_list'), name="api_report_test"),
            url(r"^(?P<resource_name>%s)/files/$" % self._meta.resource_name,
                self.wrap_view('report_files'), name="api_report_test"),
            url(r"^(?P<resource_name>%s)/files/download/(?P<fid>[\w\d_.\-@]+)/$" % self._meta.resource_name,
                self.wrap_view('report_files_download'), name="api_report_test"),
            url(r"^(?P<resource_name>%s)/files/download/directly/(?P<fid_encoded>[\w\d_.\-\=\+@]+)/$" % self._meta.resource_name,
                self.wrap_view('report_files_download_directly'), name="api_report_test"),
            url(r"^(?P<resource_name>%s)/files/delete/$" % self._meta.resource_name,
                self.wrap_view('report_files_delete'), name="api_report_test"),
            url(r"^(?P<resource_name>%s)/detail/(?P<rid>[\w]+)/$" % self._meta.resource_name,
                self.wrap_view('report_detail'), name="api_report_test"),
            url(r"^(?P<resource_name>%s)/trends/$" % self._meta.resource_name,
                self.wrap_view('report_trends'), name="api_report_test"),
            url(r"^(?P<resource_name>%s)/trends/del/$" % self._meta.resource_name,
                self.wrap_view('delete_trend'), name="api_report_test"),
            url(r"^(?P<resource_name>%s)/new/$" % self._meta.resource_name,
                self.wrap_view('report_new'), name="api_report_test"),
            url(r"^(?P<resource_name>%s)/listen_report_post/$" % self._meta.resource_name,
                self.wrap_view('listen_report_post'), name="api_listen_report_input"),
            url(r"^(?P<resource_name>%s)/(?P<rid>[\w]+)/$" % self._meta.resource_name,
                self.wrap_view('report_update'), name="api_report_test"),
            url(r"^(?P<resource_name>%s)/delete/(?P<rid>[\w]+)/$" % self._meta.resource_name,
                self.wrap_view('report_delete'), name="api_report_test"),
            url(r"^(?P<resource_name>%s)/enable/(?P<rid>[\w\d_.-]+)/(?P<enable>[\w]{1})/$" % self._meta.resource_name,
                self.wrap_view('report_enable'), name="api_report_enable"),
            url(r"^(?P<resource_name>%s)/resourcegroup/filter/$" % self._meta.resource_name,
                self.wrap_view('reourcegroup_filter'), name="api_sourcegroups_rg_filter"),
            url(r"^(?P<resource_name>%s)/resourcegroup/list/assigned/(?P<rid>[\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('get_resourcegroup_assigned_list'), name="api_get_resourcegroup_assigned_list"),
            url(r"^(?P<resource_name>%s)/resourcegroup/list/(?P<action>[\w_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('get_resourcegroup_list'), name="api_get_resourcegroup_list"),
            url(r"^(?P<resource_name>%s)/resourcegroup/ungrouped/$" % self._meta.resource_name,
                self.wrap_view('get_resourcegroup_ungrouped'), name="api_get_resourcegroup_ungrouped"),
        ]


    ###########################################################################################################
    #   author: "Junwei Zhao"
    #   date: 10/24/2016
    #   Module: Report
    #   subject: Change code from directly manipulating database to calling Restful API provided by Frontend
    #   Modified APIs:
    #            1. report_list(self, request, **kwargs)
    #            2. report_detail(self, request, **kwargs)
    #            3. report_new(self, request, **kwargs)
    #            4. report_update(self, request, **kwargs)
    #            5. report_delete(self, request, **kwargs)
    #   Returned error Codes and meanings:
    #            1. 000: authentication failed/error
    #            2. 010: unknow server error
    #            3. 100: report has already existed
    #            4. 101: report is not existed
    #            5. 102: doamin error for new created report
    ###########################################################################################################
    @staticmethod
    def error_handler(response, isAuth=False):
        """
            Error handler to handle almost all occured errors.
            Error Codes and meanings:
            000: auth failed/error
            010: unknow server error
            100: report has already existed
            101: reprot is not existed
            102: doamin error for new created report
            110: submitted crontab expression invalid syntax
        """

        if isAuth:
            # authentication failed/error
            dummy = err_data.build_error({}, "auth error")
            dummy['location'] = "/auth/login/"
            dummy['error_code'] = "000"
        else:
            errorCode = int(response.get('error_code', 500))
            error = response.get('error', 'Server Error')
            dummy = err_data.build_error({}, error)

            if errorCode == 580:
                dummy['error_code'] = "100"
            elif errorCode == 581:
                dummy['error_code'] = "101"
            elif errorCode == 582:
                dummy['error_code'] = "102"
            elif errorCode == 7:
                dummy['error_code'] = "110"
            else:
                dummy['error_code'] = "010"

            dummy['error'] = error

        return dummy


    @staticmethod
    def generate_param(es_check, params={}):
        """
            Used to generate the parameters mapping that gets passed to the Backend/Frontend in http url.
            Default form will be containing two entries: 'token' and 'operator'.
            If additional parameters are specified in terms of dictionary, then those specified params will be grouped with default and get passed.
        """

        default = {
            'token': es_check['t'],
            'operator': es_check['u']
        }

        if params:
            return dict(default, **params)

        return default


    @staticmethod
    def generate_response(objRef, data, request):
        """
            Used to generate http response regards to its associated http request.
        """

        bundle = objRef.build_bundle(obj=data, data=data, request=request)
        response_data = bundle
        resp = objRef.create_response(request, response_data)

        return resp


    @staticmethod
    def check_auth(request, **kwargs):
        """
            Used to check and return authentication result
        """

        my_auth = MyBasicAuthentication()
        return my_auth.is_authenticated(request, **kwargs)


    def report_list(self, request, **kwargs):
        """
            Used to get the list of all current existing reports
        """

        self.method_check(request, allowed=['get'])
        dummy_data = {}

        es_check = ReportResource.check_auth(request, **kwargs)

        if es_check:
            permits = []

            owner = str(es_check["i"])+"|"+str(es_check["u"])+"|"+str(es_check["t"])
            param = ReportResource.generate_param(es_check, {'owner': owner})

            res = BackendRequest.get_report_list(param)

            if res['result']:
                data = res.get('list', [])
                dummy_data['status'] = "1"
                dummy_data['list'] = data

                for i in data:
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "Report",
                        "action": "Update"
                    })
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "Report",
                        "action": "Delete"
                    })
                permits.append({
                    "target": "Report",
                    "action": "Create"
                })
                permits.append({
                    "target": "DerelictResource",
                    "action": "Possess"
                })

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
                dummy_data = ReportResource.error_handler(res)
        else:
            dummy_data = ReportResource.error_handler(None, True)

        return ReportResource.generate_response(self, data=dummy_data, request=request)



    def report_detail(self, request, **kwargs):
        """
            Used to get all details of given report identified by its id
        """

        self.method_check(request, allowed=['get'])
        report_id = kwargs["rid"]
        dummy_data = {}

        es_check = ReportResource.check_auth(request, **kwargs)

        if es_check:
            owner = str(es_check["i"])+"|"+str(es_check["u"])+"|"+str(es_check["t"])
            param = ReportResource.generate_param(es_check, {'owner': owner, 'id': report_id})

            res = BackendRequest.get_report_detail(param)

            if res['result']:
                dummy_data['status'] = "1"
                dummy_data['data'] = res.get('res', {})
                rce_contents = (dummy_data['data'].get('content', ""))

                contents = []
                for i in range(len(rce_contents)):
                    # print rce_contents[i]
                    contents.append(json.loads(rce_contents[i]))

                dummy_data['data']['content'] = (contents)
                # content_split = content.split(',')
                # contents = []
                # for item in content_split:
                    # if "|-|" in item:
                        # trend_id,trend_name = item.split("|-|")
                    # else:
                        # trend_id = item.split("|")[0]
                        # trend_name = item[33:].split("|")[0]
                    # new_id = trend_id
                    # if len(trend_id) > 10:
                        # new_res = BackendRequest.convert_id({
                            # "trend_id": trend_id,
                            # "token": es_check["t"],
                            # "operator": es_check["u"],
                        # })
                        # if new_res["result"]:
                            # new_id = new_res["id"]
                    # contents.append({
                        # "key": new_id,
                        # "value": trend_name
                    # })
            else:
                dummy_data = ReportResource.error_handler(res)
        else:
            dummy_data = ReportResource.error_handler(None, True)

        return ReportResource.generate_response(self, data=dummy_data, request=request)


    def report_new(self, request, **kwargs):
        """
            Used to gather all data passed from browser and create an new report
        """

        self.method_check(request, allowed=['post'])
        req_data = request.POST
        dummy_data = {}

        es_check = ReportResource.check_auth(request, **kwargs)

        if es_check:
            param = ReportResource.generate_param(es_check, {'resource_group_ids': req_data.get('ids', "")})

            rce_contents = json.loads(req_data.get('content', ''))
            contents = []
            for i in range(len(rce_contents)):
                # print rce_contents[i]
                contents.append(json.dumps(rce_contents[i]))

            data = {
                'name': req_data.get('name', ''),
                'subject': req_data.get('subject', ''),
                'owner': str(es_check["i"])+"|"+str(es_check["u"])+"|"+str(es_check["t"]),
                'email': req_data.get('emails', ''),
                'frequency': req_data.get('frequency', ''),
                'crontab': req_data.get('crontab', "0"),
                # 'content': json.dumps(req_data.get('content', '')),
                'content': contents,
                'trigger_time': req_data.get('triggerTime', ''),
                'domain': es_check["d"],
                'resource_group_ids': req_data.get('ids', ""),
                'enabled': True if req_data.get('enabled', "false") == 'true' else False
            }

            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "create",
                "model": "report",
                "user_name": es_check["u"],
                "user_id": es_check["i"],
                "domain": es_check["d"],
                "target": req_data.get('name', ''),
                "result": "success"
            }

            res = BackendRequest.create_report(param, data)

            if res['result']:
                dummy_data['status'] = "1"
                dummy_data.update(res)
                del dummy_data['result']
            else:
                dummy_data = ReportResource.error_handler(res)
                to_log["result"] = "error"
                to_log["msg"] = res.get("error", "")
            audit_logger.info(json.dumps(to_log))
        else:
            dummy_data = ReportResource.error_handler(None, True)

        return ReportResource.generate_response(self, data=dummy_data, request=request)


    def report_update(self, request, **kwargs):
        """
            Used to gather all data passed from browser and update an existing report identified by its id.
        """

        self.method_check(request, allowed=['post'])
        report_id = kwargs["rid"]
        req_data = request.POST
        dummy_data = {}

        es_check = ReportResource.check_auth(request, **kwargs)

        if es_check:
            param = ReportResource.generate_param(es_check, {'id': report_id, 'resource_group_ids': req_data.get('ids', "")})

            rce_contents = json.loads(req_data.get('content', ''))
            contents = []
            for i in range(len(rce_contents)):
                # print rce_contents[i]
                contents.append(json.dumps(rce_contents[i]))

            data = {
                'name': req_data.get('name', ''),
                'subject': req_data.get('subject', ''),
                'owner': str(es_check["i"])+"|"+str(es_check["u"])+"|"+str(es_check["t"]),
                'email': req_data.get('emails', ''),
                'frequency': req_data.get('frequency', ''),
                'crontab': req_data.get('crontab', "0"),
                'content': contents,
                'trigger_time': req_data.get('triggerTime', ''),
                'domain': es_check["d"],
                'enabled': True if req_data.get('enabled', "false") == 'true' else False
            }

            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "update",
                "model": "report",
                "user_name": es_check["u"],
                "user_id": es_check["i"],
                "domain": es_check["d"],
                "target": req_data.get('name', ''),
                "result": "success"
            }

            res = BackendRequest.update_report(param, data)

            if res['result']:
                dummy_data['status'] = "1"
                dummy_data.update(res)
                del dummy_data['result']
            else:
                dummy_data = ReportResource.error_handler(res)
                to_log["result"] = "error"
                to_log["msg"] = res.get("error", "")
            audit_logger.info(json.dumps(to_log))
        else:
            dummy_data = ReportResource.error_handler(None, True)

        return ReportResource.generate_response(self, data=dummy_data, request=request)


    def report_delete(self, request, **kwargs):
        """
            Used to delete an existing report identified by its id.
        """

        self.method_check(request, allowed=['post'])
        report_id = kwargs["rid"]
        dummy_data = {}

        es_check = ReportResource.check_auth(request, **kwargs)

        if es_check:
            owner = str(es_check["i"])+"|"+str(es_check["u"])+"|"+str(es_check["t"])
            param = ReportResource.generate_param(es_check, {'owner': owner, 'id': report_id})

            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "delete",
                "model": "report",
                "user_name": es_check["u"],
                "user_id": es_check["i"],
                "domain": es_check["d"],
                "target": report_id,
                "result": "success"
            }

            res = BackendRequest.delete_report(param)

            if res['result']:
                dummy_data['status'] = "1"
                dummy_data['list'] = res.get('list', [])
                dummy_data['id'] = res.get('id', "")
            else:
                dummy_data = ReportResource.error_handler(res)
                to_log["result"] = "error"
                to_log["msg"] = res.get("error", "")
            audit_logger.info(json.dumps(to_log))
        else:
            dummy_data = ReportResource.error_handler(None, True)

        return ReportResource.generate_response(self, data=dummy_data, request=request)


    def report_enable(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        report_id = kwargs['rid']
        report_enabled = int(kwargs['enable'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'id': report_id,
                'token': es_check['t'],
                'operator': es_check['u']
            }
            if report_enabled == 1:
                # enabled ==> disbaled
                res = BackendRequest.disable_report(param)
            else:
                # disabled ==> enabled
                res = BackendRequest.enable_report(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["enabled"] = res.get("res", {}).get("enabled", False)
                dummy_data["msg"] = "enable/disable successfully"
            else:
                dummy_data = err_data.build_error(res)
                # dummy_data["list"] = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def listen_report_post(self, request, **kwargs):
        """
            Restful API provided to frontend to get timered reports back through http post method.
            Method: POST
            URL: protocol://domain[:port]/api/v0/report/listen_report_post/
            Posted data: SPL 1.8 changed the form of returning data, check spl docs for more deatails.
        """

        self.method_check(request, allowed=['post'])
        dummy_data = {}
        # post data contains params like name, id, etc and a 'data' list contains a list of search results
        body_unicode = request.body.encode('utf-8')
        try:
            results = json.loads(ast.literal_eval(body_unicode))
        except Exception as e:
            results = json.loads(body_unicode)

        try:
            # re_logger.info("listen_report_post_raw_data: %s", results['data']);
            search_res_list = results['data']
            data = []

            for search_res in search_res_list:
                if "result" in search_res and search_res['result']:
                    # 'hasUseTable' indicates whether to use _build_stats_new or _build_stats
                    if search_res['hasUseTable']:
                        # build_stats_new accepts two arguments: search result as dict and parameter dict
                        data_item = _build_stats_new(search_res["result"], search_res['param'])
                    else:
                        # build_stats accepts one argument: 'stats' list in search result, now getting from ["result"]["sheets"]["row"]
                        data_item = _build_stats(search_res["result"]["sheets"].get('rows',[]))
                    data_item['param'] = search_res['param']
                    # add processed search result to the data list
                    data.append(data_item)
            results['data']  = data

            # if data list is not empty
            if results['data']:
                build_report(results)
            else:
                re_logger.info("No build report task to run")
            dummy_data['result'] = True
            dummy_data['status'] = "1"
        except Exception as e:
            # when error occurs, do two things: 1. write error's stack to log 2. print error's stacktrace to console
            re_logger.exception("listen_report_post raises error: %s", e)
            traceback.print_exc()

            dummy_data['result'] = False
            dummy_data['error'] = e

        return ReportResource.generate_response(self, data=dummy_data, request=request)


    def get_resourcegroup_list(self, request, **kwargs):
        """
            Get a list of available resource groups in aspect of current user.
        """

        self.method_check(request, allowed=['get'])
        dummy_data = {}

        es_check = ReportResource.check_auth(request, **kwargs)

        if es_check:
            # 'action' specifies what action is performed: Read, Assign
            # 'target' specifies what module is requesting
            param = {}
            if kwargs['action'].lower() == "read":
                param['action'] = "Read"
                param['category'] = "Report"
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = "ResourceGroup"
            elif kwargs['action'].lower() == "assign":
                param['action'] = "Assign"
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = "Report"

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

        return ReportResource.generate_response(self, dummy_data, request)


    def get_resourcegroup_assigned_list(self, request, **kwargs):
        """
        """

        self.method_check(request, allowed=['get'])
        report_id = kwargs.get('rid', "")
        dummy_data = {}

        es_check = ReportResource.check_auth(request, **kwargs)

        if es_check:
            param = ReportResource.generate_param(es_check, {'resource_id': report_id, 'category': "Report"})

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

        return ReportResource.generate_response(self, dummy_data, request)


    def reourcegroup_filter(self, request, **kwargs):
        """
        """

        self.method_check(request, allowed=['post'])

        req_data = request.POST
        ids = req_data.get('ids', "")
        dummy_data = {}

        es_check = ReportResource.check_auth(request, **kwargs)

        if es_check:
            # reource group ids is passed to frontend in string form which each id is separated by comma
            param = ReportResource.generate_param(es_check, {'ids': ids})

            res = BackendRequest.get_batch_report(param)

            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["list"] = res['list']
                dummy_data["total"] = len(res['list'])

                permits = []
                for i in res['list']:
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "Report",
                        "action": "Update"
                    })
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "Report",
                        "action": "Delete"
                    })
                permits.append({
                    "target": "Report",
                    "action": "Create"
                })
                permits.append({
                    "target": "DerelictResource",
                    "action": "Possess"
                })

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
                dummy_data['status'] = 0
                dummy_data['msg'] = res.get('error', "Unknow server error")
        else:
            dummy_data['status'] = 0
            dummy_data['msg'] = "auth failed/error"

        return ReportResource.generate_response(self, dummy_data, request)

    def get_resourcegroup_ungrouped(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'category': "Report",
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
        return ReportResource.generate_response(self, dummy_data, request)


    def report_files(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}

        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            domain = es_check["d"]
            owner = str(es_check["i"])+"|"+str(es_check["u"])+"|"+str(es_check["t"])
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'report_path')
            tmp_path = data_path + "yottaweb_reports/" + es_check["t"] + "/" + str(es_check["i"]) + "/"
            tmp_files = os.listdir(tmp_path)
            file_list = []
            for one_file in tmp_files:
                file_list.append({
                    'name': one_file,
                    'owner': es_check['u'],
                    'created_time': one_file.split('_')[-1]
                })
            dummy_data["list"] = file_list
            dummy_data["status"] = "1"
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def report_files_delete(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}

        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            post_data = request.POST
            domain = es_check["d"]
            owner = str(es_check["i"])+"|"+str(es_check["u"])+"|"+str(es_check["t"])
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'report_path')
            tmp_path = data_path + "yottaweb_reports/" + es_check["t"] + "/" + str(es_check["i"]) + "/"
            old_file = post_data.get("name", "")
            if old_file:
                target_file = os.path.join(tmp_path, old_file)
                if os.path.isfile(target_file):
                    os.remove(target_file)
                tmp_files = os.listdir(tmp_path)
                file_list = []
                for one_file in tmp_files:
                    file_list.append({
                        'name': one_file,
                        'owner': es_check['u'],
                        'created_time': one_file.split('_')[-1]
                    })
                dummy_data["list"] = file_list
                dummy_data["status"] = "1"
            else:
                data = err_data.build_error({}, "Delete report file error!")
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def report_files_download_directly(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}

        fid_encoded = kwargs['fid_encoded']

        if fid_encoded:
            my_utils = MyUtils()
            _decrypt_path = my_utils.b64Decrypt(fid_encoded.encode("utf-8"))
            re_logger.info("report_files_download_directly decrypted_path: %s", _decrypt_path)
            file_path = base64.urlsafe_b64decode(_decrypt_path) if _decrypt_path else ""
            re_logger.info("report_files_download_directly: %s", file_path)
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'report_path')
            tmp_path = data_path + "yottaweb_reports/" + file_path
            if file_path:
                file_name = file_path.split("/")[-1]
                wrapper = FileWrapper(file(file_path))
                resp = HttpResponse(wrapper, content_type='text/plain')

                # resp = self.create_response(request, wrapper)
                resp['Content-Length'] = os.path.getsize(file_path)
                resp['Content-Encoding'] = 'utf-8'
                resp['Content-Disposition'] = 'attachment;filename=%s' % file_name
                return resp
            else:
                data = err_data.build_error({}, "Download report file error!")
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def report_files_download(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}

        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            domain = es_check["d"]
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'report_path')
            tmp_path = data_path + "yottaweb_reports/" + es_check["t"] + "/" + str(es_check["i"]) + "/"
            file_name = kwargs['fid']
            file_path = tmp_path + kwargs['fid']
            if file_name:
                wrapper = FileWrapper(file(file_path))
                resp = HttpResponse(wrapper, content_type='text/plain')

                # resp = self.create_response(request, wrapper)
                resp['Content-Length'] = os.path.getsize(file_path)
                resp['Content-Encoding'] = 'utf-8'
                resp['Content-Disposition'] = 'attachment;filename=%s' % file_name
                return resp
            else:
                data = err_data.build_error({}, "Delete report file error!")
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def report_trends(self, request, **kwargs):
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
                dummy_data["status"] = "1"
                list = []
                for item in res.get('trends', []):
                    list.append({
                        "key": item.get("id"),
                        "value": item.get("name")
                    })
                dummy_data["list"] = list
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

    def delete_trend(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_data = request.POST

        trend_id = post_data.get("report_id", "")

        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': trend_id
            }
            res = BackendRequest.delete_trend(param)
            if res['result']:
                dummy_data["status"] = "1"
                list_param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                list_res = BackendRequest.get_all_trends(list_param)
                list = []
                if list_res['result']:
                    for item in list_res.get('trends', []):
                        list.append({
                            "key": item.get("id"),
                            "value": item.get("name")
                        })
                dummy_data["list"] = list
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


    def draw_line(self, line_data, *args,**kw):
        drawing = Drawing(400, 200)
        lp = LinePlot()
        lp.x = 30
        lp.y = -20
        lp.height = 200
        lp.width = 400
        lp.data = line_data
        lp.xValueAxis.labels.fontName       = 'Helvetica'
        lp.xValueAxis.labels.fontSize       = 7
        lp.xValueAxis.forceZero             = 0
        lp.xValueAxis.avoidBoundFrac           = 1
        lp.xValueAxis.gridEnd                  = 115
        lp.xValueAxis.tickDown                 = 3
        lp.xValueAxis.labelTextFormat = lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(x)/1000))

        lp.yValueAxis.tickLeft              = 3
        lp.yValueAxis.labels.fontName       = 'Helvetica'
        lp.yValueAxis.labels.fontSize       = 7
        for i in range(len(line_data)):
            lp.lines[i].strokeColor = colors.toColor('hsl(%s,80%%,40%%)'%(i*60))
        drawing.add(lp)

        title = Label()
        title.fontName   = 'Helvetica-Bold'
        title.fontSize   = 14
        title.x          = 200
        title.y          = 180
        title._text      = 'Chart Title'
        title.maxWidth   = 180
        title.height     = 20
        title.textAnchor ='middle'
        drawing.add(title)

        return drawing

    def build_stats(self, stats):
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
        return result

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


class LineChart(_DrawingEditorMixin, Drawing):
    def __init__(self,data,width=300,height=200,*args,**kw):
        Drawing.__init__(self,width,height,*args,**kw)
        self._add(self,LinePlot(),name='chart',validate=None,desc="The main chart")
        self.chart.width      = 300
        self.chart.height     = 180
        self.chart.x          = 30
        self.chart.y          = 40
        for i in range(len(data)):
            self.chart.lines[i].strokeColor = colors.toColor('hsl(%s,80%%,40%%)'%(i*60))
        # self.chart.lines[0].strokeColor = color01
        # self.chart.lines[1].strokeColor = color02
        # self.chart.lines[2].strokeColor = color03
        # self.chart.lines[3].strokeColor = color04
        # self.chart.lines[4].strokeColor = color05
        # self.chart.lines[5].strokeColor = color06
        # self.chart.lines[6].strokeColor = color07
        # self.chart.lines[7].strokeColor = color08
        # self.chart.lines[8].strokeColor = color09
        # self.chart.lines[9].strokeColor = color10
        self.chart.data             = data
        self.chart.fillColor         = backgroundGrey
        self.chart.lineLabels.fontName              = 'Helvetica'
        self.chart.xValueAxis.labels.fontName       = 'Helvetica'
        self.chart.xValueAxis.labels.fontSize       = 7
        self.chart.xValueAxis.forceZero             = 0
        self.chart.xValueAxis.avoidBoundFrac           = 1
        self.chart.xValueAxis.gridEnd                  = 115
        self.chart.xValueAxis.tickDown                 = 3
        self.chart.xValueAxis.visibleGrid              = 1
        self.chart.xValueAxis.labelTextFormat = lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(x)/1000))

        self.chart.yValueAxis.tickLeft              = 3
        self.chart.yValueAxis.labels.fontName       = 'Helvetica'
        self.chart.yValueAxis.labels.fontSize       = 7
        self._add(self,Label(),name='Title',validate=None,desc="The title at the top of the chart")
        self.Title.fontName   = 'Helvetica-Bold'
        self.Title.fontSize   = 7
        self.Title.x          = 100
        self.Title.y          = 135
        self.Title._text      = 'Chart Title'
        self.Title.maxWidth   = 180
        self.Title.height     = 20
        self.Title.textAnchor ='middle'
        self._add(self,Legend(),name='Legend',validate=None,desc="The legend or key for the chart")
        self.Legend.colorNamePairs = [(color01, 'Widgets'), (color02, 'Sprockets')]
        self.Legend.fontName       = 'Helvetica'
        self.Legend.fontSize       = 7
        self.Legend.x              = 153
        self.Legend.y              = 85
        self.Legend.dxTextSpace    = 5
        self.Legend.dy             = 5
        self.Legend.dx             = 5
        self.Legend.deltay         = 5
        self.Legend.alignment      ='right'
        self._add(self,Label(),name='XLabel',validate=None,desc="The label on the horizontal axis")
        self.XLabel.fontName       = 'Helvetica'
        self.XLabel.fontSize       = 7
        self.XLabel.x              = 85
        self.XLabel.y              = 10
        self.XLabel.textAnchor     ='middle'
        self.XLabel.maxWidth       = 100
        self.XLabel.height         = 20
        self.XLabel._text          = "X Axis"
        self._add(self,Label(),name='YLabel',validate=None,desc="The label on the vertical axis")
        self.YLabel.fontName       = 'Helvetica'
        self.YLabel.fontSize       = 7
        self.YLabel.x              = 12
        self.YLabel.y              = 80
        self.YLabel.angle          = 90
        self.YLabel.textAnchor     ='middle'
        self.YLabel.maxWidth       = 100
        self.YLabel.height         = 20
        self.YLabel._text          = "Y Axis"
        self.chart.yValueAxis.forceZero           = 1
        self.chart.xValueAxis.forceZero           = 1
        self._add(self,0,name='preview',validate=None,desc=None)
