# wangqiushi (@yottabyte.cn)
# ma.yangguang(@yottabyte.cn)
# 2014/06/12
# Copyright 2014 Yottabyte
# file description : dashboard.

from django.shortcuts import render
from yottaweb.apps.basic.resources import MyBasicAuthentication
from django.http import HttpResponseRedirect
from yottaweb.apps.backend.resources import BackendRequest
from django.http import Http404
from django.core.exceptions import PermissionDenied

import json


def backup(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            with_sg = check_with_sourcegroup(is_login)
            cf_per = check_with_permission(is_login)
            page_data = {"active": "source", "subnav": "backup", "user": is_login["u"], 
                        "email": is_login["e"], "token": is_login["t"], "userid": is_login["i"], 
                        "role": is_login["r"], "with_sg": with_sg, "cf_per": cf_per}
            return render(request, 'backup/backup.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
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


