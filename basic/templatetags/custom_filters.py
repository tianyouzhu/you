# -*- coding: utf-8 -*-
# wu.ranbo@yottabyte.cn
# 2015-05-13
# Copyright 2015 Yottabyte
# filename: yottaweb/middleware/filters.py
# file description: 自定义template的filters
__author__ = 'wu.ranbo'
import ConfigParser
import os

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

try:
    _config_parser = ConfigParser.ConfigParser()
    _config_parser.read(os.getcwd() + '/config' + "/yottaweb.ini")
    _ldap_suffix = _config_parser.get('ldap', 'rizhiyi_name_posfix')
except Exception, e:
    print e
    _ldap_suffix = None

@register.filter(name='short_name')
@stringfilter
def short_name(fullname):
    if _ldap_suffix and fullname.endswith(_ldap_suffix):
        return fullname[:(-1 * len(_ldap_suffix))]
    else:
        return fullname
