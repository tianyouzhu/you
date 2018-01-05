# -*- coding: utf-8 -*-
# wang.qiushi@yottabyte.cn
# 2017-2-6
# Copyright 2017 Yottabyte
# file description: rizhiyi_yottaweb的history表
__author__ = 'wang.qiushi'

from django.db import models

class History(models.Model):
    user_id = models.CharField(max_length=11, default='None')
    token = models.CharField(max_length=255, default='None')
    query = models.TextField(default='None')
    create_time = models.DateTimeField(auto_now_add=True, default='1970-01-01 00:00:00')
    