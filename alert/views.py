# wangqiushi (@yottabyte.cn)
# 2014/07/24
# Copyright 2014 Yottabyte
# file description : views.py.
__author__ = 'wangqiushi'

from django.shortcuts import render
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
from django.http import HttpResponseRedirect
import json
import os
import ConfigParser
from django.core.exceptions import PermissionDenied

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    syslog = cf.get('alert', 'syslog')
except Exception, e:
    print e
    syslog = "no"


def alerts(request, **kwargs):
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
            page_data = {"active": "alert", "user": is_login["u"], "email": is_login["e"],
                        "role": is_login["r"], "userid": is_login["i"], "with_sg": with_sg,
                        "rgid": request.GET.get("rgid", "")
                        }
            return render(request, 'alert/alerts.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def records(request, **kwargs):
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
            page_data = {"active": "alert", "user": is_login["u"], "email": is_login["e"],
                        "role": is_login["r"], "userid": is_login["i"], "with_sg": with_sg,
                        "alert_id": request.GET.get("alert_id", "")
                        }
            return render(request, 'alert/records.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')

def alerts_new(request, **kwargs):
    alert = {
        'alert_id': '',
        'saved_searches': [],
        'alert_mails': [],
        'alert_release': '0',
        'level': '1',
        'alert_mail_enable': True,
        'alert_release': '0',
        'includeLatestEvents': True,
        'alert_enable': True
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
            with_sg = check_with_sourcegroup(is_login)
            page_data = {'alert': alert, "active": "alert", "user": is_login["u"],
                        "email": is_login["e"], "with_sg": with_sg, "syslog": syslog,
                        "role": is_login["r"], "userid": is_login["i"]
                        }
            return render(request, 'alert/update.html', {"page_data": json.dumps(page_data)})
        else:
            raise PermissionDenied
    else:
        return HttpResponseRedirect('/auth/login/')


def update(request, offset, **kwargs):
    alert_id = offset.encode('utf-8')

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
            alert_res = BackendRequest.get_alert({
                'id': alert_id,
                'token': is_login['t'],
                'operator': is_login['u']
            })
            # print "###########alert_res: ",alert_res
            if alert_res['result']:
                a_alert = alert_res['alert']
                alert = {
                    'alert_id': alert_id,
                    'alert_name': a_alert['name'].encode('utf-8'),
                    'alert_description': a_alert.get("description", "").encode('utf-8'),
                }
                # for meta in alert['alert_meta']:
                    # meta['alias'] = meta.get('alias','').encode('utf-8')
                    # for config in meta.get('config',[]):
                        # config['alias'] = config.get('alias','').encode('utf-8')
                        # config['default_value'] = config.get('default_value','').encode('utf-8')
                        # config['name'] = config.get('name','').encode('utf-8')
                        # config['value'] = config.get('value','').encode('utf-8')
                # alert['alert_meta'] = json.dumps(alert['alert_meta'])
            else:
                alert = {
                    'alert_id': alert_id,
                    'alert_name': '',
                    'alert_description': '',
                }
            page_data = {'alert': alert, "active": "alert", "user": is_login["u"],
                        "email": is_login["e"], "with_sg": with_sg, "syslog": syslog,
                        "role": is_login["r"], "userid": is_login["i"]
                        }
            return render(request, 'alert/update.html', {"page_data": json.dumps(page_data)})
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
