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
from django import template
from django.utils.safestring import mark_safe
import ConfigParser
import os
import json

register = template.Library()

@register.filter
def jsonify(list):
    return mark_safe(json.dumps(list))

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    service_ports = dict(cf.items('service_ports'))
except Exception, e:
    print e
    service_ports = {}



def list(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        with_sg = check_with_sourcegroup(is_login)
        cf_per = check_with_permission(is_login)
        return render(request, 'agent/list.html',
                      {"active": "source", "subnav": "agent", "user": is_login["u"], "email": is_login["e"],
                       "token": is_login["t"], "userid": is_login["i"],
                       "role": is_login["r"], "with_sg": with_sg,
                       "cf_per": cf_per, "rgid": request.GET.get("rgid", "")})
    else:
        return HttpResponseRedirect('/auth/login/')

def config(request, ip_port, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        with_sg = check_with_sourcegroup(is_login)
        cf_per = check_with_permission(is_login)
        os = request.GET.get('os', "linux")
        version = request.GET.get('version', '')
        platform = request.GET.get('platform', 'linux')
        proxy = request.GET.get('proxy', '')
        page_data = {"active": "source", "subnav": "agent", "user": is_login["u"], "email": is_login["e"],
                     "token": is_login["t"], "userid": is_login["i"],
                     "role": is_login["r"], "with_sg": with_sg, 'proxy': proxy,
                     "cf_per": cf_per, "ip_port": ip_port, "os": os, "version": version, "platform": platform}
        return render(request, 'agent/config.html', {"page_data": json.dumps(page_data)})
    else:
        return HttpResponseRedirect('/auth/login/')

def batch_update_config(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        with_sg = check_with_sourcegroup(is_login)
        cf_per = check_with_permission(is_login)
        return render(request, 'agent/batch_update_config.html',
                      {"active": "source", "subnav": "agent", "user": is_login["u"], "email": is_login["e"],
                       "token": is_login["t"], "userid": is_login["i"],
                       "role": is_login["r"], "with_sg": with_sg,
                       "cf_per": cf_per})
    else:
        return HttpResponseRedirect('/auth/login/')

def agent_add_data(request, ip_port, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)


    if is_login:
        arr = ip_port.split(":")
        if (len(arr) == 2):
            ip = arr[0]
        else:
            ip = ""
        param = {
            # "token": is_login["t"],
            "size": 50,
            "start": 0,
            "orderby": "ip",
            "ip": ip,
            "isfuzzy": False,
            'token': is_login['t'],
            'operator': is_login['u']
        }

        # print "#################param: ", param
        res = BackendRequest.get_agent_status(param)

        agents = res.get('agent_status')
        for agent in agents:
            if agent.get("ip") in ip_port:
                os = agent.get("os")

                proxy_ip =  agent.get("proxy_ip", '')
                proxy_port = str(agent.get('proxy_port', ''))

                if (proxy_ip != '') and (proxy_port != ''):
                    proxy = proxy_ip + ":" + proxy_port
                else:
                    proxy = ""

                version = agent.get("cur_version")
                platform = agent.get("platform")
                break
            else:
                os = ""
                proxy = ""
                version = ""
                platform = ""


        with_sg = check_with_sourcegroup(is_login)
        cf_per = check_with_permission(is_login)
        page_data = {"active": "source", "subnav": "agent", "user": is_login["u"], "email": is_login["e"],
                     "token": is_login["t"], "userid": is_login["i"],
                     "role": is_login["r"], "with_sg": with_sg, "proxy": proxy,
                     "cf_per": cf_per,"ip_port":ip_port, "os": os, "version": version, "platform": platform}
        return render(request, 'agent/adddata.html',
                      {"page_data": json.dumps(page_data), "proxy": proxy,
                       "ip_port":ip_port, "os": os, "version": version, "platform": platform})
    else:
        return HttpResponseRedirect('/auth/login/')

def serverheka_add_data(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)

    if is_login:
        with_sg = check_with_sourcegroup(is_login)
        cf_per = check_with_permission(is_login)
        return render(request, 'agent/serverheka_adddata.html',
                  {"active": "source", "subnav": "agent", "user": is_login["u"], "email": is_login["e"],
                   "token": is_login["t"], "userid": is_login["i"],
                   "role": is_login["r"], "with_sg": with_sg,
                   "cf_per": cf_per, "service_ports": jsonify(service_ports)})
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

def agent_steps(request, name, **kwargs):
    return render(request, 'agent/steps/'+name+'.html')


