# wangqiushi (@yottabyte.cn)
# ma.yangguang(@yottabyte.cn)
# 2014/06/12
# Copyright 2014 Yottabyte
# file description : dashboard.

from django.shortcuts import render
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.variable.resources import MyVariable
from django.http import HttpResponseRedirect
from yottaweb.apps.backend.resources import BackendRequest
from django.http import Http404
import os
import json


def overview(request, cid, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        try:
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            real_file = config_path + '/apps.json'
            info = {}
            with open(real_file, 'r') as f:
                config = json.load(f)
            apps = config["apps"]
            for item in apps:
                if item["id"] == cid:
                    info = item
        except Exception, e:
            print e
            info = {}
        page_data = {"active": "applications", "subnav": "overview", "user": is_login["u"], "email": is_login["e"],
                                           "token": is_login["t"], "userid": is_login["i"], "app_info": info,
                                           "role": is_login["r"]}
        return render(request, 'application/custom/trace.html', {"page_data": json.dumps(page_data)})
        # else:
            # raise Http404
    else:
        return HttpResponseRedirect('/auth/login/')


def table(request, cid, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        try:
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            real_file = config_path + '/tables.json'
            info = {}
            with open(real_file, 'r') as f:
                config = json.load(f)
            tables = config["tables"]
            for item in tables:
                if item["id"] == cid:
                    info = item
        except Exception, e:
            print e
            info = {}
        page_data = {"active": "applications", "subnav": "overview", "user": is_login["u"], "email": is_login["e"],
                                           "token": is_login["t"], "userid": is_login["i"], "table_info": info,
                                           "role": is_login["r"]}
        return render(request, 'application/custom/table.html', {"page_data": json.dumps(page_data)})
        # else:
            # raise Http404
    else:
        return HttpResponseRedirect('/auth/login/')
