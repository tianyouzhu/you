# -*- coding: utf-8 -*-
# wangqiushi (wang.qiushi@yottabyte.cn)
# 2015/11/21
# Copyright 2015 Yottabyte
# file description : application custom api

from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.variable.resources import MyVariable
import ast
import json
import os

err_data = ContributeErrorData()


class ApplicationListResource(Resource):
    class Meta:
        resource_name = 'applicationlist'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^application/list/$", self.wrap_view('app_list'), name="api_step"),
        ]

    def app_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            real_file = config_path + '/apps.json'
            traces = []
            tables = []
            try:
                with open(real_file, 'r') as f:
                    config = json.load(f)
                _tmp_traces = config["apps"]
                for item in _tmp_traces:
                    print item
                    traces.append({
                        "name": item.get("name", ""),
                        "link": "/app/custom/" + item.get("id", "") + "/",
                        "permission": "true"
                    })
            except Exception, e:
                print e
            table_file = config_path + '/tables.json'
            try:
                with open(table_file, 'r') as f:
                    config = json.load(f)
                _tmp_tables = config["tables"]
                for item in _tmp_tables:
                    tables.append({
                        "name": item.get("name", ""),
                        "link": "/app/table/" + item.get("id", "") + "/",
                        "permission": "true"
                    })
            except Exception, e:
                print e
                tables = []
            dummy_data["status"] = "1"
            print traces
            apacheTable = [
                {
                    "name": "今日概况",
                    "link": "/app/apache/",
                    "permission": "app/",
                },
                {
                    "name": "访问资源",
                    "link": "/app/apache/resource/",
                    "permission": "app/"
                },
                {
                    "name": "访客分析",
                    "link": "/app/apache/visitor/",
                    "permission": "app/"
                },
                {
                    "name": "服务状态",
                    "link": "/app/apache/service/",
                    "permission": "app/"
                },
            ]
            dummy_data["apps"] = [
                {
                    "group": "Apache",
                    "items": apacheTable
                }, {
                    "group": "关联搜索",
                    "items": traces
                }, {
                    "group": "应用表格",
                    "items": tables
                }]

        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

