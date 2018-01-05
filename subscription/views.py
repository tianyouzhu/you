# -*- coding: utf-8 -*-
# wu.ranbo@yottabyte.cn
# 2014-12-01
# Copyright 2014 Yottabyte
# file description: 下套餐订单subscription/application/new，和

from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from decimal import Decimal
from datetime import datetime
import json
import traceback

from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.subscription.models import Order
from yottaweb.apps.subscription.services import Package,OrderOperate
from yottaweb.apps.subscription import utility

def new(request, **kwargs):
    my_auth = MyBasicAuthentication()
    is_login = my_auth.is_authenticated(request, **kwargs)

    domain_name = utility.domain_name(request)
    validate_order = Order.current_validate_order(domain_name)
    if validate_order:
        current_subscription = {
            'end_day': validate_order.pre_expire_time,
            'start_day': validate_order.validate_time,
            'volume': utility.mb_to_gb(validate_order.volume),
            'price': validate_order.charge,
            'order_id': validate_order.order_id(),
        }
        current_subscriptions = [current_subscription]
    else:
        current_subscriptions = []

    if is_login:
        return render(request, 'subscription/new.html', {"user": is_login["u"], "email": is_login["e"],
                                                         "userid": is_login["i"],
                                                        "current_subscriptions": current_subscriptions,
                                                        "role": is_login["r"]}
                     )
    else:
        return HttpResponseRedirect('/auth/login/')

@require_http_methods(["POST"])
def create(request, **kwargs):
    es_check =  MyBasicAuthentication().is_authenticated(request, **kwargs)
    if (not es_check) or (es_check['r'] != "owner"):
        return HttpResponse(json.dumps({'redirect_url': '/auth/login', 'status': 'failed'}))
    else:
        payinfo = Package.get_package(
            utility.domain_name(request),
            utility.gb_to_mb(int(request.POST.get('volume'))),
            str(request.POST.get('payplan')),
            int(request.POST.get('paynumber', 1)),
            utility.str_to_datetime(request.POST.get('prevalidatetime', utility.today_str() ))
           )

        dummy_data = {}
        if es_check and payinfo:
            order = OrderOperate.create(dict(
                    volume = payinfo.get('volume'),
                    pay_plan= payinfo.get('payplan'),
                    number = payinfo.get('paynumber'),
                    charge = str(payinfo.get('charge')),

                    month_price = Decimal(str(payinfo.get('monthcharge'))),
                    pre_validate_time = payinfo.get('prevalidatetime'),

                    token = es_check['t'],
                    operator = es_check['u'],
                    domain_name = utility.domain_name(request),
                    account_name = es_check['u'],

                    invoice_flag = request.POST.get('needreceipt'),
                    company_name = request.POST.get('cominfo[name]'),
                    post_address = request.POST.get('cominfo[address]'),
                    contact_name = request.POST.get('cominfo[person]'),
                    contact_phone = request.POST.get('cominfo[tel]'),

                ))
            if order:
                dummy_data["status"] = 1
                dummy_data["msg"] = "success!"
                return HttpResponse(json.dumps({'redirect_url': '/account/usage/', 'status': 'success'}))
            else:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "create order failed."
                return HttpResponse(json.dumps({'redirect_url': '/subscription/new', 'status': 'failed'}))

        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "get error!"
            return HttpResponse(json.dumps({'redirect_url': '/auth/login', 'status': 'failed'}))
