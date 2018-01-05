from tastypie.resources import Resource
from django.conf.urls import url
from django.core.servers.basehttp import FileWrapper
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.variable.resources import MyVariable
import os
import datetime
import time
import math
from django.http import HttpResponse
__author__ = 'zhaixiaoyu'
err_data = ContributeErrorData()


class PaymentResource(Resource):
    # Just like a Django ``Form`` or ``Model``, we're defining all the
    # fields we're going to handle with the API here.

    class Meta:
        resource_name = 'payment'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/list/beneficiary/$" % self._meta.resource_name,
                self.wrap_view('payment_beneficiary_list'), name="payment_beneficiary_list"),
            url(r"^(?P<resource_name>%s)/list/appname/$" % self._meta.resource_name,
                self.wrap_view('payment_appname_list'), name="payment_appname_list"),
            url(r"^(?P<resource_name>%s)/list/appname/unassigned/$" % self._meta.resource_name,
                self.wrap_view('payment_appname_unassigned_list'), name="payment_appname_unassigned_list"),
            url(r"^(?P<resource_name>%s)/list/appname/assigned/$" % self._meta.resource_name,
                self.wrap_view('payment_appname_assigned_list'), name="payment_appname_assigned_list"),
            url(r"^(?P<resource_name>%s)/list/appname/(?P<bid>[\w\d_.\-@]+)/$" % self._meta.resource_name,
                self.wrap_view('payment_appname_by_beneficiary'), name="payment_appname_by_beneficiary"),
            url(r"^(?P<resource_name>%s)/beneficiary/assign/(?P<bid>[\w\d_.\-@]+)/$" % self._meta.resource_name,
                self.wrap_view('payment_beneficiary_assign'), name="payment_beneficiary_assign"),
            url(r"^(?P<resource_name>%s)/beneficiary/detail/(?P<bid>[\w\d_.\-@]+)/$" % self._meta.resource_name,
                self.wrap_view('payment_beneficiary_detail'), name="payment_beneficiary_detail"),
            url(r"^(?P<resource_name>%s)/beneficiary/delete/(?P<bid>[\w\d_.\-@]+)/$" % self._meta.resource_name,
                self.wrap_view('payment_beneficiary_delete'), name="payment_beneficiary_delete"),
            url(r"^(?P<resource_name>%s)/beneficiary/new/$" % self._meta.resource_name,
                self.wrap_view('payment_beneficiary_new'), name="payment_beneficiary_new"),
            url(r"^(?P<resource_name>%s)/beneficiary/usage/(?P<bid>[\w\d_.\-@]+)/$" % self._meta.resource_name,
                self.wrap_view('payment_beneficiary_usage'), name="payment_beneficiary_usage"),
            url(r"^(?P<resource_name>%s)/beneficiary/daily/(?P<bid>[\w\d_.\-@]+)/$" % self._meta.resource_name,
                self.wrap_view('payment_beneficiary_daily'), name="payment_beneficiary_daily"),
            url(r"^(?P<resource_name>%s)/beneficiary/(?P<bid>[\w\d_.\-@]+)/$" % self._meta.resource_name,
                self.wrap_view('payment_beneficiary_update'), name="payment_beneficiary_update"),
            url(r"^(?P<resource_name>%s)/appname/detail/(?P<aid>[\w\d_.\-@]+)/$" % self._meta.resource_name,
                self.wrap_view('payment_appname_detail'), name="payment_appname_detail"),
            url(r"^(?P<resource_name>%s)/appname/new/$" % self._meta.resource_name,
                self.wrap_view('payment_appname_new'), name="payment_appname_new"),
            url(r"^(?P<resource_name>%s)/appname/assign/(?P<aid>[\w\d_.\-@]+)/$" % self._meta.resource_name,
                self.wrap_view('payment_appname_assign'), name="payment_appname_assign"),
        ]

    def payment_beneficiary_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }

            res = BackendRequest.get_beneficiary_list(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["total"] = len(res['list'])
                dummy_data["beneficiary_list"] = res['list']
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

    def payment_appname_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_appname_list(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["total"] = len(res['list'])
                dummy_data["appname_list"] = res['list']
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

    def payment_appname_unassigned_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_unassigned_appname_list(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["total"] = len(res['list'])
                dummy_data["appname_list"] = res['list']
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

    def payment_appname_assigned_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_assigned_appname_list(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["total"] = len(res['list'])
                dummy_data["appname_list"] = res['list']
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

    def payment_appname_by_beneficiary(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        bid = kwargs['bid']
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'beneficiary_id': bid
            }
            res = BackendRequest.get_appname_list_of_beneficiary(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["total"] = len(res['list'])
                dummy_data["appname_list"] = res['list']
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
    
    def payment_beneficiary_detail(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        bid = kwargs['bid']
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': bid
            }

            res = BackendRequest.get_beneficiary(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["total"] = len(res['beneficiary'])
                dummy_data["beneficiary"] = res['beneficiary']
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
    
    def payment_beneficiary_delete(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        bid = kwargs['bid']
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': bid
            }

            res = BackendRequest.delete_beneficiary(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["total"] = len(res['beneficiary'])
                dummy_data["beneficiary"] = res['beneficiary']
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
    
    def payment_beneficiary_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        post_dict = request.POST
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'name': post_dict.get('name')
            }

            res = BackendRequest.create_beneficiary(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["total"] = len(res['beneficiary'])
                dummy_data["beneficiary"] = res['beneficiary']
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
    
    def payment_beneficiary_update(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        bid = kwargs['bid']
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        post_dict = request.POST
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': bid,
                'name': post_dict.get('name')
            }
            if 'description' in post_dict:
                param['description'] = post_dict.get('description', "")

            res = BackendRequest.update_beneficiary(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["total"] = len(res['beneficiary'])
                dummy_data["beneficiary"] = res['beneficiary']
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

    def payment_appname_detail(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        aid = kwargs['aid']
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': aid
            }

            res = BackendRequest.get_appname(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["total"] = len(res['appname'])
                dummy_data["appname"] = res['appname']
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
    
    def payment_beneficiary_assign(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        bid = kwargs['bid']
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        post_dict = request.POST
        dummy_data = {}
        if es_check:
            ids = post_dict.get("appnames_ids", "-1")
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'ids': ids,
                'beneficiary_id': bid
            }

            res = BackendRequest.reassign_appnames(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["total"] = len(res['appnames'])
                dummy_data["appname"] = res['appnames']
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

    def payment_beneficiary_usage(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        bid = kwargs['bid']
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            now = datetime.datetime.now()
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'beneficiary_id': bid,
                'end_datetime': now.strftime("%Y-%m-%d %H:%M:%S"),
                'start_datetime': (now + datetime.timedelta(-30)).strftime("%Y-%m-%d %H:%M:%S")
            }

            res = BackendRequest.get_beneficiary_usages(param)
            if res['result']:
                stats = []
                day = 0
                dateMap = {}
                for day in range(30):
                    dateMap[(now + datetime.timedelta(day-30)).strftime("%Y-%m-%d")] = 0
                for i in res['list']:
                    dateStr = i['usage_datetime'].split()[0]
                    if dateStr in dateMap:
                        dateMap[dateStr] = i['day_usage_in_bytes']
                for day in range(30):
                    dateStr = (now + datetime.timedelta(day-30)).strftime("%Y-%m-%d")
                    if dateStr in dateMap:
                        stats.append(dateMap[dateStr])
                while (len(stats) < 30):
                    stats.append("0")
                #stats.reverse()
                data = []
                today = datetime.date.today()
                today_timestamp = time.mktime((today - datetime.timedelta(1)).timetuple()) * 1000
                step = 60*60*24*1000
                days = 29
                unit = {
                    "0": "Byte",
                    "1": "KB",
                    "2": "MB",
                    "3": "GB",
                    "4": "TB",
                    "5": "PB"
                }
                max_value = float(max(stats))
                log_value = 0 if max_value == 0 else int(math.log(max_value, 1024))
                log_value = log_value if log_value <= 5 else 5
                cur_unit = unit.get(str(log_value), "PB")

                g = lambda x: x if x == 0 else round((float(x)/math.pow(1024, log_value)), 4)
                for i in stats:
                    data.append([today_timestamp-days * step, g(i)])
                    days -= 1
                dummy_data["status"] = "1"
                dummy_data["data"] = data
                dummy_data["unit"] = cur_unit
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

    def payment_beneficiary_daily(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        bid = kwargs['bid']
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        post_dict = request.POST
        date = post_dict.get('date')
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'usage_datetime': date,
                'beneficiary_id': bid,
            }

            res = BackendRequest.get_beneficiary_usages_distribution(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["total"] = len(res['data'])
                dummy_data["data"] = res['data']
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
    
    def payment_appname_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        post_dict = request.POST
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'appname': post_dict.get('name')
            }

            res = BackendRequest.create_appname(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["total"] = len(res['appname'])
                dummy_data["appname"] = res['appname']
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

    def payment_appname_assign(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        aid = kwargs['aid']
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        post_dict = request.POST
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'id': aid,
                'beneficiary_id': post_dict.get("beneficiary_id", "")
            }

            res = BackendRequest.assign_appname(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["total"] = len(res['appname'])
                dummy_data["appname"] = res['appname']
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
