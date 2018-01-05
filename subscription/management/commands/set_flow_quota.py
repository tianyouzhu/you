# -*- coding: utf-8 -*-
# wu.ranbo@yottabyte.cn
# 2014-12-05
# Copyright 2014 Yottabyte
# file description: 根据order表来请求后端设置流量限制
__author__ = 'wu.ranbo'

from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from yottaweb.apps.subscription.services import OrderOperate, DomainOperate
from yottaweb.apps.subscription.models import Order

class Command(BaseCommand):
    help = 'manually set flow quota.' # expire and validate order should already set flow quota.

    option_list = BaseCommand.option_list + (
        make_option('--domain-name',
                    action='store', type='string', dest='domain',
                    help='domain name which to refresh flow quota'),
        make_option('--all',
                    action='store_true', dest='all', default=False,
                    help="refresh all domain's limit flow quota."),
        )

    def handle(self, *args, **options):
        try:
            if options['all']:
                for o in list(Order.objects.filter(status='validated')):
                    DomainOperate.set_volume_limit_by_domain(o.domain_name)
                self.stdout.write('Success!')
            elif options['domain_name']:
                d = Order.objects.get(status='validated', domain_name=options['domain_name'])
                if d:
                    DomainOperate.set_volume_limit_by_domain(d)
                    self.stdout.write('Success!')
                else:
                    self.stdout.write('Failed!')

        except Exception,e:
            self.stdout.write('Error!')
            self.stdout.write(e.message)
