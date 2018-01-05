# wangqiushi (wang.qiushi@yottabyte.cn)
# 2014/12/26
# Copyright 2014 Yottabyte
# file description : resources.py
__author__ = 'wangqiushi'
from yottaweb.settings.base import ES_URL
import requests
import urllib
import json
import logging
import ConfigParser
import os
import time
import random
import string
# get es url from yottaweb.ini
cf = ConfigParser.ConfigParser()
conf_file = os.getcwd() + '/config/yottaweb.ini'

try:
    cf.read(conf_file)
    get_fe_string = cf.get('frontend', 'frontend_url')
    es_url_string = get_fe_string if get_fe_string else "http://127.0.0.1:8080"
except Exception, e:
    print e
    es_url_string = "http://127.0.0.1:8080"

es_url_list = es_url_string.split(",")
URL = es_url_list[0]


try:
    cf.read(conf_file)
    additional_params = cf.items('additional_params')
except Exception, e:
    print e
    additional_params = []

log = logging.getLogger('django.request')


def switch_frontend(cur):
    idx = es_url_list.index(cur)
    if idx == len(es_url_list)-1:
        return es_url_list[0]
    else:
        return es_url_list[idx+1]



class BackendRequest():
    def __init__(self):
        pass

    #
    @staticmethod
    def _prepare_params(params):
        _tmp_params = {}
        for pair in additional_params:
            _tmp_params[pair[0]] = pair[1]
        return dict(_tmp_params, **params)
        # extra_params = es_additional_params

    # interfaces about domain and token
    @staticmethod
    def create_domain(param, data):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_domain"}, **param)
        try:
            if data:
                p = urllib.urlencode(params)
                url = URL + "?" + p
                body = json.dumps(data)
                res = requests.post(url, data=body, timeout=10.000)
            else:
                # print "create_domain:", params
                res = requests.get(URL, params=params, timeout=3.000)
                log.info("create_domain: %s", res.url)
        except Exception, e:
            log.error("create_domain error: %s", e)
            return {'result': False}
        result = res.json()
        log.info("create_domain result: %s", result)
        return result

    @staticmethod
    def get_domain(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_domain"}, **param)
        # print "get_domain:", params
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("get_domain: %s", res.url)
        except Exception, e:
            print e
            log.error("get_domain error: %s", e)
            return {'result': False}
        result = res.json()
        log.info("get_domain result: %s", result)
        return result

    @staticmethod
    def activate_domain(param):
        global URL
        params = dict({"act": "activate_domain"}, **param)
        # print "get_domain:", params
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("activate_domain: %s", res.url)
        except Exception, e:
            print e
            log.error("activate_domain error: %s", e)
            return {'result': False}
        result = res.json()
        log.info("activate_domain result: %s", result)
        return result

    @staticmethod
    def update_domain(param):
        global URL
        params = dict({"act": "update_domain"}, **param)

        try:
            res  = requests.get(URL, params=params, timeout=30.000)
            log.info("update_domain: %s", res.url)
            result = res.json()
            log.info("update_domain result: %s", result)
            return result
        except Exception, e:
            print e
            log.error("update_domain error: %s", e)
            return {'result': False}

    @staticmethod
    def get_func_auth(param):
        global URL
        params = dict({"act": "get_func_auth"}, **param)
        # print "get_domain:", params
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("get_func_auth: %s", res.url)
        except Exception, e:
            print e
            log.error("get_func_auth error: %s", e)
            return {'result': False}
        result = res.json()
        log.info("get_func_auth result: %s", result)
        return result

    @staticmethod
    def get_upload_bytes_stat(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_upload_bytes_stat"}, **param)
        # print "get_domain:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("get_upload_bytes_stat: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_upload_bytes_stat result: %s", result)
        return result

    # interfaces about account
    @staticmethod
    def login(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "login"}, **param)
        # print "login:", params
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("login: %s", res.url)
        except Exception, e:
            if len(es_url_list) > 1:
                count = len(es_url_list)
                rst = {}
                i = 0
                while i < count-1:
                    new_url = switch_frontend(URL)
                    URL = new_url
                    i=i+1
                    try:
                        res = requests.get(URL, params=params, timeout=30.000)
                        log.info("login: %s", res.url)
                        rst = res
                        break
                    except Exception, e:
                        log.info("login error: %s", e)
                if not rst:
                    return {'result': False, 'error': "server error"}
                else:
                    result = rst.json()
                    log.info("frontend_url: %s", URL)
                    log.info("login result: %s", result)
                    return result
            else:
                log.info("login error: %s", e)
                return {'result': False, 'error': "server error"}
        result = res.json()
        log.info("login result: %s", result)
        return result

    @staticmethod
    def try_frontend(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "login"}, **param)
        # print "login:", params
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("try_frontend url: %s", res.url)
        except Exception, e:
            if len(es_url_list) > 1:
                count = len(es_url_list)
                rst = {}
                i = 0
                while i < count-1:
                    new_url = switch_frontend(URL)
                    URL = new_url
                    i += 1
                    try:
                        res = requests.get(URL, params=params, timeout=30.000)
                        log.info("try_frontend url: %s", res.url)
                        break
                    except Exception, e:
                        log.info("try_frontend error: %s", e)
            else:
                log.error("try_frontend error: %s", e)
        log.info("try_frontend frontend_url is: %s", URL)
        return URL

    @staticmethod
    def send_reset_passwd_email(param, datas):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "send_reset_passwd_email"}, **param)
        p = urllib.urlencode(params)
        url = URL + "?" + p
        body = json.dumps(datas)

        try:
            res = requests.post(url, data=body, timeout=10.000)
            log.info("send_reset_passwd_email: %s", res.url)
        except Exception, e:
            print e
            return {'result': False, 'error': "server error"}
        result = res.json()
        log.info("send_reset_passwd_email result: %s", result)
        return result

    @staticmethod
    def reset_passwd(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "reset_passwd"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            log.info("reset_passwd: %s", res.url)
        except Exception, e:
            print e
            return {'result': False, 'error': "server error"}
        result = res.json()
        log.info("reset_passwd result: %s", result)
        return result

    @staticmethod
    def get_account_list(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_account_list"}, **param)
        # print "get_account_list:", params
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("get_account_list: %s", res.url)
        result = res.json()
        log.info("get_account_list result: %s", result)
        return result

    @staticmethod
    def create_account(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_account"}, **param)
        # print "create_account:", params
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("create_account: %s", res.url)
        result = res.json()
        log.info("create_account result: %s", result)
        return result

    @staticmethod
    def update_account(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "update_account"}, **param)
        # print "update_account:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("update_account: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("update_account result: %s", result)
        return result

    @staticmethod
    def delete_account(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_account"}, **param)
        # print "delete_account:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("delete_account: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("delete_account result: %s", result)
        return result

    @staticmethod
    def list_urls(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "list_urls"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("list_urls: %s", res.url)
        result = res.json()
        log.info("list_urls result: %s", result)
        return result


    @staticmethod
    def get_role_list(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "list_role"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("list_role: %s", res.url)
        result = res.json()
        log.info("list_role result: %s", result)
        return result

    @staticmethod
    def create_role(param, data):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_role"}, **param)
        p = urllib.urlencode(params)
        url = URL + "?" + p
        body = json.dumps(data)
        res = requests.post(url, data=body, timeout=3.000)
        log.info("create_role: %s", res.url)
        result = res.json()
        log.info("create_role result: %s", result)
        return result

    @staticmethod
    def get_role(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_role"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("get_role: %s", res.url)
        result = res.json()
        log.info("get_role result: %s", result)
        return result

    @staticmethod
    def update_role(param, data):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "update_role"}, **param)
        try:
            p = urllib.urlencode(params)
            url = URL + "?" + p
            body = json.dumps(data)
            res = requests.post(url, data=body, timeout=3.000)
            log.info("update_role: %s", res.url)
        except Exception, e:
            log.error("update_role error: %s", e)
            return {'result': False}
        result = res.json()
        log.info("update_role result: %s", result)
        return result

    @staticmethod
    def delete_role(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_role"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("delete_role: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("delete_role result: %s", result)
        return result

    @staticmethod
    def get_permissionmeta_list(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "list_permission_meta"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("list_permission_meta: %s", res.url)
        result = res.json()
        log.info("list_permission_meta result: %s", result)
        return result

    @staticmethod
    def privilege_list_resource_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "privilege_list_resource_group"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("privilege_list_resource_group: %s", res.url)
        result = res.json()
        log.info("privilege_list_resource_group result: %s", result)
        return result

    @staticmethod
    def get_permission_meta(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_permission_meta"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("get_permission_meta: %s", res.url)
        result = res.json()
        log.info("get_permission_meta result: %s", result)
        return result

    @staticmethod
    def get_resource_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_resource_group"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("get_resource_group: %s", res.url)
        result = res.json()
        log.info("get_resource_group result: %s", result)
        return result

    @staticmethod
    def update_resource_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "update_resource_group"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("update_resource_group: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("update_resource_group result: %s", result)
        return result

    @staticmethod
    def create_resource_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_resource_group"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("create_resource_group: %s", res.url)
        result = res.json()
        log.info("create_resource_group result: %s", result)
        return result

    @staticmethod
    def delete_resource_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_resource_group"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("delete_resource_group: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("delete_resource_group result: %s", result)
        return result

    @staticmethod
    def get_batch_account(param):
        global URL
        param = BackendRequest._prepare_params(param)
        if "ids" in param and param['ids'] == "":
            return {u'accounts': [], u'result': True}
        params = dict({"act": "get_batch_account"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("get_batch_account: %s", res.url)
        result = res.json()
        log.info("get_batch_account result: %s", result)
        return result

    @staticmethod
    def get_batch_saved_search(param):
        global URL
        param = BackendRequest._prepare_params(param)
        if "ids" in param and param['ids'] == "":
            return {u'saved_searchs': [], u'result': True}
        params = dict({"act": "get_batch_saved_search"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("get_batch_saved_search: %s", res.url)
        result = res.json()
        log.info("get_batch_saved_search result: %s", result)
        return result

    @staticmethod
    def get_batch_dashboard_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        if "ids" in param and param['ids'] == "":
            return {u'dashboard_groups': [], u'result': True}
        params = dict({"act": "get_batch_dashboard_group"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("get_batch_dashboard_group: %s", res.url)
        result = res.json()
        log.info("get_batch_dashboard_group result: %s", result)
        return result

    @staticmethod
    def get_batch_trend(param):
        global URL
        param = BackendRequest._prepare_params(param)
        if "ids" in param and param['ids'] == "":
            return {u'trends': [], u'result': True}
        params = dict({"act": "get_batch_trend"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("get_batch_trend: %s", res.url)
        result = res.json()
        log.info("get_batch_trend result: %s", result)
        return result

    @staticmethod
    def get_batch_alert(param):
        global URL
        param = BackendRequest._prepare_params(param)
        if "ids" in param and param['ids'] == "":
            return {u'alerts': [], u'result': True}
        params = dict({"act": "get_batch_alert"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("get_batch_alert: %s", res.url)
        result = res.json()
        log.info("get_batch_alert result: %s", result)
        return result

    @staticmethod
    def get_batch_sourcegroup(param):
        param = BackendRequest._prepare_params(param)
        if "ids" in param and param['ids'] == "":
            return {u'source_groups': [], u'result': True}
        params = dict({"act": "get_batch_source_group"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("get_batch_sourcegroup: %s", res.url)
        result = res.json()
        log.info("get_batch_sourcegroup result: %s", result)
        return result

    @staticmethod
    def get_batch_saved_schedule(param):
        param = BackendRequest._prepare_params(param)
        if "ids" in param and param['ids'] == "":
            return {u'saved_schedules': [], u'result': True}
        params = dict({"act": "get_batch_saved_schedule"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("get_batch_saved_schedule: %s", res.url)
        result = res.json()
        log.info("get_batch_saved_schedule result: %s", result)
        return result

    @staticmethod
    def get_batch_dictionary(param):
        param = BackendRequest._prepare_params(param)
        if "ids" in param and param['ids'] == "":
            return {u'list': [], u'result': True}
        # format incompatible
        params = dict({"act": "dict_batch"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("get_batch_dictionary: %s", res.url)
        result = res.json()
        log.info("get_batch_dictionary result: %s", result)
        return result

    @staticmethod
    def get_batch_report(param):
        param = BackendRequest._prepare_params(param)
        if "ids" in param and param['ids'] == "":
            return {u'list': [], u'result': True}
        # format incompatible
        params = dict({"act": "report_batch"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("get_batch_report: %s", res.url)
        result = res.json()
        log.info("get_batch_report result: %s", result)
        return result

    @staticmethod
    def get_batch_config(param):
        param = BackendRequest._prepare_params(param)
        if "ids" in param and param['ids'] == "":
            return {u'list': [], u'result': True}
        # format incompatible
        params = dict({"act": "config_batch"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("get_batch_config: %s", res.url)
        result = res.json()
        log.info("get_batch_config result: %s", result)
        return result

    @staticmethod
    def list_assigned_resource_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "list_assigned_resource_group"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("list_assigned_resource_group: %s", res.url)
        result = res.json()
        log.info("list_assigned_resource_group result: %s", result)
        return result

    @staticmethod
    def list_derelict_resource_ids(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "list_derelict_resource_ids"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("list_derelict_resource_ids: %s", res.url)
        result = res.json()
        log.info("list_derelict_resource_ids result: %s", result)
        return result

    @staticmethod
    def permit_list_resource_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "permit_list_resource_group"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("permit_list_resource_group: %s", res.url)
        result = res.json()
        log.info("permit_list_resource_group result: %s", result)
        return result

    @staticmethod
    def get_all_user_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_all_user_group"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("get_all_user_group: %s", res.url)
        result = res.json()
        log.info("get_all_user_group result: %s", result)
        return result

    @staticmethod
    def get_user_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_user_group"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("get_user_group: %s", res.url)
        result = res.json()
        log.info("get_user_group result: %s", result)
        return result

    @staticmethod
    def create_user_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_user_group"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("create_user_group: %s", res.url)
        result = res.json()
        log.info("create_user_group result: %s", result)
        return result

    @staticmethod
    def update_user_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "update_user_group"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("update_user_group: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("update_user_group result: %s", result)
        return result

    @staticmethod
    def can_visit(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "can_visit"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("can_visit: %s", res.url)
        result = res.json()
        log.info("can_visit result: %s", result)
        return result

    @staticmethod
    def permit_can(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "permit_can"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("permit_can: %s", res.url)
        result = res.json()
        log.info("permit_can result: %s", result)
        return result

    @staticmethod
    def batch_permit_can(param, data):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "batch_permit_can"}, **param)
        try:
            p = urllib.urlencode(params)
            url = URL + "?" + p
            body = json.dumps(data)
            res = requests.post(url, data=body, timeout=3.000)
            log.info("batch_permit_can: %s", res.url)
        except Exception, e:
            log.error("batch_permit_can error: %s", e)
            return {'result': False}
        result = res.json()
        log.info("batch_permit_can result: %s", result)
        return result

    @staticmethod
    def assign_manager_role(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "assign_manager_role"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("assign_manager_role: %s", res.url)
        result = res.json()
        log.info("assign_manager_role result: %s", result)
        return result

    @staticmethod
    def assign_role(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "assign_role"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("assign_role: %s", res.url)
        result = res.json()
        log.info("assign_role result: %s", result)
        return result

    @staticmethod
    def assign_user(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "assign_user"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("assign_user: %s", res.url)
        result = res.json()
        log.info("assign_user result: %s", result)
        return result

    @staticmethod
    def delete_user_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_user_group"}, **param)
        # print "delete_account:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("delete_user_group: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("delete_user_group result: %s", result)
        return result

    @staticmethod
    def get_account(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_account"}, **param)
        # print "get_account:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("get_account: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_account result: %s", result)
        return result

    @staticmethod
    def delete_account_action(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_account_action"}, **param)
        # print "add_account_action:", params
        try:
            res = requests.post(URL, params=params, timeout=3.000)
            log.info("delete_account_action: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("delete_account_action result: %s", result)
        return result

    @staticmethod
    def add_account_action(param, datas):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "add_account_action"}, **param)
        # print "add_account_action:", params
        p = urllib.urlencode(params)
        url = URL + "?" + p
        body = json.dumps(datas)
        # print body
        try:
            res = requests.post(url, data=body, timeout=10.000)
            log.info("add_account_action: %s", res.url)
            # print res.url
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("add_account_action result: %s", result)
        return result

    @staticmethod
    def get_account_action(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_account_action"}, **param)
        # print "get_account_action:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("get_account_action: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_account_action result: %s", result)
        return result

    # interfaces about source_group
    @staticmethod
    def get_source_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_source_group"}, **param)
        # print "get_source_group:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("get_source_group: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_source_group result: %s", result)
        return result

    @staticmethod
    def create_source_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_source_group"}, **param)
        # print "create_source_group:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("create_source_group: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("create_source_group result: %s", result)
        return result

    @staticmethod
    def get_source_group_related_infos(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_source_group_related_infos"}, **param)
        # print "update_source_group:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("get_source_group_related_infos: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_source_group_related_infos result: %s", result)
        return result

    @staticmethod
    def update_source_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "update_source_group"}, **param)
        # print "update_source_group:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("update_source_group: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("update_source_group result: %s", result)
        return result

    @staticmethod
    def delete_source_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_source_group"}, **param)
        # print "delete_source_group:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("delete_source_group: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("delete_source_group result: %s", result)
        return result


    @staticmethod
    def assign_source_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "assign_source_group"}, **param)
        # print "delete_source_group:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("assign_source_group: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("assign_source_group result: %s", result)
        return result

    @staticmethod
    def cancel_source_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "cancel_source_group"}, **param)
        # print "delete_source_group:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("cancel_source_group: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("cancel_source_group result: %s", result)
        return result

    @staticmethod
    def get_upload_status(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_domain"}, **param)
        # print "get_source_group:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("get_source_group: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_source_group result: %s", result)
        return result

    # interfaces about alert
    @staticmethod
    def get_all_alert(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_all_alert"}, **param)
        # print "get_all_alert:", params
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("get_all_alert: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_all_alert result: %s", result)
        return result

    @staticmethod
    def get_alert(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_alert"}, **param)
        # print "get_alert:", params
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            log.info("get_alert: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_alert result: %s", result)
        return result

    @staticmethod
    def preview_alert(param):
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "preview_alert"}, **param)
        body = json.dumps(params.pop('alert_meta'))
        p = urllib.urlencode(params)
        url = URL + "?" + p
        try:
            res = requests.post(url, data=body, timeout=600.000)
            log.info("preview_alert: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("preview_alert result: %s", result)
        return result

    @staticmethod
    def create_alert(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_alert"}, **param)
        # print "create_alert:", params
        body = json.dumps(params.pop('alert_meta'))
        p = urllib.urlencode(params)
        url = URL + "?" + p
        try:
            res = requests.post(url, data=body, timeout=10.000)
            log.info("create_alert: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("create_alert result: %s", result)
        return result

    @staticmethod
    def update_alert(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "update_alert"}, **param)
        if 'alert_meta' in params:
            body = json.dumps(params.pop('alert_meta'))
        else:
            body = json.dumps("")
        p = urllib.urlencode(params)
        url = URL + "?" + p
        try:
            res = requests.post(url, data=body, timeout=10.000)
            log.info("update_alert: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        log.info("update_alert frontend res: %s", res)
        result = res.json()
        log.info("update_alert result: %s", result)
        return result

    @staticmethod
    def delete_alert(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_alert"}, **param)
        # print "delete_alert:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("delete_alert: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("delete_alert result: %s", result)
        return result

    @staticmethod
    def attempt_run_alert(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "attempt_run_alert"}, **param)
        body = json.dumps(params.pop('alert_meta'))
        p = urllib.urlencode(params)
        url = URL + "?" + p
        try:
            res = requests.post(url, data=body, timeout=600.000)
            log.info("attempt_run_alert: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("attempt_run_alert result: %s", result)
        return result

    # interfaces about source_group
    @staticmethod
    def get_all_saved_schedule(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_all_saved_schedule"}, **param)
        # print "get_all_saved_search:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("get_all_saved_schedule: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_all_saved_schedule result: %s", result)
        return result

    @staticmethod
    def create_schedule(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_saved_schedule"}, **param)
        # print "create_alert:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("create_saved_schedule : %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("create_saved_schedule  result: %s", result)
        return result

    @staticmethod
    def update_schedule(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "update_schedule"}, **param)
        # print "update_schedule:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("update_schedule: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("update_schedule result: %s", result)
        return result

    @staticmethod
    def delete_saved_schedule(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_saved_schedule"}, **param)
        # print "create_alert:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("delete_saved_schedule : %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("delete_saved_schedule  result: %s", result)
        return result

    @staticmethod
    def enable_schedule(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "enable_saved_schedule"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("enable_saved_schedule : %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("enable_saved_schedule  result: %s", result)
        return result

    @staticmethod
    def disable_schedule(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "disable_saved_schedule"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("disable_saved_schedule : %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("disable_saved_schedule  result: %s", result)
        return result

    # interfaces about source_group
    @staticmethod
    def get_saved_schedule(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_saved_schedule"}, **param)
        # print "get_all_saved_search:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("get_saved_schedule: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_saved_schedule result: %s", result)
        return result

    @staticmethod
    def get_schedule_result(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_schedule_result"}, **param)
        # print "get_all_saved_search:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("get_schedule_result: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_schedule_result result: %s", result)
        return result


    # interfaces about source_group
    @staticmethod
    def get_all_saved_search(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_all_saved_search"}, **param)
        # print "get_all_saved_search:", params
        try:
            res = requests.get(URL, params=params, timeout=20.000)
            log.info("get_all_saved_search: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        if result["result"]:
            log.info("get_all_saved_search result: %s", result.get("result",""))
        else:
            log.info("get_all_saved_search result: %s", result.get("error",""))
        return result

    @staticmethod
    def get_saved_search(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_saved_search"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("get_saved_search: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_saved_search result: %s", result)
        return result


    @staticmethod
    def create_saved_search(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_saved_search"}, **param)
        # print "create_saved_search:", params
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("create_saved_search: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("create_saved_search result: %s", result)
        return result

    @staticmethod
    def update_saved_search(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "update_saved_search"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("update_saved_search: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("update_saved_search result: %s", result)
        return result

    @staticmethod
    def delete_saved_search(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_saved_search"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("delete_saved_search: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("delete_saved_search result: %s", result)
        return result

    @staticmethod
    def search_logtail(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "logtail"}, **param)
        try:
            log.info("logtail start")
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("logtail: %s", res.url)
        except Exception, e:
            log.error("logtail error: %s", e)
            return {'result': False}
        result = res.json()
        log.info("logtail result: %s", result)
        return result

    @staticmethod
    def search_submit(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "submit"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("submit: %s", res.url)
        except Exception, e:
            log.error("submit error: %s", e)
            return {'result': False}
        result = res.json()
        log.info("submit result: %s", result)
        return result

    @staticmethod
    def search_download_submit(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "download"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("download submit: %s", res.url)
        except Exception, e:
            log.error("download submit error: %s", e)
            return {'result': False}
        result = res.json()
        log.info("download submit result: %s", result)
        return result

    @staticmethod
    def search_offlinetask_submit(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "background"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("offlinetask submit: %s", res.url)
        except Exception, e:
            log.error("offlinetask submit error: %s", e)
            return {'result': False}
        result = res.json()
        log.info("offlinetask submit result: %s", result)
        return result

    @staticmethod
    def search_preview(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "preview"}, **param)
        sid = params.get("sid", "default")
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("[%s] preview: %s" % (sid, res.url))
        except Exception, e:
            log.error("[%s] preview error: %s" % (sid, e))
            return {'result': False}
        result = res.json()
        log.info("[%s] preview result: %s" % (sid, result))
        # log.info("[%s] preview result rc: %s" % (sid, result["rc"]))
        return result

    @staticmethod
    def search_stats_events(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "statevents"}, **param)
        sid = params.get("sid", "default")
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("[%s] statevents: %s" % (sid, res.url))
        except Exception, e:
            log.error("[%s] statevents error: %s" % (sid, e))
            return {'result': False}
        result = res.json()
        log.info("[%s] statevents result: %s" % (sid, result))
        return result

    @staticmethod
    def search_kill(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "kill"}, **param)
        sid = params.get("sid", "default")
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("[%s] kill: %s" % (sid, res.url))
        except Exception, e:
            log.error("[%s] kill error: %s" % (sid, e))
            return {'result': False}
        result = res.json()
        log.info("[%s] kill result: %s" % (sid, result))
        return result

    @staticmethod
    def search_pause(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "pause"}, **param)
        sid = params.get("sid", "default")
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("[%s] pause: %s" % (sid, res.url))
        except Exception, e:
            log.error("[%s] pause error: %s" % (sid, e))
            return {'result': False}
        result = res.json()
        log.info("[%s] pause result: %s" % (sid, result))
        return result

    @staticmethod
    def search_recover(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "recover"}, **param)
        sid = params.get("sid", "default")
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("[%s] recover: %s" % (sid, res.url))
        except Exception, e:
            log.error("[%s] recover error: %s" % (sid, e))
            return {'result': False}
        result = res.json()
        log.info("[%s] recover result: %s" % (sid, result))
        return result

    @staticmethod
    def search_heartbeat(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "heartbeat"}, **param)
        sid = params.get("sid", "default")
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("[%s] heartbeat: %s" % (sid, res.url))
        except Exception, e:
            log.error("[%s] heartbeat error: %s" % (sid, e))
            return {'result': False}
        result = res.json()
        log.info("[%s] heartbeat result: %s" % (sid, result))
        return result

    @staticmethod
    def search_topfields(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "topfields"}, **param)
        sid = params.get("sid", "default")
        try:
            res = requests.get(URL, params=params, timeout=30.000)
            log.info("[%s] topfields: %s" % (sid, res.url))
        except Exception, e:
            log.error("[%s] topfields error: %s" % (sid, e))
            return {'result': False}
        result = res.json()
        log.info("[%s] topfields result: %s" % (sid, result))
        return result

    @staticmethod
    def context_search(param):
        global URL

        _id = str(int(time.time()*1000))+"_"+str(random.randint(1000,9999))+"_"+string.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 3)).replace(" ","")

        param = BackendRequest._prepare_params(param)
        params = dict({"act": "context_search"}, **param)
        timeout = True
        try:
            start = int(time.time()*1000)
            log.info('context_search [%s] start: %d'%(_id, start))
            res = requests.get(URL + "es_status/", params=params, timeout=120.000)
            log.info('context_search [%s]: %s'%(_id, res.url))
            # print '#####################url: ', res.url
            timeout = False
            result = res.json()
        except Exception, e:
            log.info('context_search [%s] error: %s' % (_id, e))
            end = int(time.time()*1000)
            log.info('context_search [%s] cost: %d' % (_id, end-start))
            error = 'system' if not timeout else 'timeout'
            return {'result': False, 'error': error}
        # print "search result:", result
        end = int(time.time()*1000)
        if not result["result"]:
            log.error("context_search [%s] result: %s and cost: %d ms" % (_id, result['error'], end-start))
        else:
            log.info("context_search [%s] result: %s and cost: %d ms" % (_id, result['result'], end-start))
        return result

    # search interface
    @staticmethod
    def search(param):
        global URL

        _id = str(int(time.time()*1000))+"_"+str(random.randint(1000,9999))+"_"+string.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 3)).replace(" ","")

        param = BackendRequest._prepare_params(param)
        params = dict({"act": "search"}, **param)
        timeout = True
        try:
            start = int(time.time()*1000)
            log.info('search [%s] start: %d'%(_id, start))
            res = requests.get(URL + "es_status/", params=params, timeout=120.000)
            log.info('search [%s]: %s'%(_id, res.url))
            # print '#####################url: ', res.url
            timeout = False
            result = res.json()
        except Exception, e:
            log.info('search [%s] error: %s' % (_id, e))
            end = int(time.time()*1000)
            log.info('search [%s] cost: %d' % (_id, end-start))
            error = 'system' if not timeout else 'timeout'
            return {'result': False, 'error': error}
        # print "search result:", result
        end = int(time.time()*1000)
        if not result.get("result"):
            log.error("search [%s] result: %s and cost: %d ms" % (_id, result['error'], end-start))
        else:
            log.info("search [%s] result: %s and cost: %d ms" % (_id, result['result'], end-start))
        return result

    @staticmethod
    def multi_search(param, post_data):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "search"}, **param)
        timeout = True
        p = urllib.urlencode(params)
        url = URL + "?" + p
        body = json.dumps(post_data)
        try:
            res = requests.post(url, data=body, timeout=120.000)
            log.info('search: %s', res.url)
            # print '#####################url: ', res.url
            timeout = False
            result = res.json()
        except Exception, e:
            log.info('search-error: %s', e)
            error = 'system' if not timeout else 'timeout'
            return {'result': False, 'error': error}
        # print "search result:", result
        log.info("search result: %s", result['result'])
        return result

    @staticmethod
    def field_search(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "field_search"}, **param)
        try:
            res = requests.post(URL, params=params, timeout=120.000)
            log.info('field_search: %s', res.url)
            # print '#####################url: ', res.url
            result = res.json()
        except Exception, e:
            log.info('field_search-error: %s', e)
            return {'result': False, 'error': error}
        # print "search result:", result
        log.info("field_search result: %s", result['result'])
        return result

    @staticmethod
    def update_dashboard(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({}, **param)
        try:
            res = requests.post(URL, params=params, timeout=3.000)
            log.info("update_dashboard contents params: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("update_dashboard contents result: %s", result)
        return result

    @staticmethod
    def get_dashboard_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_dashboard_group"}, **param)
        try:
            res = requests.post(URL, params=params, timeout=30.000)
            log.info("get_dashboard_group contents params: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_dashboard_group contents result: %s", result)
        return result

    @staticmethod
    def get_all_dashboard_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_all_dashboard_group"}, **param)
        try:
            res = requests.post(URL, params=params, timeout=30.000)
            log.info("get_all_dashboard_group contents params: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_all_dashboard_group contents result: %s", result)
        return result

    @staticmethod
    def create_dashboard_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_dashboard_group"}, **param)
        try:
            res = requests.post(URL, params=params, timeout=30.000)
            log.info("create_dashboard_group contents params: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("create_dashboard_group contents result: %s", result)
        return result

    @staticmethod
    def delete_dashboard_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_dashboard_group"}, **param)
        try:
            res = requests.post(URL, params=params, timeout=30.000)
            log.info("delete_dashboard_group contents params: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("delete_dashboard_group contents result: %s", result)
        return result

    @staticmethod
    def update_dashboard_group(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "update_dashboard_group"}, **param)
        try:
            res = requests.post(URL, params=params, timeout=30.000)
            log.info("update_dashboard_group contents params: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("update_dashboard_group contents result: %s", result)
        return result

    @staticmethod
    def create_dashboard_tab(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_dashboard"}, **param)
        try:
            res = requests.post(URL, params=params, timeout=30.000)
            log.info("create_dashboard_tab contents params: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("create_dashboard_tab contents result: %s", result)
        return result

    @staticmethod
    def update_dashboard_tab(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "update_dashboard"}, **param)
        body = json.dumps(params.pop('content'))
        p = urllib.urlencode(params)
        url = URL + "?" + p
        try:
            res = requests.post(url, data=body, timeout=30.000)
            log.info("update_dashboard_tab contents params: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("update_dashboard_tab contents result: %s", result)
        return result

    @staticmethod
    def get_all_trends(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_all_trends"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info('get_all_trends: %s', res.url)
        except Exception, e:
            print e
            log.info('get_all_trends error: %s', str(e))
            return {'result': False}
        result = res.json()
        log.info('get_all_trends result:%s', result)
        return result

    @staticmethod
    def convert_id(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "convert_id"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info('convert_id: %s', res.url)
        except Exception, e:
            print e
            log.info('convert_id error: %s', str(e))
            return {'result': False}
        result = res.json()
        log.info('convert_id result:%s', result)
        return result

    @staticmethod
    def get_trend(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_trend"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info('get_trend: %s', res.url)
        except Exception, e:
            print e
            log.info('get_trend error: %s', str(e))
            return {'result': False}
        result = res.json()
        log.info('get_trend result:%s', result)
        return result

    @staticmethod
    def create_trend(param, data):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_trend"}, **param)
        p = urllib.urlencode(params)
        url = URL + "?" + p
        body = json.dumps(data)
        try:
            res = requests.post(url, data=body, timeout=10.000)
            log.info('create_trend: %s', res.url)
        except Exception, e:
            print e
            log.info('create_trend error: %s', str(e))
            return {'result': False}
        result = res.json()
        log.info('create_trend result:%s', result)
        return result

    @staticmethod
    def delete_trend(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_trend"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info('delete_trend: %s', res.url)
        except Exception, e:
            print e
            log.info('delete_trend error: %s', str(e))
            return {'result': False}
        result = res.json()
        log.info('delete_trend result:%s', result)
        return result

    @staticmethod
    def update_trend(param, data):
        global URL
        # param = BackendRequest._prepare_params(param)
        # params = dict({"act": "update_trend"}, **param)
        # try:
        #     res = requests.get(URL, params=params, timeout=3.000)
        #     log.info('update_trend: %s', res.url)
        # except Exception, e:
        #     print e
        #     log.info('update_trend error: %s', str(e))
        #     return {'result': False}
        # result = res.json()
        # log.info('update_trend result:%s', result)
        # return result
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "update_trend"}, **param)
        p = urllib.urlencode(params)
        url = URL + "?" + p
        body = json.dumps(data)
        try:
            if body:
                res = requests.post(url, data=body, timeout=10.000)
            else:
                res = requests.post(url, timeout=10.000)
            log.info('update_trend: %s', res.url)
        except Exception, e:
            print e
            log.info('update_trend error: %s', str(e))
            return {'result': False}
        result = res.json()
        log.info('update_trend result:%s', result)
        return result

    @staticmethod
    def add_account_trend(param, datas):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "add_account_trend"}, **param)
        p = urllib.urlencode(params)
        url = URL + "?" + p
        body = json.dumps(datas)
        # print body
        try:
            res = requests.post(url, data=body, timeout=10.000)
            log.info("add_account_trend: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("add_account_trend result:%s", result)
        return result

    @staticmethod
    def call_account_trend(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info('call_account_trend: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('call_account_trend result:%s', result)
        return result

    @staticmethod
    def update_account_trend_name(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            log.info('update_account_trend_name: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('update_account_trend_name result:%s', result)
        return result

    @staticmethod
    def get_logtype(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_logtype"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            log.info('get_logtype: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('get_logtype result:%s', result)
        return result


    @staticmethod
    def get_logtype_profiles(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_logtype_profiles"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            log.info('get_logtype_profiles: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('get_logtype_profiles result:%s', result)
        return result

    @staticmethod
    def toggle_logtype(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "toggle_logtype"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            log.info('toggle_logtype: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('toggle_logtype result:%s', result)
        return result

    @staticmethod
    def toggle_security(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "toggle_security"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            log.info('toggle_logtype: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('toggle_logtype result:%s', result)
        return result


    @staticmethod
    def delete_logtype(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_logtype"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            log.info('delete_logtype: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('delete_logtype result:%s', result)
        return result


    @staticmethod
    def verify_logtype(param, datas):
        global URL
        # URL = "http://192.168.1.70:8181/"
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "verify_logtype"}, **param)
        p = urllib.urlencode(params)
        url = URL + "?" + p
        body = json.dumps(datas)
        # print body
        try:
            res = requests.post(url, data=body, timeout=10.000)
            log.info("verify_logtype: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("verify_logtype result:%s", result)
        return result


    @staticmethod
    def create_logtype(param, datas):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_logtype"}, **param)
        p = urllib.urlencode(params)
        url = URL + "?" + p
        body = json.dumps(datas)
        # print body
        try:
            res = requests.post(url, data=body, timeout=10.000)
            log.info("create_logtype: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("create_logtype result:%s", result)
        return result


    @staticmethod
    def update_logtype(param, datas):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "update_logtype"}, **param)
        p = urllib.urlencode(params)
        url = URL + "?" + p
        body = json.dumps(datas)
        # print body
        try:
            res = requests.post(url, data=body, timeout=10.000)
            log.info("update_logtype: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("update_logtype result:%s", result)
        return result

    @staticmethod
    def get_agent_status(param):
        global URL
        # URL = 'http://192.168.1.31:8080/'
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_agent_status"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            #print URL, params
            log.info('get_agent_status: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('get_agent_status result:%s', result)
        return result

    @staticmethod
    def add_resource_to_group(param):
        global URL
        # URL = 'http://192.168.1.31:8080/'
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "add_resource_to_group"}, **param)
        try:
            res = requests.post(URL, params=params, timeout=10.000)
            log.info('add_resource_to_group: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('add_resource_to_group result:%s', result)
        return result

    @staticmethod
    def remove_resource_from_group(param):
        global URL
        # URL = 'http://192.168.1.31:8080/'
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "remove_resource_from_group"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            log.info('remove_resource_from_group: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('remove_resource_from_group result: %s', result)
        return result


    @staticmethod
    def delete_agent(param):
        global URL
        # URL = 'http://192.168.1.31:8080/'
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_agent"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            log.info('delete_agent: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('delete_agent result:%s', result)
        return result

    @staticmethod
    def get_search_stats(param):
        global URL
        # URL = 'http://192.168.1.71:8080/'
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_search_stats"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=20.000)
            log.info('get_search_stats: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('get_search_stats result:%s', result)
        return result

    # 2016-01-04 by huang.huajun
    # for server heka config
    @staticmethod
    def get_agent_config(param):
        global URL
        # URL = 'http://192.168.1.31:8080/'
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_agent_config"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            #print URL, params
            log.info('get_agent_config: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('get_agent_config result:%s', result)
        return result

    @staticmethod
    def add_agent_config(param):
        global URL
        # URL = 'http://192.168.1.31:8080/'
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "add_agent_config"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            #print URL, params
            log.info('add_agent_config: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('add_agent_config result:%s', result)
        return result

    @staticmethod
    def add_agent_package(param):
        global URL
        # URL = 'http://192.168.1.31:8080/'
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "add_agent_package"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            #print URL, params
            log.info('add_agent_package: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('add_agent_package result:%s', result)
        return result

    @staticmethod
    def update_agent(param):
        global URL
        # URL = 'http://192.168.1.31:8080/'
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "update_agent"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            #print URL, params
            log.info('update_agent: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('update_agent result:%s', result)
        return result

    @staticmethod
    def get_agent_package(param):
        global URL
        # URL = 'http://192.168.1.31:8080/'
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_agent_package"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            #print URL, params
            log.info('get_agent_package: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('get_agent_package result:%s', result)
        return result

    @staticmethod
    def delete_agent_package(param):
        global URL
        # URL = 'http://192.168.1.31:8080/'
        print "PPPPPPPPPPPPPPPPPPPPPPP %s" % param
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_agent_package"}, **param)
        try:
            print "PPPPPPPPPP %s" % params
            res = requests.get(URL, params=params, timeout=10.000)
            #print URL, params
            print "DDDDDDDDDDD %s" % res
            log.info('delete_agent_package: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('delete_agent_package result:%s', result)
        return result


    @staticmethod
    def modify_agent_config(param):
        global URL
        # URL = 'http://192.168.1.31:8080/'
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "modify_agent_config"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            #print URL, params
            log.info('modify_agent_config: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('modify_agent_config result:%s', result)
        return result

    @staticmethod
    def delete_agent_config(param):
        global URL
        # URL = 'http://192.168.1.31:8080/'
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_agent_config"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            #print URL, params
            log.info('del_agent_config: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('del_agent_config result:%s', result)
        return result

    @staticmethod
    def get_licence_info(param):
        global URL
        # URL = 'http://192.168.1.71:8080/'
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_license_info"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            log.info('get_license_info: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('get_search_stats result:%s', result)
        return result

    @staticmethod
    def get_records(param):
        global URL
        # URL = 'http://192.168.1.71:8080/'
        param = BackendRequest._prepare_params(param)
        params = dict({}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            log.info('get_records: %s', res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info('get_records result:%s', result)
        return result

    @staticmethod
    def get_notice(param):
        global URL
        # URL = 'http://192.168.1.71:8080/'
        param = BackendRequest._prepare_params(param)
        params = dict({}, **param)
        try:
            res = requests.get(URL, params=params, timeout=10.000)
            log.info('get_notice: %s', res.url)
        except Exception, e:
            print e
            return {'result': False, 'error': 'Get notice error!'}
        result = res.json()
        if result["result"]:
            log.info('get_notice result:%s', result.get("result",""))
        else:
            log.info('get_notice result:%s', result.get("error",""))
        return result

    @staticmethod
    def get_appname_ttl(param):
        global URL
        # _URL = 'http://192.168.1.117:8080/'
        _URL = URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_appname_ttl"}, **param)
        try:
            res = requests.post(_URL, params=params, timeout=30.000)
            log.info("get_appname_ttl contents params: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_appname_ttl contents result: %s", result)
        return result

    @staticmethod
    def get_ttl_bk_times(param):
        global URL
        # _URL = 'http://192.168.1.117:8080/'
        _URL = URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_valid_appname_ttl"}, **param)
        try:
            res = requests.post(_URL, params=params, timeout=30.000)
            log.info("get_valid_appname_ttl contents params: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("get_valid_appname_ttl contents result: %s", result)
        return result

    @staticmethod
    def update_ttls(param):
        global URL
        # _URL = 'http://192.168.1.117:8080/'
        _URL = URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_appname_ttl"}, **param)
        try:
            res = requests.post(_URL, params=params, timeout=30.000)
            print "###################update ttls url : ",res.url
            log.info("create_appname_ttl contents params: %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("create_appname_ttl contents result: %s", result)
        return result

    ############################################################################
    #   author: "Junwei Zhao"
    #   date: 10/17/2016
    #   Dictionary section
    #   frontend dictionary api wrappers
    ############################################################################
    @staticmethod
    def get_dict_list(param):
        # construct url and dictionary for HTTP "GET"'s query string
        # global URL
        _URL = URL
        params = BackendRequest.form_params(param, "dict_lists")

        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("get_dict_list: %s", res.url)

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("get_dict_list result: %s", result)

        return result

    @staticmethod
    def get_dict_list_title(param):
        _URL = URL
        params = BackendRequest.form_params(param, "dict_lists_title")

        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("get_dict_list_title: %s", res.url)

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("get_dict_list_title result: %s", result)

        return result


    @staticmethod
    def get_dict_detail(param):
        _URL = URL
        params = BackendRequest.form_params(param, "dict_detail")

        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("get_dict_detail: %s", res.url)

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("get_dict_detail result: %s", result)

        return result


    @staticmethod
    def delete_dict(param):
        # global URL
        _URL = URL
        params = BackendRequest.form_params(param, "dict_delete")

        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("delete_dict: %s", res.url)

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("delete_dict result: %s", result)

        return result


    @staticmethod
    def update_dict(param, file=""):
        # global URL
        _URL = URL
        params = BackendRequest.form_params(param, "dict_update")
        body = file

        # p = urllib.urlencode(params)
        # url = URL + "?" + p

        try:
            res = requests.post(_URL, params=params, data=body, timeout=30.000)
            log.info("update_dict: %s", res.url)

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("update_dict result: %s", result)

        return result


    @staticmethod
    def upload_dict(param, file=""):
        # global URL
        _URL = URL
        params = BackendRequest.form_params(param, "dict_upload")
        body = file

        # p = urllib.urlencode(params)
        # url = URL + "?" + p

        try:
            res = requests.post(_URL, params=params, data=body, timeout=30.000)
            log.info("upload_dict: %s", res.url)

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("upload_dict result: %s", result)

        return result


    @staticmethod
    def dict_exist(param):
        # get existing csv files list
        file_name = str(param.get('name', ""))
        rtn = BackendRequest.get_dict_list(param)

        # check if uploading/updating file has already been stored in the database
        if rtn["result"]:
            dict_list = rtn.get('list', [])

            if len(dict_list):
                for item in dict_list:
                    if str(item.get('name', "")) == file_name:
                        return True

        return False


    ############################################################################
    #   author: "Junwei Zhao"
    #   date: 10/18/2016
    #   Config section
    #   frontend config api wrappers
    ############################################################################
    @staticmethod
    def get_config_list(param):
        _URL = URL
        params = BackendRequest.form_params(param, "config_list")

        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("get_config_list: %s", res.url)
            if int(res.status_code) == 500:
                return BackendRequest.print_and_rtn_exception_wrapper()

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("get_config_list result: %s", result)
        BackendRequest.reformat_config_category_id(result.get('list', []))
        return result


    @staticmethod
    def get_config_detail(param):
        _URL = URL
        params = BackendRequest.form_params(param, "config_detail")

        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("get_config_detail: %s", res.url)
            print res.url
            if int(res.status_code) == 500:
                return BackendRequest.print_and_rtn_exception_wrapper()

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("get_config_detail result: %s", result)
        return result


    @staticmethod
    def delete_config(param):
        _URL = URL
        params = BackendRequest.form_params(param, "config_delete")

        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("delete_config: %s", res.url)
            if int(res.status_code) == 500:
                return BackendRequest.print_and_rtn_exception_wrapper()

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("delete_config result: %s", result)
        BackendRequest.reformat_config_category_id(result.get('list', []))
        return result


    @staticmethod
    def get_category_list(param):
        _URL = URL
        params = BackendRequest.form_params(param, "category_list")

        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("get_category_list: %s", res.url)
            if int(res.status_code) == 500:
                return BackendRequest.print_and_rtn_exception_wrapper()

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("get_category_list result", result)
        return result


    @staticmethod
    def create_config(param, data={}):
        _URL = URL
        params = BackendRequest.form_params(param, "config_new")
        # pass data as string format instead of json
        data = json.dumps(data)

        try:
            res = requests.post(_URL, params=params, data=data, timeout=30.000)
            log.info("create_config: %s", res.url)

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("create_config result: %s", result)
        return result


    @staticmethod
    def update_config(param, data={}):
        _URL = URL
        params = BackendRequest.form_params(param, "config_update")
        data = json.dumps(data)

        try:
            res = requests.post(_URL, params=params, data=data, timeout=30.000)
            log.info("update_config: %s", res.url)

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("update_config result: %s", result)
        # result['category_id'] = result['categoryId']
        # del result['categoryId']

        return result

    # reformat key "categoryId" to "category_id"
    @staticmethod
    def reformat_config_category_id(result):
        if result and len(result):
            for item in result:
                item['category_id'] = item['categoryId']
                del item['categoryId']


    ############################################################################
    #   author: "Junwei Zhao"
    #   date: 10/21/2016
    #   Report section
    #   frontend report api wrappers
    ############################################################################
    @staticmethod
    def get_report_list(param):
        _URL = URL
        params = BackendRequest.form_params(param, "report_list")

        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("get_report_list: %s", res.url)

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("get_report_list result: %s", result)

        return result

    @staticmethod
    def get_report_detail(param):
        _URL = URL
        params = BackendRequest.form_params(param, "report_detail")

        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("get_report_detail: %s", res.url)

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("get_report_detail result: %s", result)

        return result


    @staticmethod
    def create_report(param, data={}):
        _URL = URL
        params = BackendRequest.form_params(param, "report_new")
        data = json.dumps(data)

        try:
            res = requests.post(_URL, params=params, data=data, timeout=30.000)
            log.info("create_report: %s", res.url)

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("create_report result: %s", result)

        return result


    @staticmethod
    def update_report(param, data={}):
        _URL = URL
        params = BackendRequest.form_params(param, "report_update")
        data = json.dumps(data)
        log.info("update_report: %s", data)
        try:
            res = requests.post(_URL, params=params, data=data, timeout=30.000)
            log.info("update_report: %s", res.url)

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("update_report result: %s", result)

        return result


    @staticmethod
    def enable_report(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "report_enable"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("report_enable : %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("report_enable  result: %s", result)
        return result


    @staticmethod
    def disable_report(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "report_disable"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info("report_disable : %s", res.url)
        except Exception, e:
            print e
            return {'result': False}
        result = res.json()
        log.info("report_disable  result: %s", result)
        return result


    @staticmethod
    def delete_report(param):
        _URL = URL
        params = BackendRequest.form_params(param, "report_delete")

        try:
            res = requests.post(_URL, params=params, timeout=30.000)
            log.info("delete_report: %s", res.url)

            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)

        log.info("delete_report result: %s", result)

        return result


    @staticmethod
    def delete_download(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_file"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info('delete_download: %s', res.url)
        except Exception, e:
            print e
            log.info('delete_download error: %s', str(e))
            return {'result': False}
        result = res.json()
        log.info('delete_download result:%s', result)
        return result

    @staticmethod
    def get_job_list(param):
        _URL = URL
        params = BackendRequest.form_params(param, "joblist")
        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("get_job_list: %s", res.url)
            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)
        log.info("get_job_list result: %s", result)
        return result

    @staticmethod
    def drill_down(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "drill_down"}, **param)
        try:
            res = requests.post(URL, params=params, timeout=30.000)
            log.info("drill_down contents params: %s", res.url)
        except Exception, e:
            print e
            return {'rc': 1}
        result = res.json()
        log.info("drill_down contents result: %s", result)
        return result

    @staticmethod
    def drill_down_filter(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "filter"}, **param)
        try:
            res = requests.post(URL, params=params, timeout=30.000)
            log.info("filter contents params: %s", res.url)
        except Exception, e:
            print e
            return {'rc': 1}
        result = res.json()
        log.info("filter contents result: %s", result)
        return result

    @staticmethod
    def delete_offlinetask(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_file"}, **param)
        try:
            res = requests.get(URL, params=params, timeout=3.000)
            log.info('delete_offlinetask: %s', res.url)
        except Exception, e:
            print e
            log.info('delete_offlinetask error: %s', str(e))
            return {'result': False}
        result = res.json()
        log.info('delete_offlinetask result:%s', result)
        return result

    ############################################################################
    #   author: "Junwei Zhao"
    #   date: 10/18/2016
    #   Utility Functions
    ############################################################################
    # return given parameters grouped with proper act name
    @staticmethod
    def form_params(param, act):
        param = BackendRequest._prepare_params(param)
        return dict({'act': act}, **param)


    # if any exception related to http transmission, json parsing and database operation
    # print exception and return a mocking response back to its previous caller with error info
    @staticmethod
    def print_and_rtn_exception_wrapper(error="Server Error"):
        print error
        return {
            'result': False,
            'errorCode': 500,
            'error': error
        }

    @staticmethod
    def get_index_info_list(param):
        _URL = URL
        params = BackendRequest.form_params(param, "get_index_info_list")
        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("get_index_info_list: %s", res.url)
            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)
        log.info("get_index_info_list result: %s", result)
        return result

    @staticmethod
    def get_index_info(param):
        _URL = URL
        params = BackendRequest.form_params(param, "get_index_info")
        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("get_index_info: %s", res.url)
            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)
        log.info("get_index_info result: %s", result)
        return result

    @staticmethod
    def create_index_info(param):
        _URL = URL
        params = BackendRequest.form_params(param, "create_index_info")
        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("create_index_info: %s", res.url)
            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)
        log.info("create_index_info result: %s", result)
        return result

    @staticmethod
    def update_index_info(param):
        _URL = URL
        params = BackendRequest.form_params(param, "update_index_info")
        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("update_index_info: %s", res.url)
            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)
        log.info("update_index_info result: %s", result)
        return result

    @staticmethod
    def delete_index_info(param):
        _URL = URL
        params = BackendRequest.form_params(param, "delete_index_info")
        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("delete_index_info: %s", res.url)
            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)
        log.info("delete_index_info result: %s", result)
        return result


    @staticmethod
    def get_index_match_rule_list(param):
        _URL = URL
        params = BackendRequest.form_params(param, "get_index_match_rule_list")
        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("get_index_match_rule_list: %s", res.url)
            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)
        log.info("get_index_match_rule_list result: %s", result)
        return result

    @staticmethod
    def get_index_match_rule(param):
        _URL = URL
        params = BackendRequest.form_params(param, "get_index_match_rule")
        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("get_index_match_rule: %s", res.url)
            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)
        log.info("get_index_match_rule result: %s", result)
        return result

    @staticmethod
    def create_index_match_rule(param):
        _URL = URL
        params = BackendRequest.form_params(param, "create_index_match_rule")
        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("create_index_match_rule: %s", res.url)
            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)
        log.info("create_index_match_rule result: %s", result)
        return result

    @staticmethod
    def update_index_match_rule(param):
        _URL = URL
        params = BackendRequest.form_params(param, "update_index_match_rule")
        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("update_index_match_rule: %s", res.url)
            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)
        log.info("update_index_match_rule result: %s", result)
        return result

    @staticmethod
    def delete_index_match_rule(param):
        _URL = URL
        params = BackendRequest.form_params(param, "delete_index_match_rule")
        try:
            res = requests.get(_URL, params=params, timeout=30.000)
            log.info("delete_index_match_rule: %s", res.url)
            result = res.json()
        except Exception as e:
            return BackendRequest.print_and_rtn_exception_wrapper(e)
        log.info("delete_index_match_rule result: %s", result)
        return result

    @staticmethod
    def get_beneficiary_list(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_beneficiary_list"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("get_beneficiary_list: %s", res.url)
        result = res.json()
        log.info("get_beneficiary_list result: %s", result)
        return result
    
    @staticmethod
    def get_beneficiary(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_beneficiary"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("get_beneficiary: %s", res.url)
        result = res.json()
        log.info("get_beneficiary result: %s", result)
        return result

    @staticmethod
    def create_beneficiary(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_beneficiary"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("create_beneficiary: %s", res.url)
        result = res.json()
        log.info("create_beneficiary result: %s", result)
        return result
    
    @staticmethod
    def update_beneficiary(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "update_beneficiary"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("update_beneficiary: %s", res.url)
        result = res.json()
        log.info("update_beneficiary result: %s", result)
        return result
    
    @staticmethod
    def delete_beneficiary(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "delete_beneficiary"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("delete_beneficiary: %s", res.url)
        result = res.json()
        log.info("delete_beneficiary result: %s", result)
        return result
    
    @staticmethod
    def get_beneficiary_usages(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_beneficiary_usages"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("get_beneficiary_usages: %s", res.url)
        result = res.json()
        log.info("get_beneficiary_usages result: %s", result)
        return result

    @staticmethod
    def get_appname_list(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_appname_list"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("get_appname_list: %s", res.url)
        result = res.json()
        log.info("get_appname_list result: %s", result)
        return result
    
    @staticmethod
    def get_appname(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_appname"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("get_appname: %s", res.url)
        result = res.json()
        log.info("get_appname result: %s", result)
        return result

    @staticmethod
    def get_assigned_appname_list(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_assigned_appname_list"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("get_assigned_appname_list: %s", res.url)
        result = res.json()
        log.info("get_assigned_appname_list result: %s", result)
        return result

    @staticmethod
    def get_unassigned_appname_list(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_unassigned_appname_list"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("get_unassigned_appname_list: %s", res.url)
        result = res.json()
        log.info("get_unassigned_appname_list result: %s", result)
        return result
    
    @staticmethod
    def assign_appname(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "assign_appname"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("assign_appname: %s", res.url)
        result = res.json()
        log.info("assign_appname result: %s", result)
        return result

    @staticmethod
    def reassign_appnames(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "reassign_appnames"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("reassign_appnames: %s", res.url)
        result = res.json()
        log.info("reassign_appnames result: %s", result)
        return result

    @staticmethod
    def get_appname_list_of_beneficiary(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_appname_list_of_beneficiary"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("get_appname_list_of_beneficiary: %s", res.url)
        result = res.json()
        log.info("get_appname_list_of_beneficiary result: %s", result)
        return result
    
    @staticmethod
    def create_appname(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "create_appname"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("create_appname: %s", res.url)
        result = res.json()
        log.info("create_appname result: %s", result)
        return result

    @staticmethod
    def get_beneficiary_usages_distribution(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "get_beneficiary_usages_distribution"}, **param)
        res = requests.get(URL, params=params, timeout=3.000)
        log.info("get_beneficiary_usages_distribution: %s", res.url)
        result = res.json()
        log.info("get_beneficiary_usages_distribution result: %s", result)
        return result
    
    @staticmethod
    def verify_resource_package(param, data):
        global URL
        param = BackendRequest._prepare_params(param)
        try:
            p = urllib.urlencode(param)
            url = URL + "?" + p
            body = data
            res = requests.post(url, data=body, timeout=3.000)
            log.info("verify_resource_package: %s", res.url)
        except Exception, e:
            log.error("verify_resource_package error: %s", e)
            return {'result': False}
        result = res.json()
        log.info("verify_resource_package result: %s", result)
        return result

    @staticmethod
    def import_resource_package(param, data):
        global URL
        param = BackendRequest._prepare_params(param)
        try:
            p = urllib.urlencode(param)
            url = URL + "?" + p
            body = data
            res = requests.post(url, data=body, timeout=60.000)
            log.info("import_resource_package: %s", res.url)
        except Exception, e:
            log.error("import_resource_package error: %s", e)
            return {'result': False}
        result = res.json()
        log.info("import_resource_package result: %s", result)
        return result

    @staticmethod
    def export_resource_package(param):
        global URL
        param = BackendRequest._prepare_params(param)
        params = dict({"act": "export_resource_package"}, **param)
        res = requests.get(URL, params=params, timeout=10.000)
        log.info("export_resource_package: %s", res.url)
        result = res.json()
        log.info("export_resource_package result: %s", result)
        return result
