# wangqiushi (@yottabyte.cn)
# 2016/09/01
# Copyright 2015 Yottabyte
# file description : views.py.
__author__ = 'wangqiushi'

from django.shortcuts import render
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
from django.http import HttpResponseRedirect
from django.http import Http404
from django.core.exceptions import PermissionDenied

import json


def schedules(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {"active": "schedule", "user": is_login["u"], "email": is_login["e"],
                         "role": is_login["r"], "userid": is_login["i"],
                         "rgid": request.GET.get("rgid", "")
                         }
            return render(request, 'schedule/schedule.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def schedule_content(request, s_id, **kwargs):
    schedule_id = s_id.encode('utf-8')
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            res = BackendRequest.get_saved_schedule ({
                'token': is_login['t'],
                'id': schedule_id,
                'operator': is_login['u']
            })
            if res['result']:
                schedule_info = res.get('saved_schedule', {})
                name = schedule_info.get('name', '')

                page_data = {"active": "schedule", 'id': schedule_id, "name": name, "user": is_login["u"],
                            "email": is_login["e"], "role": is_login["r"], "userid": is_login["i"]
                            }
                return render(request, 'schedule/schedule_content.html', {"page_data": json.dumps(page_data)})
            else:
                raise Http404
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def schedule_update(request, s_id, **kwargs):
    schedule_id = s_id.encode('utf-8')
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            res = BackendRequest.get_saved_schedule({
                'token': is_login['t'],
                'id': schedule_id,
                'operator': is_login['u']
            })
            if res['result']:
                schedule_info = res.get('saved_schedule', {})
                name = schedule_info.get('name', '')
                page_data = {"active": "schedule", 'id': schedule_id, "name": name, "user": is_login["u"],
                            "email": is_login["e"], "role": is_login["r"], "userid": is_login["i"]
                            }
                return render(request, 'schedule/schedule_update.html', {"page_data": json.dumps(page_data)})
            else:
                raise Http404
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def schedule_detail(request, s_id, s_ts, **kwargs):
    schedule_id = s_id.encode('utf-8')
    schedule_timestamp = s_ts.encode('utf-8')
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            res = BackendRequest.get_saved_schedule ({
                'token': is_login['t'],
                'id': schedule_id,
                'operator': is_login['u']
            })
            if res['result']:
                schedule_info = res.get('saved_schedule', {})
                name = schedule_info.get('name', '')
                page_data = {"active": "schedule", 'id': schedule_id, "name": name, "user": is_login["u"], 'timestamp': schedule_timestamp,
                            "email": is_login["e"], "role": is_login["r"], "userid": is_login["i"]
                            }
                return render(request, 'schedule/schedule_detail.html', {"page_data": json.dumps(page_data)})
            else:
                raise Http404
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

