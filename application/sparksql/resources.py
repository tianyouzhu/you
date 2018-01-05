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
from yottaweb.apps.basic.resources import ContributeErrorData
import ast
import json
import requests
import ConfigParser
import os
import logging
import time
import os
import csv

err_data = ContributeErrorData()

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    SPARKSQL_HOST = cf.get('sparksql', 'host')
except Exception, e:
    SPARKSQL_HOST = 'http://localhost'


class SparksqlResource(Resource):
    class Meta:
        resource_name = 'sparksql'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/list_tasks/$" % (self._meta.resource_name),
                self.wrap_view('list_tasks'), name="api_list_tasks"),
            url(r"^(?P<resource_name>%s)/execute/$" % (self._meta.resource_name),
                self.wrap_view('execute'), name="api_execute"),
            url(r"^(?P<resource_name>%s)/delete_task/$" % (self._meta.resource_name),
                self.wrap_view('delete_task'), name="api_delete_task"),
            url(r"^(?P<resource_name>%s)/check_status/$" % (self._meta.resource_name),
                self.wrap_view('check_status'), name="api_check_status"),
            url(r"^(?P<resource_name>%s)/fetch_result_data/$" % (self._meta.resource_name),
                self.wrap_view('fetch_result_data'), name="api_fetch_result_data"),
            url(r"^(?P<resource_name>%s)/export_csv/$" % (self._meta.resource_name),
                self.wrap_view('export_csv'), name="api_export_csv"),
        ]

    def list_tasks(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            url = SPARKSQL_HOST + '/api/list_tasks'
            data = {
                    "user": es_check.get('u'),
                    "start_time": 0,
            }
            self.auditLog(data,es_check);

            data = json.dumps(data)

            result = requests.post(url, data=data)
            print "result.status_code: ", result.status_code
            if result.status_code == 200:
                res = result.json()
                print "res: ", res
                if res.get('status')== 0:#0:success;-1:error
                    dummy_data["status"] = 1
                    dummy_data["data"] =res.get('result').get('tasks')
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
                    dummy_data["msg"] = res.get('message')
            else:
                data = err_data.build_error({})
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def execute(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        statement = request.POST.get('statement')

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        print "###################es_check:  ", es_check
        if es_check:
            url = SPARKSQL_HOST + '/api/execute'
            print "###############url: ", url
            data = {
                    "user": es_check.get('u'),
                    "statement": statement,
            }
            self.auditLog(data,es_check);
            data = json.dumps(data)
            print "###############data: ", data

            result = requests.post(url, data=data)
            print "result.status_code: ", result.status_code
            if result.status_code == 200:
                res = result.json()
                print "res: ", res
                if res.get('status')== 0:#0:success;-1:error
                    dummy_data["status"] = 1
                    dummy_data["data"] =res.get('result').get('taskid') 
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
                    dummy_data["msg"] = res.get('message')
            else:
                data = err_data.build_error({})
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def delete_task(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        taskid = request.POST.get('taskid')

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        print "###################es_check:  ", es_check
        if es_check:
            url = SPARKSQL_HOST + '/api/delete_task'
            print "###############url: ", url
            data = {
                    "user": es_check.get('u'),
                    "taskid": taskid,
            }
            self.auditLog(data,es_check);
            data = json.dumps(data)
            print "###############data: ", data

            result = requests.post(url, data=data)
            print "result.status_code: ", result.status_code
            if result.status_code == 200:
                res = result.json()
                print "res: ", res
                if res.get('status')== 0:#0:success;-1:error
                    dummy_data["status"] = 1
                    dummy_data["data"] =res.get('result').get('status') 
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
                    dummy_data["msg"] = res.get('message')
            else:
                data = err_data.build_error({})
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def check_status(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        taskid = request.POST.get('taskid')

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        print "###################es_check:  ", es_check
        if es_check:
            url = SPARKSQL_HOST + '/api/check_status'
            print "###############url: ", url
            data = {
                    "user": es_check.get('u'),
                    "taskid": taskid,
            }
            data = json.dumps(data)
            print "###############data: ", data

            result = requests.post(url, data=data)
            print "result.status_code: ", result.status_code
            if result.status_code == 200:
                res = result.json()
                print "check_status res: ", res
                if res.get('status')== 0:#0:success;-1:error
                    dummy_data["status"] = 1
                    dummy_data["data"] =res.get('result').get('status') 
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
                    dummy_data["msg"] = res.get('message')
            else:
                data = err_data.build_error({})
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def fetch_result_data(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        taskid = request.POST.get('taskid')
        index = request.POST.get('index')
        pagesize= request.POST.get('pagesize')

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            url = SPARKSQL_HOST + '/api/fetch_result_data'
            print "###############url: ", url
            data = {
                    "taskid": taskid,
                    "user": es_check.get('u'),
                    "index": index,
                    "pagesize":pagesize 
            }
            self.auditLog(data,es_check);
            data = json.dumps(data)
            print "###############data: ", data

            result = requests.get(url, data=data)
            print "result.status_code: ", result.status_code
            if result.status_code == 200:
                res = result.json()
                # print "fetch_result_datla res: ", res
                if res.get('status')== 0:#0:success;-1:error
                    dummy_data["status"] = 1
                    dummy_data["data"] =res.get('result')  
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
                    dummy_data["msg"] = res.get('message')
            else:
                data = err_data.build_error({})
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def export_csv(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        taskid = request.POST.get('taskid')
        print "###############export_csv",taskid
        # time.sleep(32)

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            url = SPARKSQL_HOST + '/api/fetch_result_data'
            print "###############url: ", url
            data = {
                    "taskid": taskid,
                    "user": es_check.get('u'),
                    "index": 0,
                    "pagesize":10000 
            }
            self.auditLog(data,es_check);
            data = json.dumps(data)
            print "###############data: ", data

            result = requests.get(url, data=data)
            print "result.status_code: ", result.status_code
            if result.status_code == 200:
                res = result.json()
                print "fetch_result_datla res: ", res
                if res.get('status')== 0:#0:success;-1:error
                    dummy_data["status"] = 1
                    if res.get('result').get('type')=='table':
                        downloadUrl = self.getDownloadUrl(res.get('result'),es_check.get('d'),es_check.get('u'),taskid)
                        print "#############downloadUrl: ",downloadUrl
                        dummy_data["data"] = downloadUrl
                    else:
                        dummy_data["data"] = 'error'
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
                    dummy_data["msg"] = res.get('message')
            else:
                data = err_data.build_error({})
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def getDownloadUrl(self, data,domain,user,taskid):
        print "########getDownloadUrl"
        root_path = os.getcwd()
        tmp_path = root_path + "/yottaweb_tmp/" + domain + "/" + user + "/"
        print "###########tmp_path: ",tmp_path
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        name = 'sparksql_'+'rizhiyi_' + user.encode("utf-8") + '_' + taskid 
        file_name = str(name) + ".csv"
        file_path = tmp_path + file_name
        print "###########file_name: ",file_name

        names = []
        for item in data.get('meta'):
            names.append(item.get('name'))
            # names.append('中文测试')

        with open(file_path, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            spamwriter.writerow(names)
            for values in data.get('data'):
                spamwriter.writerow(values) 

        return file_name


    def auditLog(self,data,es_check):
        print "##################audit log"
        try:
            data = {
                    "user": es_check.get('u'),
                    "start_time": 0,
                    }
            logger = logging.getLogger('yottaweb.audit')
            to_log = dict.copy(data)
            to_log["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            to_log["action"] = "spark_sql"
            to_log["user_name"] = es_check.get('u')
            to_log["user_id"] = es_check.get('i')
            logger.info(json.dumps(to_log))
        except:
            pass
          

