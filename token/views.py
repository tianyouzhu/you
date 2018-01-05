__author__ = 'wangqiushi; yangguang'
from django.shortcuts import render
from django.shortcuts import render
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
from django.http import HttpResponseRedirect


def tokens(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
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
        return render(request, 'token/tokens.html', {"active": "source", "subnav":"tokens","user": is_login["u"],
                                                        "email": is_login["e"],"cf_per": config_permission,
                                                        "role": is_login["r"], "userid": is_login["i"],
                                                        "with_sg": with_sg
                                                        })
    else:
        return HttpResponseRedirect('/auth/login/')


