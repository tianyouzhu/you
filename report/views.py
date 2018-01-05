# -*- coding: utf-8 -*-
# wangqiushi,mayangguang (wang.qiushi@yottabyte.cn,ma.yangguang@yottabyte.cn)
# 2014/07/30
# Copyright 2014 Yottabyte
# file description : views.py.
__author__ = 'wangqiushi'
from django.shortcuts import render
from django.db.models import Q
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
from django.http import HttpResponseRedirect
import os
import ConfigParser
import pymysql
import json
from django.core.exceptions import PermissionDenied


try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    retention = cf.get('usage', 'retention')
    limit = cf.get('usage', 'limit')
    release_type = cf.get('release', 'type')
    timeline_color = cf.get('custom', 'timeline_color')
    if release_type == 'SaaS':
        # !!!!ATTENTION!!!!!!!!!!!!!!!!
        # 想要SASS分开打包，新建个页面看自己套餐信息？还有当前套餐信息在这显示也有版本分化的问题了。
        from yottaweb.apps.subscription.models import Order
        from yottaweb.apps.subscription import utility
except Exception, e:
    print e
    timeline_color = '#1e9eef'
    retention = 7
    limit = 209715200

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

def reports(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {"user": is_login["u"], "active":"report", "email": is_login["e"], "subnav": "reports",
                         "role": is_login["r"], "userid": is_login["i"], "rgid": request.GET.get("rgid", "")
                         }
            return render(request, 'report/list.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def reports_list(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            return render(request, 'report/list_view.html', {"user": is_login["u"], "email": is_login["e"],
                                                        "userid": is_login["i"],"subnav": "reports",
                                                            "role": is_login["r"]
                                                            })
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def reports_new(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    report = {
        'id': ""
    }

    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {'report': report, "active":"report", "user": is_login["u"], "email": is_login["e"],
                        "subnav": "reprot", "role": is_login["r"], "userid": is_login["i"], "trend_ids": request.GET.get("trend_ids", "")
                        }
            return render(request, 'report/new.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def report_update(request, offset, **kwargs):
    report_id = offset
    report = {
        'id': report_id.encode('utf-8')
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
            # get source group information
            report_param = {
                'account': report_id,
                'token': is_login['t'],
                "operator": is_login['u']
            }
            domain = is_login["d"]
            owner = str(is_login["i"]) + "|" + str(is_login["u"]) + "|" + str(is_login["t"])

            try:
                conn = pymysql.connect(host=host, user=user, passwd=pwd, db=database, charset='utf8',
                                    cursorclass=pymysql.cursors.DictCursor)
                cur = conn.cursor()
                sql = "SELECT * FROM Report WHERE domain='%s' AND owner='%s' AND id='%s' ORDER BY id" % (
                domain, owner, report_id)
                cur.execute(sql)
                res = cur.fetchone()

                cur.close()
                conn.close()

                page_data = {'report': report, "active":"report", "user": is_login["u"], "email": is_login["e"],
                        "subnav": "reprot", "role": is_login["r"], "userid": is_login["i"]
                        }
                return render(request, 'report/new.html', {"page_data": json.dumps(page_data)})
            except pymysql.Error, e:
                return HttpResponseRedirect('/auth/login/')
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')
