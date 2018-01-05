# -*- coding: utf-8 -*-
# wu.ranbo@yottabyte.cn
# 2016-05-19
# Copyright 2016 Yottabyte
# filename: yottaweb/apps/alert/plugins/simple_email.py
# file description: 最简单的告警，所有客户都会带着
__author__ = 'wu.ranbo'

import logging
import requests
import json
import copy
req_logger = logging.getLogger("django.request")

META = {
    "name": "http_forwarder",
    "version": 1,
    "alias": "告警转发",
    "configs": [
        {
            "name": "address",
            "alias": "http转发地址",
            "presence": True,
            "value_type": "string",
            "default_value": "",
            "style": {
                "rows": 1,
                "cols": 30
            }
        }
        ]
    }

def datetime_to_timestamp(dt):
    return int(dt.strftime("%s"))*1000 + dt.microsecond/1000

def deparse_alert_post(out_alert_post):
    alert_post = copy.deepcopy(out_alert_post)
    alert_post['send_time'] = datetime_to_timestamp(alert_post['send_time'])
    alert_post['exec_time'] = datetime_to_timestamp(alert_post['exec_time'])
    trigger = alert_post['strategy']['trigger']
    if 'start_time' in trigger:
        trigger['start_time'] = datetime_to_timestamp(trigger['start_time'])
    if 'end_time' in trigger:
        trigger['end_time'] = datetime_to_timestamp(trigger['end_time'])
    if 'baseline_start_time' in trigger:
        trigger['baseline_start_time'] = datetime_to_timestamp(trigger['baseline_start_time'])
    if 'baseline_end_time' in trigger:
        trigger['baseline_end_time'] = datetime_to_timestamp(trigger['baseline_end_time'])

    if 'compare_desc_text' in trigger:
        del trigger['compare_desc_text']
    alert_post['strategy']['trigger'] = trigger
    del alert_post['_alert_meta']
    return alert_post

def content(params, alert):
    origin_alert = deparse_alert_post(alert)
    return json.dumps(origin_alert, ensure_ascii=False, indent=4).encode("utf-8", "ignore")

def handle(params, alert):
    try:
        address = params['configs'][0]['value']
        origin_alert = deparse_alert_post(alert)
        requests.post(address, data=json.dumps(origin_alert))
        req_logger.debug("alert.plugs.htt_forwarder send to %s, data:%s.", address, origin_alert)
    except Exception, e:
        req_logger.error("alert.plugins.http_forwarder got exception %s", e)
        raise e
