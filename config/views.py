# -*- coding: utf-8 -*-
# wangqiushi (wang.qiushi@yottabyte.cn)
# 2015/01/07
# Copyright 2015 Yottabyte
# file description : views.py
from django.shortcuts import render
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render
import pymysql
import ConfigParser
import os
import json
from django.core.exceptions import PermissionDenied

__author__ = 'wangqiushi; yangguang'


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


def configs(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            with_sg = 'no'
            sg_param = {
                'account': is_login['i'],
                'token': is_login['t'],
                'operator': is_login['u']
            }
            sg_res = BackendRequest.get_source_group(sg_param)
            if sg_res['result']:
                item = sg_res.get('items', [])
                if item:
                    with_sg = 'yes'
            cf_per = check_with_permission(is_login)
            page_data = {"active": "source", "subnav": "configs", "user": is_login["u"],
                         "email": is_login["e"],
                         "role": is_login["r"], "userid": is_login["i"],
                         "with_sg": with_sg, "cf_per": cf_per,
                         "rgid": request.GET.get("rgid", "")
                         }
            return render(request, 'extract/list.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def configs_new(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            with_sg = 'no'
            cf_per = check_with_permission(is_login)
            page_data = {"active": "source", "subnav": "configs", "user": is_login["u"],
                         "email": is_login["e"],
                         "role": is_login["r"], "userid": is_login["i"],
                         "config_id": "", "with_sg": with_sg, "cf_per": cf_per}
            return render(request, 'extract/new.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def configs_steps(request, name, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)

    visit_permit = BackendRequest.can_visit({
        "token": is_login['t'],
        "operator": is_login['u'],
        "requestUrl": request.path[1:]
    })
    if visit_permit['result'] and visit_permit['can_visit']:
        return render(request, 'config/steps/'+name+'.html', {"active": "source", "subnav": "configs"})
    else:
        raise PermissionDenied


def configs_helper(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            with_sg = 'no'
            cf_per = check_with_permission(is_login)
            return render(request, 'config/usual.html', {"active": "source", "subnav": "configs", "user": is_login["u"],
                                                            "email": is_login["e"],
                                                            "role": is_login["r"], "userid": is_login["i"],
                                                            "config_obj": {}, "with_sg": with_sg, "cf_per": cf_per})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def configs_update(request, id, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)

    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            domain = is_login["d"]
            try:
                conn = pymysql.connect(host=host, user=user, passwd=pwd, db=database, charset='utf8',
                                    cursorclass=pymysql.cursors.DictCursor)
                cur = conn.cursor()
                sql = "SELECT id FROM Domain WHERE name=%s"
                cur.execute(sql, domain)
                res = cur.fetchone()
                domain_id = res.get("id", "")
                if domain_id:
                    sql = "SELECT * FROM ParserRule WHERE id=%s AND domain_id IN (%s,%s)"
                    cur.execute(sql, (id, domain_id, '0'))
                    detail_res = cur.fetchone()
                    print detail_res
                    c_id = detail_res.get("category_id", 0)
                    print c_id
                    if not c_id == 1000:
                        raise Http404
                    with_sg = 'no'
                    cf_per = check_with_permission(is_login)
                    page_data = {"active": "source", "subnav": "configs", "user": is_login["u"],
                                 "email": is_login["e"],
                                 "role": is_login["r"], "userid": is_login["i"],
                                 "with_sg": with_sg, 'config_id': id, "cf_per": cf_per}
                    return render(request, 'extract/new.html', {"page_data": json.dumps(page_data)})
                else:
                    raise Http404
            except pymysql.Error, e:
                raise Http404
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def check_with_permission(login):
    config_permission = "no"
    func_auth_res = BackendRequest.get_func_auth({
        'token': login['t']
    })

    if func_auth_res['result']:
        if func_auth_res["results"]["parser_conf"]:
            config_permission = "yes"

    return config_permission
