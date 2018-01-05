__author__ = 'zhaixiaoyu'

from django.shortcuts import render
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
from django.http import HttpResponseRedirect
import json
import os
import ConfigParser
from django.core.exceptions import PermissionDenied

def payments(request, **kwargs):
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
            page_data = {"user": is_login["u"], "email": is_login["e"],
                        "userid": is_login["i"], "with_sg": with_sg
                        }
            return render(request, 'payment/list.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def update(request, offset, **kwargs):
    bid = offset.encode('utf-8')
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
            page_data = {"user": is_login["u"], "email": is_login["e"], "beneficiary_id": bid,
                        "userid": is_login["i"], "with_sg": with_sg
                        }
            return render(request, 'payment/update.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def new(request, **kwargs):
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
            page_data = {"user": is_login["u"], "email": is_login["e"], "beneficiary_id": "",
                        "userid": is_login["i"], "with_sg": with_sg
                        }
            return render(request, 'payment/update.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def usage(request, offset, **kwargs):
    bid = offset.encode('utf-8')
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
            page_data = {"user": is_login["u"], "email": is_login["e"], "beneficiary_id": bid,
                        "userid": is_login["i"], "with_sg": with_sg
                        }
            return render(request, 'payment/usage.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def check_with_sourcegroup(login):
    with_sg = 'no'
    if login['r'] == "user":
        sg_param = {
            'account': login['i'],
            'token': login['t']
        }
        sg_res = BackendRequest.get_source_group(sg_param)
        if sg_res['result']:
            item = sg_res.get('items', [])
            if item:
                with_sg = 'yes'
    return with_sg
