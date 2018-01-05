# -*- coding: utf-8 -*-
# wangqiushi (wang.qiushi@yottabyte.cn)
# 2014/11/11
# Copyright 2014 Yottabyte
# file description : resources.py

from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
import time
import urllib
import smtplib, sys
import ConfigParser
import os
from email.mime.text import MIMEText
__author__ = 'wangqiushi'
err_data = ContributeErrorData()

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    send_address = cf.get('email', 'send')
    to_address = cf.get('email', 'to')
    pwd = cf.get('email', 'passwd')
    smtp_port = cf.get('email', 'smtp_port')
    smtp_server = cf.get('email', 'smtp_server')
except Exception, e:
    print e
    send_address = 'feedback@rizhiyi.com'
    to_address = 'contact@rizhiyi.com'


class FeedbackResource(Resource):
    class Meta:
        resource_name = 'feedback'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/$" % self._meta.resource_name,
                self.wrap_view('feedback_new'), name="api_feedback"),
            ]

    def feedback_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        req_data = request.POST
        feedback_type = req_data.get('type', '')
        feedback_content = req_data.get('content', '')
        feedback_referrer = req_data.get('ref', '')

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            user_info_res = BackendRequest.get_account({
                "id": es_check['i'],
                'token': es_check['t'],
                'operator': es_check['u']
            })
            account = {
                "username": "",
                "fullname": "",
                "email": ""
            }
            if user_info_res["result"]:
                one_account = user_info_res.get('accounts', [])[0]
                account['username'] = one_account['name']
                account['fullname'] = one_account['full_name']
                account['email'] = one_account['email']

            ua = request.META.get('HTTP_USER_AGENT')

            email = "问题描述："+ feedback_content + "</br></br>" + "-----------------------------------------</br>" + "useragent: " + \
                ua + "</br>" + "url:" + feedback_referrer + "</br>" + "</br>-----------------------------------------</br>" + "用户名:" + \
                    account['username'] +"</br>姓名:" + account["fullname"] + "</br>邮件:" + \
                account['email']
            res = self.send_mail(feedback_type, email)
            if res:
                dummy_data["status"] = "1"
            else:
                dummy_data = err_data.build_error({})
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    @staticmethod
    def send_mail(sub, content):
        mail_to_list = [to_address]
        mail_host = smtp_server
        mail_user = send_address
        mail_pass = pwd
        '''''
            to_list:发给谁
            sub:主题
            content:内容
            send_mail("sub","content")
            '''
        me = mail_user + "<" + mail_user + ">"
        msg = MIMEText(content, _subtype='html', _charset='gb2312')  # 创建一个实例，这里设置为html格式邮件
        msg['Subject'] = sub
        msg['From'] = me
        msg['To'] = ";".join(mail_to_list)
        try:
            s = smtplib.SMTP_SSL(mail_host, smtp_port)
            # s.connect(mail_host)
            s.login(mail_user, mail_pass)
            s.sendmail(me, mail_to_list, msg.as_string())
            s.close()
            return True
        except Exception, e:
            print str(e)
            return False
