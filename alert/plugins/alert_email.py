# -*- coding: utf-8 -*-
# wu.ranbo@yottabyte.cn
# 2016-05-19
# Copyright 2016 Yottabyte
# filename: yottaweb/apps/alert/plugins/simple_email.py
# file description: 最简单的告警，所有客户都会带着
__author__ = 'wu.ranbo'

from django.template import Context, Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# from email import Encoders

import ConfigParser
import smtplib
import logging
import os

re_logger = logging.getLogger("django.request")

META = {
        "name": "email",
        "version": 1,
        "alias": "邮件告警",
        "configs": [
            {
                "name": "subject",
                "alias": "标题",
                "presence": True,
                "value_type": "string",
                "default_value": "[告警邮件][{% if alert.strategy.trigger.level == \"low\" %}低{% elif alert.strategy.trigger.level == \"mid\" %}中{%elif alert.strategy.trigger.level == \"high\"%}高{% endif %}]{{alert.name}}",
                "style": {
                    "rows": 1,
                    "cols": 15
                }
            },
            {
                "name": "receiver",
                "alias": "接收邮箱(多个用逗号分隔)",
                "presence": True,
                "value_type": "string",
                "input_type": "email",
                "default_value": "",
                "style": {
                    "rows": 1,
                    "cols": 20
                }
            },
            {
                "name": "content_tmpl",
                "alias": "内容模板",
                "presence": True,
                "value_type": "template",
                "default_value": """
<br>
{% if alert.is_alert_recovery %}
告警{{ alert.name }}已经恢复。<br><br>
{% else %}
告警名称: {{ alert.name }}<br>
告警级别：{% if alert.strategy.trigger.level == "low" %}低{% elif alert.strategy.trigger.level == "mid" %}中{%elif alert.strategy.trigger.level == "high"%}高{% endif %}<br>
告警描述: {{ alert.description }}<br>
告警产生时间: {{ alert.send_time|date:"Y年n月d日 H:i:s" }}<br>
告警时间范围: {{ alert.strategy.trigger.start_time|date:"Y年n月d日 H:i:s" }}到{{ alert.strategy.trigger.end_time|date:"Y年n月d日 H:i:s" }}<br>
日志分组: {{ alert.search.source_group }}<br>
查询语句: {{ alert.search.query }}<br>
过滤条件: {{ alert.search.filter}}<br><br>
查询链接: {{web_conf.custom.web_address}}/search/?sourcegroup={{ alert.search.source_group }}&time_range={{alert.strategy.trigger.start_time|date:"Uu"|slice:":-3"}},{{alert.strategy.trigger.end_time|date:"Uu"|slice:":-3"}}&filters={{ alert.search.filter}}&query={{alert.search.query}}&title={{alert.name}}&_t={{alert.send_time|date:"Uu"|slice:":-3"}}&page=1&size=20&order=desc&index=new<br>
<br>
{% if alert.strategy.name == "count"  %}
触发条件：{{ alert.strategy.trigger.compare_desc_text }}<br>
触发事件总数：{{ alert.result.total }}<br><br>
最近事件：<br>
  {% if alert.result.hits %}
    {% for hit in alert.result.hits %}
    appname:{{ hit.appname }}, tag:{{ hit.tag|join:";" }}, hostname:{{ hit.hostname }}<br>
    {{ hit.raw_message }} <br>
     --------------------------------------------<br><br>
    {% endfor %}
  {% endif %}

{% elif alert.strategy.name == "field_stat" %}
  触发条件： {{ alert.strategy.trigger.compare_desc_text }}<br>
  {% if alert.strategy.trigger.method == "cardinality" %}
    超过阈值的结果:<br>
    <table>
    <tr><td>键值:</td><td> 次数:</td></tr>
    {% for b in alert.result.terms %}
      {% if b.doc_count > alert.strategy.trigger.compare_value|first %}
      <tr><td>{{ b.key|ljust:"40" }}</td><td>{{ b.doc_count|ljust:"40" }}</td></tr>
      {% endif %}
    {% endfor %}
   </table>
  {% else %}
  {{ alert.strategy.trigger.field }}的值为{{ alert.result.value }}<br>
  {% endif %}

{% elif alert.strategy.name == "sequence_stat" %}
触发条件： {{ alert.strategy.trigger.compare_desc_text }}<br>

{% elif alert.strategy.name == "baseline_cmp" %}

基线的时间范围：{{ alert.strategy.trigger.baseline_start_time|date:"Y年n月d日 H:i:s" }} 到　{{ alert.strategy.trigger.baseline_end_time|date:"Y年n月d日 H:i:s" }}　<br>
统计时间范围：{{ alert.strategy.trigger.baseline_end_time|date:"Y年n月d日 H:i:s" }} 到 {{ alert.strategy.trigger.end_time|date:"Y年n月d日 H:i:s" }}<br>
触发条件： {{ alert.strategy.trigger.compare_desc_text }}<br>
基线值：{{ alert.strategy.trigger.baseline_base_value}} <br>
当前值：{{ alert.result.value }} <br>

{% elif alert.strategy.name == "spl_query" %}
触发条件：{{ alert.strategy.trigger.compare_desc_text }}<br>

{% if alert.result.columns %}
告警结果：<br>
<table>
<tr>
  {% for k in alert.result.columns %}
  <td>{{ k.name}}</td>
  {% endfor %}
</tr>
  {% for result_row in alert.result.hits %}
  <tr>
    {% for k in alert.result.columns %}
       {% for rk, rv in result_row.items %}
         {% if rk == k.name %}
         <td>{{ rv }}</td>
         {% endif %}
       {% endfor %}
    {% endfor %}
  </tr>
  {% endfor %}
{% endif %}
</table>


{% endif %}

{% if alert.result.extend_total > 0 or alert.result.extend_result_total_hits > 0 or alert.result.extend_result_sheets_total %}
<br>
===========================================================<br>
当前扩展搜索检索了{{ alert.result.extend_result_total_hits }}条数据，现返回{{ alert.result.extend_result_sheets_total }}个结果<br>
时间范围: {{ alert.strategy.trigger.start_time|date:"Y年n月d日 H:i:s" }}到{{ alert.strategy.trigger.end_time|date:"Y年n月d日 H:i:s" }}<br>
日志分组: {{ alert.search.extend_source_group }}<br>
查询语句: {{ alert.search.extend_query }}<br>
过滤条件: {{ alert.search.extend_filter}}<br><br>

<table>
{% if alert.result.extend_hits %}
{% if "raw_message" in alert.result.extend_hits.0.keys %}
{% for ext in alert.result.extend_hits %}
<tr><td>{{ ext.raw_message }}</td></tr>
{% endfor %}

{% elif "_count" in alert.result.extend_hits.0.keys %}

{% for ext in alert.result.extend_hits %}
{% for sis in ext.source %}
<tr><td>{{ sis.raw_message }}</td></tr>
{% endfor %}
<tr><td>---------------------</td></tr>
{% endfor %}

{% else %}
<tr>
{% for ks in alert.result.extend_hits.0.keys %}
<td>{{ ks }}</td>
{% endfor %}
</tr>
{% for ext in alert.result.extend_hits %}
    <tr>
    {% for the_key in ext.keys %}
    {% for key, value in ext.items %}
       {% if key == the_key %}
       <td>{{value}}</td>
       {% endif %}
    {% endfor %}
    {% endfor %}
    </tr>
{% endfor %}

{% endif %}

{% endif %}
</table>

{% endif %}

{% endif %}
                """,
                "style": {
                    "rows": 30,
                    "cols": 60
                }
            }
            ]
        }

def _web_conf_obj():
    confobj = {}
    try:
        cf = ConfigParser.ConfigParser()
        real_path = os.getcwd() + '/config'
        cf.read(real_path + "/yottaweb.ini")
        for section in cf.sections():
            confobj[section] = {}
            for k,v in cf.items(section):
                confobj[section][k] = v
    except Exception, e:
        re_logger.error("_yottaweb_conf_obj get failed!")
    return confobj

def _render(conf_obj, tmpl_str):
    t = Template(tmpl_str)
    c = Context(conf_obj)
    _content = t.render(c)
    return _content

def content(params, alert):
    template_str = params.get('configs')[2].get('value')
    conf_obj = {'alert': alert, 'web_conf': _web_conf_obj()}
    _content = _render(conf_obj, template_str)
    return _content

def handle(params, alert):
    # print(alert)
    # print "###########################mail params: ",params
    # print "###########################mail alert: ", alert

    # render subject
    subject_tmpl = params.get('configs')[0].get('value')
    subject_conf_obj = {'alert': alert}
    subject = _render(subject_conf_obj, subject_tmpl)

    receiver_str = params.get('configs')[1].get('value')
    _content = content(params, alert)

    send_mail(subject, receiver_str, _content)


def send_mail(subject, receiver, content):
    # print "###########################mail subject: ",subject
    # print "###########################mail receiver: ",receiver
    # print "###########################mail content: ",content

    try:
        cf = ConfigParser.ConfigParser()
        real_path = os.getcwd() + '/config'
        cf.read(real_path + "/yottaweb.ini")
        use_ssl = cf.get('email', 'use_ssl')
        need_login = cf.get('email', 'need_login')
        send_address = cf.get('email', 'send')
        smtp_pwd = cf.get('email', 'passwd')
        smtp_port = cf.get('email', 'smtp_port')
        smtp_server = cf.get('email', 'smtp_server')
    except Exception, e:
        print e
        use_ssl = "no"
        need_login = "yes"
        send_address = 'notice@yottabyte.cn'

    sub = subject
    content = content
    mail_to_list = receiver.split(',')
    if not mail_to_list:
        return
    mail_host = smtp_server
    mail_user = send_address
    mail_pass = smtp_pwd
    #
    # to_list:发给谁
    # sub:主题
    # content:内容
    # send_mail("sub","content")

    #
    main_msg = MIMEMultipart()
    me = mail_user
    msg = MIMEText(content, _subtype='html', _charset='gb18030')  # 创建一个实例，这里设置为html格式邮件
    main_msg.attach(msg)
    main_msg['Subject'] = sub
    main_msg['From'] = me
    main_msg['To'] = ";".join(mail_to_list)

    contype = 'application/octet-stream'
    maintype, subtype = contype.split('/', 1)

    # data = open(target_file, 'rb')
    # file_msg = MIMEBase(maintype, subtype)
    # file_msg.set_payload(data.read( ))
    # data.close( )
    # Encoders.encode_base64(file_msg)

    # 设置附件头
    # basename = os.path.basename(target_file)
    # file_msg.add_header('Content-Disposition', 'attachment', filename = basename)
    # main_msg.attach(file_msg)

    try:
        if use_ssl == "yes":
            s = smtplib.SMTP_SSL(mail_host, smtp_port)
        else:
            s = smtplib.SMTP(mail_host, smtp_port)
        # s.connect(mail_host)
        if need_login == "yes":
            s.login(mail_user, mail_pass)

        # re_logger.error(main_msg.as_string())
        s.sendmail(me, mail_to_list, main_msg.as_string())
        s.close()
        re_logger.info("Send email[ %s ] of report successful!" % (sub))
        return True
    except Exception, e:
        re_logger.error("Send mail [ %s ] Error: %s" % (sub, str(e)))
        return False
