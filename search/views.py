# wangqiushi (@yottabyte.cn)
# 2014/06/12
# Copyright 2014 Yottabyte
# file description : resources.py.
__author__ = 'wangqiushi'
from django.shortcuts import render
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
from django.http import HttpResponseRedirect
import os
import ConfigParser
import json
from django.core.exceptions import PermissionDenied

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    fields_limit = cf.get('fields', 'fields_limit')
    timeline_color = cf.get('custom', 'timeline_color')
    auto_search = cf.get('custom', 'auto_search')
    loading_auto_search = cf.get('custom', 'loading_auto_search')
except Exception, e:
    print e
    fields_limit = 50
    timeline_color = '#1e9eef'
    auto_search = 'yes'
    loading_auto_search = 'yes'

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    syslog = cf.get('alert', 'syslog')
except Exception, e:
    print e
    syslog = 'no'


def search(request, **kwargs):
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
            page_data = {"active": "search", "user": is_login["u"], "email": is_login["e"],
                         "role": is_login["r"], "userid": is_login["i"],
                         "timeline_color": timeline_color, "syslog": syslog,
                         "with_sg": with_sg, "fields_limit": fields_limit, 'ri': is_login["ri"],
                         'loading_auto_search': loading_auto_search, 'auto_search': auto_search}
            return render(request, 'search/search.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')
