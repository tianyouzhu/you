# -*- coding: utf-8 -*-
# wu.ranbo@yottabyte.cn
# 2014-12-03
# Copyright 2014 Yottabyte
# file description: subscription使用的utility
__author__ = 'wu.ranbo'

from decimal import Decimal
from datetime import tzinfo, timedelta, datetime
import time
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse

DAY_TIME_FORMT = '%Y-%m-%d'
YEAR_STR = 'year'
MONTH_STR = 'month'

class FixedOffset(tzinfo):
    """Fixed offset in minutes: `time = utc_time + utc_offset`."""
    def __init__(self, offset_str):
        offset = int(offset_str[-4:-2])*60 + int(offset_str[-2:])
        if offset_str[0] == "-":
            offset = -offset

        self.__offset = timedelta(minutes=offset)
        hours, minutes = divmod(offset, 60)
        #NOTE: the last part is to remind about deprecated POSIX GMT+h timezones
        #  that have the opposite sign in the name;
        #  the corresponding numeric value is not used e.g., no minutes
        self.__name = '<%+03d%02d>%+d' % (hours, minutes, -hours)
    def utcoffset(self, dt=None):
        return self.__offset
    def tzname(self, dt=None):
        return self.__name
    def dst(self, dt=None):
        return timedelta(0)
    def __repr__(self):
        return 'FixedOffset(%d)' % (self.utcoffset().total_seconds() / 60)

class UTC(tzinfo):
    def utcoffset(self, dt):
        return timedelta(0)
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return timedelta(0)
utc = UTC()

def str_to_datetime(datetime_str):
    ret = parse(datetime_str).replace(tzinfo=FixedOffset('+0000')) # NOTE:china only
    return ret

def str_to_day(day_str):
    return beginning_of_day(str_to_datetime(day_str))

def compute_expired_day(validate_day, pay_plan, number):
    if pay_plan == YEAR_STR:
        return validate_day + relativedelta(years=number, days=-1)
    elif pay_plan == MONTH_STR:
        return validate_day + relativedelta(months=number, days=-1)

    ##
    # @brief 计算在两个日期之间有几个应付费的月，不足满月的向上加一个月
    # 例如：在数据库中我们存储订单起止日期为2014-1-2到2014-2-1含义是用户使用时间是正好一个整月,终止日是end_of_day,起始日是beginning_of_day。
    # 但relativedelta(2014-2-1,2014-1-1)返回值是30天而不是一个月
    # @param start_day: datetime
    # @param end_day: datetime
    # @returns: Number
def compute_months_between(start_day, end_day):
    _start_day = start_day + relativedelta(days=-1)
    delta = relativedelta(beginning_of_day(end_day), beginning_of_day(_start_day))

    years = delta.years
    months = delta.months
    days = delta.days

    if days > 0:
        return years * 12 + months + 1
    else:
        return years * 12 + months

def compute_years_between(start_day, end_day):
    _start_day = start_day + relativedelta(days=-1)
    delta = relativedelta(beginning_of_day(end_day), beginning_of_day(_start_day))

    years = delta.years
    months = delta.months
    days = delta.days
    if days > 0 or months > 0:
        return years + 1
    else:
        return years

def mb_to_b(mb):
    return mb * 1024 * 1024

def mb_to_gb(mb):
    r = float(float(mb)/float(1024))
    if r < 1:
        return r
    else:
        return mb / 1024

def gb_to_mb(gb):
    return gb * 1024

def datetime_to_day(i_datetime):
    return i_datetime.replace(year=i_datetime.year, month=i_datetime.month, day=i_datetime.day, hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)

def beginning_of_day(i_day):
    try:
        d = datetime_to_day(i_day)
        return d
    except: # 传入可能是date
        d = datetime.combine(i_day, datetime.min.time())
        d = datetime_to_day(d)
        return d

def day_str(i_datetime):
    return beginning_of_day(i_datetime).strftime(DAY_TIME_FORMT)

def today_str():
    return day_str(datetime.now(utc).date())

def today():
    return beginning_of_day(datetime.now(utc))

def domain_name(request):
    domain_name = request.META.get('HTTP_HOST').split('.')[0]
    return domain_name


  # 虚拟订单号，隐藏数据库信息
__MAXID = 2147483647  # (2**31 - 1)
__PRIME = 4115032003 #a very big prime number of your choice (like 9 digits big)
__PRIME_INVERSE = 1325023467 #another big integer number so that (PRIME * PRIME_INVERSE) & MAXID == 1
__RNDXOR = 1986101300 #some random big integer number, just not bigger than MAXID

def db_pk_to_order_id(pk):
  return str((((pk* __PRIME) & __MAXID) ^ __RNDXOR))

def order_id_to_db_pk(order_id): # order_id is str
  return ((int(order_id) ^ __RNDXOR) * __PRIME_INVERSE) & __MAXID

