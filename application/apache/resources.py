# -*- coding: utf-8 -*-
# mayangguang (ma.yanguang@yottabyte.cn)
# 2015/03/25
# Copyright 2015 Yottabyte
# file description : security api

from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
import json
import requests
import ConfigParser
import os

err_data = ContributeErrorData()

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    FRONTEND_URL = cf.get('frontend', 'frontend_url')
except Exception, e:
    FRONTEND_URL = 'http://localhost'


class ApacheResource(Resource):
    class Meta:
        resource_name = 'apache'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/uv/$" % (self._meta.resource_name),
                self.wrap_view('uv'), name="api_uv"),
            url(r"^(?P<resource_name>%s)/isp_ip_to_resp_len/$" % (self._meta.resource_name),
                self.wrap_view('isp_ip_to_resp_len'), name="api_isp_ip_to_resp_len"),
            url(r"^(?P<resource_name>%s)/service_res/$" % (self._meta.resource_name),
                self.wrap_view('service_res'), name="api_service_res"),
        ]


    def uv(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        time_range = request.POST.get('time_range')

        #print "###############time_range: ", time_range

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        #print "############es_check: ", es_check
        if es_check:
            time_range = time_range
            owner_name = es_check.get('u')
            owner_id = es_check.get('i')
            token = es_check.get('t')
            url = FRONTEND_URL + 'es_status/?category=api_stat&owner_name=' + owner_name + '&source_group=all&act=search&owner_id=' + owner_id + '&time_range=' + time_range + '&order&token=' + token + '&query=*&filter_field&page=0&size=20'
            #print "###############url: ", url
            data = {
                "query": {
                    "distinct_count": {
                        "cardinality": {
                            "field": "apache.clientip"
                        }
                    }
                }
            }

            data = json.dumps(data)
            result = requests.post(url, data=data)
            #print "result.status_code: ", result.status_code

            if result.status_code == 200:
                res = result.json()
                #print "res: ", res
                if res['result']:
                    dummy_data["status"] = 1
                    count = res.get('data').get('distinct_count').get('value')
                    dummy_data["data"] = {'count': count}
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
            else:
                data = err_data.build_error({})
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def isp_ip_to_resp_len(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        type = request.POST.get('type')
        time_range = request.POST.get('time_range')

        #print "###############time_range: ", time_range

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        #print "############es_check: ", es_check
        if es_check:
            time_range = time_range
            owner_name = es_check.get('u')
            owner_id = es_check.get('i')
            token = es_check.get('t')
            url = FRONTEND_URL + 'es_status/?category=api_stat&owner_name=' + owner_name + '&source_group=all&act=search&owner_id=' + owner_id + '&time_range=' + time_range + '&order&token=' + token + '&query=*&filter_field&page=0&size=20'
            #print "###############url: ", url
            data = {
                "query": {
                    "missing_result": {
                        "missing": {
                            "field": "apache.resp_len"
                        }
                    },
                    "split_result": {
                        "terms": {
                            "field": "apache.clientip" if type == 'ip_resp_len' else 'apache.geo.isp',
                            "order": {"resp_len_stats_result": "desc"},
                            "size": 10
                        },
                        "group": {
                            "resp_len_stats_result": {
                                "sum": {
                                    "field": "apache.resp_len"
                                }
                            }
                        }
                    }
                }
            }
            data = json.dumps(data)
            result = requests.post(url, data=data)
            #print "result.status_code: ", result.status_code

            if result.status_code == 200:
                res = result.json()
                #print "res: ", res
                if res['result']:
                    dummy_data["status"] = 1
                    resData = []
                    if res.get('total') != res.get('data').get('missing_result').get('doc_count'):
                        buckets = res.get('data').get('split_result').get('buckets')
                        #print "##############buckets", buckets
                        for bucket in buckets:
                            item = {
                                'key': bucket.get('key'),
                                'value': bucket.get('resp_len_stats_result').get('value'),
                            }
                            resData.append(item)
                    dummy_data["data"] = sorted(resData, key=lambda k: k['value'],reverse=True)
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
            else:
                data = err_data.build_error({})
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def service_res(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        type = request.POST.get('type')
        time_range = request.POST.get('time_range')

        #print "###############time_range: ", time_range

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        #print "############es_check: ", es_check
        if es_check:
            time_range = time_range
            owner_name = es_check.get('u')
            owner_id = es_check.get('i')
            token = es_check.get('t')
            url = FRONTEND_URL + 'es_status/?category=api_stat&owner_name=' + owner_name + '&source_group=all&act=search&owner_id=' + owner_id + '&time_range=' + time_range + '&order&token=' + token + '&query=*&filter_field&page=0&size=20'
            #print "###############url: ", url
            data = {
                "query": {
                    "missing_result": {
                        "missing": {
                            "field": "apache."+type
                        }
                    },
                    "terms_nest_result": {
                        "terms": {
                            "field": "apache.request_path:string",
                            "order": {"len_avg.avg": "desc"},
                            "size": 10
                        },
                        "group": {
                            "len_avg": {
                                "stats": {
                                    "field": "apache.%s:number" % type
                                }
                            }
                        }
                    }
                }
            }
            data = json.dumps(data)
            result = requests.post(url, data=data)
            #print "result.status_code: ", result.status_code

            if result.status_code == 200:
                res = result.json()
                #print "res: ", res
                if res['result']:
                    dummy_data["status"] = 1
                    resData = []
                    #print "###############121212res: ",res
                    if res.get('total') != res.get('data').get('missing_result').get('doc_count'):
                        buckets = res.get('data').get('terms_nest_result').get('buckets')
                        for bucket in buckets:
                            item = {
                                'key': bucket.get('key'),
                                'value': bucket.get('len_avg').get('avg'),
                            }
                            resData.append(item)
                    dummy_data["data"] = sorted(resData, key=lambda k: k['value'],reverse=True)
                else:
                    data = err_data.build_error(res)
                    dummy_data = data
            else:
                data = err_data.build_error({})
                dummy_data = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp




