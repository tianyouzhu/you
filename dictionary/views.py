__author__ = 'wangqiushi; yangguang'
from django.shortcuts import render
from django.shortcuts import render
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied

import json

def lists(request, **kwargs):
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
            config_permission = "no"
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

            func_auth_res = BackendRequest.get_func_auth({
                'token': is_login['t']
            })
            if func_auth_res['result']:
                if func_auth_res["results"]["parser_conf"]:
                    config_permission = "yes"
            page_data = {"active": "dictionary", "subnav":"dictionary", "user": is_login["u"], 
                        "email": is_login["e"], "cf_per": config_permission, "role": is_login["r"], 
                        "userid": is_login["i"], "with_sg": with_sg, "rgid": request.GET.get('rgid', "")}
            return render(request, 'dictionary/list.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


