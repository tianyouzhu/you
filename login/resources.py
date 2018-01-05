# wangqiushi (wang.qiushi@yottabyte.cn)
# 2014/11/27
# Copyright 2014 Yottabyte
# file description : resources.py
from tastypie import fields
from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
from urlparse import urlparse
import hashlib
import base64
import ConfigParser
import time
import os
import re
import logging
import json
__author__ = 'wangqiushi'
err_data = ContributeErrorData()

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    from_url = cf.get('from', 'from_url')
except Exception, e:
    print e
    from_url = ".rizhiyi.com"

try:
    if not cf:
        cf = ConfigParser.ConfigParser()
        real_path = os.getcwd() + '/config'
        cf.read(real_path + "/yottaweb.ini")
    init_page = cf.get('custom', 'login_page')
except Exception, e:
    init_page = ""

SECRET = "d18ndf98q@09&78d234lPI8991fas4"


class LoginResource(Resource):

    class Meta:
        resource_name = 'login'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^auth/login$",
                self.wrap_view('auth_login'), name="api_auth_login"),
            url(r"^auth/reset$",
                self.wrap_view('auth_reset'), name="api_auth_reset"),
            url(r"^auth/password/update$",
                self.wrap_view('auth_password_update'), name="api_auth_reset"),
        ]

    def auth_login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        username = request.POST['username']
        password = request.POST['password']
        password = hashlib.md5(password).hexdigest()
        referer = request.META.get('HTTP_REFERER')
        host = urlparse(referer).netloc
        domain = host.split('.')[0]
        audit_logger = logging.getLogger("yottaweb.audit")
        param = {
            "domain": domain,
            "name": username,
            "passwd": password
        }
        # print password

        # user info for yottaD
        req = BackendRequest.login(param)
        es_check = req['result']
        token = ""
        if es_check:
            # print user['username']
            # request.session['user_id'] = hashlib.md5(user['id']).hexdigest()
            token = req.get('token', "")
            request.session['user_name'] = username
            request.session['user_pwd'] = password
            request.session['user_tkn'] = token
            request.session['user_id'] = req.get('owner_id', "")

            link = ""
            res = BackendRequest.list_urls({
                "token": token,
                "operator": username
            })
            if res['result']:
                for u in ["dashboard/", "search/", "alerts/", "schedule/", "app/"]:
                    if u in res['urls']:
                        if u == "dashboard/":
                            link = u
                            break
                        elif u == "search/":
                            link = u
                            break
                        elif u == "alerts/":
                            link = u
                            break
                        elif u == "schedule/":
                            link = u
                            break
                        elif u == "app/":
                            link = u
                            break
            if link == "":
                init_page = "account/users/" + str(req.get('owner_id')) + "/"
            else:
                init_page = link
            dummy_data = {
                'status': '1',
                'location': '/' + init_page,
                'ri': req.get('report_info', {})
            }
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "login",
                "module": "login",
                "user_name": username,
                "user_id": req.get('owner_id', ""),
                "domain": domain,
                "result": "success"
            }
            bundle = self.build_bundle(
                obj=dummy_data, data=dummy_data, request=request)
            res_data = bundle
        else:
            #0: server error, 1:password or user wrong
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "login",
                "module": "login",
                "user_name": username,
                "user_id": req.get('owner_id', ""),
                "domain": domain,
                "result": "error",
                "msg": req['error']
            }
            data = err_data.build_error(req)
            data["ri"] = req.get('report_info', {}),
            dummy_data = data

            bundle = self.build_bundle(
                obj=dummy_data, data=dummy_data, request=request)
            res_data = bundle

        audit_logger.info(json.dumps(to_log))

        resp = self.create_response(request, res_data)
        if es_check:
            cookie_string = hashlib.md5(
                username + ',' + domain + ',' + token).hexdigest()
            request.session['user_yottac'] = cookie_string
            request.session.set_expiry(259200)

        # resp.set_cookie('yottac', value=cookie_string, max_age=None, expires=None, path='/', domain='.rizhiyi.com',
        #                     secure=None, httponly=True)
        return resp

    def auth_password_update(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        username = request.POST['username']
        password = request.POST['password']
        repassword = request.POST['repassword']
        email = request.POST['email']
        domain = request.POST['domain']

        if password != repassword:
            dummy_data = err_data.build_error({}, 'password is not equal!', '101')

            bundle = self.build_bundle(
                obj=dummy_data, data=dummy_data, request=request)
            res_data = bundle
            resp = self.create_response(request, res_data)
            return resp

        referer = request.META.get('HTTP_REFERER')
        host = urlparse(referer).netloc
        this_domain = host.split('.')[0]
        if this_domain != domain:
            dummy_data = err_data.build_error({}, 'domain is not equal!', '102')
            bundle = self.build_bundle(
                obj=dummy_data, data=dummy_data, request=request)
            res_data = bundle
            resp = self.create_response(request, res_data)
            return resp

        password = hashlib.md5(password).hexdigest()
        param = {
            "domain": domain,
            "name": username,
            "email": email,
            "passwd": password
        }
        # print password

        # user info for yottaD
        req = BackendRequest.reset_passwd(param)
        es_check = req['result']
        token = ""
        if es_check:
            dummy_data = {
                'status': '1'
            }

            bundle = self.build_bundle(
                obj=dummy_data, data=dummy_data, request=request)
            res_data = bundle
        else:
            #0: server error, 1:password or user wrong
            dummy_data = err_data.build_error(req)

            bundle = self.build_bundle(
                obj=dummy_data, data=dummy_data, request=request)
            res_data = bundle

        resp = self.create_response(request, res_data)
        return resp

    def auth_reset(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        username = request.POST['username']
        email = request.POST['email']
        referrer = request.META.get('HTTP_REFERER')
        host = urlparse(referrer).netloc
        domain = host.split('.')[0]
        param = {
            "domain": domain,
            "name": username,
            "email": email
        }
        for_base64 = base64.b64encode(param['domain'] + "|||" + param['name'] +
                                      "|||" + param['email'] + "|||" + str(time.time()))

        for_md5 = hashlib.md5(for_base64 + SECRET).hexdigest()
        email_address = "https://"+param['domain'] + from_url + "/auth/password/" + for_md5 + "/" + for_base64 + "/"
        req = BackendRequest.send_reset_passwd_email(param, email_address)
        es_check = req['result']
        # es_check = False
        if es_check:
            dummy_data = {
                'status': '1'
            }

            bundle = self.build_bundle(
                obj=dummy_data, data=dummy_data, request=request)
            res_data = bundle
        else:
            dummy_data = err_data.build_error(req)

            bundle = self.build_bundle(
                obj=dummy_data, data=dummy_data, request=request)
            res_data = bundle

        resp = self.create_response(request, res_data)
        return resp

    def auto_login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        username = request.POST['username']
        password = request.POST['password']
        password = hashlib.md5(password).hexdigest()

        # print password

        # user info for yottaD
        user = {'id': 'uid_001', 'username': 'u', 'password': '83878c91171338902e0fe0fb97a8c47a', }

        if user['username'] == username and user['password'] == password:
            # print user['username']
            request.session['user_id'] = hashlib.md5(user['id']).hexdigest()
            dumyData = {
                'status': '1',
                'location': '/dashboard',
            }

            bundle = self.build_bundle(
                obj=dumyData, data=dumyData, request=request)
            resData = bundle
            resp = self.create_response(request, resData)
            return resp
        else:
            dumyData = {
                'status': '0',
                'err_code': '1',
                'msg': 'username or password is not right',
            }

            bundle = self.build_bundle(
                obj=dumyData, data=dumyData, request=request)
            resData = bundle
            resp = self.create_response(request, resData)
            return resp

    @staticmethod
    def __check_param(self, param, request):
        """
        This method checks the parameter to find out whether the password is equal to repassword and
        the required field is full-filled.
        :param self:
        :param request:
        :return: 1.has_error:whether the parameter has error. 2.msg:error message. 3.error_code: the code of error
        """
        res = {
            "has_error": False,
            "msg": "",
            "error_code": "0"
        }
        # post_dict = dict(request.POST._iteritems())

        if param["repasswd"] != param["passwd"]:
            res["msg"] = "password not equal to repassword"
            res["err_code"] = "1"
            res["has_error"] = True
            return res
        has_error = False
        for k, v in param.iteritems():
            if v == "" and k != "company":
                has_error = True
                break
        if has_error:
            res["msg"] = "parameter required error"
            res["err_code"] = "2"
            res["has_error"] = True
            return res
        else:
            res["msg"] = ""
            res["err_code"] = "1"
            res["has_error"] = False
            return res


