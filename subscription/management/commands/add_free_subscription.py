# -*- coding: utf-8 -*-
# wu.ranbo@yottabyte.cn
# 2014-12-05
# Copyright 2014 Yottabyte
# file description: 操作命令
__author__ = 'wu.ranbo'

from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from yottaweb.apps.subscription.services import OrderOperate
from yottaweb.apps.subscription.models import Order

class Command(BaseCommand):
    help = 'Make subscription order expire.'

    option_list = BaseCommand.option_list + (
        make_option('--domain-name',
                    action='store', type='string', dest='domain_name',
                    help='give the domain name a validated free subscription order'),
        )

    def handle(self, *args, **options):
        try:
            if options['domain_name']:
                order = Order.fake_free_order(options['domain_name'])

                order.save()
                self.stdout.write('Success!')
            else:
                self.stdout.write('Failed!')
        except Exception,e:
            self.stdout.write('Error!')
            self.stdout.write(e.message)
