# -*- coding: utf-8 -*-
# wu.ranbo@yottabyte.cn
# 2016-06-17
# Copyright 2016 Yottabyte
# filename: custom/cmschina/apps/alert/plugins/cms_rsyslog.py
# file description: 增加招商银行的插件
__author__ = 'wu.ranbo'

from django.template import Context, Template
import logging
import logging.handlers
import socket

req_logger = logging.getLogger("django.request")

# getLogger得到的是singleton
syslogger = logging.getLogger('AlertPluginSyslog')
syslogger.setLevel(logging.DEBUG)

META = {
    "name": "cms_rsyslog",
    "version": 1,
    "alias": "rsyslog告警",
    "configs": [
        {
            "name": "addresses",
            "alias": "Syslog地址",
            "presence": True,
            "value_type": "string",
            "default_value": "",
            "style": {
                "rows": 1,
                "cols": 15
            }
        },
        {
            "name": "socktype",
            "alias": "发送协议",
            "presence": True,
            "value_type": "string",
            "input_type": "drop_down",
            "input_candidate": ["TCP", "UDP"],
            "default_value": "UDP",
            "style": {
                "rows": 1,
                "cols": 15
            }
        },
        {
            "name": "serverity",
            "alias": "Serverity",
            "presence": True,
            "value_type": "string",
            "input_type": "drop_down",
            "input_candidate": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            "default_value": "INFO",
            "style": {
                "rows": 1,
                "cols": 15
            }
        },
        {
            "name": "facility",
            "alias": "Facility",
            "presence": True,
            "value_type": "string",
            "default_value": "local0",
            "style": {
                "rows": 1,
                "cols": 15
            }

        },
        {
            "name": "message",
            "alias": "Syslog内容",
            "presence": True,
            "value_type": "string",
            "style": {
                "rows": 5,
                "cols": 60
            },
            "default_value": "{{ alert.name }}|{{ alert.strategy.trigger.start_time|date:\"Y-m-d H:i:s\" }}|{{ alert.strategy.trigger.end_time|date:\"Y-m-d H:i:s\" }}|{{ alert.search.query }}"
        }
    ]
}


# 调用处有整体裹起来的异常处理
def handle(params, alert):
    try:
        message = content(params, alert)
        configs = params.get('configs')
        address = configs[0].get('value')
        s_type = configs[1].get('value').lower()
        serverity = configs[2].get('value').lower()
        facility = configs[3].get('value').lower()

        arr = address.split(':')
        if len(arr) != 2:
            req_logger.error("rsyslog alert config address wrong!")
            raise "rsyslog alert config address wrong!"
        ip = arr[0]
        port = int(arr[1])

        socket_type = socket.SOCK_DGRAM
        if s_type == 'tcp':   # 其他都是udp
            socket_type = socket.SOCK_STREAM

        log_handler = logging.handlers.SysLogHandler(address=(ip, port),
                                                facility=facility,
                                                socktype=socket_type)
        syslogger.addHandler(log_handler)
        if serverity == 'debug':
            syslogger.debug(message)
        elif serverity == 'info':
            syslogger.info(message)
        elif serverity == 'warning':
            syslogger.warning(message)
        elif serverity == 'error':
            syslogger.error(message)
        elif serverity == 'critical':
            syslogger.critical(message)
        else:
            req_logger.error("alert:%s use a illegal syslog serverity %s", alert["name"], serverity)
            syslogger.info(message)

        log_handler.flush()  # flush保证
        log_handler.close()  # 主动关闭socket
        syslogger.removeHandler(log_handler)
    except Exception, e:
        req_logger.error("alert.plugins.syslog got exception %s", e)
        raise e

def content(params, alert):
    configs = params.get('configs')
    template_str = configs[4].get('value')
    conf_obj = {}
    conf_obj['alert'] = alert
    return _render(template_str, conf_obj)

def _render(tmpl_str, conf_obj):
    t = Template(tmpl_str)
    c = Context(conf_obj)
    return t.render(c)
