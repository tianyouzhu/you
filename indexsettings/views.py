__author__ = 'daibin'
from django.shortcuts import render
from django.shortcuts import render_to_response
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
from django.http import HttpResponseRedirect

import json

from django.core.exceptions import PermissionDenied

def indexinfo(request, **kwargs):
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
            page_data = {"active": "indexsettings", "subnav":"indexsettings", "user": is_login["u"], "email": is_login["e"],
                        "role": is_login["r"], "userid": is_login["i"], "rgid": request.GET.get('rgid', ""), "cf_per": cf_per}
            return render(request, 'indexsettings/indexinfo.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def create_index_info(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:

            index_info = {
                'id': '',
                'name': '',
                'description': '',
                'domain_id': '',
                'expired_time': '',
                'expired_time_unit': 'd',
                'rotation_period': '',
                'rotation_period_unit': 'd',
                'disabled': 'false',
                'act': 'new'
            }
            cf_per = check_with_permission(is_login)
            page_data = {'index_info': index_info, "active": "indexsettings",
                        "user": is_login["u"],"email": is_login["e"],
                        "role": is_login["r"], "userid": is_login["i"],
                        "rgid": request.GET.get('rgid', ""), "cf_per": cf_per
                        }
            return render(request, 'indexsettings/indexinfonew.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def update_index_info(request, offset, **kwargs):
    indexInfo_id = offset.encode('utf-8')

    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            index_info_res = BackendRequest.get_index_info({
                'id': indexInfo_id,
                'token': is_login['t'],
                'operator': is_login['u']
            })
            if index_info_res['result']:
                a_index_info = index_info_res['index_info']
                index_info = {
                    'id': indexInfo_id,
                    'name': a_index_info['name'].encode('utf-8'),
                    'description': a_index_info['description'].encode('utf-8'),
                    'domain_id': a_index_info['domain_id'],
                    'disabled': 'true' if a_index_info['disabled'] else 'false',
                    'act': 'update'
                }
                expired_time = a_index_info['expired_time'].encode('utf-8')
                index_info['expired_time'] = expired_time[0:-1]
                index_info['expired_time_unit'] = expired_time[-1]
                rotation_period = a_index_info['rotation_period'].encode('utf-8')
                index_info['rotation_period'] = rotation_period[0:-1]
                index_info['rotation_period_unit'] = rotation_period[-1]
            cf_per = check_with_permission(is_login)
            page_data = {'index_info': index_info, "active": "indexsettings",
                        "user": is_login["u"],"email": is_login["e"],
                        "role": is_login["r"], "userid": is_login["i"],
                        "rgid": request.GET.get('rgid', ""), "cf_per": cf_per
                        }
            return render(request, 'indexsettings/indexinfoupdate.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def indexmatchrule(request, **kwargs):
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
            page_data = {"active": "indexsettings", "subnav":"indexsettings",
                        "user": is_login["u"], "email": is_login["e"],
                        "role": is_login["r"], "userid": is_login["i"],
                        "rgid": request.GET.get('rgid', ""), "cf_per": cf_per
                        }
            return render(request, 'indexsettings/indexmatchrule.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def create_index_match_rule(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            index_match_rule = {
                'index_id': '',
                'appname': '',
                'tag': '',
                'description': '',
                'raw_message_regex': ''
            }
            cf_per = check_with_permission(is_login)
            page_data = {'index_match_rule': index_match_rule, "active": "indexsettings",
                        "user": is_login["u"], "email": is_login["e"],
                        "role": is_login["r"], "userid": is_login["i"],
                        "rgid": request.GET.get('rgid', ""), "cf_per": cf_per
                        }
            return render(request, 'indexsettings/indexmatchrulenew.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def update_index_match_rule(request, offset, **kwargs):
    indexMatchRule_id = offset.encode('utf-8')

    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        visit_permit = BackendRequest.can_visit({
            "token": is_login['t'],
            "operator": is_login['u'],
            "requestUrl": request.path[1:]
        })
        if visit_permit['result'] and visit_permit['can_visit']:
            index_match_rule_res = BackendRequest.get_index_match_rule({
                'id': indexMatchRule_id,
                'token': is_login['t'],
                'operator': is_login['u']
            })
            if index_match_rule_res['result']:
                a_index_match_rule = index_match_rule_res['rule']
                index_id = a_index_match_rule['index_id'],
                index_info = BackendRequest.get_index_info({
                    'id': index_id,
                    'token': is_login['t'],
                    'operator': is_login['u']
                })
                index_name = ''
                if index_info['result']:
                    index_name = index_info['index_info']['name'].encode('utf-8')
                index_match_rule = {
                    'id': indexMatchRule_id,
                    'index_id': a_index_match_rule['index_id'],
                    'index_name': index_name,
                    'appname': a_index_match_rule['appname'].encode('utf-8'),
                    'description': a_index_match_rule['description'].encode('utf-8'),
                    'tag': a_index_match_rule['tag'].encode('utf-8'),
                    'raw_message_regex': a_index_match_rule['raw_message_regex'].encode('utf-8')
                }
            else:
                index_match_rule = {
                    'id': indexMatchRule_id,
                    'index_id': '',
                    'index_name': '',
                    'appname': '',
                    'description': '',
                    'tag': '',
                    'raw_message_regex': ''
                }
            cf_per = check_with_permission(is_login)
            page_data = {'index_match_rule': index_match_rule, "active": "indexsettings",
                        "user": is_login["u"], "email": is_login["e"],
                        "role": is_login["r"], "userid": is_login["i"],
                        "rgid": request.GET.get('rgid', ""), "cf_per": cf_per
                        }
            return render(request, 'indexsettings/indexmatchruleupdate.html', {"page_data": json.dumps(page_data)})
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
