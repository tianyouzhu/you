# -*- coding: utf-8 -*-
# wu.ranbo@yottabyte.cn
# 2014-12-01
# Copyright 2014 Yottabyte
# file description: 提供功能实现的类, 大了再拆分文件
__author__ = 'wu.ranbo'

from django.db import transaction, connection

from dateutil.relativedelta import relativedelta
from datetime import datetime
from decimal import Decimal
import traceback
import inspect

from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.subscription.models import Order, Operation
from yottaweb.apps.subscription.utility import compute_expired_day, compute_years_between, compute_months_between, YEAR_STR, MONTH_STR, utc, beginning_of_day, mb_to_b


class OrderOperate(object): # 订单状态机，
    SYSTEM_AUTO = 'SYSTEM_AUTO'
    @staticmethod
    def pay(order, paid_price=None, paid_time=None, operator_name=None):
        try:
            with transaction.atomic():
                order = Order.objects.get(pk=order.pk) # 数据承诺,要reload,函数参数来传递要赋值的
                if order.status != 'init': return False

                ret = False
                order.status = 'paid'
                if paid_price:
                    order.paid_price = Decimal(str(paid_price))
                else:
                    order.paid_price = Decimal(str(order.charge))

                order.paid_time = paid_time or datetime.now(utc)

                order_operation = Operation(action='pay', order=order, operator_name=operator_name or OrderOperate.SYSTEM_AUTO)

                order.save()
                order_operation.save()
                ret = True
        except Exception, e:
            e.message = ('yottaweb.apps.subscription.services.OrderOperate.pay:%s.' % e)
            print e
            ret = False

        return ret


    @staticmethod
    def validate(order, operator_name=None):

        try:
            with transaction.atomic():
                order = Order.objects.get(pk=order.pk) # reload
                if order.status != 'paid': return False

                validated_order = Order.current_validate_order(order.domain_name)
                if not validated_order:
                    validated_order = Order.fake_free_order(order.domain_name)

                if validated_order.volume > order.volume or int(validated_order.paid_to_day().strftime('%s')) > int(order.paid_to_day().strftime('%s')): return False

                order.status = 'validated'
                order.validate_time = datetime.now(utc)
                order.pre_expire_time = compute_expired_day(order.validate_time, order.pay_plan, order.number)

                order_operation = Operation(action='validate', order=order, operator_name=operator_name or OrderOperate.SYSTEM_AUTO)

                validated_order.status = 'expired'
                validated_order.expire_time = datetime.now(utc)

                validated_order.save()
                order.save()
                order_operation.save()

                return True
        except Exception, e:
            e.message = ('yottaweb.apps.subscription.services.OrderOperate.validate:%s' % e)
            print e.message
            return False


    @staticmethod
    def expire(order, operator_name=None):
        order = Order.objects.get(pk=order.pk)
        if order.status != 'validated': return False

        expire_flag = False
        try:
            with transaction.atomic():
                order.status = 'expired'
                order.expire_time = datetime.now(utc)

                order_operation = Operation(action='expire', order=order, operator_name = operator_name or OrderOperate.SYSTEM_AUTO)

                order.save()
                order_operation.save()
                expire_flag = True
        except Exception,e:
            e.message = ('yottaweb.apps.subscription.services.OrderOperate.expire:%s.' % 'e')
            print e
            expire_flag = False

        if not expire_flag: return False

        # do after expire
        Order.fake_free_order(order.domain_name).save()
        return (expire_flag)


    @staticmethod
    def create(param_dict):

        order = Order.build(param_dict)

        try:
            order.status = 'init'

            order.day_unit_price = Decimal(str(Order.month_price_to_day(order.month_price)))

            order.pre_expire_time = compute_expired_day(order.pre_validate_time, order.pay_plan, order.number)
            order.charge = Decimal(str(order.charge))
            order.month_price = Decimal(str(order.month_price))
            order.day_unit_price = Decimal(str(order.day_unit_price))
            order.paid_price = Decimal(str(order.paid_price))
            order.save()
        except Exception, e:
            e.message = ('yottaweb.apps.subscription.services.OrderOperate.create:%s.' % e)
            print e
            traceback.format_exc()
            order = False
        return order


    @staticmethod
    def compute_price(domain_name, volume, pay_plan, pay_number, pre_validate_time):
        pair_key = (volume, pay_plan)
        if not Package.has_package(pair_key): return False

        validated_order = Order.current_validate_order(domain_name)
        if not validated_order:
            validated_order = Order.fake_free_order(domain_name)

        # 套餐生效日期在现有套餐之后
        if int(validated_order.pre_expire_time.strftime('%s')) < int(pre_validate_time.strftime('%s')):
            return (Package.package_price(pair_key, pay_number))

        # 比如，用户原先生效日期起止是2014-1-10到2014-2-10，新下了一个订单起始日期如果是2014-2-10则因为终止日期的含义是到end_of_day(2014-2-10),用户原套餐used_days=30天而不是一个月relativedelta(2014-2-10,2014-1-10)就是30天，如果用户下失效日期后一天，才是正好衔接起两个套餐relativedelta(2014-2-11,2014-1-10)返回是一个月。
        # 注意这里跟 utility.compute_months_between 方法的不同。
        used_time = relativedelta(
            beginning_of_day(pre_validate_time),
            beginning_of_day(validated_order.validate_time))
        used_years = used_time.years
        used_months = used_time.months + 12 * used_years
        used_days = used_time.days
        used_money = validated_order.day_unit_price * used_days + validated_order.month_price * used_months

        # !!! ATTENTION !!!!!!!!!
        # NOTE: 这里只适用套餐定价不会改变的情况 !!!!!!!
        # 等将来套餐定价改变时候，需要将origin_charge存入到数据库中才行。!!!!!!
        # !!! ATTENTION !!!!!!!!!
        origin_charge = Package.package_price((int(validated_order.volume),
                                               str(validated_order.pay_plan)),
                                              validated_order.number)
        rest_money = (origin_charge - used_money)
        if rest_money < 0: rest_money = 0

        ret = Package.package_price(pair_key, pay_number) - rest_money
        if ret < 0:
            return 0
        else:
            return ret


class DomainOperate(object):
    @staticmethod
    def set_volume_limit_by_domain(domain_name):
        order = Order.objects.get(status='validated', domain_name=domain_name) # NOTE if return not only one row, get() will raise Exception
        ret = DomainOperate.set_volume_limit(order.domain_name, mb_to_b(order.volume))
        return ret


    @staticmethod
    def set_volume_limit(domain_name, volume):
        ret = False
        try:
            with transaction.atomic():
                cursor = connection.cursor()

                cursor.execute("UPDATE rizhiyi_system.Domain SET limit_flow_quota = %s WHERE name = %s", [volume, domain_name])
                ret = True
        except Exception, e:
            e.message = 'yottaweb.apps.subscription.services.DomainOperate.set_volume_limit:' + e.message
            print e
            ret = False
        return ret


class Package(object):
    MIN_ON_SELL_VOLUMN = 1024
    _META_PRICE = {
        (512, MONTH_STR): Decimal('0.00'),
        (1024, MONTH_STR): Decimal('300.00'), # 1GB month 280RMB
        (2048, MONTH_STR): Decimal('600.00'),
        (5120, MONTH_STR): Decimal('1500.00'),
        (10240, MONTH_STR): Decimal('3000.00'),
        (15360, MONTH_STR): Decimal('4500.00'),
        (20480, MONTH_STR): Decimal('6000.00')
    }
    FREE_PLAN = (512, MONTH_STR)
    PRICE = dict(_META_PRICE)

    for month_pair in PRICE.keys():
        year_pair = (month_pair[0], YEAR_STR)
        PRICE[year_pair] = PRICE[month_pair] * 10

    ON_SELL_PRICE = dict([i for i in PRICE.items() if i[0][0] >= MIN_ON_SELL_VOLUMN])

    @staticmethod
    def package_price(pair, number): # pair = (volume, plan_str)
        return Package.PRICE[pair] * Decimal(number)

    @staticmethod
    def has_package(pair):
        return (pair in Package.PRICE)

    @staticmethod
    def get_package(domain_name, volume, pay_plan, pay_number, pre_validate_time):
        pair_key = (volume, pay_plan)
        if pair_key in Package.PRICE.keys():

            return {
                'volume': volume,
                'payplan': pay_plan,
                'paynumber': pay_number,
                'charge': OrderOperate.compute_price(domain_name, volume, pay_plan, pay_number, pre_validate_time),
                'yearcharge': Package.PRICE[(volume, YEAR_STR)],
                'monthcharge': Package.PRICE[(volume, MONTH_STR)],
                'preexpiretime': compute_expired_day(pre_validate_time, pay_plan, pay_number),
                'prevalidatetime': pre_validate_time
            }
        else:
            return False

    ##
    # @brief:
    # @param:old_volume
    # @param:old_paid_to_day: !已经有付款到哪天。免费无付款。
    # @param:new_pre_validate_day
    # @param:pay_plan
    # @returns:
    @staticmethod
    def limit_plan_info(old_volume, old_paid_to_day, new_pre_validate_day, pay_plan):
        all_on_sell_volumes = sorted([pair[0] for pair in Package.ON_SELL_PRICE.keys() if pair[1] == pay_plan])
        if int(new_pre_validate_day.strftime('%s')) > int(old_paid_to_day.strftime('%s')):

            return {
                YEAR_STR: { 'volumes': all_on_sell_volumes, 'numbers': range(1, 13) },
                MONTH_STR: { 'volumes': all_on_sell_volumes , 'numbers': range(1, 13) }
            }
        else:
            volumes = [ v for v in all_on_sell_volumes if v > old_volume]
            if len(volumes) == 0:
                volumes.append(all_on_sell_volumes.pop())
            return {
                YEAR_STR: {
                    'volumes': volumes,
                    'numbers': range(compute_years_between(new_pre_validate_day, old_paid_to_day), 13)},
                MONTH_STR: {
                    'volumes': volumes,
                    'numbers': range(compute_months_between(new_pre_validate_day, old_paid_to_day), 13)}
            }
