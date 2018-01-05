# -*- coding: utf-8 -*-
# wu.ranbo@yottabyte.cn
# 2014-12-01
# Copyright 2014 Yottabyte
# file description:
__author__ = 'wu.ranbo'

from tastypie.resources import Resource
from django.conf.urls import url

from datetime import datetime
import traceback

from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.subscription.services import Package
from yottaweb.apps.subscription.models import Order
from yottaweb.apps.subscription import utility

class SubscriptionResource(Resource):
    class Meta:
        resource_name = 'subscription'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/paylimit" % self._meta.resource_name,
                self.wrap_view('paylimit'),
                name="subscription_paylimit"
                ),
            url(r"^(?P<resource_name>%s)/payinfo$" % self._meta.resource_name,
                self.wrap_view('payinfo'),
                name="subscription_payinfo"
                )
        ]

    def paylimit(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        es_check = MyBasicAuthentication().is_authenticated(request, **kwargs)

        dummy_data = {}
        if es_check and es_check['r'] == 'owner':
            new_pre_validate_time = utility.str_to_datetime(request.POST.get('prevalidatetime', utility.day_str(datetime.now(utility.utc)) ))
            new_pay_plan = str(request.POST.get('payplan'))

            domain_name = utility.domain_name(request)
            old_order = Order.current_validate_order(domain_name)

            if not old_order:
                old_order = Order.fake_free_order(domain_name)

            paylimit = Package.limit_plan_info(old_order.volume,
                                              old_order.paid_to_day(),
                                              new_pre_validate_time,
                                              new_pay_plan)
            if paylimit:
                dummy_data['status'] = 'success'
                paylimit['year']['volumes'] = [ utility.mb_to_gb(v) for v in paylimit['year']['volumes']]
                paylimit['month']['volumes'] = [ utility.mb_to_gb(v) for v in paylimit['month']['volumes']]
                dummy_data['data'] = paylimit
            else:
                dummy_data['status'] = 'failed'
                dummy_data['message'] = 'limit_plan_info return error.'
        else:
            dummy_data['status'] = 'failed'
            dummy_data['message'] = 'check user not present.'

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp


    def payinfo(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        es_check = MyBasicAuthentication().is_authenticated(request, **kwargs)

        dummy_data = {}
        if es_check and es_check['r'] == 'owner':

            payinfo = Package.get_package(
                utility.domain_name(request),
                utility.gb_to_mb(int(request.POST.get('volume'))),
                str(request.POST.get('payplan')),
                int(request.POST.get('paynumber', 0)),
                utility.str_to_datetime(request.POST.get('prevalidatetime', utility.today_str() ))
               )

            if payinfo:
                dummy_data['status'] = 1
                dummy_data['monthcharge'] = payinfo.get('monthcharge')
                dummy_data['yearcharge'] = payinfo.get('yearcharge')
                dummy_data['charge'] = payinfo.get('charge')
                dummy_data['preexpiretime'] = payinfo.get('preexpiretime')
            else:
                dummy_data['status'] = '0'
                dummy_data['msg'] = 'get package info erro!'
        else:
            dummy_data['status'] = '0'
            dummy_data['msg'] = 'get error!'

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp
