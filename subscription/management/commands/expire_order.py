# -*- coding: utf-8 -*-
# wu.ranbo@yottabyte.cn
# 2014-12-05
# Copyright 2014 Yottabyte
# file description: 操作命令
__author__ = 'wu.ranbo'

from django.core.management.base import BaseCommand, CommandError

from optparse import make_option
from datetime import datetime

from yottaweb.apps.subscription import utility
from yottaweb.apps.subscription.services import OrderOperate, DomainOperate
from yottaweb.apps.subscription.models import Order

class Command(BaseCommand):
    help = 'Make subscription order expire.'

    option_list = BaseCommand.option_list + (
        make_option('--order-id',
                    action='store', type='int', dest='order_id',
                    help='the order id.which show to custom'),
        make_option('--db-primary-key',
                    action='store', type='int', dest='db_primary_key',
                    help='the database primary key of order table'),
        make_option('--all',
                    action='store_true', dest='all',
                    help='set all expired.'),
        )

    def handle(self, *args, **options):
        try:
            pk = None
            if options['order_id']:
                pk = Order.order_id_to_pk(options['order_id'])
            if options['db_primary_key']:
                pk = options['db_primary_key']

            if pk:
                order = Order.objects.get(pk=pk)

                flag = OrderOperate.expire(order, operator_name='SHELL_OPERATE')

                set_domain_flag = False
                if flag:
                    set_domain_flag = DomainOperate.set_volume_limit_by_domain(order.domain_name)

                if flag and set_domain_flag:
                    self.stdout.write('Success!')
                else:
                    self.stdout.write('Failed!')
                    return False

            if options['all']:
                orders = Order.objects.filter(status='validated')
                today = utility.today()
                _os = []
                for o in list(orders):
                    if utility.beginning_of_day(o.pre_expire_time) <= today:
                        _os.append(o)

                ret_flag = True
                for o in _os:
                    flag = OrderOperate.expire(o, operator_name='SHELL_OPERATE')
                    self.stdout.write(o.domain_name)
                    if flag:
                        set_domain_flag = DomainOperate.set_volume_limit_by_domain(o.domain_name)
                    if not flag or not set_domain_flag:
                        ret_flag = False
                        self.stdout.write('Failed!')
                        return False

                if ret_flag: self.stdout.write('Success!')

        except Exception, e:
            self.stdout.write('Error!')
            self.stdout.write(e.message)
