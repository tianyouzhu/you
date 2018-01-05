# wangqiushi (wang.qiushi@yottabyte.cn) mayangguang (ma.yanguang@yottabyte.cn)
# 2014/07/15
# Copyright 2014 Yottabyte
# file description : resources.py
from tastypie import fields
from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.auth.views import auth_register
import hashlib
import base64
import ConfigParser
import time
import os
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
SECRET = "d18ndf98q@09&78d234lPI8991fas4"


class AuthResource(Resource):
    # Just like a Django ``Form`` or ``Model``, we're defining all the
    # fields we're going to handle with the API here.

    class Meta:
        resource_name = 'auth'
        always_return_data = True
        include_resource_uri = False
        domain_blacklist = ['blog', 'www', 'log', 'test', 'admin', 'official', 'rizhiyi', 'yottabyte',
                            'monitor', 'login', 'auth', 'alert', 'alarm', 'search', 'user', 'panel', 'mail', 'master',
                            'postmaster', 'news', 'dev', 'develop', 'testing', 'report', 'ucloud', 'domain', 'config']

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/register$" % self._meta.resource_name,
                self.wrap_view('auth_register'), name="api_auth_register"),
            url(r"^(?P<resource_name>%s)/director$" % self._meta.resource_name,
                self.wrap_view('auth_director'), name="api_auth_register"),
            url(r"^(?P<resource_name>%s)/register/partner$" % self._meta.resource_name,
                self.wrap_view('auth_register_partner'), name="api_auth_register"),
        ]

    def auth_register(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_dict = request.POST
        param = {
            "token": "system",
            "from": post_dict.get('from', ''),
            "name": post_dict.get('username', ''),
            "full_name": post_dict.get('fullname', ''),
            "company": post_dict.get('company', ''),
            "email": post_dict.get('email', ''),
            "phone": post_dict.get('phone', ''),
            "server": post_dict.get('server', 0),
            "domain": post_dict.get('domain', ''),
            "passwd": post_dict.get('password', ''),
            "repasswd": post_dict.get('repassword', '')
        }
        param_check = self.__check_param(self, param, request)
        param['passwd'] = hashlib.md5(param['passwd']).hexdigest()
        param['repasswd'] = hashlib.md5(param['repasswd']).hexdigest()

        es_check = False
        dummy_data = {}
        token = ""
        if param['domain'] in self._meta.domain_blacklist:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "domain is used"
            dummy_data["err_code"] = "3"
        elif param_check['has_error']:
                dummy_data["status"] = "0"
                dummy_data["msg"] = param_check['msg']
                dummy_data["err_code"] = param_check['err_code']
        else:
            # go to es-fe check user&password
            req = BackendRequest.create_domain(param,'')
            es_check = req['result']
            if es_check:
                token = req.get('token', '')
                request.session['user_name'] = param['name']
                request.session['user_pwd'] = param['passwd']
                request.session['user_tkn'] = token
                dummy_data["status"] = "1"
                dummy_data["location"] = "http://"+param['domain']+param['from']+"/search/"
            else:
                data = err_data.build_error(req)
                dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        if es_check:
            cookie_string = hashlib.md5(param['name'] + ',' + param['domain'] + ',' + token).hexdigest()
            request.session['user_yottac'] = cookie_string
        return resp

    def auth_director(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_dict = request.POST
        param = {
            "token": "system",
            "from": post_dict.get('from', ''),
            "name": post_dict.get('username', ''),
            "full_name": post_dict.get('fullname', ''),
            "company": post_dict.get('company', ''),
            "email": post_dict.get('email', ''),
            "phone": post_dict.get('phone', ''),
            "server": post_dict.get('server', 0),
            "domain": post_dict.get('domain', ''),
            "passwd": post_dict.get('password', ''),
            "repasswd": post_dict.get('repassword', '')
        }
        param_check = self.__check_param(self, param, request)
        param['passwd'] = hashlib.md5(param['passwd']).hexdigest()
        param['repasswd'] = hashlib.md5(param['repasswd']).hexdigest()

        es_check = False
        dummy_data = {}
        token = ""
        if param['domain'] in self._meta.domain_blacklist:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "domain is used"
            dummy_data["err_code"] = "3"
        elif param_check['has_error']:
                dummy_data["status"] = "0"
                dummy_data["msg"] = param_check['msg']
                dummy_data["err_code"] = param_check['err_code']
        else:
            # todo: new interface-- send active email to user when register and return token
            # key: active code
            # url: email url
            user_info_str = base64.b64encode(param['email'] + "|||" + param['domain'] + "|||" +
                                             str(time.time()))
            param['activate_key'] = hashlib.md5(user_info_str + SECRET).hexdigest()
            param['pre_activate'] = 1
            param['send_email'] = 1
            mail_url = "https://" + param['domain'] + from_url + "/auth/register/active/" + param['activate_key'] + "/" + \
                       user_info_str + "/"
            req = BackendRequest.create_domain(param, mail_url)
            es_check = req['result']
            if es_check:
                token = req.get('token', '')
                request.session['user_name'] = param['name']
                request.session['user_pwd'] = param['passwd']
                request.session['user_tkn'] = token
                for_base64 = base64.b64encode(param['email'] + '|||' + param['domain'] + '|||' + token)
                for_md5 = hashlib.md5(for_base64 + SECRET).hexdigest()
                dummy_data["status"] = "1"
                dummy_data["location"] = "https://"+param['domain']+param['from']+"/auth/register_info/"+for_md5+"/"+\
                                         for_base64+"/"
            else:
                data = err_data.build_error(req)
                dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        if es_check:
            cookie_string = hashlib.md5(param['name'] + ',' + param['domain'] + ',' + token).hexdigest()
            request.session['user_yottac'] = cookie_string
        return resp

    def auth_register_partner(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_dict = request.POST
        return auth_register(request)
        #return auth_register

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


