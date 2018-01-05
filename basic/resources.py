# wangqiushi (wang.qiushi@yottabyte.cn)
# 2014/12/26
# Copyright 2014 Yottabyte
# file description : resources.py
__author__ = 'wangqiushi'
from django.contrib.sessions.models import Session
from django.conf import settings
from tastypie.authentication import BasicAuthentication
from yottaweb.settings.base import ES_URL
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.variable.resources import MyVariable
from urlparse import urlparse
import hashlib
import requests
import urllib
import json
import logging
import ConfigParser
import os
import base64
# get es url from yottaweb.ini
cf = ConfigParser.ConfigParser()
conf_file = os.getcwd() + '/config/yottaweb.ini'
try:
    cf.read(conf_file)
    es_url = cf.get('frontend', 'frontend_url')
except Exception, e:
    print e
    es_url = ES_URL

try:
    cf.read(conf_file)
    additional_params = cf.items('additional_params')
except Exception, e:
    print e
    additional_params = []

URL = es_url
log = logging.getLogger('django.request')

local_language = MyVariable().get_var('i18n', 'local') if MyVariable().get_var('i18n', 'local') else "zhCN"

try:
    local = "".join(local_language.split("_"))
    local = local[0:2]+'_'+local[2:4]
    path = os.path.dirname(os.path.realpath(__file__))
    real_path = path + "/../../static/i18n/" + local.lower() + ".json"
    with open(real_path, 'r') as content_file:
        content = content_file.read()
    # content = content.split(";")[0].split("=")[1]
    obj = json.loads(content)
    error_code_obj = obj['ERRORCODE']
    error_code_spl_obj = obj['SPLERRORCODE']
except Exception, e:
    print e
    error_code_obj = {}
    error_code_spl_obj = {}

class MyBasicAuthentication(BasicAuthentication):

    def is_authenticated(self, request, **kwargs):
        if settings.SESSION_COOKIE_NAME not in request.COOKIES:
            print "is_authenticated:cookie session not has"
            return False
        se_id = request.COOKIES[settings.SESSION_COOKIE_NAME]
        try:
            s = Session.objects.get(pk=se_id)
        except Exception, e:
            print "is_authenticated: session.objects.get failed"
            print e
            return False
        if 'user_name' not in s.get_decoded():
            print "is_authenticated: user_name not in session.get_decoded"
            return False
        if 'user_name' in s.get_decoded():
            try:
                u = s.get_decoded()['user_name']
                t = s.get_decoded()['user_tkn']
                i = s.get_decoded()['user_id']
            except Exception, e:
                print e
                print "is_authenticated: session.getdecode,user_name, tkn, id failed"
                return False

            domain = self.get_sub_domain_referrer(request)
            if not domain:
                print "is_authenticated: no domain"
                return False

            # print "auth:", u, t, domain
            if 'user_yottac' in s.get_decoded():
                apk = s.get_decoded()['user_yottac']
                if hashlib.md5(u + "," + domain + "," + t).hexdigest() != apk:
                    print "is_authenticated: md5 user_yottac not fit"
                    return False
            else:
                return False
            p = s.get_decoded()['user_pwd']
            param = {
                "domain": domain,
                "name": u,
                "passwd": p,
                "token": t
            }
            req = BackendRequest()
            res = req.login(param)
            if res["result"]:
                return {'e': '', 'u': u, 'p': p, 't': t, 'i': i, 'r': res.get('role', 'user'),
                        "ri": res.get("report_info", {}), 'd': domain}
            else:
                print "is_authenticated: backendrequest.login faield."
                return False
        print "is_authenticated: nothing so false"
        return False

    def get_sub_domain_host(self, request):
        host = request.META.get('HTTP_HOST')
        # print(request)
        # host = urlparse(referer).netloc
        try:
            domain = host.split('.')[0]
        except Exception, e:
            log.error('domain_error: %s', e)
            domain = ''
        return domain

    def get_sub_domain_referrer(self, request):
        referrer = request.META.get('HTTP_REFERER')
        try:
            host = urlparse(referrer).netloc
            domain = host.split('.')[0]
        except Exception, e:
            log.error('referrer_error: %s', e)
            domain = ''
        return domain

    # Optional but recommended
    def get_identifier(self, request):
        return request.user.username


class ContributeErrorData():

    def build_error(self, res, msg="server error", error_type='100'):
        error_code = res.get("error_code", -1)
        if res.get("error") == "operator permission denied":
            msg = "operator permission denied"
        if error_code >= 500:
            msg = res["error"]
            data = {
                "status": 0,
                "error_type": "001",
                "msg": error_code_obj.get(str(error_code), msg)
            }
        elif error_code >= 0:
            data = {
                "status": 0,
                "error_type": "010",
                "msg": msg
            }
        else:
            data = {
                "status": 0,
                "error_type": error_type,
                "msg": msg
            }

        return data

    def build_error_new(self, error_code='1', param={}, msg="", origin="normal"):
        _msg = error_code_obj.get(str(error_code), msg) if origin == "normal" else error_code_spl_obj.get(str(error_code), msg);
        _data = {
            "status": "0",
            "msg": _msg,
            "error_code": str(error_code)
        }
        data_merged = dict(_data, **param)
        return data_merged
