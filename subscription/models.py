# -*- coding: utf-8 -*-
# wu.ranbo@yottabyte.cn
# 2014-12-01
# Copyright 2014 Yottabyte
# file description: 对应数据库的表Subscription，用户提交的一次申请
__author__ = 'wu.ranbo'

from django.db import models

from dateutil.relativedelta import relativedelta
from datetime import datetime
from decimal import Decimal

from yottaweb.apps.subscription import utility

class Order(models.Model):
    _FREE_VOLUMNE = 512
    status = models.CharField(max_length=128, default='init') # init, paid, validated, expired

    create_time = models.DateTimeField(auto_now_add=True, default='1970-01-01 00:00:00')

    volume = models.IntegerField(default=0) # 单位M
    pay_plan = models.CharField(max_length=255, default='None') #'month', 'year'
    number = models.IntegerField(default=0) # 买了几份
    charge = models.DecimalField(default=0.0, max_digits=10, decimal_places=2) # 单位RMB元, 套餐售价
    month_price = models.DecimalField(default=0.0, max_digits=10, decimal_places=2) # 月费为当前基本计价单位
    day_unit_price = models.DecimalField(default=0.0, max_digits=10, decimal_places=2) # 由月费算出的日单价，免费套餐以上均为0

    paid_price = models.DecimalField(default=0.0, max_digits=10, decimal_places=2) # 单位RMB元，实际支付价格

    paid_time = models.DateTimeField(default='1970-01-01 00:00:00') # 支付时间
    pre_validate_time = models.DateTimeField(default='1970-01-01 00:00:00') # 预计生效时间
    validate_time = models.DateTimeField(default='1970-01-01 00:00:00') # 实际生效时间
    pre_expire_time = models.DateTimeField(default='1970-01-01 00:00:00') # 预计过期时间
    expire_time = models.DateTimeField(default='1970-01-01 00:00:00') # 实际过期时间

    token = models.CharField(max_length=255, default='None')
    domain_name = models.CharField(max_length=128) # NOTE! 必须指定。
    account_name = models.CharField(max_length=255, default='None')

    invoice_flag = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, default='None')
    post_address = models.CharField(max_length=255, default='None')
    contact_name = models.CharField(max_length=255, default='None')
    contact_phone = models.CharField(max_length=255, default='None')

    def is_free(self):
        return self.volume == self._FREE_VOLUMNE

    def order_id(self):
        return utility.db_pk_to_order_id(self.pk)


    # 含义：用户已付款到哪一天(除了免费套餐，应该都==pre_expire_time)
    # 比如买十个月送两个月的订单，应算到第十二个月。
    # 这样这个日期用来计算套餐升级时候以哪天为最近日期，这样升级时候也必须把我们送的两个月给升级了。
    def paid_to_day(self):
        if self.is_free():
            return utility.beginning_of_day(datetime.now(utility.utc)) - relativedelta(days=1)
        else:
            return utility.beginning_of_day(self.pre_expire_time)

    @classmethod
    def order_id_to_pk(cls, order_id):
        return utility.order_id_to_db_pk(order_id)

    @classmethod
    def month_price_to_day(cls, month_price):
        return Decimal(str(month_price))/ Decimal('30.00')

    @classmethod
    def current_validate_order(cls, domain_name):
        orders = list(cls.objects.filter(domain_name=domain_name, status='validated'))
        # assert(len(orders) <= 1) #
        if len(orders) >= 1:
            return orders[0]
        else:
            return False

    # @brief:
    # @param:param_dict; {volume, pay_plan, number, charge, month_price, pre_validate_time, token ,domain_name, account_name, invoice_flag, company_name, post_address, contact_name, contact_phone}
    # @returns:
    @classmethod
    def build(cls, param_dict):
        order = cls(**param_dict)

        return order

    def create(cls, param_dict):
        order = build(param_dict)
        order.save()

    @classmethod
    def fake_free_order(cls, domain_name):
        order = Order(
            status = 'validated',

            volume = cls._FREE_VOLUMNE,
            pay_plan = 'month',
            number = '1',
            charge = Decimal('0.0'),
            month_price = Decimal('0.0'),
            day_unit_price = Decimal('0.0'),
            paid_price = Decimal('0.0'),

            paid_time = datetime.now(utility.utc),
            pre_validate_time = datetime.now(utility.utc),
            validate_time = datetime.now(utility.utc),
            pre_expire_time = datetime.now(utility.utc),
            expire_time = datetime.now(utility.utc),

            domain_name = domain_name
            )
        return order

class Operation(models.Model):
    order = models.ForeignKey(Order)
    action = models.CharField(max_length=255, default='None')
    time = models.DateTimeField(auto_now_add=True, default='1970-01-01 00:00:00')
    operator_name = models.CharField(max_length=255, default='None')
