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
import json
import ConfigParser
import logging
from django.core.exceptions import PermissionDenied

logger = logging.getLogger("django.request")


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
    show_fullname = cf.get('custom', 'fullname')
except Exception, e:
    print e
    show_fullname = "yes"


def users(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {"user": is_login["u"], "email": is_login["e"], "userid": is_login["i"], "role": is_login["r"]}
            return render(request, 'account/users.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def usage(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    domain_name = request.META.get('HTTP_HOST').split('.')[0]
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            domain_info = BackendRequest.get_domain({'token': is_login['t']})
            if domain_info['result']:
                info_detail = domain_info.get('domain', {'limit_quota': -1})
                return_limit = info_detail.get('limit_quota', limit)
                # if not return_limit or return_limit < 0:
                #     return_limit = limit
                token_limit = return_limit if return_limit == -1 else float(return_limit)/1024/1024

                result_hash = {
                    "user": is_login["u"],
                    "userid": is_login["i"],
                    "role": is_login["r"],
                    "timeline_color": timeline_color,
                    "info": {"limit": token_limit, "retention": retention}
                }

                if release_type == 'SaaS':
                    validated_orders = []
                    for o in list(Order.objects.filter(status='validated', domain_name=domain_name).order_by('-create_time')):
                        validated_orders.append({
                            'end_day': o.pre_expire_time,
                            'start_day': o.validate_time,
                            'volume': utility.mb_to_gb(o.volume),
                            'price': o.charge,
                            'order_id': o.order_id(),
                            'create_day': o.create_time
                            })
                    other_orders = []
                    for o in Order.objects.filter(Q(status='init') | Q(status='paid'), domain_name=domain_name).order_by('-create_time'):
                        status_str = ""
                        if o.status == 'init' or o.status == 'paid':
                            status_str = '待处理'
                        if o.status == 'expired':
                            status_str = '已失效'

                        other_orders.append({
                            'end_day': o.pre_expire_time,
                            'start_day': o.pre_validate_time,
                            'volume': utility.mb_to_gb(o.volume),
                            'price': o.charge,
                            'order_id': o.order_id(),
                            'status': status_str,
                            'create_day': o.create_time
                            })

                    result_hash["validated_orders"] = validated_orders
                    result_hash["other_orders"] = other_orders

                page_data = result_hash
                return render(request, 'account/usage.html', {"page_data": json.dumps(page_data)})

            else:
                return HttpResponseRedirect('/auth/login/')
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def users_new(request, **kwargs):
    account = {
        'user_id': '',
        'username': '',
        'fullname': '',
        'email': '',
        'phone': '',
        'user_groups': []
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
            page_data = {'account': account, "email": is_login["e"],
                        "user": is_login["u"], "role": is_login["r"],
                        "userid": is_login["i"], "show_fullname": show_fullname}
            return render(request, 'account/users_new.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def update(request, uid, **kwargs):
    user_id = uid
    account = {
        'user_id': user_id.encode('utf-8'),
        'username': '',
        'fullname': '',
        'email': '',
        'phone': '',
        'user_groups': []
    }
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if (visit_permit['result'] and visit_permit['can_visit']) or user_id == str(is_login['i']):
            user_param = {
                'id': user_id,
                'token': is_login['t'],
                'operator': is_login['u']
            }
            res = BackendRequest.get_account(user_param)
            if res['result']:
                one_account = res.get('accounts', [])[0]
                account['username'] = one_account['name'].encode('utf-8')
                account['fullname'] = one_account['full_name'].encode('utf-8')
                account['email'] = one_account['email'].encode('utf-8')
                account['phone'] = one_account['phone'].encode('utf-8')
                account['user_groups'] = one_account['user_groups']

            page_data = {'account': account, "email": is_login["e"],
                        "user": is_login["u"], "userid": is_login["i"]}
            return render(request, 'account/users_new.html', {"page_data": json.dumps(page_data)})

        else:
            raise PermissionDenied
    elif is_login:
        page_data = {"user": is_login["u"], "email": is_login["e"], "userid": is_login["i"]}
        return render(request, 'account/users.html', {"page_data": json.dumps(page_data)})
    else:
        return HttpResponseRedirect('/auth/login/')


def usergroups(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            return render(request, 'account/usergroup.html', {"user": is_login["u"], "email": is_login["e"], "userid": is_login["i"], "role": is_login["r"]})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def usergroups_new(request, **kwargs):
    group = {
        'id': '',
        'name': ''
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
            page_data = {'group': group, "email": is_login["e"],
                        "user": is_login["u"], "userid": is_login["i"]}
            return render(request, 'account/usergroup_new.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def usergroups_update(request, ug_id, **kwargs):
    group = {
        'id': ug_id
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
            param = {
                'token': is_login['t'],
                'operator': is_login['u'],
                'id': ug_id
            }
            res = BackendRequest.get_user_group(param)
            if res['result']:
                page_data = {'group': group, "email": is_login["e"], "role": is_login["r"],
                        "user": is_login["u"], "userid": is_login["i"]}
                return render(request, 'account/usergroup_new.html', {"page_data": json.dumps(page_data)})
            else:
                logger.error("%s get user group error, redirect to usergroup list!", is_login['u'])
                return render(request, 'account/usergroup.html', {"user": is_login["u"], "userid": is_login["i"], "role": is_login["r"] })
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def roles(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {"user": is_login["u"], "userid": is_login["i"], "role": is_login["r"]}
            return render(request, 'account/roles.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def roles_new(request, **kwargs):
    role_data = {
        'role_id': "",
        'copy_id': ""
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
            page_data = {"edit_role": role_data, "user": is_login["u"], "userid": is_login["i"], "role": is_login["r"]}
            return render(request, 'account/roles_new.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def roles_update(request, role_id, **kwargs):
    role_data = {
        'role_id': role_id.encode('utf-8'),
        'copy_id': ""
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
            page_data = {"edit_role": role_data, "user": is_login["u"], "userid": is_login["i"], "role": is_login["r"]}
            return render(request, 'account/roles_new.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def roles_copy(request, copy_id, **kwargs):
    role_data = {
        'role_id': "",
        'copy_id': copy_id.encode('utf-8')
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
            page_data = {"edit_role": role_data, "user": is_login["u"], "userid": is_login["i"], "role": is_login["r"]}
            return render(request, 'account/roles_new.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def roles_assign(request, role_id, **kwargs):
    role_data = {
        'role_id': role_id.encode('utf-8')
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
            page_data = {"assign_role": role_data, "user": is_login["u"], "userid": is_login["i"], "role": is_login["r"]}
            return render(request, 'account/roles_assign.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def resourcegroups(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            page_data = {"user": is_login["u"], "userid": is_login["i"], "role": is_login["r"], "type": request.GET.get("type", "")}
            return render(request, 'account/resourcegroups.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def resourcegroups_new(request, **kwargs):
    rg_data = {
        'rg_id': ""
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
            page_data = {"edit_rg": rg_data, "user": is_login["u"], "userid": is_login["i"], "role": is_login["r"]}
            return render(request, 'account/resourcegroups_new.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def resourcegroups_update(request, rg_id, **kwargs):
    rg_data = {
        'rg_id': rg_id.encode('utf-8')
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
            page_data = {"edit_rg": rg_data, "user": is_login["u"], "userid": is_login["i"], "role": is_login["r"]}
            return render(request, 'account/resourcegroups_new.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')
