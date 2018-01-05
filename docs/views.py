# -*- coding: utf-8 -*-
# wangqiushi(wang.qiushi@yottabyte.cn)
# 2015/08/19
# Copyright 2015 Yottabyte
# file description : views.py.
__author__ = 'wangqiushi'
from django.shortcuts import render
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
from django.http import HttpResponseRedirect


def docs(request, page, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)
    if is_login:
        return render(request, 'docs/docs.html', {"user": is_login["u"], "email": is_login["e"],
                                                     "userid": is_login["i"],"role": is_login["r"],
                                                     "target": "docs/html/"+page+".html"
                                                    })
    else:
        return HttpResponseRedirect('/auth/login/')
