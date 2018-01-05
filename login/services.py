# -*- coding: utf-8 -*-
# wu.ranbo@yottabyte.cn
# 2015-12-16
# Copyright 2015 Yottabyte
# filename: yottaweb/apps/login/services.py
# file description: 将业务逻辑从controller到service方便复用
__author__ = 'wu.ranbo'

import re
import time
import hashlib

from yottaweb.apps.backend.resources import BackendRequest

def login_with_password(domain, username, password, init_page):
    password = hashlib.md5(password).hexdigest()
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
    session_data = {}
    if es_check:
        # print user['username']
        # request.session['user_id'] = hashlib.md5(user['id']).hexdigest()
        token = req.get('token', "")
        dummy_data = {
            'status': '1',
            'location': '/' + init_page,
            'ri': req.get('report_info', {})
        }
        to_log = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "action": "login",
            "user_name": username,
            "user_id": req.get('owner_id', ""),
            "domain": domain,
            "result": "success"
        }

        cookie_string = hashlib.md5(
            username + ',' + domain + ',' + token).hexdigest()
        session_data['user_yottac'] = cookie_string
        session_data['user_name'] = username
        session_data['user_pwd'] = password
        session_data['user_tkn'] = token
        session_data['user_id'] = req.get('owner_id', "")
    else:
        # 0: server error, 1:password or user wrong
        to_log = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "action": "login",
            "user_name": username,
            "user_id": req.get('owner_id', ""),
            "domain": domain,
            "result": "error",
            "msg": req['error']
        }
        err_code = "1" if req['error'] == "non existed user" else "0"
        if req['error'] == 'passwd is invalid':
            err_code = "2"
        if re.search('not activate', req['error'], re.IGNORECASE):
            err_code = "3"
        if re.search('non existed domain', req['error'], re.IGNORECASE):
            err_code = "4"
        dummy_data = {
            'status': '0',
            'err_code': err_code,
            'ri': req.get('report_info', {}),
            'msg': 'username or password is not right',
        }

    return dummy_data, session_data, to_log
