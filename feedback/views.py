# wangqiushi (wang.qiushi@yottabyte.cn)
# 2014/11/11
# Copyright 2014 Yottabyte
# file description : views.py.

__author__ = 'wangqiushi'
from django.shortcuts import render
from yottaweb.apps.basic.resources import MyBasicAuthentication
from django.http import HttpResponseRedirect


def feedback(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    referrer = request.META.get('HTTP_REFERER')
    ref = referrer
    if is_login:
        return render(request, 'feedback/feedback.html', {"user": is_login["u"], "email": is_login["e"],
                                                             "role": is_login["r"], "userid": is_login["i"],
                                                             "ref": ref})
    else:
        return HttpResponseRedirect('/auth/login/')
