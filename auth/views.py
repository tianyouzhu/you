__author__ = 'wangqiushi; yangguang'
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.partner.resources import ThirdPartnerAuth
from yottaweb.apps.backend.resources import BackendRequest
from urlparse import urlparse
import ConfigParser
import os
import hashlib
import base64
import time

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    from_url = cf.get('from', 'from_url')
except Exception, e:
    print e
    from_url = ".rizhiyi.com"
SECRET = "d18ndf98q@09&78d234lPI8991fas4"


@csrf_exempt
def auth_register(request):
    # get es url from yottaweb.ini
    post_data = request.POST
    signed_request = post_data.get('AccessToken', '')
    if signed_request:
        auth = ThirdPartnerAuth.auth(signed_request)
        if auth:
            info = {
                'fullname': auth.get('UserName', '').encode('utf-8'),
                'username': auth.get('UserEmail', '').encode('utf-8'),
                'company': auth.get('CompanyName', '').encode('utf-8'),
                'phone': auth.get('UserPhone', '').encode('utf-8'),
                'from': from_url
            }
            return render(request, 'auth/register.html', {'info': info, 'url': '/api/v0/auth/register'}, context_instance=RequestContext(request))
        else:
            info = {
                'from': from_url
            }
            return render(request, 'auth/register_own.html', {'info': info, 'url': '/api/v0/auth/director'}, context_instance=RequestContext(request))
    else:
        info = {
            'from': from_url
        }
        return render(request, 'auth/register_own.html', {'info': info, 'url': '/api/v0/auth/director'}, context_instance=RequestContext(request))


def auth_register_agree(request):
    return render(request, 'auth/agreement.html', {})


def auth_register_info(request, **kwargs):
    for_md5 = kwargs.get('for_md5', "")
    for_base64 = kwargs.get('for_base64', "")
    if for_md5 and for_base64:
        new_md5 = hashlib.md5(for_base64 + SECRET).hexdigest()
        if new_md5 == for_md5:
            ex_base64 = base64.b64decode(for_base64)
            ex_arr = ex_base64.split("|||")
            email = ex_arr[0]
            domain = ex_arr[1]
            host = request.META.get('HTTP_HOST')
            cur_domain = host.split('.')[0]
            if not cur_domain == domain:
                return render(request, 'auth/register_info.html', {"type": "param"})
            else:
                return render(request, 'auth/register_info.html', {'email': email, "type": "success"})
        else:
            return render(request, 'auth/register_info.html', {"type": "param"})
    else:
        return render(request, 'auth/register_info.html', {"type": "param"})


def auth_register_active(request, **kwargs):
    for_md5 = kwargs.get('for_md5', "")
    for_base64 = kwargs.get('for_base64', "")
    if for_md5 and for_base64:
        new_md5 = hashlib.md5(for_base64 + SECRET).hexdigest()
        if new_md5 == for_md5:
            ex_base64 = base64.b64decode(for_base64)
            ex_arr = ex_base64.split("|||")
            email = ex_arr[0]
            domain = ex_arr[1]
            host = request.META.get('HTTP_HOST')
            cur_domain = host.split('.')[0]
            if not cur_domain == domain:
                return render(request, 'auth/register_info.html', {"type": "param"})
            else:
                res_active = BackendRequest.activate_domain({
                    'activate_key': for_md5,
                    'domain':domain
                })
                if res_active['result']:
                    return render(request, 'auth/register_info.html', {'domain': domain, "type": "active"})
                elif res_active['error_code'] == 34:
                    return render(request, 'auth/register_info.html', {'domain': domain, "type": "allreadyActive"})
                else:
                    return render(request, 'auth/register_info.html', {'domain': domain, "type": "unactive"})
        else:
            return render(request, 'auth/register_info.html', {"type": "param"})
    else:
        return render(request, 'auth/register_info.html', {"type": "param"})

