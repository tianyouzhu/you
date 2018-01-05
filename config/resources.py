# -*- coding: utf-8 -*-
# wangqiushi (wang.qiushi@yottabyte.cn)
# 2015/01/07
# Copyright 2015 Yottabyte
# file description : resources.py
from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.config import parser
from collections import Counter
from fieldLearn.MultiFieldLearn import learn
from fieldLearn.MultiFieldLearn import JavaRegexRule
import types
import logging
import pymysql
import json
import re
import ConfigParser
import os
__author__ = 'wangqiushi'

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    database = cf.get('db', 'fe_name')
    user = cf.get('db', 'user')
    pwd = cf.get('db', 'password')
    host = cf.get('db', 'host')
except Exception, e:
    print e
    database = "root"
    user = "root"
    pwd = "123456"
    host = "127.0.0.1"

logger = logging.getLogger("django.request")
err_data = ContributeErrorData()


class ConfigResource(Resource):

    class Meta:
        resource_name = 'configs'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/lists/$" % self._meta.resource_name,
                self.wrap_view('config_list'), name="api_config_list"),
            url(r"^(?P<resource_name>%s)/category/$" % self._meta.resource_name,
                self.wrap_view('category_list'), name="api_category_list"),
            url(r"^(?P<resource_name>%s)/search/$" % (self._meta.resource_name),
                self.wrap_view('search'), name="api_search"),
            url(r"^(?P<resource_name>%s)/zones/$" % (self._meta.resource_name),
                self.wrap_view('zone'), name="api_search"),
            url(r"^(?P<resource_name>%s)/verify/$" % self._meta.resource_name,
                self.wrap_view('config_verify'), name="api_config_verify"),
            url(r"^(?P<resource_name>%s)/detail/(?P<cf_id>(\d+))/$" % self._meta.resource_name,
                self.wrap_view('config_detail'), name="api_config_detail"),
            url(r"^(?P<resource_name>%s)/copy/(?P<cf_id>(\d+))/$" % self._meta.resource_name,
                self.wrap_view('config_copy'), name="api_config_detail"),
            url(r"^(?P<resource_name>%s)/new/$" % self._meta.resource_name,
                self.wrap_view('config_new'), name="api_config_new"),
            url(r"^(?P<resource_name>%s)/delete/$" % self._meta.resource_name,
                self.wrap_view('config_del'), name="api_config_del"),
            url(r"^(?P<resource_name>%s)/update/(?P<cf_id>(\d+))/$" % self._meta.resource_name,
                self.wrap_view('config_update'), name="api_config_update"),
            url(r"^(?P<resource_name>%s)/update/(?P<cf_name>([\w\d_\-]+|\*{1}))/(?P<cf_tg>[\d]{1})/$" % self._meta.resource_name,
                self.wrap_view('config_active'), name="api_config_active"),
            url(r"^(?P<resource_name>%s)/check/(?P<cf_name>([\w\d_\-]+|\*{1}))/$" % self._meta.resource_name,
                self.wrap_view('config_check_appname'), name="api_config_check"),
            url(r"^(?P<resource_name>%s)/security_support/$" % self._meta.resource_name,
                self.wrap_view('config_security_support'), name="api_config_list"),
            url(r"^(?P<resource_name>%s)/toggle_security/(?P<cf_name>([\w\d_\-]+|\*{1}))/(?P<cf_security>[\d]{1})/$" % self._meta.resource_name,
                self.wrap_view('config_toggle_security'), name="api_config_active"),
            url(r"^(?P<resource_name>%s)/automatic/regex/$" % self._meta.resource_name,
                self.wrap_view('config_auto_regex'), name="api_config_active"),
            url(r"^(?P<resource_name>%s)/automatic/parse/$" % self._meta.resource_name,
                self.wrap_view('config_auto_parse'), name="api_config_active"),
            url(r"^(?P<resource_name>%s)/automatic/regex/verifyall/$" % self._meta.resource_name,
                self.wrap_view('config_auto_regex_verify_all'), name="api_config_active"),
            url(r"^(?P<resource_name>%s)/resourcegroup/filter/$" % self._meta.resource_name,
                self.wrap_view('reourcegroup_filter'), name="api_sourcegroups_rg_filter"),
            url(r"^(?P<resource_name>%s)/resourcegroup/list/assigned/(?P<cid>[\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('get_resourcegroup_assigned_list'), name="api_get_resourcegroup_assigned_list"),
            url(r"^(?P<resource_name>%s)/resourcegroup/list/(?P<action>[\w_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('get_resourcegroup_list'), name="api_get_resourcegroup_list"),
            url(r"^(?P<resource_name>%s)/resourcegroup/ungrouped/$" % self._meta.resource_name,
                self.wrap_view('get_resourcegroup_ungrouped'), name="api_get_resourcegroup_ungrouped")
        ]


    ###########################################################################################################
    #   author: "Junwei Zhao"
    #   date: 10/24/2016
    #   module: Config
    #   subject: Change code from directly manipulating database to calling Restful API provided by Frontend
    #   Modified APIs:
    #            1. config_list(self, request, **kwargs)
    #            2. category_list(self, request, **kwargs)
    #            3. config_detail(self, request, **kwargs)
    #            4. config_del(self, request, **kwargs)
    #            5. cofig_new(self, request, **kwargs)
    #            6. config_update(self, request, **kwargs)
    #            6. config_copy(self, request, **kwargs)
    #   Returned error Codes and meanings:
    #            1. s_11: authentication failed/error
    #            2. s_00: name empty
    #            3. s_01: name been used
    #            4. s_02: rule has been used
    #            5. s_04: rule is not existed
    #            6. s_05: config's id is empty
    #            7. s_10: general server error
    ###########################################################################################################
    @staticmethod
    def error_handler(res, authError):
        """
            Error codes and meaning:
            s_11: authentication failed/error
            s_00: name empty
            s_01: name been used
            s_02: rule has been used
            s_04: rule is not existed
            s_05: config's id is empty
            s_10: general server error
        """

        dummy = {}

        if authError:
            dummy = err_data.build_error({}, "auth error!")
            dummy['location'] = "/auth/login/"
            dummy['error_code'] = "s_11"
        else:
            errorCode = int(res.get('errorCode', 500))
            error = res.get('error', "Server Error")

            if errorCode == 500 or errorCode == 0:
                dummy = err_data.build_error({})
                dummy['error_code'] = "s_10"
            elif errorCode == 568:
                dummy = err_data.build_error({}, "Rule Name is not specified!")
                dummy["error_code"] = "s_00"
            elif errorCode == 569:
                dummy = err_data.build_error({}, "Config's id can't be found!")
                dummy['error_code'] = "s_05"
            elif errorCode == 570:
                dummy = err_data.build_error({}, "Rule has been used!")
                dummy['error_code'] = "s_02"
            elif errorCode == 571:
                dummy = err_data.build_error({}, "Rule is not existed!")
                dummy['error_code'] = "s_04"

        dummy['error'] = str(error)

        return dummy


    @staticmethod
    def check_auth(request, **kwargs):
        """
            Used to check and return authentication result
        """

        my_auth = MyBasicAuthentication()
        return my_auth.is_authenticated(request, **kwargs)


    @staticmethod
    def generate_param(es_check, params={}):
        """
            Used to generate parameters dictionary passed to the Backend/Frontend carried in http's url.
            Default form will be passing two items: 'token' and 'operator'.
            If additional parameters are specified, then those specified params will be grouped with default and get passed.
        """

        default = {
            'token': es_check['t'],
            'operator': es_check['u']
        }

        if params:
            return dict(default, **params)

        return default


    @staticmethod
    def generate_response(objRef, data, request):
        """
            Used to generate response regards to the previous request.
        """

        bundle = objRef.build_bundle(obj=data, data=data, request=request)
        response_data = bundle
        resp = objRef.create_response(request, response_data)

        return resp


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


    # @staticmethod
    # def fix_ua_does_not_contain_rule(rulelist):
    #     # fix 'ua' doesn't have rule field if with/without setting condition
    #     for each in rulelist:
    #         if 'ua' in each:
    #             ua = each.get('ua')
    #             if 'condition' in ua:
    #                 ua['rule'] = [{'condition': ua.get('condition', {})}]
    #                 del ua['condition']
    #             else:
    #                 ua['rule'] = [{'condition': None}]


    def config_list(self, request, **kwargs):
        """
            Used to get a list of currently existing configs
        """

        self.method_check(request, allowed=['get'])
        dummy_data = {}

        es_check = ConfigResource.check_auth(request, **kwargs)

        if es_check:
            param = ConfigResource.generate_param(es_check)
            res = BackendRequest.get_config_list(param)
            permits = []

            if res['result']:
                dummy_data['status'] = "1"
                data = res.get('list', [])
                dummy_data['list'] = data

                for i in data:
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "ParserRule",
                        "action": "Update"
                    })
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "ParserRule",
                        "action": "Delete"
                    })
                permits.append({
                    "target": "ParserRule",
                    "action": "Create"
                })
                permits.append({
                    "target": "DerelictResource",
                    "action": "Possess"
                })
                permit_param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_data = {
                    'permits': permits
                }
                permit_res = BackendRequest.batch_permit_can(permit_param, permit_data)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
            else:
                dummy_data = ConfigResource.error_handler(res, False)
        else:
            dummy_data = ConfigResource.error_handler(None, True)

        return ConfigResource.generate_response(self, dummy_data, request)


    def category_list(self, request, **kwargs):
        """
            Used to get a list of config categories
        """

        self.method_check(request, allowed=['get'])
        dummy_data = {}

        es_check = ConfigResource.check_auth(request, **kwargs)

        if es_check:
            param = ConfigResource.generate_param(es_check)
            res = BackendRequest.get_category_list(param)

            if res['result']:
                dummy_data['status'] = "1"
                dummy_data['list'] = res.get('list', [])
            else:
               dummy_data = ConfigResource.error_handler(res, False)
        else:
            dummy_data = ConfigResource.error_handler(None, True)

        return ConfigResource.generate_response(self, dummy_data, request)


    def config_detail(self, request, **kwargs):
        """
            Used to get the details of a given config which is identified by its config id
        """

        self.method_check(request, allowed=['get'])
        cf_id = kwargs['cf_id']
        dummy_data = {}

        es_check = ConfigResource.check_auth(request, **kwargs)

        if not cf_id:
            mock = {
                'result': False,
                'error_code': 569,
                'error': "Config's id can't be found!"
            }
            dummy_data = ConfigResource.error_handler(mock, False)
        elif es_check:
            param = ConfigResource.generate_param(es_check, {'id': cf_id})
            res = BackendRequest.get_config_detail(param)

            if res['result']:
                dummy_data = res
                print res

                # fix names incompatible problem
                data = dummy_data.get('data', {})

                data['logtype'] = data.get('logType', "")
                del data['logType']

                data['asignData'] = data.get('assignData', [])
                del data['assignData']

                asignData = data['asignData']
                for each in asignData:
                    each['appnames'] = each.get('appNames', "")
                    del each['appNames']

                # rebuild conf
                param = {
                    'conf': []
                }

                for i in data['conf']:
                    cf_type = i.keys()[0]
                    cf_rule = i[cf_type]
                    if cf_type == "grok":
                        cur_source = cf_rule["rule"][0].get("source", "").encode('utf-8')
                        source = [cur_source] if cur_source else []
                        pp = {
                            "type": "reg",
                            "name": "",
                            "expression": cf_rule["rule"][0]["pattern"][0][0].encode('utf-8'),
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule["rule"][0].get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },

                            "curSource": cur_source,
                            "sources": source,
                            "fold": True
                        }
                        if len(cf_rule["rule"][0]["pattern"]) > 1:
                            pp["multiExpression"] = ",".join(cf_rule["rule"][0]["pattern"][1]).encode('utf-8')
                        param['conf'].append(pp)
                    elif cf_type == "kv":
                        if "rule" in cf_rule:
                            prefix = ",".join(cf_rule["rule"][0]["drop_key_prefix"]).encode('utf-8') if \
                                cf_rule["rule"][0].get("drop_key_prefix", []) else ''
                            reserved_key = ",".join(cf_rule["rule"][0]["reserved_key"]).encode('utf-8') if \
                                cf_rule["rule"][0].get("reserved_key", []) else ''
                            drop_key = ",".join(cf_rule["rule"][0]["drop_key"]).encode('utf-8') if \
                                cf_rule["rule"][0].get("drop_key", []) else ''

                            param['conf'].append({
                                "type": "kv",
                                "name": "",
                                "expression": "",
                                "expression_fieldSplit": cf_rule["rule"][0]["field_split"][0].encode('utf-8'),
                                "expression_kvSplit": cf_rule["rule"][0]["value_split"][0].encode('utf-8'),
                                "expression_keyPrefix": prefix,
                                "expression_keyReserved": reserved_key,
                                "expression_keyDrop": drop_key,
                                "modify": "no",
                                "condition": {
                                    "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                    "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                    "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                                } if cf_rule["rule"][0].get("condition", {}) else {
                                    "field": "",
                                    "condition": "",
                                    "value": ""
                                },
                                "curSource": cf_rule["rule"][0]["source"].encode('utf-8'),
                                "sources": [cf_rule["rule"][0]["source"].encode('utf-8')],
                                "fold": True
                            })
                        if "match_kv_rule" in cf_rule:
                            prefix = ",".join(cf_rule["match_kv_rule"][0]["drop_key_prefix"]).encode('utf-8') if \
                                cf_rule["match_kv_rule"][0].get("drop_key_prefix", []) else ''
                            reserved_key = ",".join(cf_rule["match_kv_rule"][0]["reserved_key"]).encode('utf-8') if \
                                cf_rule["match_kv_rule"][0].get("reserved_key", []) else ''
                            drop_key = ",".join(cf_rule["match_kv_rule"][0]["drop_key"]).encode('utf-8') if \
                                cf_rule["match_kv_rule"][0].get("drop_key", []) else ''

                            kv_match_group = cf_rule["match_kv_rule"][0].get("kv_match_group", [])
                            match_groups = []
                            for item in kv_match_group:
                                match_groups.append({
                                    "key_regex": item["key_regex"],
                                    "value_regex": item["value_regex"],
                                    "value_split": ",".join(item["value_split"]) if item["value_split"] else ""
                                })

                            param['conf'].append({
                                "type": "kv_match",
                                "name": "",
                                "expression": "",
                                "expression_keyPrefix": prefix,
                                "expression_keyReserved": reserved_key,
                                "expression_keyDrop": drop_key,
                                "kvMatch_matchGroup": match_groups,
                                "modify": "no",
                                "kvMatch_findFirstOnly": 'false' if not item.get('find_first_only', False) else 'true',
                                "kvMatch_reserveAllValues": 'false' if not item.get('reserve_all_values_for_one_key', False) else 'true',
                                "condition": {
                                    "field": cf_rule["match_kv_rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                    "condition": cf_rule["match_kv_rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                    "value": cf_rule["match_kv_rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                                } if cf_rule["match_kv_rule"][0].get("condition", {}) else {
                                    "field": "",
                                    "condition": "",
                                    "value": ""
                                },
                                "curSource": cf_rule["match_kv_rule"][0]["source"].encode('utf-8'),
                                "sources": [cf_rule["match_kv_rule"][0]["source"].encode('utf-8')],
                                "fold": True
                            })

                    elif cf_type == "split":
                        param['conf'].append({
                            "type": "split",
                            "name": "",
                            "expression": cf_rule["rule"][0]["split_string"].encode('utf-8'),
                            "names": ','.join(cf_rule["rule"][0]["names"]),
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule["rule"][0].get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "curSource": cf_rule["rule"][0]["source"].encode('utf-8'),
                            "sources": [cf_rule["rule"][0]["source"].encode('utf-8')],
                            "fold": True
                        })
                    elif cf_type == "json":
                        cur_source = cf_rule["rule"][0].get("source", "").encode('utf-8')
                        source = [cur_source] if cur_source else []

                        param['conf'].append({
                            "type": "json",
                            "name": "",
                            "expression": "",
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule["rule"][0].get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "curSource": cur_source,
                            "sources": source,
                            "fold": True
                        })
                    elif cf_type == "xml":
                        cur_source = cf_rule["rule"][0].get("source", "").encode('utf-8')
                        source = [cur_source] if cur_source else []

                        param['conf'].append({
                            "type": "xml",
                            "name": "",
                            "expression": "",
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule["rule"][0].get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "curSource": cur_source,
                            "sources": source,
                            "fold": True
                        })
                    elif cf_type == "format":
                        cur_source = ','.join(cf_rule["rule"][0].get("params", ['']))
                        source = cur_source if cf_rule["rule"][0].get("params", ['']) else []

                        param['conf'].append({
                            "type": "format",
                            "name": "",
                            "params": ",".join(cf_rule["rule"][0]["params"]),
                            "expression": cf_rule["rule"][0]["printf"].encode('utf-8'),
                            "target": cf_rule["rule"][0]["target"].encode('utf-8'),
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule["rule"][0].get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "curSource": cur_source,
                            "sources": source,
                            "fold": True
                        })
                    elif cf_type == "syslog_priority":
                        cur_source = cf_rule.get("source", "").encode('utf-8')
                        source = [cur_source] if cur_source else []

                        param['conf'].append({
                            "type": "syslog_priority",
                            "name": "",
                            "expression": "",
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule.get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "curSource": cur_source,
                            "sources": source,
                            "fold": True
                        })
                    elif cf_type == "urldecode":
                        param['conf'].append({
                            "type": "url",
                            "name": "",
                            "expression": "",
                            "condition": {
                                "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule["rule"][0].get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "modify": "no",
                            "curSource": cf_rule["rule"][0]["source"].encode('utf-8'),
                            "sources": [cf_rule["rule"][0]["source"].encode('utf-8')],
                            "fold": True
                        })
                    elif cf_type == "geo":
                        param['conf'].append({
                            "type": "geo",
                            "name": "",
                            "expression": "",
                            "target": cf_rule["rule"][0]["target"].encode('utf-8'),
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule["rule"][0].get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "curSource": cf_rule["rule"][0]["source"].encode('utf-8'),
                            "sources": [cf_rule["rule"][0]["source"].encode('utf-8')],
                            "fold": True
                        })
                    elif cf_type == "phone":
                        param['conf'].append({
                            "type": "phone",
                            "name": "",
                            "expression": "",
                            "target": cf_rule["rule"][0]["target"].encode('utf-8'),
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule["rule"][0].get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "curSource": cf_rule["rule"][0]["source"].encode('utf-8'),
                            "sources": [cf_rule["rule"][0]["source"].encode('utf-8')],
                            "fold": True
                        })
                    elif cf_type == "telephone":
                        param['conf'].append({
                            "type": "telephone",
                            "name": "",
                            "expression": "",
                            "target": cf_rule["rule"][0]["target"].encode('utf-8'),
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule["rule"][0].get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "curSource": cf_rule["rule"][0]["source"].encode('utf-8'),
                            "sources": [cf_rule["rule"][0]["source"].encode('utf-8')],
                            "fold": True
                        })
                    elif cf_type == "json":
                        param['conf'].append({
                            "type": "json",
                            "name": "",
                            "expression": "",
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule["rule"][0].get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "curSource": "",
                            "sources": [],
                            "fold": True
                        })
                    elif cf_type == "ua":
                        param['conf'].append({
                            "type": "ua",
                            "name": "",
                            "expression": "",
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule.get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "curSource": cf_rule["source"].encode('utf-8'),
                            "sources": [cf_rule["source"].encode('utf-8')],
                            "fold": True
                        })
                    elif cf_type == "date" or cf_type == "auto_match_date":
                        cur_source = cf_rule.get("source", "").encode('utf-8')
                        source = [cur_source] if cur_source else []
                        param['conf'].append({
                            "type": "timestamp",
                            "name": "",
                            "expression": cf_rule["rule"][0].encode('utf-8'),
                            "prefix": cf_rule.get("prefix", "").encode('utf-8'),
                            "max_lookahead": int(cf_rule.get("max_lookahead", "80")),
                            "zone": cf_rule.get("zone", "Asia/Shanghai").encode('utf-8'),
                            "locale": cf_rule.get("locale", "en").encode('utf-8'),
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule.get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "curSource": cur_source,
                            "sources": source,
                            "fold": True
                        })
                    elif cf_type == "dict":
                        ext_field = ",".join(cf_rule["rule"][0]["ext_fields"]).encode('utf-8') if \
                            cf_rule["rule"][0].get("ext_fields", []) else ''
                        param['conf'].append({
                            "type": "dict",
                            "name": "",
                            "expression": '',
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule["rule"][0].get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "curSource": cf_rule["rule"][0]["source"].encode('utf-8'),
                            "sources": [cf_rule["rule"][0]["source"].encode('utf-8')],
                            "curDict": cf_rule["rule"][0]["id"],
                            "dictField": cf_rule["rule"][0]["field"]["title"].encode('utf-8') if isinstance(cf_rule["rule"][0]["field"], dict)
                                         else cf_rule["rule"][0]["field"].encode('utf-8'),
                            "dictExtField": ext_field,
                            "fold": True
                        })
                    elif cf_type == "numeric":
                        sources = []
                        for obj in cf_rule["rule"]:
                            sources.append(obj.get('source','').encode('utf-8'))

                        param['conf'].append({
                            "type": "num",
                            "name": "",
                            "expression": cf_rule["rule"][0]["numeric_type"].encode('utf-8'),
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule["rule"][0].get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "radix": cf_rule["rule"][0].get("radix", 10),
                            "curSource": ','.join(sources),
                            "sources": sources,
                            "fold": True
                        })
                    elif cf_type == "converter":
                        param['conf'].append({
                            "type": "converter",
                            "name": "",
                            "expression": "",
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule["rule"][0].get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "opType": cf_rule["rule"][0].get("op_type", "long2ip").encode('utf-8'),
                            "curSource": cf_rule["rule"][0]["source"].encode('utf-8'),
                            "sources": [cf_rule["rule"][0]["source"].encode('utf-8')],
                            "fold": True
                        })
                    elif cf_type == "hex":
                        param['conf'].append({
                            "type": "hex",
                            "name": "",
                            "expression": "",
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule["rule"][0].get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "curSource": cf_rule["rule"][0]["source"].encode('utf-8'),
                            "codecType": cf_rule["rule"][0].get("codec_type", "GBK").encode('utf-8'),
                            "sources": [cf_rule["rule"][0]["source"].encode('utf-8')],
                            "fold": True
                        })
                    elif cf_type == "replacer":
                        curDesensitize = cf_rule["rule"][0].get("anonymity", False)
                        if curDesensitize:
                            param['conf'].append({
                                "type": "desensitize",
                                "name": "",
                                "expression": cf_rule["rule"][0]["regex"].encode('utf-8'),
                                "modify": "no",
                                "condition": {
                                    "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                    "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                    "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                                } if cf_rule["rule"][0].get("condition", {}) else {
                                    "field": "",
                                    "condition": "",
                                    "value": ""
                                },
                                "replacement": cf_rule["rule"][0]["replacement"].encode('utf-8'),
                                "regex_prefix": cf_rule["rule"][0]["regex_prefix"].encode('utf-8'),
                                "regex_suffix": cf_rule["rule"][0]["regex_suffix"].encode('utf-8'),
                                "replaceFirst": 'false' if not cf_rule["rule"][0].get('replace_first', False) else 'true',
                                "curSource": cf_rule["rule"][0]["source"].encode('utf-8'),
                                "sources": [cf_rule["rule"][0]["source"].encode('utf-8')],
                                "fold": True,
                                "desensitize": True
                            })
                        else:
                            param['conf'].append({
                                "type": "replacer",
                                "name": "",
                                "expression": cf_rule["rule"][0]["regex"].encode('utf-8'),
                                "modify": "no",
                                "condition": {
                                    "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                    "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                    "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                                } if cf_rule["rule"][0].get("condition", {}) else {
                                    "field": "",
                                    "condition": "",
                                    "value": ""
                                },
                                "replacement": cf_rule["rule"][0]["replacement"].encode('utf-8'),
                                "replaceFirst": 'false' if not cf_rule["rule"][0].get('replace_first', False) else 'true',
                                "curSource": cf_rule["rule"][0]["source"].encode('utf-8'),
                                "sources": [cf_rule["rule"][0]["source"].encode('utf-8')],
                                "fold": True,
                                "desensitize": False
                            })
                    elif cf_type == "remove":
                        _cur_source = cf_rule["rule"][0].get("source", [])
                        cur_source = ",".join(_cur_source)
                        source = _cur_source

                        param['conf'].append({
                            "type": "remove",
                            "name": "",
                            "expression": "",
                            "modify": "no",
                            "condition": {
                                "field": cf_rule["rule"][0]["condition"]["rule"]["field"].encode('utf-8'),
                                "condition": cf_rule["rule"][0]["condition"]["rule"]["condition"].encode('utf-8'),
                                "value": cf_rule["rule"][0]["condition"]["rule"]["value"].encode('utf-8')
                            } if cf_rule["rule"][0].get("condition", {}) else {
                                "field": "",
                                "condition": "",
                                "value": ""
                            },
                            "curSource": cur_source,
                            "sources": source,
                            "fold": True
                        })


                data['conf'] = param['conf']
                del param

                dummy_data['data'] = data
            else:
               dummy_data = ConfigResource.error_handler(res, False)
        else:
            dummy_data = ConfigResource.error_handler(None, True)

        return ConfigResource.generate_response(self, dummy_data, request)

    def config_copy(self, request, **kwargs):
        """
            Used to get the details of a given config which is identified by its config id
        """

        self.method_check(request, allowed=['post'])
        cf_id = kwargs['cf_id']
        dummy_data = {}

        es_check = ConfigResource.check_auth(request, **kwargs)

        if not cf_id:
            mock = {
                'result': False,
                'error_code': 569,
                'error': "Config's id can't be found!"
            }
            dummy_data = ConfigResource.error_handler(mock, False)
        elif es_check:
            param = ConfigResource.generate_param(es_check, {'id': cf_id})
            res = BackendRequest.get_config_detail(param)

            if res['result']:
                # fix names incompatible problem
                data = res.get('data', {})
                _oldName = data.get("ruleName", '')
                assignData = data.get('assignData', [])
                assign_data = {}
                counter = 0
                new_name = request.POST.get("name", "")
                for item in assignData:
                    shrink_item = {
                        'appnames': item.get('appNames', "").encode('utf-8'),
                        'tags': item.get('tags', "").encode('utf-8')
                    }
                    assign_data[str(counter)] = shrink_item
                    counter += 1
                data = {
                    'ruleName': new_name,
                    'logType': data.get('logType', "").encode('utf-8'),
                    'rule': data['conf'],
                    'assignData': assign_data
                }
                param = ConfigResource.generate_param(es_check, {'resource_group_ids': request.POST.get("ids", "")})

                _copy_res = BackendRequest.create_config(param, data)
                if _copy_res['result']:
                    dummy_data['status'] = "1"
                    dummy_data['id'] = _copy_res.get("id", "")
                else:
                    dummy_data = ConfigResource.error_handler(_copy_res, False)
            else:
               dummy_data = ConfigResource.error_handler(res, False)
        else:
            dummy_data = ConfigResource.error_handler(None, True)

        return ConfigResource.generate_response(self, dummy_data, request)


    def config_del(self, request, **kwargs):
        """
            Used to delete the given config which is identified by its config id
        """

        self.method_check(request, allowed=['post'])
        post_data = request.POST
        # get config id
        cf_id = post_data.get("id", "")
        dummy_data = {}

        es_check = ConfigResource.check_auth(request, **kwargs)

        if not cf_id:
            mock = {
                'result': False,
                'error_code': 569,
                'error': "Config's id can't be found!"
            }
            dummy_data = ConfigResource.error_handler(mock, False)
        elif es_check:
            param = ConfigResource.generate_param(es_check, {'id': cf_id})
            res = BackendRequest.delete_config(param)

            if res['result']:
                dummy_data['status'] = "1"
                dummy_data['list'] = res.get('list', [])
            else:
               dummy_data = ConfigResource.error_handler(res, False)
        else:
            dummy_data = ConfigResource.error_handler(None, True)

        return ConfigResource.generate_response(self, dummy_data, request)


    def config_new(self, request, **kwargs):
        """
            Used to create a new config
        """

        self.method_check(request, allowed=['post'])
        dummy_data = {}

        es_check = ConfigResource.check_auth(request, **kwargs)

        if es_check:
            post_data = parser.parse(request.POST.urlencode().encode('utf-8'))
            conf_data = post_data.get("postData", {})
            asign_data = post_data.get("asignData", []).values() if post_data.get("asignData", []) else post_data.get("asignData", [])
            rule_name = conf_data.get('ruleName', '')
            logtype = conf_data.get('logtype', '')
            config_param = self.build_param(conf_data)

            if not rule_name:
                mock = {
                    'result': False,
                    'error_code': 568,
                    'error': "Rule name is not specified!"
                }
                dummy_data = ConfigResource.error_handler(mock, False)
            elif config_param:
                param = ConfigResource.generate_param(es_check, {'resource_group_ids': conf_data.get('ids', "")})

                assign_data = {}
                counter = 0
                for item in asign_data:
                    shrink_item = {
                        'appnames': item.get('appnames', ""),
                        'tags': item.get('tags', "")
                    }
                    assign_data[str(counter)] = shrink_item
                    counter += 1

                data = {
                    'ruleName': rule_name,
                    'logType': logtype,
                    'rule': config_param['rule'],
                    'assignData': assign_data
                }
                print data
                res = BackendRequest.create_config(param, data)

                if res['result']:
                    dummy_data = res
                    dummy_data['status'] = "1"
                else:
                    dummy_data = ConfigResource.error_handler(res, False)
            else:
                dummy_data = ConfigResource.error_handler({}, False)
        else:
            dummy_data = ConfigResource.error_handler(None, True)

        return ConfigResource.generate_response(self, dummy_data, request)


    def config_update(self, request, **kwargs):
        """
            Used to update any existing config which is identified by its config id
        """

        self.method_check(request, allowed=['post'])
        cf_id = kwargs['cf_id']
        dummy_data = {}

        es_check = ConfigResource.check_auth(request, **kwargs)

        if es_check:
            post_data = parser.parse(request.POST.urlencode().encode('utf-8'))
            conf_data = post_data.get("postData", {})
            asign_data = post_data.get("asignData", []).values() if post_data.get("asignData", []) else post_data.get("asignData", [])
            rule_name = conf_data.get('ruleName', '')
            logtype = conf_data.get('logtype', '')
            config_param = self.build_param(conf_data)

            if not rule_name:
                mock = {
                    'result': False,
                    'error_code': 568,
                    'error': "Rule name is not specified!"
                }
                dummy_data = ConfigResource.error_handler(mock, False)
            elif config_param:
                param = ConfigResource.generate_param(es_check, {'id': cf_id, 'resource_group_ids': conf_data.get('ids', "")})

                assign_data = {}
                counter = 0
                for item in asign_data:
                    shrink_item = {
                        'appnames': item.get('appnames', ""),
                        'tags': item.get('tags', "")
                    }
                    assign_data[str(counter)] = shrink_item
                    counter += 1

                data = {
                    'ruleName': rule_name,
                    'logType': logtype,
                    'rule': config_param['rule'],
                    'assignData': assign_data
                }
                print data
                res = BackendRequest.update_config(param, data)

                if res['result']:
                    dummy_data = res
                    dummy_data['status'] = "1"
                else:
                    dummy_data = ConfigResource.error_handler(res, False)
            else:
                dummy_data = ConfigResource.error_handler({}, False)
        else:
            dummy_data = ConfigResource.error_handler(None, True)

        return ConfigResource.generate_response(self, dummy_data, request)




    def get_resourcegroup_list(self, request, **kwargs):
        """Get a list of available resource groups in aspect of current user.
        """

        self.method_check(request, allowed=['get'])
        dummy_data = {}

        es_check = ConfigResource.check_auth(request, **kwargs)

        if es_check:
            # 'action' specifies what action is performed: Read, Assign
            # 'target' specifies what module is requesting
            param = {}
            if kwargs['action'].lower() == "read":
                param['action'] = "Read"
                param['category'] = "ParserRule"
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = "ResourceGroup"
            elif kwargs['action'].lower() == "assign":
                param['action'] = "Assign"
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = "ParserRule"

            res = BackendRequest.permit_list_resource_group(param)

            if res['result']:
                data = self.rebuild_resource_group_list(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["list"] = data
            else:
                dummy_data['status'] = 0
                dummy_data['msg'] = res.get('error', "Unknow server error")
        else:
            dummy_data['status'] = 0
            dummy_data['msg'] = "auth failed/error"

        return ConfigResource.generate_response(self, dummy_data, request)


    def get_resourcegroup_assigned_list(self, request, **kwargs):
        """
        """

        self.method_check(request, allowed=['get'])
        config_id = kwargs.get('cid', "")
        dummy_data = {}

        es_check = ConfigResource.check_auth(request, **kwargs)

        if es_check:
            param = ConfigResource.generate_param(es_check, {'resource_id': config_id, 'category': "ParserRule"})

            res = BackendRequest.list_assigned_resource_group(param)

            if res['result']:
                data = self.rebuild_assigned_resource_group_list(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["list"] = data
            else:
                dummy_data["status"] = 0
                dummy_data["msg"] = res.get('error', 'get source group history error!')
        else:
            dummy_data["status"] = "0"

        return ConfigResource.generate_response(self, dummy_data, request)


    def reourcegroup_filter(self, request, **kwargs):
        """
        """

        self.method_check(request, allowed=['post'])

        req_data = request.POST
        ids = req_data.get('ids', "")
        dummy_data = {}

        es_check = ConfigResource.check_auth(request, **kwargs)

        if es_check:
            # reource group ids is passed to frontend in string form which each id is separated by comma
            param = ConfigResource.generate_param(es_check, {'ids': ids})

            res = BackendRequest.get_batch_config(param)

            if res['result']:
                data = res['list']
                for item in data:
                    item['category_id'] = item['categoryId']
                    del item['categoryId']
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["list"] = data

                permits = []
                for i in data:
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "ParserRule",
                        "action": "Update"
                    })
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "ParserRule",
                        "action": "Delete"
                    })
                permits.append({
                    "target": "ParserRule",
                    "action": "Create"
                })
                permits.append({
                    "target": "DerelictResource",
                    "action": "Possess"
                })
                
                permit_param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_data = {
                    'permits': permits
                }
                permit_res = BackendRequest.batch_permit_can(permit_param, permit_data)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
            else:
                dummy_data['status'] = 0
                dummy_data['msg'] = res.get('error', "Unknow server error")
        else:
            dummy_data['status'] = 0
            dummy_data['msg'] = "auth failed/error"

        return ConfigResource.generate_response(self, dummy_data, request)

    def get_resourcegroup_ungrouped(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'category': "ParserRule",
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.list_derelict_resource_ids(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["ids"] = res['resource_ids']
            else:
                dummy_data["status"] = 0
                dummy_data['msg'] = res.get('error', "Unknow server error")
        else:
            dummy_data["status"] = "0"

        return ConfigResource.generate_response(self, dummy_data, request)

    def _build_config_list(self, data):
        rtn = {}
        for item in data:
            rule_id = item.get("id", "")
            if rule_id:
                if rule_id not in rtn:
                    rtn[rule_id] = {
                        "name": item.get("name", ""),
                        "category_id": item.get("category_id", 1000),
                        "correlation": []
                    }
                    rtn[rule_id]["correlation"] = []
                appnames = "*" if not item.get("appnames", "*") else item.get("appnames", "*")
                tags = "*" if not item.get("tags", "*") else item.get("tags", "*")
                if rtn[rule_id]["category_id"] == 1000 and appnames == "*" and tags == "*":
                    appnames = ""
                    tags = ""
                if appnames and tags:
                    rtn[rule_id]["correlation"].append(appnames+"("+tags+")")
        config_list = []
        for (k, v) in rtn.items():
            config_list.append({
                "id": k,
                "name": v["name"],
                "category_id": v["category_id"],
                "correlation": v["correlation"]
            })
        return config_list


    def search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        dummy_data = {}
        req_data = request.GET
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            group_id = req_data.get("group_id", "")
            if group_id:
                param = {
                    "jid": group_id,
                    "category": "events",
                    "token": es_check["t"],
                    "operator": es_check["u"],
                    "owner_name": es_check["u"],
                    "owner_id": es_check["i"],
                    "sid": req_data.get("sid", ""),
                    "size": 100,
                    "usetable": "true",
                    "page": int(req_data["page"]) - 1
                }
            else:
                param = {
                    "query": req_data["query"],
                    "token": es_check["t"],
                    "operator": es_check["u"],
                    "owner_name": es_check["u"],
                    "owner_id": es_check["i"],
                    "time_range": "-1d,now" if req_data["time_range"] == "," else req_data["time_range"],
                    "order": req_data["order"],
                    "size": 100,
                    "sid": req_data.get("sid", ""),
                    "page": int(req_data.get("page", 0)) - 1,
                    "filter_field": req_data["filters"],
                    "usetable": "true",
                    "category": "events",
                    "field": req_data.get("field", ""),
                    # "source_group": "0811test"
                    "source_group": req_data["sourcegroup"]
                }
            res = BackendRequest.search(param)
            if res["rc"] == 0:
                if res["result"]["sheets"]:
                    type, rst, hits = self._build_events_new(res)
                    dummy_data["table"] = {
                        "head": res["result"]["sheets"].get("_field_infos_", []),
                        "body": rst,
                        "total": res["result"]["sheets"].get("total", 0)
                    }
                    dummy_data["status"] = "1"
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""))
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

    def _build_body(self, res):
        type = res.get("type", "query").lower()
        if type == "stats":
            return res.get("stats")
        elif type == "query":
            return res.get("hits")
        elif type == "transaction":
            return res.get("groups")

    def _build_events(self, logs):
        result = []
        for i in logs:
            tokens = i.get("tokens", [])
            source = i.get("_source", {})
            tmp_fields = i.get("fields", {})
            a_event = {}
            _fields = {}
            _static_fields = {}
            for (k, v) in source.items():
                _fields[k] = v
            # a_event["_tmp_fields"] = tmp_fields
            row = self.multiToOne(_fields)
            result.append(row)
        return result

    def _build_events_new(self, res, with_status="no"):
        print with_status
        type = res.get("type", "stats").lower() if with_status == "no" else "query"
        hits = {}
        if type == "stats":
            body = []
            data = {
                "status": 1,
                "table": {
                    "head": hits.get("_field_infos_", []),
                    "body": body
                }
            }

            return type, res["result"]["sheets"]["rows"], data
        elif type == "query":
            rst = []
            for item in res["result"]["sheets"]["rows"]:
                a_event = item
                tokens = []
                hlight = {"raw_message": ""}
                high_light = hlight["raw_message"]
                hl = re.findall(r'<em>(.*?)</em>', high_light)
                tokens = sorted(tokens, key=len, reverse=True)
                raw_msg = item.get("raw_message", "")
                ori = [{
                    "s": raw_msg,
                    "find": False
                }]
                target = self.contribute(tokens, ori, hl)
                a_event["_cus_raw"] = {
                    "segment_tree": target
                }
                if "_tokens" in a_event:
                    del a_event["_tokens"]
                if "_highlight" in a_event:
                    del a_event["_highlight"]
                rst.append(a_event)
            return type, rst, hits
        elif type == "transaction":
            result = []
            heads = res.get("_field_infos_", [])
            for group in res["result"]["sheets"]["rows"]:
                source = group.get("source", [])
                events = []
                cus_fields = {}
                group_fields = {}
                new_group = group
                key_timestamp = group.get("min_timestamp", 0)
                if "_cache_id_" in new_group:
                    del new_group["_cache_id_"]
                if "_id_" in new_group:
                    del new_group["_id_"]
                if "source" in new_group:
                    del new_group["source"]
                if "max_timestamp" in new_group:
                    del new_group["max_timestamp"]
                if "min_timestamp" in new_group:
                    del new_group["min_timestamp"]

                new_group["hostname"] = []
                new_group["appname"] = []
                new_group["logtype"] = []
                new_group["tag"] = []
                # for a_head in heads:
                #     if not a_head["name"] == "source" and not a_head.get("groupby", False):
                #         group_fields[a_head["name"]] = group[a_head["name"]] if isinstance(group[a_head["name"]],
                #                                                                            list) else [
                #             group[a_head["name"]]]
                #         del new_group[a_head["name"]]
                for event in source:
                    events.append(event["raw_message"])
                    new_group["hostname"].append(event.get("hostname", ""))
                    new_group["appname"].append(event.get("appname", ""))
                    new_group["logtype"].append(event.get("logtype", ""))
                    event["tag"] = event["tag"] if isinstance(event["tag"], list) else [event["tag"]]
                    new_group["tag"] = list(set(new_group["tag"] + event["tag"]))
                    # if event.get("security", {}):
                    #     own_fields["security"] = {}
                    #     own_fields["security"] = self.merge_dict(own_fields["security"], event.get("security", {}))
                    cus_fields = self.merge_dict(cus_fields, event)
                    if "hostname" in cus_fields:
                        del cus_fields["hostname"]
                    if "appname" in cus_fields:
                        del cus_fields["appname"]
                    if "logtype" in cus_fields:
                        del cus_fields["logtype"]
                    if "tag" in cus_fields:
                        del cus_fields["tag"]
                    del cus_fields["raw_message"]

                new_group["hostname"] = list(set(new_group["hostname"]))
                new_group["appname"] = list(set(new_group["appname"]))
                new_group["logtype"] = list(set(new_group["logtype"]))

                new_group["events"] = events
                new_group["timestamp"] = key_timestamp
                new_group["fields"] = cus_fields
                new_group["group_fields"] = group_fields
                result.append(new_group)
            return type, result, hits


    def contribute(self, tokens, sor, hl):
        result = []
        find = False
        if len(tokens) > 500:
            return sor
        for i in sor:
            if not i["find"] and len(tokens) > 0 and re.search(tokens[0], i["s"], re.IGNORECASE):
                a_str = i["s"]
                m = re.search(tokens[0], i["s"], re.IGNORECASE)
                start = m.start()
                lens = len(tokens[0])
                st = a_str[0:start]
                cr = a_str[start:(start + lens)]
                ed = a_str[(start + lens):len(a_str)]
                if len(st) != 0:
                    result.append({
                        "s": st,
                        "find": False
                    })
                if len(cr) != 0:
                    result.append({
                        "s": cr,
                        "find": True,
                        "highlight": cr in hl
                    })
                if len(ed) != 0:
                    result.append({
                        "s": ed,
                        "find": False
                    })
                find = True
            else:
                result.append(i)
        if len(tokens) > 1:
            del tokens[0]
            result = self.contribute(tokens, result, hl)
        return result


    def multiToOne(self, fl, parent=""):
        # convert dict which likes {"a":{"b":1}} to {"a.b":1}
        result = {}
        for (k,v) in fl.items():
            to_next = parent+"."+k if parent else k
            if isinstance(v, dict):
                result.update(self.multiToOne(v, to_next))
            else:
                result[to_next] = v
        return result


    def zone(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            path = os.path.dirname(os.path.realpath(__file__))
            json_data = open(path + '/timezone.json')
            data = json.load(json_data)
            dummy_data["status"] = "1"
            dummy_data["list"] = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def config_auto_regex(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            post_data = parser.parse(request.POST.urlencode().encode('utf-8'))
            event = post_data.get("event", "")
            cus_field = post_data.get("cusField", {})
            multi = post_data.get("multi", {}).values()
            examples = {}
            markedEvents = []
            event_dict = {
                "_event": {
                    "_raw": event.decode('utf8')
                }
            }
            for item in cus_field:
                event_dict[item] = [int(x) for x in cus_field[item].values()]
            # one_raw = dict(event_dict, **cus_field)
            one_raw = event_dict
            markedEvents.append(one_raw)

            for item in multi:
                one_item = {
                    "_event": {
                        "_raw": item["event"].decode('utf8')
                    }
                }
                if item.get("cusField", {}):
                    for key in item["cusField"]:
                        one_item[key] = item["cusField"][key].values()
                markedEvents.append(one_item)

            rules = learn("_raw", markedEvents, [], examples, "")
            rtn_reg = []
            rtn_fields = []
            rtn_logs = []
            error_code = "000"
            for _e in markedEvents:
                for rule in rules:
                    extractions = rule.findExtractions(_e)
                    if len(extractions) > 0:
                        matched_fields = extractions
                        rtn_field = {}
                        for fi in matched_fields:
                            if fi in _e:
                                rtn_field[fi] = matched_fields[fi]
                        rtn_fields.append(rtn_field)
                        rtn_reg.append(rule.getJavaRegexStr())
                        rtn_logs.append(_e["_event"]["_raw"])
                        break
                    else:
                        rtn_fields.append({})
                        rtn_reg.append("")
                        rtn_logs.append(_e["_event"]["_raw"])
                        error_code = "001"
                        logger.error("rule didn't find:", _e)
                        break
            dummy_data["status"] = "1"
            dummy_data["error_code"] = error_code
            dummy_data["fields"] = rtn_fields
            dummy_data["rules"] = rtn_reg
            dummy_data["events"] = rtn_logs
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def config_auto_parse(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            post_data = parser.parse(request.POST.urlencode().encode('utf-8'))
            event = post_data.get("event", "")
            cus_rule = post_data.get("rule", "")
            expect_regex = [cus_rule]
            event_dict = {
                "_event": {
                    "_raw": event
                }
            }
            rule = JavaRegexRule(expect_regex)
            result = rule.findExtractions(event_dict)
            rtn_reg = [cus_rule]
            rtn_fields = [result]
            rtn_logs = [event]
            error_code = "000"
            dummy_data["status"] = "1"
            dummy_data["error_code"] = error_code
            dummy_data["fields"] = rtn_fields
            dummy_data["rules"] = rtn_reg
            dummy_data["events"] = rtn_logs
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def config_auto_regex_verify_all(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            post_data = parser.parse(request.POST.urlencode().encode('utf-8'))
            event = post_data.get("event", "")
            cus_field = post_data.get("cusField", {})
            events = post_data.get("samples", {}).values()

            examples = {}
            markedEvents = []
            event_dict = {
                "_event": {
                    "_raw": event
                }
            }
            for item in cus_field:
                event_dict[item] = [int(x) for x in cus_field[item].values()]
            # one_raw = dict(event_dict, **cus_field)
            one_raw = event_dict
            markedEvents.append(one_raw)
            rules = learn("_raw", markedEvents, [], examples, "")
            verify_result = []
            for _e in events:
                for rule in rules:
                    temp = {
                        "_event": {
                            "_raw": _e
                        }
                    }
                    extractions = rule.findExtractions(temp)
                    if len(extractions) > 0:
                        verify_result.append("yes")
                        break
                    else:
                        verify_result.append("no")
                        break
            dummy_data["status"] = "1"
            dummy_data["verified"] = verify_result
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def config_verify(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            post_data = parser.parse(request.POST.urlencode().encode('utf-8'))
            logtype = post_data.get('logtype', '')
            param = self.build_param(post_data)
            logger.info("Verify_config_post_data: %s", json.dumps(param))
            if param:
                res = BackendRequest.verify_logtype({
                    # "token": es_check['t'],
                    "domain": es_check['d'],
                    "logtype": logtype
                }, param)
                if res['result']:
                    data = res.get('contents', [])
                    dummy_data["status"] = "1"
                    dummy_data["data"], dummy_data["keys"], dummy_data["statistics"] = build_verified_data(data)
                else:
                    dummy_data = err_data.build_error({}, "verify failed")
            else:
                data = err_data.build_error({}, "verify failed")
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def config_active(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        appname = kwargs['cf_name']
        enable = kwargs['cf_tg']
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            res = BackendRequest.toggle_logtype({
                "token": es_check["t"],
                "operator": es_check["u"],
                "name": appname,
                "enable": enable
            })

            if res['result']:
                dummy_data["status"] = "1"
            else:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "active config error!"

        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "active config error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def config_check_appname(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        appname = kwargs['cf_name']
        if es_check:
            cf_param = {
                'name': appname,
                'token': es_check['t'],
                'operator': es_check['u']
            }
            cf_res = BackendRequest.get_logtype(cf_param)
            if cf_res['result']:
                item = cf_res.get('content', {})['conf']
                if item:
                    dummy_data["status"] = "1"
                    dummy_data["check"] = "1"
                else:
                    dummy_data["status"] = "1"
                    dummy_data["check"] = "0"
            else:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "get config error!"
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "get config error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def config_security_support(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            res = BackendRequest.get_func_auth({
                "token": es_check["t"],
                "operator": es_check["u"]
            })
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["enable"] = res["results"]["enable_security"]
            else:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "get enable_security info error!"

        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "is not authenticated!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def config_toggle_security(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        appname = kwargs['cf_name']
        enable = kwargs['cf_security']
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            res = BackendRequest.toggle_security({
                "token": es_check["t"],
                "operator": es_check["u"],
                "name": appname,
                "enable": enable
            })

            if res['result']:
                dummy_data["status"] = "1"
            else:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "active config error!"

        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "active config error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    @staticmethod
    def build_param(post_data):

        custom_grok = post_data.get('custom_grok', {})
        sample_logs = post_data.get('sample_logs', []).values()
        # sample_logs = ["1234", "1234"]
        conf = post_data.get('conf', {}).values()

        # date = post_data.get('date', {})
        # grok = post_data.get('grok', {})
        # kv = post_data.get('kv', {})
        # split = post_data.get('split', {})
        # numeric = post_data.get('numeric', {})

        param = {
            'rule': [],
            'appname': post_data.get('appname', ""),
            'hostname': post_data.get('hostname', ""),
            'tag': post_data.get('tag', ""),
            'source': post_data.get('source', "")
        }
        if sample_logs:
            param['sample_logs'] = sample_logs
        if custom_grok:
            param['grok'] = custom_grok
        if conf:
            for item in conf:
                if item['type'] == 'reg':
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        if item.get('multiExpression', ''):
                            param['rule'].append({
                                "grok": {
                                    "rule": [{
                                        "source": item.get('curSource', ''),
                                        "multiline":  True,
                                        "condition": {
                                            "rule": _condition
                                        },
                                        "pattern": [[
                                            item.get('expression', '')
                                        ], item.get('multiExpression').split(",")]
                                    }]
                                }
                            })
                        else:
                            param['rule'].append({
                                "grok": {
                                    "rule": [{
                                        "source": item.get('curSource', ''),
                                        "multiline":  False,
                                        "condition": {
                                            "rule": _condition
                                        },
                                        "pattern": [[
                                            item.get('expression', '')
                                        ]]
                                    }]
                                }
                            })
                    else:
                        if item.get('multiExpression', ''):
                            param['rule'].append({
                                "grok": {
                                    "rule": [{
                                        "source": item.get('curSource', ''),
                                        "multiline":  True,
                                        "pattern": [[
                                            item.get('expression', '')
                                        ], item.get('multiExpression').split(",")]
                                    }]
                                }
                            })
                        else:
                            param['rule'].append({
                                "grok": {
                                    "rule": [{
                                        "source": item.get('curSource', ''),
                                        "multiline":  False,
                                        "pattern": [[
                                            item.get('expression', '')
                                        ]]
                                    }]
                                }
                            })
                if item['type'] == "kv":
                    key_prefix = item.get('expression_keyPrefix', '')
                    key_prefix = key_prefix.split(",") if key_prefix else []
                    reserved_key = item.get('expression_keyReserved', '')
                    reserved_key = reserved_key.split(",") if reserved_key else []
                    drop_key = item.get('expression_keyDrop', '')
                    drop_key = drop_key.split(",") if drop_key else []
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        if item.get('expression_keyPrefix', ''):
                            param["rule"].append({
                                "kv": {
                                    "rule": [{
                                        "source": item.get('curSource', ''),
                                        "field_split": [item.get('expression_fieldSplit', '')],
                                        "value_split": [item.get('expression_kvSplit', '')],
                                        "drop_key_prefix": key_prefix,
                                        "reserved_key": reserved_key,
                                        "condition": {
                                            "rule": _condition
                                        },
                                        "drop_key": drop_key
                                    }]
                                }
                            })
                        else:
                            param["rule"].append({
                                "kv": {
                                    "rule": [{
                                        "source": item.get('curSource', ''),
                                        "field_split": [item.get('expression_fieldSplit', '')],
                                        "value_split": [item.get('expression_kvSplit', '')],
                                        "reserved_key": reserved_key,
                                        "condition": {
                                            "rule": _condition
                                        },
                                        "drop_key": drop_key
                                    }]
                                }
                            })
                    else:
                        if item.get('expression_keyPrefix', ''):
                            param["rule"].append({
                                "kv": {
                                    "rule": [{
                                        "source": item.get('curSource', ''),
                                        "field_split": [item.get('expression_fieldSplit', '')],
                                        "value_split": [item.get('expression_kvSplit', '')],
                                        "drop_key_prefix": key_prefix,
                                        "reserved_key": reserved_key,
                                        "drop_key": drop_key
                                    }]
                                }
                            })
                        else:
                            param["rule"].append({
                                "kv": {
                                    "rule": [{
                                        "source": item.get('curSource', ''),
                                        "field_split": [item.get('expression_fieldSplit', '')],
                                        "value_split": [item.get('expression_kvSplit', '')],
                                        "reserved_key": reserved_key,
                                        "drop_key": drop_key
                                    }]
                                }
                            })

                if item['type'] == "kv_match":
                    key_prefix = item.get('expression_keyPrefix', '')
                    key_prefix = key_prefix.split(",") if key_prefix else []
                    reserved_key = item.get('expression_keyReserved', '')
                    reserved_key = reserved_key.split(",") if reserved_key else []
                    drop_key = item.get('expression_keyDrop', '')
                    drop_key = drop_key.split(",") if drop_key else []
                    match_groups = item.get('kvMatch_matchGroup', []).values()
                    kv_match_group = []
                    print match_groups
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    for inner_item in match_groups:
                        kv_match_group.append({
                            "key_regex": inner_item["key_regex"],
                            "value_regex": inner_item["value_regex"],
                            "value_split": inner_item["value_split"].split(",")
                        })
                    if _condition["field"]:
                        param["rule"].append({
                            "kv": {
                                "match_kv_rule": [{
                                    "source": item.get('curSource', ''),
                                    "kv_match_group": kv_match_group,
                                    "drop_key_prefix": key_prefix,
                                    "reserved_key": reserved_key,
                                    "condition": {
                                            "rule": _condition
                                        },
                                    "drop_key": drop_key,
                                    "find_first_only": False if item.get('kvMatch_findFirstOnly', 'false') == 'false' else True,
                                    "reserve_all_values_for_one_key": False if item.get('kvMatch_reserveAllValues', 'false') == 'false' else True
                                }]
                            }
                        })
                    else:
                        param["rule"].append({
                            "kv": {
                                "match_kv_rule": [{
                                    "source": item.get('curSource', ''),
                                    "kv_match_group": kv_match_group,
                                    "drop_key_prefix": key_prefix,
                                    "reserved_key": reserved_key,
                                    "drop_key": drop_key,
                                    "find_first_only": False if item.get('kvMatch_findFirstOnly', 'false') == 'false' else True,
                                    "reserve_all_values_for_one_key": False if item.get('kvMatch_reserveAllValues', 'false') == 'false' else True
                                }]
                            }
                        })

                if item['type'] == 'split':
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        param['rule'].append({
                            "split": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "condition": {
                                            "rule": _condition
                                        },
                                    "split_string": item.get('expression', ''),
                                    "names": item['names'].split(',') if item.get('names', '') else []
                                }]
                            }
                        })
                    else:
                        param['rule'].append({
                            "split": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "names": item['names'].split(',') if item.get('names', '') else [],
                                    "split_string": item.get('expression', '')
                                }]
                            }
                        })
                if item['type'] == "timestamp":
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    source = item.get('curSource', '')
                    if _condition["field"]:
                        if source == "raw_message":
                            param['rule'].append({
                                "auto_match_date": {
                                    "source": source,
                                    "condition": {
                                            "rule": _condition
                                        },
                                    "prefix": item.get("prefix", ""),
                                    "max_lookahead": item.get("max_lookahead", "80"),
                                    "zone": item.get("zone", "Asia/Shanghai"),
                                    "locale": item.get("locale", "en"),
                                    "rule": [item.get('expression', '')]
                                }
                            })
                        else:
                            param['rule'].append({
                                "date": {
                                    "source": source,
                                    "condition": {
                                            "rule": _condition
                                        },
                                    "prefix": item.get("prefix", ""),
                                    "max_lookahead": item.get("max_lookahead", "80"),
                                    "zone": item.get("zone", "Asia/shanghai"),
                                    "locale": item.get("locale", "en"),
                                    "rule": [item.get('expression', '')]
                                }
                            })
                    else:
                        if source == "raw_message":
                            param['rule'].append({
                                "auto_match_date": {
                                    "source": source,
                                    "prefix": item.get("prefix", ""),
                                    "max_lookahead": item.get("max_lookahead", "80"),
                                    "zone": item.get("zone", "Asia/Shanghai"),
                                    "locale": item.get("locale", "en"),
                                    "rule": [item.get('expression', '')]
                                }
                            })
                        else:
                            param['rule'].append({
                                "date": {
                                    "source": source,
                                    "prefix": item.get("prefix", ""),
                                    "max_lookahead": item.get("max_lookahead", "80"),
                                    "zone": item.get("zone", "Asia/shanghai"),
                                    "locale": item.get("locale", "en"),
                                    "rule": [item.get('expression', '')]
                                }
                            })
                if item['type'] == "json":
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        if item.get('curSource', ''):
                            param['rule'].append({
                                "json": {
                                    "rule": [{
                                        "condition": {
                                            "rule": _condition
                                        },
                                        "source": item.get('curSource', '')
                                    }]
                                }
                            })
                        else:
                            param['rule'].append({
                                "json": {
                                    "rule": [{
                                        "condition": {
                                            "rule": _condition
                                        }
                                    }]
                                }
                            })
                    else:
                        if item.get('curSource', ''):
                            param['rule'].append({
                                "json": {
                                    "rule": [{
                                        "source": item.get('curSource', '')
                                    }]
                                }
                            })
                        else:
                            param['rule'].append({
                                "json": {
                                    "rule": [{
                                    }]
                                }
                            })
                if item['type'] == "syslog_priority":
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        if item.get('curSource', ''):
                            param['rule'].append({
                                "syslog_priority": {
                                    "condition": {
                                            "rule": _condition
                                        },
                                    "source": item.get('curSource', '')
                                }
                            })
                        else:
                            param['rule'].append({
                                "syslog_priority": {
                                    "rule": [{
                                        "condition": {
                                            "rule": _condition
                                        }
                                    }]
                                }
                            })
                    else:
                        if item.get('curSource', ''):
                            param['rule'].append({
                                "syslog_priority": {
                                    "source": item.get('curSource', '')
                                }
                            })
                        else:
                            param['rule'].append({
                                "syslog_priority": {
                                    "rule": [{}]
                                }
                            })
                if item['type'] == "xml":
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        if item.get('curSource', ''):
                            param['rule'].append({
                                "xml": {
                                    "rule": [{
                                        "condition": {
                                            "rule": _condition
                                        },
                                        "source": item.get('curSource', '')
                                    }]
                                }
                            })
                        else:
                            param['rule'].append({
                                "xml": {
                                    "rule": [{
                                        "condition": {
                                            "rule": _condition
                                        }
                                    }]
                                }
                            })
                    else:
                        if item.get('curSource', ''):
                            param['rule'].append({
                                "xml": {
                                    "rule": [{
                                        "source": item.get('curSource', '')
                                    }]
                                }
                            })
                        else:
                            param['rule'].append({
                                "xml": {
                                    "rule": [{}]
                                }
                            })
                if item['type'] == "geo":
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        param['rule'].append({
                            "geo": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "condition": {
                                            "rule": _condition
                                        },
                                    "target": item.get('target', 'geo'),
                                    "field": ["all"]
                                }]
                            }
                        })
                    else:
                        param['rule'].append({
                            "geo": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "target": item.get('target', 'geo'),
                                    "field": ["all"]
                                }]
                            }
                        })
                if item['type'] == "phone":
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        param['rule'].append({
                            "phone": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "condition": {
                                            "rule": _condition
                                        },
                                    "target": item.get('target', 'phone'),
                                    "field": ["all"]
                                }]
                            }
                        })
                    else:
                        param['rule'].append({
                            "phone": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "target": item.get('target', 'phone'),
                                    "field": ["all"]
                                }]
                            }
                        })
                if item['type'] == "telephone":
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        param['rule'].append({
                            "telephone": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "condition": {
                                            "rule": _condition
                                        },
                                    "target": item.get('target', 'phone'),
                                    "field": ["all"]
                                }]
                            }
                        })
                    else:
                        param['rule'].append({
                            "telephone": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "target": item.get('target', 'phone'),
                                    "field": ["all"]
                                }]
                            }
                        })
                if item['type'] == "url":
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        param['rule'].append({
                            "urldecode": {
                                "rule": [{
                                    "condition": {
                                            "rule": _condition
                                        },
                                    "source": item.get('curSource', '')
                                }]
                            }
                        })
                    else:
                        param['rule'].append({
                            "urldecode": {
                                "rule": [{
                                    "source": item.get('curSource', '')
                                }]
                            }
                        })
                if item['type'] == "format":
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    _params = item.get("curSource", "").split(",") if item.get("curSource", "") else []
                    if _condition["field"]:
                        param['rule'].append({
                            "format": {
                                "rule": [{
                                    "condition": {
                                            "rule": _condition
                                        },
                                    "printf": item.get('expression', ''),
                                    "target": item.get('target', ''),
                                    "params": _params
                                }]
                            }
                        })
                    else:
                        param['rule'].append({
                            "format": {
                                "rule": [{
                                    "printf": item.get('expression', ''),
                                    "target": item.get('target', ''),
                                    "params": _params
                                }]
                            }
                        })
                if item['type'] == "ua":
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        param['rule'].append({
                            "ua": {
                                "condition": {
                                    "rule": _condition
                                },
                                "source": item.get('curSource', '')
                            }
                        })
                    else:
                        param['rule'].append({
                            "ua": {
                                "source": item.get('curSource', '')
                            }
                        })
                if item['type'] == "num":
                    tmp_sList = item.get('curSource', '').split(',')
                    tmp_ruleList = []
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        for s in tmp_sList:
                            tmp_ruleList.append(
                                {
                                    "source": s,
                                    "condition": {
                                        "rule": _condition
                                    },
                                    "numeric_type": item.get('expression', ''),
                                    "radix": int(item.get("radix", 10))
                                }
                            )
                    else:
                        for s in tmp_sList:
                            tmp_ruleList.append(
                                {
                                    "source": s,
                                    "numeric_type": item.get('expression', ''),
                                    "radix": int(item.get("radix", 10))
                                }
                            )
                    param['rule'].append({
                        "numeric": {
                            "rule": tmp_ruleList
                        }
                    })
                if item['type'] == "dict":
                    ext_field = item.get('dictExtField').split(",") if item.get('dictExtField', '') else []
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        param['rule'].append({
                            "dict": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "condition": {
                                        "rule": _condition
                                    },
                                    "id": item.get('curDict', ''),
                                    "field": item.get('dictField', ''),
                                    "ext_fields": ext_field
                                }]
                            }
                        })
                    else:
                        param['rule'].append({
                            "dict": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "id": item.get('curDict', ''),
                                    "field": item.get('dictField', ''),
                                    "ext_fields": ext_field
                                }]
                            }
                        })
                if item['type'] == "converter":
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        param['rule'].append({
                            "converter": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "condition": {
                                        "rule": _condition
                                    },
                                    "op_type": "long2ip"
                                }]
                            }
                        })
                    else:
                        param['rule'].append({
                            "converter": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "op_type": "long2ip"
                                }]
                            }
                        })
                if item['type'] == "hex":
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        param['rule'].append({
                            "hex": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "condition": {
                                        "rule": _condition
                                    },
                                    "codec_type": item.get('codecType', 'GBK'),
                                    "split_string": " "
                                }]
                            }
                        })
                    else:
                        param['rule'].append({
                            "hex": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "codec_type": item.get('codecType', 'GBK'),
                                    "split_string": " "
                                }]
                            }
                        })
                if item['type'] == 'replacer':
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        param['rule'].append({
                            "replacer": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "condition": {
                                        "rule": _condition
                                    },
                                    "regex": item.get('expression', ''),
                                    "replacement": item.get('replacement', ''),
                                    "replace_first": False if item.get('replaceFirst', 'false') == 'false' else True,
                                    "anonymity": False
                                }]
                            }
                        })
                    else:
                        param['rule'].append({
                            "replacer": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "regex": item.get('expression', ''),
                                    "replacement": item.get('replacement', ''),
                                    "replace_first": False if item.get('replaceFirst', 'false') == 'false' else True,
                                    "anonymity": False
                                }]
                            }
                        })
                if item['type'] == 'desensitize':
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        param['rule'].append({
                            "replacer": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "condition": {
                                        "rule": _condition
                                    },
                                    "regex": item.get('expression', ''),
                                    "replacement": item.get('replacement', ''),
                                    "regex_prefix": item.get("regex_prefix", ""),
                                    "regex_suffix": item.get("regex_suffix", ""),
                                    "replace_first": False if item.get('replaceFirst', 'false') == 'false' else True,
                                    "anonymity": True
                                }]
                            }
                        })
                    else:
                        param['rule'].append({
                            "replacer": {
                                "rule": [{
                                    "source": item.get('curSource', ''),
                                    "regex": item.get('expression', ''),
                                    "replacement": item.get('replacement', ''),
                                    "regex_prefix": item.get("regex_prefix", ""),
                                    "regex_suffix": item.get("regex_suffix", ""),
                                    "replace_first": False if item.get('replaceFirst', 'false') == 'false' else True,
                                    "anonymity": True
                                }]
                            }
                        })
                if item['type'] == "remove":
                    _condition = item.get('condition', {
                        "field": "",
                        "condition": "",
                        "value": ""
                    })
                    if _condition["field"]:
                        param['rule'].append({
                            "remove": {
                                "rule": [{
                                    "condition": {
                                            "rule": _condition
                                        },
                                    "source": [item.get('curSource', '')]
                                }]
                            }
                        })
                    else:
                        param['rule'].append({
                            "remove": {
                                "rule": [{
                                    "source": [item.get('curSource', '')]
                                }]
                            }
                        })


                # if item.date:
                #     param['conf'][logtype]['date'] = date
                # if grok:
                #     param['conf'][logtype]['grok'] = grok
                # if kv:
                #     param['conf'][logtype]['kv'] = kv
                # if split:
                #     param['conf'][logtype]['split'] = split
                # if numeric:
                #     param['conf'][logtype]['numeric'] = numeric
        else:
            return {}
        return param


def build_verified_data(data):
    duplicate_keys = []
    all_keys = []
    statistics = {}
    for item in data:
        fields = item.get("fields", {})
        expanded, keys = expand_key(fields, "")
        item["expanded"] = expanded
        duplicate_keys = list(set(duplicate_keys+keys))
        all_keys = all_keys + keys
        for x, y in expanded.items():
            if x in statistics:
                statistics[x] = statistics[x] + y
            else:
                statistics[x] = y
    new_statistics = {}
    for k, v in statistics.items():
        new_statistics[k] = dict(Counter(v))

    # statistics = dict(Counter(all_keys))
    return data, duplicate_keys, new_statistics


def expand_key(obj, root):
    exp = {}
    keys = []
    if not obj:
        return exp, keys
    if root:
        keys.append(root)
    for k, v in obj.items():
        if isinstance(v, types.DictionaryType):
            new_k = root + '.' + k if root else k
            children_exp, children_keys = expand_key(v, new_k)
            keys = keys + children_keys
            new_exp = dict(exp, **children_exp)
            exp = new_exp
        elif isinstance(v, types.ListType) and len(v) > 0 and isinstance(v[0], types.DictionaryType):
            for inner_v in v:
                new_k = root + '.' + k if root else k
                children_exp, children_keys = expand_key(inner_v, new_k)
                keys = keys + children_keys
                new_exp = exp.copy()
                for one_k, one_v in children_exp.items():
                    if one_k in new_exp:
                        new_exp[one_k] = new_exp[one_k] + one_v
                    else:
                        new_exp[one_k] = one_v
                exp = new_exp
        else:
            if root:
                exp[root + '.' + k] = v if isinstance(v, types.ListType) else [v]
                keys.append(root + '.' + k)
            else:
                exp[k] = v if isinstance(v, types.ListType) else [v]
                keys.append(k)
    return exp, keys


def get_keys(obj, root):
    keys = []
    if not obj:
        return []
    if root:
        keys.append(root)
    for k, v in obj.items():
        if isinstance(v, types.DictionaryType):
            children = get_keys(v, k)
            keys = keys + children
        else:
            if root:
                keys.append(root + '.' + k)
            else:
                keys.append(k)
    return keys
