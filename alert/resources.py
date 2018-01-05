# -*- coding: utf-8 -*-
# wangqiushi (@yottabyte.cn)
# 2014/07/24
# Copyright 2014 Yottabyte
# file description : resources.py.
from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
import yottaweb.apps.alert.plugins
import time
import json
import logging
import pkgutil
import traceback
import sys
import ast
import copy
from datetime import datetime

__author__ = 'wangqiushi'

audit_logger = logging.getLogger("yottaweb.audit")
req_logger = logging.getLogger("django.request")
err_data = ContributeErrorData()

class AlertResource(Resource):
    # Just like a Django ``Form`` or ``Model``, we're defining all the
    # fields we're going to handle with the API here.

    class Meta:
        resource_name = 'alerts'
        always_return_data = True
        include_resource_uri = False


    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/preview/(?P<plugin_name>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('preview_alert'), name="api_preview_alert"),
            url(r"^(?P<resource_name>%s)/attempt_run/(?P<plugin_name>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('alert_attempt_run'), name="api_alert_attempt_run"),
            url(r"^(?P<resource_name>%s)/listen_alert_post/$" % self._meta.resource_name,
                self.wrap_view('listen_alert_post'), name="api_listen_alert_input"),
            url(r"^(?P<resource_name>%s)/types/$" % self._meta.resource_name,
                self.wrap_view('alert_types'), name="api_alert_types"),
            url(r"^(?P<resource_name>%s)/lists/$" % self._meta.resource_name,
                self.wrap_view('alert_list'), name="api_alert_list"),
            url(r"^(?P<resource_name>%s)/mails/$" % self._meta.resource_name,
                self.wrap_view('alert_mail'), name="api_alert_mail"),
            url(r"^(?P<resource_name>%s)/phones/$" % self._meta.resource_name,
                self.wrap_view('alert_phone'), name="api_alert_phone"),
            url(r"^(?P<resource_name>%s)/new" % self._meta.resource_name,
                self.wrap_view('alert_new'), name="api_alert_new"),
            url(r"^(?P<resource_name>%s)/resourcegroup/filter/$" % self._meta.resource_name,
                self.wrap_view('alert_rg_filter'), name="api_alert_rg_filter"),
            url(r"^(?P<resource_name>%s)/resourcegroup/ungrouped/$" % self._meta.resource_name,
                self.wrap_view('alert_rg_ungrouped'), name="api_alert_ungrouped"),
            url(r"^(?P<resource_name>%s)/resourcegroup/list/assigned/(?P<rid>[\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('alert_rg_assigned'), name="api_alert_rg_assigned"),
            url(r"^(?P<resource_name>%s)/resourcegroup/list/(?P<action>[\w_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('alert_rg_action'), name="api_alert_rg_action"),
            url(r"^(?P<resource_name>%s)/info/(?P<aid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('alert_detail'), name="api_alert_update"),
            url(r"^(?P<resource_name>%s)/(?P<aid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('alert_update'), name="api_alert_update"),
            url(r"^(?P<resource_name>%s)/alert_full_content/(?P<aid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('alert_full_content'), name="api_alert_full_content"),
            url(r"^(?P<resource_name>%s)/del/(?P<aid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('alert_delete'), name="api_alert_delete"),
            url(r"^(?P<resource_name>%s)/enable/(?P<aid>[\w\d_.-]+)/(?P<enable>[\w]{1})/$" % self._meta.resource_name,
                self.wrap_view('alert_enable'), name="api_alert_enable"),
            url(r"^(?P<resource_name>%s)/alert_history$" % self._meta.resource_name,
                self.wrap_view('alert_history'), name="api_alert_history"),
            url(r"^(?P<resource_name>%s)/alert_detail_info/(?P<id>.+)/$" % self._meta.resource_name,
                self.wrap_view('alert_detail_info'), name="api_alert_detail_info"),
        ]

    def preview_alert(self, request, **kwargs):
        ''' same as create_alert '''
        self.method_check(request, allowed=['post'])

        req_data = request.POST
        # print "#################request.POST: ", request.POST
        post_data = {
            'alert_name': req_data.get('alert_name', ''),
            'alert_description': req_data.get('alert_description', ''),
            'alert_query': req_data.get('alert_query', ''),
            'sourcegroup': req_data.get('sourcegroup', ''),
            'category': int(req_data.get('category', '0')),
            'alert_filters': req_data.get('alert_filters', ''),
            'alert_if': req_data.get('alert_if', ''),
            'alert_mails': req_data.get('alert_mails', ''),
            'alert_mail_enable': req_data.get('alert_mail_enable', ''),
            'includeLatestEvents': req_data.get('includeLatestEvents', ''),
            'frequency': req_data.get('frequency', ''),
            'email_guide': req_data.get('alert_comment', ''),
            'rsyslog_addr': req_data.get('alert_rsyslog_addr', ''),
            'rsyslog_fields': req_data.get('alert_rsyslog_fields', ''),
            'alert_enable': req_data.get('alert_enable', ''),
        }
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'owner_name': es_check['u'],
                'name': post_data['alert_name'],
                'operator': es_check['u'],
                # 'saved_search_id': post_data['savedsearch_id'],
                'email': post_data['alert_mails'],
                'category': post_data['category'],
                'email_enabled': post_data['alert_mail_enable'],
                'email_guide': post_data["email_guide"],
                'rsyslog_addr': post_data["rsyslog_addr"],
                'rsyslog_fields': post_data["rsyslog_fields"],
                'interval': int(post_data['frequency']),
                'description': post_data['alert_description'],
                'condition': post_data['alert_if'],
                'enabled': 'no' if post_data['alert_enable'] != 'true' else 'yes',
                'crontab': req_data.get('crontab', 0),
                'alert_release': req_data.get('alert_release', 0),
                'restrain_interval': req_data.get('restrain_interval', 0),
                'max_restrain_interval': req_data.get('max_restrain_interval', 0),
                'restrain_interval': req_data.get('restrain_interval', 0),
                'max_restrain_inteval': req_data.get('max_restrain_inteval', 0),
                'alert_meta': req_data.get('alert_meta', []),
                'query': req_data.get('query', '*'),
                'filters': req_data.get('filters', ''),
                'source_groups': req_data.get('sourcegroupCn', '') if not req_data.get('sourcegroup', '') == "all" else "all",
                'sourcegroupCn': req_data.get('sourcegroupCn', ''),
                'extend_query': req_data.get('extend_query', '*'),
                'extend_filters': req_data.get('extend_filters', ''),
                'extend_source_groups': req_data.get('extend_sourcegroupCn', '') if not req_data.get('extend_sourcegroup', '') == "all" else "all",
                'extend_sourcegroupCn': req_data.get('extend_sourcegroupCn', '')
            }
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "create_alert",
                "user_name": es_check['u'],
                "user_id": es_check['i'],
                "domain": es_check['d'],
                "result": "success"
            }
            dummy_data = {'result': False, 'message': 'error'}
            plugin_name = kwargs['plugin_name']
            try:
                alert_res = BackendRequest.preview_alert(param)
                if alert_res['result']:
                    post_alert = alert_res['data']
                    # get plugin
                    plugin = False
                    for p in self.get_plugins():
                        if p.META['name'] == plugin_name:
                            plugin = p
                    # get meta
                    alert_meta = False
                    for p in json.loads(ast.literal_eval(post_alert['_alert_meta'])):
                        if p['name'] == plugin_name:
                            alert_meta = p
                    content = False
                    if plugin and alert_meta:
                        try:
                            parsed_post_alert = self.reparse_alert_post(post_alert)
                            content = plugin.content(alert_meta, parsed_post_alert)
                        except Exception, e:
                            req_logger.error("handle alert with plugin %s post got exception: %s", plugin_name, e)
                            exc_type, exc_value, exc_traceback = sys.exc_info()
                            req_logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
                            content = False
                    if content:
                        dummy_data['content'] = content
                        dummy_data['result'] = True
                    else:
                        dummy_data['content'] = 'preview content render falied! , plugin_name: %s!!!! ' % plugin_name
                        dummy_data['result'] = True
                else:
                    dummy_data['message'] = 'preview execute failed !!!! '
                    dummy_data['result'] = False

            except Exception, e:
                req_logger.error("handle alert post got exception: %s", e)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                req_logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
                dummy_data['result'] = False
                dummy_data['message'] = str(exc_type) + ' : ' + str(exc_value)
        else:
            dummy_data['message'] = 'the user auth error!!!! '
            dummy_data['result'] = False
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def listen_alert_post(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {'result': False, 'message': 'error'}
        try:
            body_unicode = request.body.encode('utf-8')
            try:
                post_alert = json.loads(ast.literal_eval(body_unicode))
            except Exception, e:
                post_alert = json.loads(body_unicode)

            #  req_logger.info("post_alert:=======  "+ str(post_alert))
            plugin_map = {}
            for plugin in self.get_plugins():
                plugin_map[plugin.META['name']] = plugin
            alert_metas = self.get_alert_metas(post_alert)
            for meta in alert_metas:
                try:
                    parsed_post_alert = self.reparse_alert_post(post_alert)
                    plugin_map[meta['name']].handle(meta, parsed_post_alert)
                except Exception, e:
                    req_logger.error("handle alert with plugin %s post got exception: %s", meta['name'], e)
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    req_logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
            dummy_data['result'] = True
            dummy_data['message'] = 'ok'
        except Exception, e:
            req_logger.error("handle alert post got exception: %s", e)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            req_logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
            dummy_data['result'] = False
            dummy_data['message'] = str(exc_type) + ' : ' + str(exc_value)
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def alert_types(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        user_check = my_auth.is_authenticated(request, **kwargs)
        if user_check:
            plugins = self.get_plugins()
            for p in plugins:
                dummy_data[p.META["name"]] = p.META
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def alert_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_all_alert(param)
            if res['result']:
                data = self.rebuild_alert_list(res['alerts'])
                dummy_data["status"] = "1"
                dummy_data["totle"] = len(data)
                dummy_data["alert_list"] = data["alertlist"]
                permit_param = {
                    'permits': data["permits"]
                }
                permit_res = BackendRequest.batch_permit_can(param, permit_param)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def alert_mail(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        data = [{"id": "lt01", "name": "tesorno@gmail.com"}, {"id": "lt02", "name": "ltestss@gmail.com"},
                {"id": "lt03", "name": "c@gmail.com"}, {"id": "lt04", "name": "fffffff@gmail.com"},
                {"id": "lt05", "name": "mingzihenchangde@gmail.com"}, {"id": "lt06", "name": "aa@gmail.com"}]
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_account_list(param)
            mail_list = {
                'emails': [],
                'usergroups': []
            }
            if res['result']:
                for i in res['accounts']:
                    mail_list['emails'].append({
                        "name": i.get('email', ''),
                        "id": i.get('id', '')
                    })

                ug_res = BackendRequest.get_all_user_group(param)
                if ug_res['result']:
                    data = ug_res.get('user_groups', [])
                    for i in data:
                        memo = ""
                        it = 0
                        users = i.get('members', [])
                        for user in users:
                            memo += "<" + user['email'] + "> "
                            it = it + 1
                            if it >= 20:
                                memo += "..."
                                break
                        mail_list['usergroups'].append({
                            "name": i.get('name', ''),
                            "ug_id": i.get('id', ''),
                            "type": "email",
                            "members": users,
                            "memo": memo
                        })
            dummy_data["status"] = "1"
            dummy_data["totle"] = len(mail_list)
            dummy_data["list"] = mail_list
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def alert_phone(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_account_list(param)
            phone_list = {
                'phones': [],
                'usergroups': []
            }
            if res['result']:
                for i in res['accounts']:
                    phone_num = i.get('phone', '')
                    if phone_num.strip():
                        phone_list['phones'].append({
                            "name": phone_num,
                            "id": i.get('id', ''),
                            "memo": i.get('name', '')
                        })

                ug_res = BackendRequest.get_all_user_group(param)
                if ug_res['result']:
                    data = ug_res.get('user_groups', [])
                    for i in data:
                        memo = ""
                        have_phone = False
                        it = 0
                        users = i.get('members', [])
                        for user in users:
                            if user['phone'].strip():
                                have_phone = True
                                memo += "<" + user['phone'] + " " + user['name'] + "> "
                                it = it + 1
                                if it >= 20:
                                    memo += "..."
                                    break
                        if have_phone:
                            phone_list['usergroups'].append({
                                "name": i.get('name', ''),
                                "ug_id": i.get('id', ''),
                                "type": "phone",
                                "members": users,
                                "memo": memo
                            })
            dummy_data["status"] = "1"
            dummy_data["total"] = len(phone_list)
            dummy_data["list"] = phone_list
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def alert_detail(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        alert_id = kwargs['aid']
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            alert_res = BackendRequest.get_alert({
                'id': alert_id,
                'token': es_check['t'],
                'operator': es_check['u']
            })
            # print "###########alert_res: ",alert_res
            if alert_res['result']:
                a_alert = alert_res['alert']
                alert = {
                    'alert_id': alert_id,
                    'alert_name': a_alert['name'].encode('utf-8'),
                    'alert_description': a_alert.get("description", "").encode('utf-8'),
                    'category': str(a_alert.get("category", "0")),
                    'level': str(a_alert.get("level", "1")),
                    'query': a_alert['query'].encode('utf-8'),
                    'filters': a_alert['filters'].encode('utf-8'),
                    'source_group': a_alert['source_groups'].encode('utf-8'),
                    'alert_mails': a_alert['email'].encode('utf-8').split(',') if len(a_alert['email']) > 0 else [],
                    'alert_mail_enable': True,
                    'alert_if': a_alert.get('condition', '').encode('utf-8'),
                    'includeLatestEvents': True,
                    'alert_owner': a_alert.get("owner_name", "").encode('utf-8'),
                    'alert_comment': a_alert.get("email_guide", "").encode('utf-8'),
                    'frequency': str(a_alert.get('interval','')).encode('utf-8'),
                    'rsyslog_addr': str(a_alert.get('rsyslog_addr', '')).encode('utf-8'),
                    'rsyslog_fields': str(a_alert.get('rsyslog_fields', '')).encode('utf-8'),
                    'alert_enable': a_alert['enabled'],
                    'crontab': str(a_alert.get('crontab','')).encode('utf-8'),
                    'extend_query': str(a_alert.get('extend_query', '0')).encode('utf-8'),
                    'extend_filters': str(a_alert.get('extend_filters', '0')).encode('utf-8'),
                    'extend_source_group': str(a_alert.get('extend_source_groups', '0')).encode('utf-8'),
                    'alert_release': str(a_alert.get('alert_release', '0')).encode('utf-8'),
                    'restrain_interval': str(a_alert.get('restrain_interval', '0')).encode('utf-8'),
                    'max_restrain_interval': str(a_alert.get('max_restrain_interval', '0')).encode('utf-8'),
                    'alert_meta': a_alert.get('alert_meta',"[]").encode('utf-8'),
                }
            else:
                alert = {
                    'alert_id': alert_id,
                    'alert_name': '',
                    'alert_description': '',
                    'query': "",
                    'filters': "",
                    'source_group': "all",
                    'alert_mails': '',
                    'alert_mail_enable': True,
                    'alert_if': '',
                    'includeLatestEvents': True,
                    'frequency': '',
                    'extend_query': "",
                    'extend_filters': "",
                    'extend_source_group': "all",
                    'level': '1',
                    'crontab': '',
                    'alert_owner': "",
                    'alert_comment': "",
                    'rsyslog_addr': '',
                    'rsyslog_fields': '',
                    'category': "0",
                    'alert_enable': False
                }
            dummy_data["status"] = "1"
            dummy_data["detail"] = alert
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def alert_new(self, request, **kwargs):
        '''
        act=create_alert&token=xx&owner_id=xx&name=xx&saved_search_id=xx&email=xx&interval=xx&condition=xx&enabled=xx&query=xx
        :param request:
        :param kwargs:
        :return:
        '''
        self.method_check(request, allowed=['post'])
        req_data = request.POST
        # print "#################request.POST: ", request.POST
        post_data = {
            'alert_name': req_data.get('alert_name', ''),
            'alert_description': req_data.get('alert_description', ''),
            'alert_query': req_data.get('alert_query', ''),
            'sourcegroup': req_data.get('sourcegroup', ''),
            'category': int(req_data.get('category', '0')),
            'level': int(req_data.get('level', '-1')),
            'alert_filters': req_data.get('alert_filters', ''),
            'alert_if': req_data.get('alert_if', ''),
            'alert_mails': req_data.get('alert_mails', ''),
            'alert_mail_enable': req_data.get('alert_mail_enable', ''),
            'includeLatestEvents': req_data.get('includeLatestEvents', ''),
            'frequency': req_data.get('frequency', ''),
            'email_guide': req_data.get('alert_comment', ''),
            'rsyslog_addr': req_data.get('alert_rsyslog_addr', ''),
            'rsyslog_fields': req_data.get('alert_rsyslog_fields', ''),
            'alert_enable': req_data.get('alert_enable', ''),
            'resource_group_ids': req_data.get('resource_group_ids', '')
        }
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'owner_name': es_check['u'],
                'operator': es_check['u'],
                'name': post_data['alert_name'],
                # 'saved_search_id': post_data['savedsearch_id'],
                'email': post_data['alert_mails'],
                'category': post_data['category'],
                'level': post_data['level'],
                'email_enabled': post_data['alert_mail_enable'],
                'email_guide': post_data["email_guide"],
                'rsyslog_addr': post_data["rsyslog_addr"],
                'rsyslog_fields': post_data["rsyslog_fields"],
                'description': post_data['alert_description'],
                'condition': post_data['alert_if'],
                'enabled': 'no' if post_data['alert_enable'] != 'true' else 'yes',
                'crontab': req_data.get('crontab', 0),
                'alert_release': req_data.get('alert_release', 0),
                'restrain_interval': req_data.get('restrain_interval', 0),
                'max_restrain_interval': req_data.get('max_restrain_interval', 0),
                'restrain_interval': req_data.get('restrain_interval', 0),
                'max_restrain_inteval': req_data.get('max_restrain_inteval', 0),
                'alert_meta': req_data.get('alert_meta', []),
                'query': req_data.get('query', '*'),
                'filters': req_data.get('filters', ''),
                'source_groups': req_data.get('sourcegroupCn', '') if not req_data.get('sourcegroup', '') == "all" else "all",
                'sourcegroupCn': req_data.get('sourcegroupCn', ''),
                'extend_query': req_data.get('extend_query', '*'),
                'extend_filters': req_data.get('extend_filters', ''),
                'extend_source_groups': req_data.get('extend_sourcegroupCn', '') if not req_data.get('extend_sourcegroup', '') == "all" else "all",
                'extend_sourcegroupCn': req_data.get('extend_sourcegroupCn', ''),
                'resource_group_ids': post_data['resource_group_ids']
            }
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "create",
                "module": "alert",
                "user_name": es_check['u'],
                "user_id": es_check['i'],
                "domain": es_check['d'],
                "target": post_data['alert_name'],
                "result": "success"
            }
            if param['crontab'] == "0":
                # when crontab is not been used
                param['interval'] = int(post_data['frequency'])
            res = BackendRequest.create_alert(param)
            # print "##################res: ", res
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["id"] = res["id"]
                dummy_data["location"] = "/alerts/"
            else:
                to_log["result"] = "error"
                to_log["msg"] = res.get("error", "")
                data = err_data.build_error(res)
                dummy_data = data
                # if res['error'] == "alert is already existed":
                #     dummy_data["msg"] = "name"
            # dummy_data["totle"] = "1"
            # dummy_data["list"] = data
            audit_logger.info(json.dumps(to_log))
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def alert_update(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        alert_id = kwargs['aid']
        req_data = request.POST
        post_data = {
            'alert_name': req_data.get('alert_name', ''),
            'alert_description': req_data.get('alert_description', ''),
            'alert_if': req_data.get('alert_if', ''),
            'category': int(req_data.get('category', '0')),
            'level': int(req_data.get('level', '-1')),
            'alert_mails': req_data.get('alert_mails', ''),
            'alert_mail_enable': req_data.get('alert_mail_enable', ''),
            'includeLatestEvents': req_data.get('includeLatestEvents', ''),
            'frequency': req_data.get('frequency', ''),
            'email_guide': req_data.get('alert_comment', ''),
            'rsyslog_addr': req_data.get('alert_rsyslog_addr', ''),
            'rsyslog_fields': req_data.get('alert_rsyslog_fields', ''),
            'alert_enable': req_data.get('alert_enable', ''),
            'resource_group_ids': req_data.get('resource_group_ids', ''),
        }
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'id': alert_id,
                'token': es_check['t'],
                'operator': es_check['u'],
                'name': post_data['alert_name'],
                'description': post_data['alert_description'],
                'email': post_data['alert_mails'],
                'category': post_data['category'],
                'level': post_data['level'],
                'email_guide': post_data["email_guide"],
                'rsyslog_addr': post_data["rsyslog_addr"],
                'rsyslog_fields': post_data["rsyslog_fields"],
                'email_enabled': post_data['alert_mail_enable'],
                'interval': req_data.get('frequency', ''),
                'condition': post_data['alert_if'],
                'enabled': 'no' if post_data['alert_enable'] != 'true' else 'yes',
                'crontab': req_data.get('crontab', 0),
                'query': req_data.get('query', '*'),
                'filters': req_data.get('filters', ''),
                'source_groups': req_data.get('sourcegroupCn', '') if not req_data.get('sourcegroup', '') == "all" else "all",
                'sourcegroupCn': req_data.get('sourcegroupCn', ''),
                'extend_query': req_data.get('extend_query', '*'),
                'extend_filters': req_data.get('extend_filters', ''),
                'extend_source_groups': req_data.get('extend_sourcegroupCn', '') if not req_data.get('extend_sourcegroup', '') == "all" else "all",
                'extend_sourcegroupCn': req_data.get('extend_sourcegroupCn', ''),
                'alert_release': int(req_data.get('alert_release', 0)),
                'restrain_interval': int(req_data.get('restrain_interval', 0)),
                'max_restrain_interval': int(req_data.get('max_restrain_interval', 0)),
                'alert_meta': req_data.get('alert_meta', []),
                'resource_group_ids': post_data['resource_group_ids'],
            }
            # print "###################param: ", param
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "update",
                "module": "alert",
                "user_name": es_check['u'],
                "user_id": es_check['i'],
                "domain": es_check['d'],
                "result": "success",
                "target": post_data['alert_name']
            }

            # print "###################adsfasdfasdf "
            res = BackendRequest.update_alert(param)
            # print "###################res: ", res
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["location"] = "/alerts/"
            else:
                to_log["result"] = "error"
                to_log["msg"] = res.get("error", "")
                data = err_data.build_error(res)
                dummy_data = data
            audit_logger.info(json.dumps(to_log))

            # dummy_data["list"] = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def alert_full_content(self, request, **kwargs):
        ''' Get all detailed data of a given alert identified its id '''
        self.method_check(request, allowed=['get'])

        alert_id = kwargs['aid']
        dummy_data = {}

        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            alert_res = BackendRequest.get_alert({
                'id': alert_id,
                'token': es_check['t'],
                'operator': es_check['u']
            })
            if alert_res['result']:
                a_alert = alert_res['alert']
                alert = {
                    'alert_id': alert_id,
                    'alert_name': a_alert['name'].encode('utf-8'),
                    'alert_description': a_alert.get("description", "").encode('utf-8'),
                    'saved_searches': [],
                    'category': str(a_alert.get("category", "0")),
                    'level': str(a_alert.get("level", "1")),
                    'alert_mails': a_alert['email'].encode('utf-8').split(',') if len(a_alert['email']) > 0 else [],
                    'alert_mail_enable': True,
                    'alert_if': a_alert.get('condition', '').encode('utf-8'),
                    'includeLatestEvents': True,
                    'alert_owner': a_alert.get("owner_name", "").encode('utf-8'),
                    'alert_comment': a_alert.get("email_guide", "").encode('utf-8'),
                    'frequency': str(a_alert.get('interval','')).encode('utf-8'),
                    'rsyslog_addr': str(a_alert.get('rsyslog_addr', '')).encode('utf-8'),
                    'rsyslog_fields': str(a_alert.get('rsyslog_fields', '')).encode('utf-8'),
                    'alert_enable': a_alert['enabled'],
                    'crontab': str(a_alert.get('crontab','')).encode('utf-8'),
                    'alert_release': str(a_alert.get('alert_release', '0')).encode('utf-8'),
                    'restrain_interval': str(a_alert.get('restrain_interval', '0')).encode('utf-8'),
                    'max_restrain_interval': str(a_alert.get('max_restrain_interval', '0')).encode('utf-8'),
                    'query': a_alert['query'].encode('utf-8'),
                    'filters': a_alert['filters'].encode('utf-8'),
                    'source_group': a_alert['source_groups'].encode('utf-8'),
                    'extend_query': str(a_alert.get('extend_query', '0')).encode('utf-8'),
                    'extend_filters': str(a_alert.get('extend_filters', '0')).encode('utf-8'),
                    'extend_source_group': str(a_alert.get('extend_source_groups', '0')).encode('utf-8'),
                    'alert_meta': a_alert.get('alert_meta',"[]").encode('utf-8')
                }
                dummy_data["status"] = "1"
                dummy_data["alert"] = alert
            else:
                alert = {
                    'alert_id': alert_id,
                    'alert_name': '',
                    'alert_description': '',
                    'savedsearch_id': '',
                    'saved_searches': [],
                    'alert_saved_search': "",
                    'alert_mails': '',
                    'alert_mail_enable': True,
                    'alert_if': '',
                    'includeLatestEvents': True,
                    'frequency': '',
                    'level': '1',
                    'crontab': '',
                    'alert_owner': "",
                    'alert_comment': "",
                    'rsyslog_addr': '',
                    'rsyslog_fields': '',
                    'category': "0",
                    'alert_enable': False
                }
                dummy_data["status"] = "0"
                dummy_data["alert"] = alert
            res = BackendRequest.get_all_saved_search({
                'token': es_check['t'],
                'operator': es_check['u']
            })
            saved_searches = []
            if res['result']:
                for i in res['items']:
                    sg = 'all' if i['source_groups'] == "all" else i['source_groups'].encode('utf-8')
                    saved_searches.append({
                        'savedsearch_id': i['id'].encode('utf-8'),
                        'name': i['name'].encode('utf-8'),
                        'query': i['query'].encode('utf-8'),
                        'filters': i['filters'].encode('utf-8'),
                        'sourcegroupCn': sg,
                        'anonymous': i['anonymous']
                    })
                alert['saved_searches'] = saved_searches
                alert['saved_searches_json'] = json.dumps(saved_searches)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def alert_delete(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        alert_id = kwargs['aid']

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "delete",
                "module": "alert",
                "user_name": es_check['u'],
                "user_id": es_check['i'],
                "domain": es_check['d'],
                "result": "success",
                "target": alert_id
            }

            res = BackendRequest.delete_alert({
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': alert_id
            })
            if res['result']:
                list_res = BackendRequest.get_all_alert({
                    'token': es_check['t'],
                    'operator': es_check['u']
                })
                if list_res['result']:
                    data = self.rebuild_alert_list(list_res['alerts'])
                    dummy_data["status"] = "1"
                    dummy_data["totle"] = len(data)
                    dummy_data["alert_list"] = data["alertlist"]
                    param = {
                        'token': es_check['t'],
                        'operator': es_check['u']
                    }
                    permit_param = {
                        'permits': data["permits"]
                    }
                    permit_res = BackendRequest.batch_permit_can(param, permit_param)
                    if permit_res['result']:
                        dummy_data["permit_list"] = permit_res["short_permits"]
                    else:
                        dummy_data["permit_list"] = []
                else:
                    dummy_data["status"] = "1"
                    dummy_data["totle"] = 0
                    dummy_data["alert_list"] = []
            else:
                to_log["result"] = "error"
                to_log["msg"] = res.get("error", "")

                data = err_data.build_error(res)
                dummy_data = data
            audit_logger.info(json.dumps(to_log))

        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def alert_enable(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        alert_id = kwargs['aid']
        alert_ids = request.GET.get('ids', "")
        alert_enable = int(kwargs['enable'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'id': alert_id,
                'token': es_check['t'],
                'operator': es_check['u'],
                'enabled': 'no' if alert_enable != 1 else 'yes',
                'resource_group_ids': alert_ids
            }
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "enable",
                "module": "alert",
                "user_name": es_check['u'],
                "user_id": es_check['i'],
                "domain": es_check['d'],
                "result": "success",
                "target": alert_id,
                "enabled": param["enabled"]
            }

            res = BackendRequest.update_alert(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["enable"] = param["enabled"]
                dummy_data["msg"] = "update success"
            else:
                to_log["result"] = "error"
                to_log["msg"] = res.get("error", "")

                data = err_data.build_error(res)
                dummy_data = data
                # dummy_data["list"] = data
            audit_logger.info(json.dumps(to_log))
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def alert_history(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        alert_id = request.GET.get('alert_id')
        page = request.GET.get('page')
        size = request.GET.get('size')
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'act': 'get_all_alert_history',
                'token': es_check['t'],
                'operator': es_check['u'],
                'alert_id': alert_id,
                'page': page,
                'size': size,
            }

            res = BackendRequest.get_records(param)
            # print "#################res: ", res
            if res['result']:
                dummy_data["status"] = 1
                dummy_data["data"] = res
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "auth error!"
            dummy_data["location"] = "/auth/login/"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def alert_detail_info(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        id = kwargs['id']
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'act': 'get_alert_history_detail_info',
                'operator': es_check['u'],
                'token': es_check['t'],
                'id': id
            }
            res = BackendRequest.get_records(param)
            if res['result']:
                try:
                    try:
                        res["result"] = json.loads(ast.literal_eval(res["result"]))
                    except Exception, e:
                        res["result"] = json.loads(res["result"])
                    plugin_map = {}
                    for plugin in self.get_plugins():
                        plugin_map[plugin.META['name']] = plugin
                    alert_metas = self.eval_alert_metas(res["result"]["_alert_meta"])
                    _alert_content = []
                    for meta in alert_metas:
                        try:
                            parsed_post_alert = self.reparse_alert_post(res["result"])
                            _alert_content.append(meta['alias'] + "<br>===========<br>" + plugin_map[meta['name']].content(meta, parsed_post_alert))
                        except Exception, e:
                            req_logger.error("handle alert with plugin %s render content got exception: %s", meta['name'], e)
                            exc_type, exc_value, exc_traceback = sys.exc_info()
                            req_logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
                    res["result"]["content"] = _alert_content
                except Exception, e:
                    _result_str = str(res["result"])
                    res["result"] = {}
                    res["result"]["content"] = [_result_str]

                dummy_data["status"] = 1
                dummy_data["data"] = res
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "auth error!"
            dummy_data["location"] = "/auth/login/"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def alert_rg_filter(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        req_data = request.POST
        post_data = req_data.get('ids', '')
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'ids': post_data,
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_batch_alert(param)
            if res['result']:
                data = self.rebuild_alert_list(res['alerts'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["alert_list"] = data["alertlist"]
                param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_param = {
                    'permits': data["permits"]
                }
                permit_res = BackendRequest.batch_permit_can(param, permit_param)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def alert_rg_action(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {}
            if (kwargs['action'].lower() == "read"):
                param['action'] = "Read"
                param['category'] = "Alert"
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = "ResourceGroup"
            elif (kwargs['action'].lower() == "assign"):
                param['action'] = "Assign"
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = "Alert"

            res = BackendRequest.permit_list_resource_group(param)
            if res['result']:
                data = self.rebuild_resource_group_list(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["alert_rg_list"] = data
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def alert_rg_assigned(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        rid = kwargs['rid']
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'resource_id': rid,
                'category': "Alert",
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.list_assigned_resource_group(param)
            if res['result']:
                data = self.rebuild_assigned_resource_group_list(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["alert_rg_list"] = data
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def alert_rg_ungrouped(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'category': "Alert",
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.list_derelict_resource_ids(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["ids"] = res['resource_ids']
            else:
                data = err_data.build_error(res)
                dummy_data = data
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def alert_attempt_run(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        req_data = request.POST
        post_data = {
            'alert_name': req_data.get('alert_name', ''),
            'alert_description': req_data.get('alert_description', ''),
            'alert_query': req_data.get('alert_query', ''),
            'sourcegroup': req_data.get('sourcegroup', ''),
            'category': int(req_data.get('category', '0')),
            'alert_filters': req_data.get('alert_filters', ''),
            'alert_if': req_data.get('alert_if', ''),
            'alert_mails': req_data.get('alert_mails', ''),
            'alert_mail_enable': req_data.get('alert_mail_enable', ''),
            'includeLatestEvents': req_data.get('includeLatestEvents', ''),
            'frequency': req_data.get('frequency', ''),
            'email_guide': req_data.get('alert_comment', ''),
            'rsyslog_addr': req_data.get('alert_rsyslog_addr', ''),
            'rsyslog_fields': req_data.get('alert_rsyslog_fields', ''),
            'alert_enable': req_data.get('alert_enable', ''),
        }
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'owner_name': es_check['u'],
                'name': post_data['alert_name'],
                'operator': es_check['u'],
                'email': post_data['alert_mails'],
                'category': post_data['category'],
                'email_enabled': post_data['alert_mail_enable'],
                'email_guide': post_data["email_guide"],
                'rsyslog_addr': post_data["rsyslog_addr"],
                'rsyslog_fields': post_data["rsyslog_fields"],
                'interval': post_data['frequency'],
                'description': post_data['alert_description'],
                'condition': post_data['alert_if'],
                'enabled': 'no' if post_data['alert_enable'] != 'true' else 'yes',
                'crontab': req_data.get('crontab', 0),
                'alert_release': req_data.get('alert_release', 0),
                'restrain_interval': req_data.get('restrain_interval', 0),
                'max_restrain_interval': req_data.get('max_restrain_interval', 0),
                'restrain_interval': req_data.get('restrain_interval', 0),
                'max_restrain_inteval': req_data.get('max_restrain_inteval', 0),
                'alert_meta': req_data.get('alert_meta', []),
                'query': req_data.get('query', '*'),
                'filters': req_data.get('filters', ''),
                'source_groups': req_data.get('sourcegroup', ''),
                'sourcegroupCn': req_data.get('sourcegroupCn', ''),
                'extend_query': req_data.get('extend_query', '*'),
                'extend_filters': req_data.get('extend_filters', ''),
                'extend_source_groups': req_data.get('extend_sourcegroupCn', '') if not req_data.get('extend_sourcegroup', '') == "all" else "all",
                'extend_sourcegroupCn': req_data.get('extend_sourcegroupCn', ''),
                'run': 'true'
            }

            plugin_name = kwargs['plugin_name']
            try:
                alert_res = BackendRequest.attempt_run_alert(param)
                if alert_res['result']:
                    post_alert = alert_res['data']
                    # get plugin
                    plugin = False
                    for p in self.get_plugins():
                        if p.META['name'] == plugin_name:
                            plugin = p
                    # get meta
                    alert_meta = False
                    for p in json.loads(ast.literal_eval(post_alert['_alert_meta'])):
                        if p['name'] == plugin_name:
                            alert_meta = p
                    content = False
                    if plugin and alert_meta:
                        try:
                            parsed_post_alert = self.reparse_alert_post(post_alert)
                            plugin.handle(alert_meta, parsed_post_alert)
                        except Exception, e:
                            req_logger.error("handle alert with plugin %s post got exception: %s", plugin_name, e)
                            exc_type, exc_value, exc_traceback = sys.exc_info()
                            req_logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
                            content = False
                        dummy_data['status'] = "1"
                    else:
                        dummy_data = err_data.build_error({}, "Attempt run alert failed!!!")
                else:
                    dummy_data = err_data.build_error(alert_res)
            except Exception, e:
                req_logger.error("handle alert post got exception: %s", e)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                req_logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
                dummy_data = err_data.build_error({}, str(exc_type) + ' : ' + str(exc_value))
            # res = BackendRequest.attempt_run_alert(param)
            # if res['result']:
            #     dummy_data["status"] = "1"
            #     dummy_data["data"] = res['data']
            # else:
            #     data = err_data.build_error(res)
            #     dummy_data = data
        else:
            dummy_data["status"] = "0"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    @staticmethod
    def rebuild_alert_list(origin):
        '''
            {"alert_id": "34859", "description": "asdfasdfadsfa", "alert_details": [0, 0, 30, 24, 3, 5, 0, 0, 0, 0, 5,
                                                                                    6, 0, 0, 0, 0, 2, 3, 56, 10, 2, 24,
                                                                                    3, 0],
             "query": "error", "sourcegroup": "all", "fields": "", "time_range": "-1d,now", "lastrun": "20140721",
             "alert_owner": "wangqiushi", "alert_name": "test1", "enable": "true", "frequency": "10min"},
        :param origin: origin alert list
        :return: target result
        '''
        target = {
            "alertlist": [],
            "permits": []
        }
        alertlist = []
        permits = []
        for i in origin:
            alertlist.append({
                "alert_id": i['id'],
                "description": i.get("description", ""),
                "alert_details": i.get("run_results", []),
                "alert_owner": i["owner_name"],
                "alert_name": i["name"],
                "enable": "true" if i["enabled"] else "false",
                "lastrun": i.get("last_run_timestamp", 0),
                "frequency": i["interval"],
                "crontab": i.get("crontab", "0"),
                "time_range": "-1d,now",
                "category": i.get("category"),
                "level": i.get("level"),
                "derelict": i.get("derelict"),
                "alert_number": i.get("alert_result_number", 0),
                "condition": i.get("condition")
            })
            permits.append({
                "resource_id": int(i['id']),
                "target": "Alert",
                "action": "Update"
            })
            permits.append({
                "resource_id": int(i['id']),
                "target": "Alert",
                "action": "Delete"
            })
        permits.append({
            "target": "Alert",
            "action": "Create"
        })
        permits.append({
            "target": "DerelictResource",
            "action": "Possess"
        })
        target["alertlist"] = alertlist
        target["permits"] = permits
        return target

    @staticmethod
    def rebuild_resource_group_list(data):
        res_list = []
        for item in data:
            final = {}
            final["type"] = item.get("category").encode('utf-8')
            final["rgname"] = item.get("name").encode('utf-8')
            final["memo"] = item.get("memo", "").encode('utf-8')
            final["domain_id"] = item.get("domain_id")
            final["creator_id"] = item.get("creator_id")
            final["rg_id"] = item.get("id")
            final["resource_ids"] = item.get("resource_ids", [])
            res_list.append(final)
        return res_list

    @staticmethod
    def rebuild_assigned_resource_group_list(data):
        res_list = []
        for item in data:
            final = {}
            final["type"] = item.get("category").encode('utf-8')
            final["rgname"] = item.get("name").encode('utf-8')
            final["memo"] = item.get("memo", "").encode('utf-8')
            final["domain_id"] = item.get("domain_id")
            final["creator_id"] = item.get("creator_id")
            final["rg_id"] = item.get("id")
            res_list.append(final)
        return res_list

    @staticmethod
    def get_plugins():
        plugins = []
        pkg = yottaweb.apps.alert.plugins
        pkgprefix = pkg.__name__ + '.'
        for importer, modname, ispkg in pkgutil.iter_modules(pkg.__path__, pkgprefix):
            try:
                if not ispkg:
                    mod = __import__(modname, fromlist="dummy")
                    plugins.append(mod)
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                req_logger.error("alert dynamic loading get_plugins failed, %s : %s", exc_type, exc_value)
                req_logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
        return plugins

    @staticmethod
    def get_alert_metas(alert_post):
        # 另一种方式是从_alert_id再读Alert表获取到表中的
        # TODO(wu.ranbo@yottabyte.cn) 现在post过来的前后多了引号
        meta_str = ast.literal_eval(alert_post['_alert_meta'])
        if len(meta_str) == 0:
            meta_str = "[]"
        return json.loads(meta_str)

    @classmethod
    def timestamp_to_datetime(cls, stamp):
        return datetime.fromtimestamp(float(stamp)/1000.0)

    @staticmethod
    def eval_alert_metas(alert_meta_str):
        ''' 传入数据库中存储的str,转为数组 '''
        meta_str = "[]"
        try:
            meta_str = ast.literal_eval(alert_meta_str)
            if len(meta_str) == 0:
                meta_str = "[]"
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            req_logger.error("eval_alert_metas failed, %s : %s", exc_type, exc_value)
            req_logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
            meta_str = "[]"
        return json.loads(meta_str)

    # 将time值都变成对象
    @classmethod
    def reparse_alert_post(cls, in_alert_post):
        alert_post = copy.deepcopy(in_alert_post)
        alert_post['send_time'] = cls.timestamp_to_datetime(alert_post['send_time'])
        alert_post['exec_time'] = cls.timestamp_to_datetime(alert_post['exec_time'])
        trigger = alert_post['strategy']['trigger']
        if 'start_time' in trigger:
            trigger['start_time'] = cls.timestamp_to_datetime(trigger['start_time'])
        if 'end_time' in trigger:
            trigger['end_time'] = cls.timestamp_to_datetime(trigger['end_time'])
        if 'baseline_start_time' in trigger:
            trigger['baseline_start_time'] = cls.timestamp_to_datetime(trigger['baseline_start_time'])
        if 'baseline_end_time' in trigger:
            trigger['baseline_end_time'] = cls.timestamp_to_datetime(trigger['baseline_end_time'])
        trigger['compare_desc_text'] = cls.trigger_condition(alert_post['strategy'])
        alert_post['strategy']['trigger'] = trigger
        return alert_post

    # 对触发条件的描述
    @classmethod
    def trigger_condition(cls, strategy):
        strategy_name = strategy['name']
        trigger = strategy['trigger']
        if strategy_name == 'count':
            return "计数" + cls.common_cmp_str(trigger['compare'], trigger['compare_value'])
        elif strategy_name == 'field_stat':
            if trigger['method'] == 'cardinality' and len(trigger['compare_value']) == 1:
                return trigger['field'] + "出现次数超过" + cls.trim_zero(trigger['compare_value'][0]) + "次"
            else:
                return trigger['field'] + cls.common_cmp_str(trigger['compare'], trigger['compare_value'])
        elif strategy_name == 'sequence_stat':
            return trigger['field'] + "连续达到" + cls.trim_zero(str(trigger['threshold'])) + "的次数" + cls.common_cmp_str(trigger['compare'], trigger['compare_value'])
        elif strategy_name == 'baseline_cmp':
            symbol = trigger['compare']
            value = trigger['compare_value']
            style = trigger['compare_style']
            if cls.is_cmp_fixed_value(style):
                return "均值" + cls.common_cmp_str(symbol, value)
            else:
                if cls.is_cmp_range(symbol):
                    return "均值" + cls.common_cmp_str(symbol) + "基线值的" + cls.trim_zero("{:0.2f}".format(float(value[0]))) + "倍到" + cls.trim_zero("{:0.2f}".format(float(value[1]))) + "倍区间。"
                else:
                    return "均值" + cls.common_cmp_str(symbol) + "基线值的" + cls.trim_zero("{:0.2f}".format(float(value[0]))) + "倍"
        elif strategy_name == 'spl_query':
            return trigger['field'] + cls.common_cmp_str(trigger['compare'], trigger['compare_value'])
        else:
            return ""

    @classmethod
    def is_cmp_range(cls, symbol):
        if symbol == 'in' or symbol == 'ex':
            return True
        return False

    # values: trigger内的compare_value，这个用来比较的数组
    @classmethod
    def is_cmp_fixed_value(cls, style):
        if style == 'fixed':
            return True
        return False

    @classmethod
    def common_cmp_str(cls, symbol, in_values=[]):
        value = in_values
        if len(value) == 0:
            value = [""]
        if symbol == '>':
            return "大于" + cls.trim_zero(str(value[0]))
        elif symbol == '<':
            return "小于" + cls.trim_zero(str(value[0]))
        elif symbol == 'in':
            if len(value) == 1:
                return "位于"
            return "位于区间" + str(value) + "内"
        elif symbol == 'ex':
            if len(value) == 1:
                return "超出"
            return "位于区间" + str(value) + "外"
        else:
            return ""

    @classmethod
    def trim_zero(cls, ins):
        s = str(ins)
        ret = s.rstrip('0').rstrip('.') if '.' in s else s
        return ret
