# wangqiushi (@yottabyte.cn)
# ma.yangguang(@yottabyte.cn)
# 2014/06/12
# Copyright 2014 Yottabyte
# file description : dashboard.

from django.shortcuts import render
from yottaweb.apps.basic.resources import MyBasicAuthentication
from django.http import HttpResponseRedirect
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.variable.resources import MyVariable
from django.http import Http404
import ConfigParser
import os
import json

# import json

# with open('config.json', 'r') as f:
#     config = json.load(f)

# #edit the data
# config['key3'] = 'value3'

# #write it back to the file
# with open('config.json', 'w') as f:
#     json.dump(config, f)


def overview(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        with_sg = check_with_sourcegroup(is_login)
        cf_per = check_with_permission(is_login)
        my_var = MyVariable()
        data_path = my_var.get_var('path', 'data_path')
        config_path = data_path + "custom"
        real_file = config_path + '/apps.json'
        try:
            with open(real_file, 'r') as f:
                config = json.load(f)
            apps = config["apps"]
        except Exception, e:
            print e
            apps = []
            config={}
        table_file = config_path + '/tables.json'
        try:
            with open(table_file, 'r') as f:
                config = json.load(f)
            tables = config["tables"]
        except Exception, e:
            print e
            tables = []
            config={}

        return render(request, 'application/overview.html',
                      {"active": "applications", "subnav": "overview", "user": is_login["u"], "email": is_login["e"],
                       "token": is_login["t"], "userid": is_login["i"], "tables": tables,
                       "role": is_login["r"], "with_sg": with_sg, "apps": apps,"config":config,
                       "cf_per": cf_per})
    else:
        return HttpResponseRedirect('/auth/login/')


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


def check_with_permission(login):
    config_permission = "no"
    func_auth_res = BackendRequest.get_func_auth({
        'token': login['t']
    })

    if func_auth_res['result']:
        if func_auth_res["results"]["parser_conf"]:
            config_permission = "yes"

    return config_permission
