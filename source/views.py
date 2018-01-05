# -*- coding=UTF-8 -*-
__author__ = 'wangqiushi; yangguang'
from django.shortcuts import render
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
from django.http import HttpResponseRedirect
from django.http import Http404
from multiprocessing.dummy import Pool as ThreadPool
import ConfigParser
import os
import json
from django.core.exceptions import PermissionDenied

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    from_url = cf.get('from', 'from_url')
    upload_url = cf.get('upload', 'upload_url')
    stream_port = cf.get('stream', 'stream_port')
except Exception, e:
    print e
    from_url = ".rizhiyi.com"
    upload_url = "http://log.rizhiyi.com/bulk"
    stream_port = "514"

host = "log" + from_url



def get_permission_worker(param):
    return BackendRequest.can_visit(param)


def source_input_agent(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        param1 = {
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        }
        param2 = {
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": "agent/upload/"
        }

        pool = ThreadPool(2)
        results = pool.map(get_permission_worker, [param1, param2])
        canVisitCurrentPage = results[0]
        canVisitUploadPage = results[1]

        if canVisitCurrentPage['result'] and canVisitCurrentPage['can_visit']:
            with_sg = check_with_sourcegroup(is_login)
            cf_per = check_with_permission(is_login)
            if (canVisitUploadPage['result'] and canVisitUploadPage['can_visit']):
                can_upload = "true"
            else:
                can_upload = "false"

            page_data = {"active": "source", "subnav": "agent", "user": is_login["u"], "email": is_login["e"],
                         "token": is_login["t"], "userid": is_login["i"],
                         "role": is_login["r"], "with_sg": with_sg,
                         "upload_url": upload_url, "host": host, "port": stream_port,
                         "cf_per": cf_per, "rgid": request.GET.get("rgid", ""),
                         "can_upload": can_upload}
            return render(request, 'agent/list.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def source_input_server_heka(request, **kwargs):
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
            return render(request, 'source/server_heka.html', {"active": "source", "subnav":"input","user": is_login["u"], "email": is_login["e"],
                                                        "token": is_login["t"], "userid": is_login["i"],
                                                            "role": is_login["r"], "with_sg": with_sg,
                                                            "upload_url": upload_url, "host": host, "port": stream_port,
                                                            "cf_per": cf_per})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def source_input_example(request, **kwargs):
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
            return render(request, 'source/source.html', {"active": "source", "subnav":"input","user": is_login["u"], "email": is_login["e"],
                                                        "token": is_login["t"], "userid": is_login["i"],
                                                            "role": is_login["r"], "with_sg": with_sg,
                                                            "upload_url": upload_url, "host": host, "port": stream_port,
                                                            "cf_per": cf_per})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def source_input_os(request, **kwargs):
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
            with_sg = check_with_sourcegroup(is_login)
            cf_per = check_with_permission(is_login)
            page_data = {"active": "source", "subnav":"input","user": is_login["u"], "email": is_login["e"],
                         "token": is_login["t"], "userid": is_login["i"],
                         "role": is_login["r"], "with_sg": with_sg,
                         "upload_url": upload_url, "host": host, "port": stream_port,
                         "cf_per": cf_per}
            return render(request, 'source/upload.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def source_input_ssa(request, **kwargs):
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
            with_sg = check_with_sourcegroup(is_login)
            cf_per = check_with_permission(is_login)
            return render(request, 'source/ssa.html', {"active": "source", "subnav":"input","user": is_login["u"], "email": is_login["e"],
                                                        "token": is_login["t"], "userid": is_login["i"],
                                                            "role": is_login["r"], "with_sg": with_sg,
                                                            "upload_url": upload_url, "host": host, "port": stream_port,
                                                            "cf_per": cf_per})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def source_detail(request, **kwargs):
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
            page_data = {"active": "source", "subnav":"input","user": is_login["u"], "email": is_login["e"],
                        "token": is_login["t"], "userid": is_login["i"], "role": is_login["r"], "with_sg": with_sg,
                        "upload_url": upload_url, "host": host, "port": stream_port, "cf_per": cf_per}
            return render(request, 'source/detail.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def source_input_linux(request, offset, **kwargs):
    platform = offset.encode('utf-8')
    if platform == "win" or platform == "linux":
        my_auth = MyBasicAuthentication()
        is_login = my_auth.is_authenticated(request, **kwargs)
        if is_login:
            visit_permit = BackendRequest.can_visit({
                "token": is_login['t'],
                "operator": is_login['u'],
                "requestUrl": request.path[1:]
            })
            if visit_permit['result'] and visit_permit['can_visit']:
                cf_per = check_with_permission(is_login)
                with_sg = check_with_sourcegroup(is_login)
                page_data = {"active": "source", "subnav": "input", "user": is_login["u"],
                             "email": is_login["e"],
                             "token": is_login["t"], "userid": is_login["i"],
                             "role": is_login["r"], "platform": platform,
                             "with_sg": with_sg, "upload_url": upload_url,
                             "cf_per": cf_per}
                return render(request, 'source/linux.html', {"page_data": json.dumps(page_data)})
            else:
                return HttpResponseRedirect('/auth/login/')
        else:
            raise PermissionDenied
    else:
        raise Http404


def source_sourcegroups(request, **kwargs):
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
            page_data = {"active": "source", "subnav": "sourcegroups", "user": is_login["u"],
                        "email": is_login["e"], "with_sg": with_sg,
                        "role": is_login["r"], "userid": is_login["i"],
                        "cf_per": cf_per, "rgid": request.GET.get("rgid", "")}
            return render(request, 'source/sourcegroups.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def source_sourcegroups_new(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            sourcegroup = {
                "id": "",
                "name": "",
                "description": "",
                "host": "",
                "application": "",
                "tag": ""
            }
            with_sg = check_with_sourcegroup(is_login)
            cf_per = check_with_permission(is_login)
            page_data = {"sourcegroup": sourcegroup, "active": "source", "subnav": "sourcegroups",
                        "email": is_login["e"], "user": is_login["u"], "userid": is_login["i"],
                        "role": is_login["r"], "with_sg": with_sg, "cf_per": cf_per}
            return render(request, 'source/sourcegroups-new.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def source_sourcegroups_update(request, offset, **kwargs):
    source_group_name = offset
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            sourcegroup = {
                "id": "",
                "name": source_group_name,
                "description": "",
                "host": "",
                "application": "",
                "tag": ""
            }
            res = BackendRequest.get_source_group({
                "token": is_login["t"],
                "name": source_group_name,
                "operator": is_login["u"]
            })
            if res["result"]:
                a_sg = res["items"][0]
                sourcegroup["id"] = a_sg.get("id", "").encode('utf-8')
                sourcegroup["name"] = a_sg.get("name", "").encode('UTF-8')
                sourcegroup["description"] = a_sg.get("description", "").encode('utf-8')
                sourcegroup["host"] = a_sg.get("hostname", "").encode('utf-8')
                sourcegroup["application"] = a_sg.get("appname", "").encode('utf-8')
                sourcegroup["tag"] = a_sg.get("tag", "").encode('utf-8')
            with_sg = check_with_sourcegroup(is_login)
            cf_per = check_with_permission(is_login)
            page_data = {"sourcegroup": sourcegroup, "active": "source", "subnav": "sourcegroups",
                        "email": is_login["e"], "user": is_login["u"], "userid": is_login["i"],
                        "role": is_login["r"], "with_sg": with_sg, "cf_per": cf_per}
            return render(request, 'source/sourcegroups-new.html', {"page_data": json.dumps(page_data)})
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
