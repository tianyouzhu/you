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
from urlparse import urlparse
import os
import ConfigParser
import logging
import time
import hashlib
import json
from django.core.exceptions import PermissionDenied


try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    timeline_color = cf.get('custom', 'timeline_color')
except Exception, e:
    print e
    timeline_color = '#1e9eef'


def dashboard_group(request, **kwargs):
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
            page_data = {
                "active": "dashboard", "user": is_login["u"],
                "email": is_login["e"], "timeline_color": timeline_color,
                "role": is_login["r"], "userid": is_login["i"], "with_sg": with_sg,
                "dashboardType": "list", "rgid": request.GET.get("rgid", "")
            }
            return render(request, 'dashboard/list.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def dashboard_group_login(request, username, password, sign, **kwargs):
    # cur_time = str(time.time()).split(".")[0]
    if not hashlib.md5(username+password).hexdigest() == sign:
        raise PermissionDenied
    auto_login_permit = MyVariable().get_var("custom", "dashboard_login") if MyVariable().get_var("custom", "dashboard_login") else "no"
    if not auto_login_permit == "yes":
        raise PermissionDenied
    referer = request.META.get('HTTP_REFERER')
    host = urlparse(referer).netloc
    domain = host.split('.')[0]
    logger = logging.getLogger("yottaweb.audit")
    param = {
        "domain": domain,
        "name": username,
        "passwd": password
    }
    # print password

    # user info for yottaD
    req = BackendRequest.login(param)
    es_check = req['result']
    token = ""
    if es_check:
        token = req.get('token', "")
        request.session['user_name'] = username
        request.session['user_pwd'] = password
        request.session['user_tkn'] = token
        request.session['user_id'] = req.get('owner_id', "")
        to_log = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "action": "login",
            "user_name": username,
            "user_id": req.get('owner_id', ""),
            "domain": domain,
            "result": "success"
        }
        cookie_string = hashlib.md5(
            username + ',' + domain + ',' + token).hexdigest()
        request.session['user_yottac'] = cookie_string
        request.session.set_expiry(259200)
        logger.info(json.dumps(to_log))
        return HttpResponseRedirect('/dashboard/')
    else:
        #0: server error, 1:password or user wrong
        to_log = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "action": "login",
            "user_name": username,
            "user_id": req.get('owner_id', ""),
            "domain": domain,
            "result": "error",
            "msg": req['error']
        }

        logger.info(json.dumps(to_log))
        return HttpResponseRedirect('/auth/login/')


def dashboard_detail(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    dashboard_id = kwargs.get("did", "")
    tab_id = kwargs.get("tid", "")
    rgids = request.GET.get('rgids', "")
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            with_sg = check_with_sourcegroup(is_login)
            page_data = {
                "active": "dashboard", "user": is_login["u"], "dashboardId": dashboard_id,
                "email": is_login["e"], "timeline_color": timeline_color,
                "role": is_login["r"], "userid": is_login["i"], "with_sg": with_sg,
                "dashboardType": "detail", "rgids": rgids, "tabId": tab_id
            }
            return render(request, 'dashboard/detail.html', {"page_data": json.dumps(page_data)})
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
