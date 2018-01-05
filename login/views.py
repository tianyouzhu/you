__author__ = 'wangqiushi; yangguang'
from django.shortcuts import render
from django.http import HttpResponseRedirect
from yottaweb.apps.basic.resources import MyBasicAuthentication
from urlparse import urlparse
import ConfigParser
import os
import hashlib
import base64
import time
import logging
import json

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    from_url = cf.get('from', 'from_url')
except Exception, e:
    print e
    from_url = ".rizhiyi.com"
SECRET = "d18ndf98q@09&78d234lPI8991fas4"


def auth_password(request, **kwargs):
    for_md5 = kwargs.get('for_md5', "")
    for_base64 = kwargs.get('for_base64', "")
    if for_md5 and for_base64:
        new_md5 = hashlib.md5(for_base64 + SECRET).hexdigest()
        if new_md5 == for_md5:
            info = {
                "username": "",
                "domain": "",
                "email": ""
            }
            ex_base64 = base64.b64decode(for_base64)
            ex_arr = ex_base64.split("|||")
            old_time = float(ex_arr[3])
            now = time.time()
            if now-old_time < 7200:
                info["domain"] = ex_arr[0]
                info["username"] = ex_arr[1]
                info["email"] = ex_arr[2]
                return render(request, 'auth/passwordUpdate.html', {"info": info})
            else:
                return render(request, 'auth/accessError.html', {"type": "timeout"})
        else:
            return render(request, 'auth/accessError.html', {"type": "param"})
    else:
        return render(request, 'auth/accessError.html', {"type": "param"})


def auth_reset(request):
    return render(request, 'auth/passwordReset.html', {})


def login(request):
    host = request.META.get('HTTP_HOST')
    if "." + host == from_url:
        return render(request, 'auth/subDomain.html', {"from_url": from_url})
    else:
        page_data = {}
        return render(request, 'login/login.html', {"page_data": json.dumps(page_data)})


def logout(request, **kwargs):
    # auth.logout(request)
    # print "#############request ",request

    url_scheme = request.META.get('wsgi.url_scheme')
    port = request.META.get('SERVER_PORT')
    referer = request.META.get('HTTP_REFERER')
    host = urlparse(referer).netloc
    domain = host.split('.')[0]
    my_auth = MyBasicAuthentication()
    es_check = my_auth.is_authenticated(request, **kwargs)

    logger = logging.getLogger("yottaweb.audit")

    to_log = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "action": "logout",
        "user_name": es_check["u"],
        "user_id": es_check["u"],
        "domain": es_check['d']
    }
    logger.info(json.dumps(to_log))

    url = url_scheme + "://" + domain + from_url + "/auth/login/"
    if int(port) != 80:
        url = url_scheme + "://" + domain + from_url + ":" + port  + "/auth/login/"
    if es_check:
        del request.session['user_name']
        del request.session['user_pwd']
        del request.session['user_tkn']
        del request.session['user_yottac']
        return HttpResponseRedirect('/auth/login/')
    else:
        return HttpResponseRedirect(url)

