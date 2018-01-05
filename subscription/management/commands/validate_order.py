# -*- coding: utf-8 -*-
# wu.ranbo@yottabyte.cn
# 2014-12-05
# Copyright 2014 Yottabyte
# file description: 操作命令
__author__ = 'wu.ranbo'

from django.core.management.base import BaseCommand, CommandError

from optparse import make_option
from decimal import Decimal

from yottaweb.apps.subscription.services import OrderOperate,DomainOperate
from yottaweb.apps.subscription.models import Order

class Command(BaseCommand):
    help = 'Make subscription order validate.'

    option_list = BaseCommand.option_list + (
        make_option('--order-id',
                    action='store', type='int', dest='order_id',
                    help='the order id.which show to custom'),
        make_option('--db-primary-key',
                    action='store', type='int', dest='db_primary_key',
                    help='the database primary key of order table'),
        make_option('--force',
                    action='store_true', dest='force', default=False,
                    help='if already paid, force to validate the order'),
        make_option('--paid-price',
                    action='store', type='int', dest='paid_price',
                    help='when the price custom paid changed, specific the real paid money. unti RMB')
        )

    def handle(self, *args, **options):
        try:
            pk = None
            paid_price = None
            if options['order_id']:
                pk = Order.order_id_to_pk(options['order_id'])
            if options['db_primary_key']:
                pk = options['db_primary_key']
            if options['paid_price']:
                paid_price = options['paid_price']

            if pk:
                order = Order.objects.get(pk=pk)
                flag_paid = OrderOperate.pay(order, paid_price, operator_name='SHELL_OPERATE')

                flag_validated = False
                if (flag_paid) or ((not flag_paid) and options['force']):
                    flag_validated = OrderOperate.validate(order, operator_name='SHELL_OPERATE')

                set_domain_flag = False
                if flag_validated:
                    set_domain_flag = DomainOperate.set_volume_limit_by_domain(order.domain_name)

                if flag_validated and set_domain_flag:
                    self.stdout.write('Success!')
                else:
                    self.stdout.write('Failed!')
        except Exception, e:
            self.stdout.write('Error!')
            self.stdout.write(e.message)
