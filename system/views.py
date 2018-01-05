# -*- coding: utf-8 -*-
# wangqiushi,mayangguang (wang.qiushi@yottabyte.cn,ma.yangguang@yottabyte.cn)
# 2014/07/30
# Copyright 2014 Yottabyte
# file description : views.py.
from django.shortcuts import render
from django.db.models import Q
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
from django.http import HttpResponseRedirect
import os
import ConfigParser
import json
from django.core.exceptions import PermissionDenied


def custom_app(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {'role': is_login['r'], "subnav": "application", "appType": "list", "user": is_login["u"],
                                               "userid": is_login["i"]}
            return render(request, 'system/custom_app.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def custom_app_new(request, **kwargs):
    app = {
        "id": ""
    }
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {'role': is_login['r'], "subnav": "application", "appType": "new", "app": app,
                                                "user": is_login["u"], "userid": is_login["i"]}
            return render(request, 'system/custom_app.html',{"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def custom_app_update(request, app_id, **kwargs):
    app = {
        "id": app_id.encode('utf-8')
    }
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {'role': is_login['r'], "subnav": "application", "appType": "update", "app": app,
                                                "user": is_login["u"], "userid": is_login["i"]}
            return render(request, 'system/custom_app.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def custom_table(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {'role': is_login['r'], "subnav": "table", "tableType": "list", "user": is_login["u"],
                                                "userid": is_login["i"]}
            return render(request, 'system/custom_table.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def custom_table_new(request, **kwargs):
    table = {
        "id": ""
    }
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {'role': is_login['r'], "subnav": "table", "tableType": "new", "tbl": table,
                                                "user": is_login["u"], "userid": is_login["i"]}
            return render(request, 'system/custom_table.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def custom_table_update(request, tbl_id, **kwargs):
    table = {
        "id": tbl_id.encode('utf-8')
    }
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {'role': is_login['r'], "subnav": "table", "tableType": "update", "tbl": table,
                                                "user": is_login["u"], "userid": is_login["i"]}
            return render(request, 'system/custom_table.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def custom_dash(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {'role': is_login['r'], "subnav": "dashboard", "dashboardType": "list",
                                                "user": is_login["u"], "userid": is_login["i"]}
            return render(request, 'system/custom_dash.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def custom_dash_new(request, **kwargs):
    dash = {
        "id": ""
    }
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {'role': is_login['r'], "subnav": "dashboard", "dashboardType": "new", "dash": dash,
                                                "user": is_login["u"], "userid": is_login["i"]}
            return render(request, 'system/custom_dash.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def custom_dash_update(request, dash_id, **kwargs):
    dash = {
        "id": dash_id.encode('utf-8')
    }
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {'role': is_login['r'], "subnav": "dashboard", "dashboardType": "update", "dash": dash,
                                                "user": is_login["u"], "userid": is_login["i"]}
            return render(request, 'system/custom_dash.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def custom_theme(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        logo = check_backup_logo()
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {'role': is_login['r'], "subnav": "theme", "user": is_login["u"], "userid": is_login["i"], "small_back": logo["small_back"], "large_back": logo["large_back"]}
            return render(request, 'system/custom_theme.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def check_backup_logo():
    logo = {'small_back': 0, 'large_back': 0}
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    navLogoSmallPathName = cf.get('logo', 'nav_logo_path_name')
    navLogoSmallPathNameBk = cf.get('logo', 'nav_logo_path_name_bk')
    navLogoLargePathName = cf.get('logo', 'login_logo_path_name')
    navLogoLargePathNameBk = cf.get('logo', 'login_logo_path_name_bk')

    if os.path.isfile(navLogoSmallPathNameBk):
        logo['small_back'] = 1

    if os.path.isfile(navLogoLargePathNameBk):
        logo['large_back'] = 1

    return logo
