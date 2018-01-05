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


def index(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        res = BackendRequest.get_func_auth({
            "token": is_login["t"],
        })
        if res["results"]["enable_security"]:
            with_sg = check_with_sourcegroup(is_login)
            cf_per = check_with_permission(is_login)
            return render(request, 'application/sparksql/index.html',
                          {"active": "applications", "subnav": "overview", "user": is_login["u"], "email": is_login["e"],
                           "token": is_login["t"], "userid": is_login["i"],
                           "role": is_login["r"], "with_sg": with_sg,
                           "cf_per": cf_per})
        else:
            raise Http404
    else:
        return HttpResponseRedirect('/auth/login/')

def referer(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        res = BackendRequest.get_func_auth({
            "token": is_login["t"],
        })
        if res["results"]["enable_security"]:
            with_sg = check_with_sourcegroup(is_login)
            cf_per = check_with_permission(is_login)
            return render(request, 'application/apache/referer.html',
                          {"active": "applications", "subnav": "referer", "user": is_login["u"], "email": is_login["e"],
                           "token": is_login["t"], "userid": is_login["i"],
                           "role": is_login["r"], "with_sg": with_sg,
                           "cf_per": cf_per})
        else:
            raise Http404
    else:
        return HttpResponseRedirect('/auth/login/')

def resource(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        res = BackendRequest.get_func_auth({
            "token": is_login["t"],
        })
        if res["results"]["enable_security"]:
            with_sg = check_with_sourcegroup(is_login)
            cf_per = check_with_permission(is_login)
            return render(request, 'application/apache/resource.html',
                          {"active": "applications", "subnav": "resource", "user": is_login["u"], "email": is_login["e"],
                           "token": is_login["t"], "userid": is_login["i"],
                           "role": is_login["r"], "with_sg": with_sg,
                           "cf_per": cf_per})
        else:
            raise Http404
    else:
        return HttpResponseRedirect('/auth/login/')

def visitor(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        res = BackendRequest.get_func_auth({
            "token": is_login["t"],
        })
        if res["results"]["enable_security"]:
            with_sg = check_with_sourcegroup(is_login)
            cf_per = check_with_permission(is_login)
            return render(request, 'application/apache/visitor.html',
                          {"active": "applications", "subnav": "visitor", "user": is_login["u"], "email": is_login["e"],
                           "token": is_login["t"], "userid": is_login["i"],
                           "role": is_login["r"], "with_sg": with_sg,
                           "cf_per": cf_per})
        else:
            raise Http404
    else:
        return HttpResponseRedirect('/auth/login/')

def service(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        res = BackendRequest.get_func_auth({
            "token": is_login["t"],
        })
        if res["results"]["enable_security"]:
            with_sg = check_with_sourcegroup(is_login)
            cf_per = check_with_permission(is_login)
            return render(request, 'application/apache/service.html',
                          {"active": "applications", "subnav": "service", "user": is_login["u"], "email": is_login["e"],
                           "token": is_login["t"], "userid": is_login["i"],
                           "role": is_login["r"], "with_sg": with_sg,
                           "cf_per": cf_per})
        else:
            raise Http404
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
