#-*- coding: utf-8 -*-
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.variable.resources import MyVariable
from yottaweb.apps.utils.resources import MyUtils
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin, String
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame
from reportlab.graphics.charts.legends import Legend, LineLegend
from reportlab.graphics.charts.lineplots import LinePlot, ScatterPlot
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import HorizontalBarChart, VerticalBarChart
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.axes import NormalDateXValueAxis
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.platypus.tables import Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib import colors
from reportlab.lib import fonts
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import Encoders

import logging
import ConfigParser
import pymysql
import string
import smtplib
import json
import datetime
import os
import ast
import subprocess
import shutil
import re
import time
import math
import hashlib
import base64
from sets import Set
import threading


logger = logging.getLogger("yottaweb.audit")
re_logger = logging.getLogger("django.request")
gray30transparent = colors.Color(0.6, 0.6, 0.6, alpha=0.3)
gray50transparent = colors.Color(0.6, 0.6, 0.6, alpha=0.5)
gray90transparent = colors.Color(0.4, 0.4, 0.4, alpha=0.9)
gray95transparent = colors.Color(0.3, 0.3, 0.3, alpha=0.95)

path = os.path.dirname(os.path.realpath(__file__))
phantomjsPath = path + "/../../../services/phantomjs-prebuilt/bin/"
pdfmetrics.registerFont(TTFont('SimHei',path+'/static/simhei.ttf'))
for facename in ['SimHei']:
    fonts.addMapping(facename, 0, 0, facename) #normal
    fonts.addMapping(facename, 0, 1, facename) #italic
    fonts.addMapping(facename, 1, 0, facename) #bold
    fonts.addMapping(facename, 1, 1, facename) #italic and bold

chartColorArr = ['#acd062', '#3eb5ed', '#ff9326', '#b0b0b0', '#1dbca6', '#df5347', '#99cdff', '#fbc717', '#c19bdf', '#3d86d2', '#18b8ce', '#e563c2', '#80b142', '#ff8fa0', '#808080', '#826db0', '#1e9eef', '#eb727f', '#9b88e6', '#ec87c0']

try:
    cf = ConfigParser.ConfigParser()
    real_path = os.getcwd() + '/config'
    cf.read(real_path + "/yottaweb.ini")
    database = cf.get('db', 'fe_name')
    user = cf.get('db', 'user')
    pwd = cf.get('db', 'password')
    host = cf.get('db', 'host')
except Exception, e:
    print e
    database = "root"
    user = "root"
    pwd = "123456"
    host = "127.0.0.1"


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
    use_html = cf.get('email', 'use_html')
except Exception, e:
    print e
    use_ssl = "no"
    need_login = "yes"
    send_address = 'notice@yottabyte.cn'

master = MyVariable().get_var("client", "master") if MyVariable().get_var("client", "master") else "no"
report_type = MyVariable().get_var("report", "type") if MyVariable().get_var("report", "type") else "pdf"

#单个图表执行时间, 默认为15s
single_trend_execute_time = int(MyVariable().get_var("report", "single_trend_execute_time")) if MyVariable().get_var("report", "single_trend_execute_time") else 15

def refresh_date(frequency, time_range):
    if frequency == "day":
        yesterday = datetime.date.today() - datetime.timedelta(1)
        unix_time = yesterday.strftime("%s")
        yesterday_from = int(unix_time) * 1000
        yesterday_end = yesterday_from + 86400000 -1
        time_range = str(yesterday_from)+","+str(yesterday_end)
    elif frequency == "mon":
        this_month_start = int(time.mktime(datetime.date(datetime.date.today().year,datetime.date.today().month,1).timetuple())) * 1000
        last_month_end = this_month_start - 1000
        last_month_start = int(time.mktime(datetime.date(datetime.date.today().year,datetime.date.today().month-1,1).timetuple()))*1000
        time_range = str(last_month_start)+","+str(last_month_end)
    elif frequency == "wek":
        today = datetime.date.today()
        today_ts = int(time.mktime(today.timetuple())) * 1000
        day_of_week = int(time.strftime('%w',time.localtime()))
        first_of_week = today_ts - (day_of_week - 1) * 86400000
        last_week_from = first_of_week - 7 * 86400000
        last_week_end = first_of_week - 1000
        time_range = str(last_week_from) + "," + str(last_week_end)
    return time_range


def build_report(results):
    name = results["name"]
    lists = results["data"]
    trend_size = len(lists)
    token = results["token"]
    id = results["id"]
    subject = results["subject"]
    my_var = MyVariable()
    data_path = my_var.get_var('path', 'report_path')
    tmp_path = data_path + "yottaweb_reports/" + token + "/" + str(id) + "/"
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)

    ts = int(time.time()) * 1000
    create_time = time.strftime('%Y/%m/%d/ %H:%M:%S', time.localtime())
    cur_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
    file_name = name + '_' + cur_time +".pdf"
    target_file = os.path.join(tmp_path, file_name)

    tmp_image_path = data_path + "yottaweb_reports/tmp_image/" + name + "/" + cur_time + "/"
    if not os.path.exists(tmp_image_path):
        os.makedirs(tmp_image_path)
    imageList = []
    singleObj = {}
    tableObj = {}

    cm = 6
    elements = []
    doc = SimpleDocTemplate(target_file, rightMargin=0, leftMargin=0, topMargin=10 * cm, bottomMargin=8 * cm, pagesize=A4)

    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='center', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='right', alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='left', alignment=TA_LEFT))

    styleN = styles["Normal"]
    #used alignment if required
    # styleN.alignment = TA_LEFT
    styleN.fontSize = 8
    styleN.fontName = 'SimHei'
    styleN.wordWrap = 'CJK'

    styleL = styles["left"]
    styleL.fontName = 'SimHei'

    # 页眉 页脚
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        filename = data_path + "static/report_logo.jpg"
        gray30transparent = colors.Color(0.6, 0.6, 0.6, alpha=0.3)
        gray50transparent = colors.Color(0.6, 0.6, 0.6, alpha=0.5)
        canvas.setStrokeColor(gray30transparent)
        canvas.setFillColor(gray50transparent)
        canvas.setLineWidth(1)
        # 页眉
        canvas.setFont('Times-Bold',12)
        canvas.drawString(4 * cm, doc.height + 11 * cm, name)
        canvas.setFont('Times-Roman',10)
        canvas.drawString(doc.width-20*cm, doc.height + 11 * cm, create_time)
        canvas.line(4*cm, doc.height + 10 * cm, doc.width-4*cm, doc.height + 10 * cm)
        # 页脚
        canvas.line(4*cm, 6 * cm, doc.width-4*cm, 6 * cm)
        if os.path.exists(filename):
            canvas.drawImage(filename, 4 * cm, 1 * cm, width=60, height=25)
        canvas.setFont('SimHei',10)
        canvas.drawString(doc.width-10*cm, 2 * cm, "第 %s 页" % doc.page)
        canvas.setStrokeColor(colors.Color(0.6, 0.6, 0.6))
        canvas.setFillColor(colors.Color(0.6, 0.6, 0.6))

    # Header
    # header = Paragraph(name * 5, styles['Normal'])
    # w, h = header.wrap(doc.width, doc.topMargin)
    # yy = header.drawOn(, doc.leftMargin, doc.height + doc.topMargin - h)

    # p_text = '<font size=14>%s</font>' % name
    # time_text = '<font size=8>%s</font>' % create_time
    #
    # elements.append(Spacer(1, 24))
    #
    # elements.append(Paragraph(p_text, styles["center"]))
    # elements.append(Spacer(1, 12))
    # elements.append(Paragraph(time_text, styles["center"]))

    for index, section in enumerate(lists):
        param = section["param"]
        section_name = param["trendName"].split("|")[0]
        chartType = param.get("chartType")
        visType = param.get("visType")
        inData = ""
        if visType == "DLFB":
            chartType = "map"
        imageList.append(chartType + '_' +section_name)
        if index == 0:
            elements.append(Spacer(1, 30))
        else:
            elements.append(Spacer(1, 50))

        imageWidth = 500
        imageHeight = 300
        outfile = hashlib.md5(section_name.upper()).hexdigest() + '.jpeg'
        tmp_option_file = hashlib.md5(section_name.upper()).hexdigest() + '.js'
        # map保存为趋势图使用的visType=DLFB(没有chartType属性), 保存为报表元素使用的是visType=STATS_NEW (chartType == map), 当二者合并时，只能使用chartType=map去判断
        if chartType == "map":
            mapData = []
            try:
                mapType = str(param["mapType"])
                field = param["field"]
                dataRange = {"min": 0, "max": 0}
                for one in section["list"]:
                    mapData.append({"name": one[field], "value": one["count_"]})
                    if one["count_"] < dataRange["min"]:
                        dataRange["min"] = one["count_"]
                    if one["count_"] > dataRange["max"]:
                        dataRange["max"] = one["count_"]
            except Exception, e:
                print e
            min = dataRange["min"]
            max = dataRange["max"] + 5 - dataRange["max"] % 5
            labelShowBoolean = 'true' if mapType != 'world' else 'false'
            mapDataStr = "["
            for one in mapData:
                if str(one["name"]) != '*':
                    mapDataStr += "{name:'" + str(one["name"])+ "',value:" + str(one["value"]) + "},"
            mapDataStr += "]"
            options = "{title:{text:'" + section_name + "',x:'left', textStyle:{fontSize:22}},dataRange: {orient: 'vertical',x: 'left',y: 'bottom',min: " + str(min) + ",max: " + str(max) + ",splitNumber: 5,formatter: '{value} 到 {value2}',color: ['#41b5ff', '#daf4ff']},"
            options += "series: [{name: '事件数',type: 'map',mapType: '" + mapType + "',mapLocation: {x: 'center', y: 'center'},roam: false,itemStyle: {normal: {label: {show: " + labelShowBoolean + "},color: '#e6e6e6',borderColor: '#4faff0',borderWidth: 1},emphasis: {color: '#ffe344'}},data: " + mapDataStr
            if mapType == 'world':
                nameMap = '''{
                    'Afghanistan': '阿富汗',
                    'Angola': '安哥拉',
                    'Albania': '阿尔巴尼亚',
                    'United Arab Emirates': '阿联酋',
                    'Argentina': '阿根廷',
                    'Armenia': '亚美尼亚',
                    'French Southern and Antarctic Lands': '法属南半球和南极领地',
                    'Australia': '澳大利亚',
                    'Austria': '奥地利',
                    'Azerbaijan': '阿塞拜疆',
                    'Burundi': '布隆迪',
                    'Belgium': '比利时',
                    'Benin': '贝宁',
                    'Burkina Faso': '布基纳法索',
                    'Bangladesh': '孟加拉',
                    'Bulgaria': '保加利亚',
                    'The Bahamas': '巴哈马',
                    'Bosnia and Herzegovina': '波斯尼亚和黑塞哥维那',
                    'Belarus': '白俄罗斯',
                    'Belize': '伯利兹',
                    'Bermuda': '百慕大',
                    'Bolivia': '玻利维亚',
                    'Brazil': '巴西',
                    'Brunei': '文莱',
                    'Bhutan': '不丹',
                    'Botswana': '博茨瓦纳',
                    'Central African Republic': '中非',
                    'Canada': '加拿大',
                    'Switzerland': '瑞士',
                    'Chile': '智利',
                    'China': '中国',
                    'Ivory Coast': '象牙海岸',
                    'Cameroon': '喀麦隆',
                    'Democratic Republic of the Congo': '刚果(金)',
                    'Republic of the Congo': '刚果',
                    'Colombia': '哥伦比亚',
                    'Costa Rica': '哥斯达黎加',
                    'Cuba': '古巴',
                    'Northern Cyprus': '北塞浦路斯',
                    'Cyprus': '塞浦路斯',
                    'Czech Republic': '捷克',
                    'Germany': '德国',
                    'Djibouti': '吉布提',
                    'Denmark': '丹麦',
                    'Dominican Republic': '多明尼加共和国',
                    'Algeria': '阿尔及利亚',
                    'Ecuador': '厄瓜多尔',
                    'Egypt': '埃及',
                    'Eritrea': '厄立特里亚',
                    'Spain': '西班牙',
                    'Estonia': '爱沙尼亚',
                    'Ethiopia': '埃塞俄比亚',
                    'Finland': '芬兰',
                    'Fiji': '斐',
                    'Falkland Islands': '福克兰群岛',
                    'France': '法国',
                    'Gabon': '加蓬',
                    'United Kingdom': '英国',
                    'Georgia': '格鲁吉亚',
                    'Ghana': '加纳',
                    'Guinea': '几内亚',
                    'Gambia': '冈比亚',
                    'Guinea Bissau': '几内亚比绍',
                    'Equatorial Guinea': '赤道几内亚',
                    'Greece': '希腊',
                    'Greenland': '格陵兰',
                    'Guatemala': '危地马拉',
                    'French Guiana': '法属圭亚那',
                    'Guyana': '圭亚那',
                    'Honduras': '洪都拉斯',
                    'Croatia': '克罗地亚',
                    'Haiti': '海地',
                    'Hungary': '匈牙利',
                    'Indonesia': '印尼',
                    'India': '印度',
                    'Ireland': '爱尔兰',
                    'Iran': '伊朗',
                    'Iraq': '伊拉克',
                    'Iceland': '冰岛',
                    'Israel': '以色列',
                    'Italy': '意大利',
                    'Jamaica': '牙买加',
                    'Jordan': '约旦',
                    'Japan': '日本',
                    'Kazakhstan': '哈萨克斯坦',
                    'Kenya': '肯尼亚',
                    'Kyrgyzstan': '吉尔吉斯斯坦',
                    'Cambodia': '柬埔寨',
                    'South Korea': '韩国',
                    'Kosovo': '科索沃',
                    'Kuwait': '科威特',
                    'Laos': '老挝',
                    'Lebanon': '黎巴嫩',
                    'Liberia': '利比里亚',
                    'Libya': '利比亚',
                    'Sri Lanka': '斯里兰卡',
                    'Lesotho': '莱索托',
                    'Lithuania': '立陶宛',
                    'Luxembourg': '卢森堡',
                    'Latvia': '拉脱维亚',
                    'Morocco': '摩洛哥',
                    'Moldova': '摩尔多瓦',
                    'Madagascar': '马达加斯加',
                    'Mexico': '墨西哥',
                    'Macedonia': '马其顿',
                    'Mali': '马里',
                    'Myanmar': '缅甸',
                    'Montenegro': '黑山',
                    'Mongolia': '蒙古',
                    'Mozambique': '莫桑比克',
                    'Mauritania': '毛里塔尼亚',
                    'Malawi': '马拉维',
                    'Malaysia': '马来西亚',
                    'Namibia': '纳米比亚',
                    'New Caledonia': '新喀里多尼亚',
                    'Niger': '尼日尔',
                    'Nigeria': '尼日利亚',
                    'Nicaragua': '尼加拉瓜',
                    'Netherlands': '荷兰',
                    'Norway': '挪威',
                    'Nepal': '尼泊尔',
                    'New Zealand': '新西兰',
                    'Oman': '阿曼',
                    'Pakistan': '巴基斯坦',
                    'Panama': '巴拿马',
                    'Peru': '秘鲁',
                    'Philippines': '菲律宾',
                    'Papua New Guinea': '巴布亚新几内亚',
                    'Poland': '波兰',
                    'Puerto Rico': '波多黎各',
                    'North Korea': '北朝鲜',
                    'Portugal': '葡萄牙',
                    'Paraguay': '巴拉圭',
                    'Qatar': '卡塔尔',
                    'Romania': '罗马尼亚',
                    'Russia': '俄罗斯',
                    'Rwanda': '卢旺达',
                    'Western Sahara': '西撒哈拉',
                    'Saudi Arabia': '沙特阿拉伯',
                    'Sudan': '苏丹',
                    'South Sudan': '南苏丹',
                    'Senegal': '塞内加尔',
                    'Solomon Islands': '所罗门群岛',
                    'Sierra Leone': '塞拉利昂',
                    'El Salvador': '萨尔瓦多',
                    'Somaliland': '索马里兰',
                    'Somalia': '索马里',
                    'Republic of Serbia': '塞尔维亚',
                    'Suriname': '苏里南',
                    'Slovakia': '斯洛伐克',
                    'Slovenia': '斯洛文尼亚',
                    'Sweden': '瑞典',
                    'Swaziland': '斯威士兰',
                    'Syria': '叙利亚',
                    'Chad': '乍得',
                    'Togo': '多哥',
                    'Thailand': '泰国',
                    'Tajikistan': '塔吉克斯坦',
                    'Turkmenistan': '土库曼斯坦',
                    'East Timor': '东帝汶',
                    'Trinidad and Tobago': '特立尼达和多巴哥',
                    'Tunisia': '突尼斯',
                    'Turkey': '土耳其',
                    'United Republic of Tanzania': '坦桑尼亚联合共和国',
                    'Uganda': '乌干达',
                    'Ukraine': '乌克兰',
                    'Uruguay': '乌拉圭',
                    'United States of America': '美国',
                    'Uzbekistan': '乌兹别克斯坦',
                    'Venezuela': '委内瑞拉',
                    'Vietnam': '越南',
                    'Vanuatu': '瓦努阿图',
                    'West Bank': '西岸',
                    'Yemen': '也门',
                    'South Africa': '南非',
                    'Zambia': '赞比亚',
                    'Zimbabwe': '津巴布韦'
                }'''
                options += ',nameMap:' + nameMap
            options += "}]}"
            imageWidth = 500
            imageHeight = 360
        else:
            if visType == "SJJSTJ":
                data = {}
                try:
                    for item in param["fields"]:
                        data[item["name"]] = []
                    for item in section["list"]:
                        for a_head in param["fields"]:
                            data[a_head["name"]].append([item["ts"], item.get(a_head["name"])])
                except Exception, e:
                    print e
                dataStr = "["
                for item in param["fields"]:
                    dataStr += "{type: '" + item["chartType"] + "',name: '" + item["name"] + "', marker:{radius:3}, data: " + str(data[item["name"]]) + "},"
                dataStr += "]"
                dataStr = dataStr.replace('None', 'null')
                xAxisStr = "{labels:{style:{fontSize:6}}, gridLineWidth: 1, tickPixelInterval:25, type: 'datetime', dateTimeLabelFormats: {millisecond: '%H:%M:%S.%L', second: '%H:%M:%S',minute: '%H:%M',hour: '%b/%e,%H:%M',day: '%b/%e',week: '%b/%e',month: '%Y/%b',year: '%Y'}}"
                inData = "{title: {text: '" + section_name + "', align:'left', style:{fontSize:12}}, xAxis: " + xAxisStr  + ", yAxis: {labels:{style:{fontSize:6}, y:0}, minorTickInterval: 'auto', lineWidth: 1,tickWidth: 1, title: {text: ''}}, colors: " + str(chartColorArr) + ","
                inData += "legend: {enabled: true, symbolWidth:14, symbolHeight:8, itemStyle:{fontSize:6, fontWeight:'bold'}, labelFormatter: function () {return this.name;}}, plotOptions: {column: {pointPadding: 0, borderWidth: 1, groupPadding: 0, pointPlacement: -0.5}}, series: " + dataStr + ",credits: {enabled: false}}"
            elif visType == "SJSFDTJ_TIME":
                dataStr = "[{data:["
                categoriesStr = "["
                def f(x):
                    x = x.replace('\"', '')
                    return ' '.join(x.split(':', 1))
                try:
                    for index, item in enumerate(section["list"]):
                        categoriesStr += "'" + "~".join(map(f, item["tr"].split(" - "))) + "',"
                        dataStr += "{y:" + str(item.get("ct")) + ", color:'" + chartColorArr[index%20] + "'},"
                except Exception, e:
                        print e
                categoriesStr += "]"
                dataStr += "]}]"
                dataStr = dataStr.replace('None', 'null')
                inData = "{chart: {type: 'column',zoomType:'x',panning: true,panKey: 'shift'}, title: {text: '" + section_name + "', align:'left', style:{fontSize:12}}, xAxis: {labels: {staggerLines:1, overflow: false, style:{fontSize:6}}, categories:" + categoriesStr  + "},"
                inData += "yAxis: {labels:{style:{fontSize:6}, y:0}, title: {text: ''}}, plotOptions: {column: { dataLabels: {enabled: true,crop: false,overflow: 'none', style:{fontSize:6}}}}, legend: {enabled: false}, series: " + dataStr + ", credits: {enabled: false}}"
            elif visType == "SJSFDTJ_VALUE":
                dataStr = "[{data:["
                categoriesStr = "["
                try:
                    for index, item in enumerate(section["list"]):
                        categoriesStr += "'" + "~".join(item["vr"].split("-")) + "',"
                        dataStr += "{y:" + str(item.get("ct")) + ", color:'" + chartColorArr[index%20] + "'},"
                except Exception, e:
                        print e
                categoriesStr += "]"
                dataStr += "]}]"
                dataStr = dataStr.replace('None', 'null')
                inData = "{chart: {type: 'column',zoomType:'x',panning: true,panKey: 'shift'}, title: {text: '" + section_name + "', align:'left', style:{fontSize:12}}, xAxis: {title: {text: '" + param["stat_field"] + "'}, labels: {staggerLines:1, overflow: false, style:{fontSize:6}}, categories:" + categoriesStr  + "},"
                inData += "yAxis: {labels:{style:{fontSize:6}, y:0}, title: {text: ''}}, plotOptions: {column: { dataLabels: {enabled: true,crop: false,overflow: 'none', style:{fontSize:6}}}}, legend: {enabled: false}, series: " + dataStr + ", credits: {enabled: false}}"
            elif visType == "ZFT_TIME":
                dataStr = "[{name:'事件数', data:["
                categoriesStr = "["
                try:
                    for item in section["list"]:
                        timestamp = int(item.get("ts"))/1000
                        value = datetime.datetime.fromtimestamp(timestamp)
                        categoriesStr += "'" + value.strftime('%Y-%m-%d %H:%M:%S') + "',"
                        dataStr += "{y:" + str(item.get("ct")) + ", color:'" + chartColorArr[0] + "'},"
                except Exception, e:
                        print e
                categoriesStr += "]"
                dataStr += "]}]"
                dataStr = dataStr.replace('None', 'null')
                inData = "{chart: {type: 'column',zoomType:'x',panning: true,panKey: 'shift'}, title: {text: '" + section_name + "', align:'left', style:{fontSize:12}}, xAxis: {labels: {staggerLines:1, overflow: false, style:{fontSize:6}}, categories:" + categoriesStr  + "},"
                inData += "yAxis: {labels:{style:{fontSize:6}, y:0}, title: {text: ''}}, plotOptions: {column: { dataLabels: {enabled: true,crop: false,overflow: 'none', style:{fontSize:6}}}}, legend: {enabled: false}, series: " + dataStr + ", credits: {enabled: false}}"
            elif visType == "ZFT_VALUE":
                interval = int(param["stat_interval"])
                dataStr = "[{name:'事件数', data:["
                categoriesStr = "["
                try:
                    for item in section["list"]:
                        cur_from = int(item.get("vs"))
                        cur_to = cur_from + interval
                        categoriesStr += "'" + str(cur_from) + "~" + str(cur_to)+ "',"
                        dataStr += "{y:" + str(item.get("ct")) + ", color:'" + chartColorArr[0] + "'},"
                except Exception, e:
                        print e
                categoriesStr += "]"
                dataStr += "]}]"
                dataStr = dataStr.replace('None', 'null')
                inData = "{chart: {type: 'column',zoomType:'x',panning: true,panKey: 'shift'}, title: {text: '" + section_name + "', align:'left', style:{fontSize:12}}, xAxis: {title: {text: '" + param["stat_field"] + "'}, labels: {staggerLines:1,overflow: false, style:{fontSize:6}}, categories:" + categoriesStr  + "},"
                inData += "yAxis: {labels:{style:{fontSize:6}, y:0}, title: {text: ''}}, plotOptions: {column: { dataLabels: {enabled: true,crop: false,overflow: 'none', style:{fontSize:6}}}}, legend: {enabled: false}, series: " + dataStr + ", credits: {enabled: false}}"
            elif visType == "ZDFLTJ":
                curField = param["field"]
                if chartType == "pie":
                    dataStr = "[{name:'所占比例', type:'pie', data:["
                    try:
                        for item in section["list"]:
                            dataStr += "['" + str(item.get(curField)) + "'," + str(item.get('ct'))  + "],"
                    except Exception, e:
                            print e
                    dataStr += "]}]"
                elif chartType == "bar":
                    dataStr = "[{name:'事件数', type:'bar', data:["
                    try:
                        for item in section["list"]:
                            dataStr += "['" + str(item.get(curField)) + "'," + str(item.get('ct')) + "],"
                    except Exception, e:
                            print e
                    dataStr += "]}]"
                elif chartType == "line":
                    data = {}
                    try:
                        for item in param["options"]:
                            data[item] = []
                        for item in section["list"]:
                            for a_head in param["options"]:
                                if item[curField] == a_head:
                                    data[a_head].append([item["ts"], item.get("ct")])
                    except Exception, e:
                        print e
                    dataStr = "["
                    for item in param["options"]:
                        dataStr += "{name: '" + str(item) + "', marker:{radius:3}, data: " + str(data[item]) + "},"
                    dataStr += "]"
                    dataStr = dataStr.replace('None', 'null')
                    xAxisStr = "{labels:{style:{fontSize:6}}, gridLineWidth: 1, tickPixelInterval:25, type: 'datetime', dateTimeLabelFormats: {millisecond: '%H:%M:%S.%L', second: '%H:%M:%S',minute: '%H:%M',hour: '%b/%e,%H:%M',day: '%b/%e',week: '%b/%e',month: '%Y/%b',year: '%Y'}}"
                    inData = "{title: {text: '" + section_name + "', align:'left', style:{fontSize:12}}, xAxis: " + xAxisStr  + ", yAxis: {labels:{style:{fontSize:6}, y:0}, minorTickInterval: 'auto', lineWidth: 1,tickWidth: 1, title: {text: ''}}, colors: " + str(chartColorArr) + ","
                    inData += "legend: {enabled: true, symbolWidth:14, symbolHeight:8, itemStyle:{fontSize:6, fontWeight:'bold'}, labelFormatter: function () {return this.name;}}, series: " + dataStr + ",credits: {enabled: false}}"
            elif visType == "ZDSZTJ":
                curField = param["field"]
                data = {}
                options = []
                try:
                    for item in section["list"]:
                        if item[curField] in data:
                            data[item[curField]].append([item["ts"], item.get("ct")])
                        else:
                            data[item[curField]] = [[item["ts"], item.get("ct")]]
                            options.append(item[curField])
                except Exception, e:
                    print e
                dataStr = "["
                for item in options:
                    dataStr += "{name: '" + str(item) + "', type: '" + chartType + "', marker:{radius:3}, data: " + str(data[item]) + "},"
                dataStr += "]"
                dataStr = dataStr.replace('None', 'null')
                xAxisStr = "{labels:{style:{fontSize:6}}, gridLineWidth: 1, tickPixelInterval:25, type: 'datetime', dateTimeLabelFormats: {millisecond: '%H:%M:%S.%L', second: '%H:%M:%S',minute: '%H:%M',hour: '%b/%e,%H:%M',day: '%b/%e',week: '%b/%e',month: '%Y/%b',year: '%Y'}}"
                inData = "{title: {text: '" + section_name + "', align:'left', style:{fontSize:12}}, xAxis: " + xAxisStr  + ", yAxis: {labels:{style:{fontSize:6}, y:0}, minorTickInterval: 'auto', lineWidth: 1,tickWidth: 1, title: {text: ''}}, colors: " + str(chartColorArr) + ","
                inData += "legend: {enabled: true, symbolWidth:14, symbolHeight:8, itemStyle:{fontSize:6, fontWeight:'bold'}, labelFormatter: function () {return this.name;}}, series: " + dataStr + ",credits: {enabled: false}}"
            elif visType == "LJBFB":
                if param["reverse"] == False:
                    categoriesStr = "["
                    options = []
                    data = {}
                    if len(section["list"]) > 0:
                        listObj = section["list"][0]
                        try:
                            for item in section["heads"]:
                                itemArr = item.split(".")
                                categoriesStr += str(itemArr[-1]) + ","
                                curField = ".".join(itemArr[1:-1])
                                curData = math.ceil(listObj.get(item))
                                if curField in data:
                                    data[curField].append(curData)
                                else:
                                    data[curField] = [curData]
                                    options.append(curField)
                        except Exception, e:
                            print e
                        categoriesStr += ']'
                        dataStr = "["
                        for item in options:
                            dataStr += "{name: '" + str(item) + "', type: 'column', marker:{radius:3}, data: " + str(data[item]) + "},"
                        dataStr += "]"
                        dataStr = dataStr.replace('None', 'null')
                        xAxisStr = "{labels:{style:{fontSize:6}, format: '{value}%'}, categories: " + categoriesStr + "}"
                        inData = "{title: {text: '" + section_name + "', align:'left', style:{fontSize:12}}, xAxis: " + xAxisStr  + ", yAxis: {labels:{style:{fontSize:6}, y:0}, title: {text: ''}, floor:0}, colors: " + str(chartColorArr) + ","
                        inData += "plotOptions: {column: { dataLabels: {enabled: true,crop: false,overflow: 'none', style:{fontSize:6}}}}, legend: {enabled: true, symbolWidth:14, symbolHeight:8, itemStyle:{fontSize:6, fontWeight:'bold'}, labelFormatter: function () {return this.name;}}, series: " + dataStr + ",credits: {enabled: false}}"
                else:
                    p_title = '<para leftIndent=46><font size=10>%s</font></para>' % section_name
                    singleObj[section_name] = {}
                    singleObj[section_name]['title'] = section_name
                    elements.append(Paragraph(p_title, styles["left"]))
                    elements.append(Spacer(1, 12))
                    if len(section["heads"]) > 0:
                        key = section["heads"][0]
                        if len(section["list"]) > 0:
                            value = format_num(section["list"][0][key], 3)
                            defaultColor = '#19B8FF'
                            value_text = '<font color="' + str(defaultColor) + '" size=20>%s' % str(value) + '%</font>'
                            singleObj[section_name]['text'] = value_text
                            elements.append(Paragraph(value_text, styles["center"]))
                            elements.append(Spacer(1, 12))
            elif visType == "DJTJ":
                curField = param["stat_field"]
                if chartType == "pie":
                    sum = 0
                    dataStr = "[{name:'所占比例', data:["
                    try:
                        for item in section["list"]:
                            dataStr += "['" + str(item.get(curField)) + "'," + str(item.get('count_'))  + "],"
                            sum += item.get('count_')
                        otherCount = section["total"] - sum if section["total"] - sum else 0
                        dataStr += "['其他'," + str(otherCount)  + "]"
                    except Exception, e:
                            print e
                    dataStr += "]}]"
                elif chartType == "bar":
                    sum = 0
                    dataStr = "[{name:'事件数', type:'bar', data:["
                    try:
                        for index, item in enumerate(section["list"]):
                            dataStr += "['" + str(item.get(curField)) + "'," + str(item.get("count_")) + "],"
                            sum += item.get('count_')
                        otherCount = section["total"] - sum if section["total"] - sum else 0
                        dataStr += "['其他'," + str(otherCount) + "]"
                    except Exception, e:
                            print e
                    dataStr += "]}]"
                else:
                    curField = param["stat_field"]
                    data = {}
                    options = []
                    try:
                        for item in section["list"]:
                            if item[curField] in data:
                                data[item[curField]].append([item["ts"], item.get("ct")])
                            else:
                                data[item[curField]] = [[item["ts"], item.get("ct")]]
                                options.append(item[curField])
                    except Exception, e:
                        print e
                    dataStr = "["
                    for item in options:
                        dataStr += "{name: '" + str(item) + "', type: '" + chartType + "', marker:{radius:3}, data: " + str(data[item]) + "},"
                    dataStr += "]"
                    dataStr = dataStr.replace('None', 'null')
                    xAxisStr = "{labels:{style:{fontSize:6}}, gridLineWidth: 1, tickPixelInterval:25, type: 'datetime', dateTimeLabelFormats: {millisecond: '%H:%M:%S.%L', second: '%H:%M:%S',minute: '%H:%M',hour: '%b/%e,%H:%M',day: '%b/%e',week: '%b/%e',month: '%Y/%b',year: '%Y'}}"
                    inData = "{title: {text: '" + section_name + "', align:'left', style:{fontSize:12}}, xAxis: " + xAxisStr  + ", yAxis: {labels:{style:{fontSize:6}, y:0}, minorTickInterval: 'auto', lineWidth: 1,tickWidth: 1, title: {text: ''}}, colors: " + str(chartColorArr) + ","
                    inData += "legend: {enabled: true, symbolWidth:14, symbolHeight:8, itemStyle:{fontSize:6, fontWeight:'bold'}, labelFormatter: function () {return this.name;}}, series: " + dataStr + ",credits: {enabled: false}}"
            elif visType == "STATS_NEW":
                if chartType == "table":
                    p_title = '<para leftIndent=46><font size=10>%s</font></para>' % section_name
                    tableObj[section_name] = {}
                    tableObj[section_name]['title'] = section_name
                    tableObj[section_name]['heads'] = section["heads"]
                    tableObj[section_name]['data'] = section["list"]
                    elements.append(Paragraph(p_title, styles["left"]))
                    elements.append(Spacer(1, 12))
                    if len(section["heads"]) > 0:
                        table_data = []
                        table_data.append(section["heads"])
                        for item in section["list"]:
                            row = []
                            for a_head in section["heads"]:
                                row.append(Paragraph(str(item.get(a_head, 0)), styleN))
                            table_data.append(row)
                        cell_width = (doc.width-10*cm)/len(section["heads"])
                        table = Table(table_data, style=[
                            ("INNERGRID", (0, 0), (-1, -1), 0.5, gray50transparent),
                            ("LINEABOVE", (0, 1), (-1, 1), 1, colors.black),
                            ('ALIGN', (0, -1), (-1, -1), 'LEFT'),
                            ('VALIGN', (0, -1), (-1, -1), 'TOP'),
                            ("FONTSIZE", (0, 0), (-1, -1), 7),
                            ("FONTNAME", (0, 0), (-1, -1), 'SimHei'),
                            ("TEXTCOLOR", (0, 0), (-1, -1), gray95transparent),
                            ("LEFTPADDING", (0, 0), (-1, -1), 2),
                            ("RIFHTPADDING", (0, 0), (-1, -1), 2)
                        ], colWidths=cell_width)
                        elements.append(table)
                elif chartType == "single":
                    p_title = '<para leftIndent=46><font size=10>%s</font></para>' % section_name
                    singleObj[section_name] = {}
                    singleObj[section_name]['title'] = section_name
                    elements.append(Paragraph(p_title, styles["left"]))
                    elements.append(Spacer(1, 12))
                    x = param["xField"]
                    if len(section["list"]) > 0:
                        value = format_num(section["list"][0][x], 3)
                        defaultColor = param["defaultColor"]["value"]
                        colorValues = param["colorValues"]
                        length = len(colorValues)
                        if length != 0:
                            for i in range(length):
                                if colorValues[i]["from"] != '*' and colorValues[i]["to"] != '*':
                                    if value >= float(colorValues[i]["from"]) and value < float(colorValues[i]["to"]):
                                        defaultColor = colorValues[i]["color"]["value"]
                                        break
                                else:
                                    if colorValues[i]["from"] == '*':
                                        if value < float(colorValues[i]["to"]):
                                            defaultColor = colorValues[i]["color"]["value"]
                                            break
                                    else:
                                        if value >= float(colorValues[i]["from"]):
                                            defaultColor = colorValues[i]["color"]["value"]
                                            break
                        value_text = '<font color="' + str(defaultColor) + '" size=20>%s</font>' % str(value)
                        singleObj[section_name]['text'] = value_text
                        elements.append(Paragraph(value_text, styles["center"]))
                        elements.append(Spacer(1, 12))
                elif chartType == "line" or chartType == "area" or chartType == "scatter" or chartType == "column":
                    yCharts = []
                    data = []
                    uniq = {}
                    tmp_uniq = {}
                    _section_by = section["by"] if section["by"] else []
                    try:
                        x = param["xField"]
                        if "yfield" in param:
                            yFields = param["yField"].split(",")
                        elif "yFields" in param:
                            yFields = param["yFields"].split(",")
                        if "yCharts" in param:
                            yCharts = param["yCharts"].split(",")
                        if len(_section_by) == 0:
                            for item in yFields:
                                uniq[item] = []
                            for one in section["list"]:
                                for item in yFields:
                                    uniq[item].append([one[x].encode("utf-8") if isinstance(one[x], basestring) else one[x], one.get(item)])
                        else:
                            for i in range(len(yFields)):
                                uniq[yFields[i]] = {}
                                tmp_uniq[yFields[i]] = {}
                            for one in section["list"]:
                                for k in range(len(yFields)):
                                    new_key = ""
                                    temp_new_key = str(one[x])
                                    for a_b in _section_by:
                                        new_key = str(one[a_b]) if new_key == "" else str(new_key) +"_" + str(one[a_b])
                                        temp_new_key += "_" + str(one[a_b])
                                    if not new_key in uniq[yFields[k]]:
                                        uniq[yFields[k]][new_key] = []
                                    if not temp_new_key in tmp_uniq[yFields[k]]:
                                        tmp_uniq[yFields[k]][temp_new_key] = one.get(yFields[k])
                                    else:
                                        if tmp_uniq[yFields[k]][temp_new_key] == None:
                                            tmp_uniq[yFields[k]][temp_new_key] = one.get(yFields[k])
                                        else:
                                            if one.get(yFields[k]) != None:
                                                tmp_uniq[yFields[k]][temp_new_key] += one.get(yFields[k])
                                    uniq[yFields[k]][new_key].append([one[x].encode("utf-8") if isinstance(one[x], basestring) else one[x], tmp_uniq[yFields[k]][temp_new_key]])
                    except Exception, e:
                        print e
                    yAxisStr = "["
                    for i in range(len(yFields)):
                        yAxisStr += "{labels:{style:{fontSize:6}, y:0}, minorTickInterval: 'auto', lineWidth: 1,tickWidth: 1, title:{text:'" + yFields[i] + "', style:{fontSize:6, fontWeight:'bold'}}"
                        if i != 0:
                            yAxisStr += ", gridLineWidth: 0, opposite: true"
                        yAxisStr += "},"
                    yAxisStr += ']'
                    series = []
                    if len(_section_by) == 0:
                        for i in range(len(yFields)):
                            curChartType = chartType
                            if yCharts and yCharts[i]:
                                curChartType = yCharts[i]
                            serie = {
                                "name": yFields[i],
                                "type": curChartType,
                                "data": uniq[yFields[i]]
                            }
                            if i != 0:
                                serie["yAxis"] = i
                            series.append(serie)
                        try:
                            xAxisTestData = uniq.values()[0]
                        except Exception, e:
                            xAxisTestData = None
                    else:
                        symbolIndex = 0
                        for j in range(len(yFields)):
                            for key, value in uniq[yFields[j]].items():
                                curChartType = chartType
                                if yCharts and yCharts[j]:
                                    curChartType = yCharts[j]
                                serie = {
                                    "name": key,
                                    "type": curChartType,
                                    "data": value,
                                    "_symbolIndex": symbolIndex
                                }
                                symbolIndex += 1
                                if j != 0:
                                    serie["yAxis"] = j
                                series.append(serie)
                        series = sorted(series, key=lambda x: x["name"])
                        for i in range(1, len(series)):
                            if series[i]["name"] == series[i-1]["name"]:
                                series[i]["linkedTo"] = ':previous'
                                series[i]["_symbolIndex"] = series[i-1]["_symbolIndex"]
                        try:
                            xAxisTestData = uniq[yFields[0]].values()[0]
                        except Exception, e:
                            xAxisTestData = None
                    dataStr = "["
                    for item in series:
                        dataStr += "{type: '" + item["type"] + "',name: '" + item["name"] + "',data: " + str(item["data"])
                        if item.get("yAxis") != None:
                            dataStr += ",yAxis:" + str(item["yAxis"])
                        if item.get("linkedTo") != None:
                            dataStr += ",linkedTo:" + "'" + item["linkedTo"] + "'"
                        if item.get("_symbolIndex") != None:
                            dataStr += ",_symbolIndex:" + str(item["_symbolIndex"])
                        dataStr += "},"
                    dataStr += "]"
                    dataStr = dataStr.replace('None', 'null')
                    if xAxisTestData != None and xAxisTestData[0] != None and re.match(r"\d{13}$", str(xAxisTestData[0][0])) != None:
                        xAxisStr = "{labels:{style:{fontSize:6}}, gridLineWidth: 1, tickPixelInterval:25, type: 'datetime', dateTimeLabelFormats: {millisecond: '%H:%M:%S.%L', second: '%H:%M:%S',minute: '%H:%M',hour: '%b/%e,%H:%M',day: '%b/%e',week: '%b/%e',month: '%Y/%b',year: '%Y'}}"
                    else:
                        xAxisStr = "{labels:{style:{fontSize:6}}, gridLineWidth: 1, tickPixelInterval:50, type: 'category'}"

                    plotOptions = "{series: {marker: {enabled: false}}}"
                    inData = "{title: {text: '" + section_name + "', align:'left', style:{fontSize:12}}, plotOptions: " + plotOptions + " ,xAxis: " + xAxisStr + ", yAxis: " + yAxisStr + ", colors: " + str(chartColorArr) + ","
                    inData += "legend: {enabled: true, symbolWidth:14, symbolHeight:8, itemStyle:{fontSize:6, fontWeight:'bold'}, labelFormatter: function () {return this.name;}}, series: " + dataStr + ",credits: {enabled: false}}"
                elif chartType == "pie":
                    uniq = {}
                    if isinstance(param["cur_ByFields"], basestring):
                        param["cur_ByFields"] = param["cur_ByFields"].split(",")
                    try:
                        x = param["xField"]
                        for one in section["list"]:
                            new_key = ""
                            for a_b in param["cur_ByFields"]:
                                new_key = str(one[a_b]) if new_key == "" else str(new_key) +"_" + str(one[a_b])
                            uniq[new_key] = one[x]
                    except Exception, e:
                        print e
                    data = sorted(uniq.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
                    dataStr = "[{type: 'pie',data:["
                    for one in data:
                        dataStr += "['" + one[0] + "'," + str(one[1]) + "],"
                    dataStr += "]}]"
                elif chartType == "bar":
                    uniq = {}
                    if isinstance(param["cur_ByFields"], basestring):
                        param["cur_ByFields"] = param["cur_ByFields"].split(",")
                    try:
                        x = param["xField"]
                        for one in section["list"]:
                            new_key = ""
                            for a_b in param["cur_ByFields"]:
                                new_key = str(one[a_b]) if new_key == "" else str(new_key) +"_" + str(one[a_b])
                            uniq[new_key] = one[x]
                    except Exception, e:
                        print e
                    data = sorted(uniq.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
                    dataStr = "[{type: 'bar',data:["
                    for one in data:
                        dataStr += "['" + one[0] + "'," + str(one[1]) + "],"
                    dataStr += "]}]"
                elif chartType == "rangeline":
                    averages = []
                    outliers = []
                    ranges = []
                    try:
                        x = param["xField"]
                        average = param["yField"]
                        outlier = param["outlierField"]
                        upper = param["upperField"]
                        lower = param["lowerField"]
                        for one in section["list"]:
                            averages.append([one[x], one[average]])
                            if one.get(outlier) != None:
                                outliers.append([one[x], one[outlier]])
                            if one.get(upper) != None and one.get(lower) != None:
                                ranges.append([one[x], one[lower], one[upper]])
                    except Exception, e:
                        print e
                    if averages[0] != None and re.match(r"\d{13}$", str(averages[0][0])) != None:
                        xAxisStr = "{labels:{style:{fontSize:6}}, gridLineWidth: 1, tickPixelInterval:25, type: 'datetime', dateTimeLabelFormats: {millisecond: '%H:%M:%S.%L', second: '%H:%M:%S',minute: '%H:%M',hour: '%b/%e,%H:%M',day: '%b/%e',week: '%b/%e',month: '%Y/%b',year: '%Y'}}"
                    else:
                        xAxisStr = "{labels:{style:{fontSize:6}}, gridLineWidth: 1, tickPixelInterval:50, type: 'category'}"
                    inData = "{title: {text: '" + section_name + "', align:'left', style:{fontSize:12}}, xAxis: " + xAxisStr + ", yAxis:{labels:{style:{fontSize:6}, y:0}, minorTickInterval: 'auto', lineWidth: 1,tickWidth: 1, title:{text:''}}, legend:{enabled: true, symbolWidth:14, symbolHeight:8, itemStyle:{fontSize:6}},series: [{name: 'Averages',data:" + str(averages) + ",zIndex:1, marker: {fillColor: 'white',lineWidth: 3,radius: 2,lineColor: Highcharts.getOptions().colors[0]}}, {name: 'Outlier',data:" + str(outliers) + ",type: 'scatter', marker: {radius: 3}, zIndex:2}, {name: 'Range',data:" + str(ranges) + ",type: 'arearange', zIndex: 0, lineWidth: 0, fillOpacity: 0.3}],credits: {enabled: false}}"
                elif chartType == "chord":
                    nodes = "["
                    links = "["
                    try:
                        fromField = param["fromField"]
                        toField = param["toField"]
                        weightField = param["weightField"]
                        tmp_set = Set()
                        for one in section["list"]:
                            tmp_set.add(one[fromField])
                            tmp_set.add(one[toField])
                            links += "{source:'" + one[fromField] + "', target:'" + one[toField] + "', weight: " + str(one[weightField]) + "},"
                            links += "{target:'" + one[fromField] + "', source:'" + one[toField] + "', weight: " + str(one[weightField]) + "},"
                        tmp_nodes = list(tmp_set)
                        for item in tmp_nodes:
                            nodes += "{name:'" +  item + "'},"
                        if nodes == "[":
                            nodes += ","
                        nodes += "]"
                        links += "]"
                    except Exception, e:
                        print e
                    options = "{title: {text: '" + section_name + "',x:'left', textStyle:{fontSize:22}}, colors: " + str(chartColorArr) + ", legend: {x: 'left', data: []}, series: [{type: 'chord', sort: 'ascending', sortSub: 'descending', radius: ['46%','50%'], showScale: false, itemStyle: {normal: {label: {rotate: true, distance: 5, textStyle: {fontSize: 12, fontWeight: 'normal'}}}}, nodes: " + nodes + ", links: " + links + "}]}"

        if chartType != "table" and chartType != "single" and chartType != "one":
            if chartType == 'pie':
                dataStr = dataStr.replace('None', 'null')
                inData = "{chart: {type: 'pie'}, title: {text: '" + section_name + "', align:'left', style:{fontSize:12}}, colors: " + str(chartColorArr) + ",legend: {enabled: false},"
                inData += "plotOptions: {pie: {innerSize: '40%',size: '50%',dataLabels: {enabled: true, style:{fontSize:6, fontWeight:'bold'}, formatter:function(){return '<b>'+this.point.name.slice(0,20)+'</b>: 约'+this.percentage.toFixed(2)+' %';}}}},"
                inData += "series: " + dataStr + ",credits: {enabled: false}}"
                imageWidth = 500
                imageHeight = 320
            elif chartType == 'bar':
                dataStr = dataStr.replace('None', 'null')
                inData = "{chart: {type: 'bar'}, title: {text: '" + section_name + "', align:'left', style:{fontSize:12}}, colors: " + str(chartColorArr) + ", xAxis: {categories: [], title: {text: ''}, labels: {style:{fontSize:6, fontWeight:'bold'}, y:0}},"
                inData += "yAxis: {min: 0,title: {text: 'Count',align: 'high', style:{fontSize:6, fontWeight:'bold'}},labels: {overflow: 'justify', style:{fontSize:6}}},legend: {enabled: false},plotOptions: {bar: {minPointLength: 3, dataLabels: {enabled: true,crop: false,overflow: 'none', style:{fontSize:6}}}},"
                inData += "series: " + dataStr + ",credits: {enabled: false}}"

            if chartType == "map" or chartType == "chord":
                cmd = phantomjsPath + 'phantomjs ' + path + '/static/echarts-convert.js -options' + ' \"' + options + '\" ' + '-outfile ' + tmp_image_path + outfile + ' -width ' + str(imageWidth * 2) + ' -height ' + str(imageHeight * 2)
            else:
                tmp_option_file_path = tmp_image_path + tmp_option_file
                if not os.path.exists(tmp_image_path):
                    os.makedirs(tmp_image_path)

                f = open(tmp_option_file_path,"w")
                f.write(inData)
                f.close()
                cmd = phantomjsPath + 'phantomjs ' + path + '/static/highcharts-convert.js -infile' + ' ' + tmp_option_file_path + ' ' + '-outfile ' + tmp_image_path + outfile + ' -width ' + str(imageWidth * 2)
            re_logger.info("##### Report CMD #####: %s", cmd)
            try:
                RunCmd([cmd], 15).Run()
                re_logger.info("cul!")
                elements.append(Image(tmp_image_path + outfile, width=imageWidth, height=imageHeight))
            except Exception, e:
                print e
                re_logger.info("subprocess error: %s", e)
    try:
        doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)
        re_logger.info("create pdf successful!")
        update_table(str(ts), results["report_id"])
        sleep_time = trend_size * single_trend_execute_time
        prev = time.time()
        while True:
            now = time.time()
            if now - prev > sleep_time:
                break
            else:
                pass
        send_mail(name, results["email"], target_file, subject, tmp_image_path, imageList, singleObj, tableObj)
        if os.path.exists(tmp_image_path):
            shutil.rmtree(tmp_image_path)
    except Exception, e:
        if os.path.exists(tmp_image_path):
            shutil.rmtree(tmp_image_path)
        print e
        re_logger.info("build report error: %s", e)


def update_table(ts, id):
    try:
        conn = pymysql.connect(host=host, user=user, passwd=pwd, db=database, charset='utf8',
                                   cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        sql = "UPDATE Report SET lasttrigger='%s' WHERE id='%s'" % (ts, id)
        print sql
        cur.execute(sql)
        conn.commit()
    except pymysql.Error, e:
        logger.info("PyMySQL Error when update_table %d: %s" % (e.args[0], e.args[1]))


def send_mail(name, emails, target_file, subject, tmp_image_path, imageList, singleObj, tableObj):
    sub = _build_subject(subject, name)
    print emails
    mail_to_list = emails.split(',')
    if not mail_to_list:
        re_logger.info("SendMail Error email:" % (emails))
        return
    mail_host = smtp_server
    mail_user = send_address
    mail_pass = smtp_pwd

    main_msg = MIMEMultipart()
    main_msg['Subject'] = sub
    main_msg['From'] = mail_user
    main_msg['To'] = ";".join(mail_to_list)

    if report_type == "url":
        my_utils = MyUtils()
        _web_address = MyVariable().get_var("custom", "web_address") if MyVariable().get_var("custom", "web_address") else "http://www.rizhiyi.com"
        _download_url = _web_address + '/api/v0/report/files/download/directly/' + \
            my_utils.b64Encrypt(base64.urlsafe_b64encode(target_file)) + '/?format=json'
        content = u"<html><body><h3>用户您好, 请使用以下链接下载报表文件</h3>"
        content += "<hr/><a style='margin-left:1%' href='"+_download_url+"'>"+'点击下载'+"</a>"
        content += "</body></html>"
        msg = MIMEText(content, _subtype = 'html', _charset = 'utf-8')  # 创建一个实例，这里设置为html格式邮件
        main_msg.attach(msg)
    else:
        with open(target_file, 'rb') as f:
            file_msg = MIMEBase('application', 'octet-stream')
            file_msg.set_payload(f.read())
            Encoders.encode_base64(file_msg)
            file_msg.add_header('Content-Disposition', 'attachment', filename = os.path.basename(target_file))
            main_msg.attach(file_msg)

        if use_html == 'no':
            msg = MIMEText(u"用户您好, 请查收附件中报表", _subtype = 'plain', _charset = 'utf-8')  # 创建一个实例，这里设置为html格式邮件
            main_msg.attach(msg)
        else:
            content = u"<html><body><h3>用户您好, 请查看邮件中的报表并下载报表文件</h3>"
            for index, image in enumerate(imageList):
                type, name = image.split('_', 1)
                if type == 'single' or type == 'one':
                    title = singleObj[name]['title']
                    text = singleObj[name]['text']
                    content += "<hr/><p style='margin-left:1%'><font size=4>" + title + "</font></p>"
                    content += "<p style='margin-left:30%'>" + text + "</p>"
                elif type == 'table':
                    title = tableObj[name]['title']
                    content += "<hr/><p style='margin-left:1%'><font size=4>" + title + "</font></p>"
                    content += "<table rules='all' cellpadding='4' width='80%' style='table-layout: fixed; word-wrap:break-word; word-break:break-all;'><tr align='left'>"
                    for head in tableObj[name]['heads']:
                        content += "<th>" + head + "</th>"
                    content += "</tr>"
                    for item in tableObj[name]['data']:
                        content += "<tr>"
                        for head in tableObj[name]['heads']:
                            content += "<td>" + str(item.get(head, "")) + "</td>"
                        content += "</tr>"
                    content += "</table></br>"
                else:
                    imageRealPath = tmp_image_path + hashlib.md5(name.upper()).hexdigest() + '.jpeg'
                    basename = os.path.basename(imageRealPath).encode('gb2312')
                    try:
                        with open(imageRealPath, 'rb') as f:
                            mime = MIMEBase('image', 'jpeg', filename = basename)
                            mime.add_header('Content-Disposition', 'attachment', filename = basename)
                            mime.add_header('Content-ID', '<' + "abc"+str(index) + '>')
                            mime.add_header('X-Attachment-Id', "abc"+str(index))
                            mime.set_payload(f.read())
                            Encoders.encode_base64(mime)
                            main_msg.attach(mime)
                            content += "<hr/><p><img src='cid:" + "abc"+str(index) + "' width='auto' height='600px'></p>"
                    except Exception, e:
                        re_logger.info("build report email error: %s", e)
            content += "</body></html>"
            print content
            msg = MIMEText(content, _subtype = 'html', _charset = 'utf-8')
            main_msg.attach(msg)
    try:
        if use_ssl == "yes":
            s = smtplib.SMTP_SSL(mail_host, smtp_port)
        else:
            s = smtplib.SMTP(mail_host, smtp_port)
        # s.connect(mail_host)
        if need_login == "yes":
            s.login(mail_user, mail_pass)
        s.sendmail(mail_user, mail_to_list, main_msg.as_string())
        s.close()
        re_logger.info("Send email[ %s ] of report successful!" % (sub))
        return True
    except Exception, e:
        re_logger.info("Send mail [ %s ] Error: %s" % (sub, str(e)))
        return False


def _build_subject(tpl, name):
    if not tpl:
        return "报表_" + name
    cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    tpl_arr = tpl.split("<%")
    f_str = ""
    for t in tpl_arr:
        if t:
            p = t.split("%>")
            for x in p:
                if x and x.strip() == "report_name":
                    f_str = f_str + name
                elif x and x.strip() == "report_time":
                    f_str = f_str + cur_time
                elif x:
                    f_str = f_str + x
    return f_str

def build_stats(stats):
    re_logger.info("data passed to build_stats: %s", stats)
    is_bucket = False
    for l in stats:
        if "bucket" in l:
            is_bucket = True
            break
    if len(stats) > 0 and is_bucket:
        result = {
            "heads": [],
            "by": [],
            "x_arr": [],
            "y_arr": [],
            "list": [],
            "method": "bucket",
            "method_cnt": 1
        }
        row_one = stats[0]

        result["x_arr"] = row_one["bucket"]

        tmp_heads = []
        if "fields" in row_one:
            tmp_heads.append("fields")
            bucket_field = row_one["bucket"][0]
            for (k, v) in row_one["fields"].items():
                result["heads"].append(k)
                if not k == bucket_field:
                    result["by"].append(k)
        if "eval" in row_one:
            tmp_heads.append("eval")
            for (k, v) in row_one["eval"].items():
                result["heads"].append(k)
                result["y_arr"].append(k)
        for (method, value) in row_one.items():
            if not method == "eval" and not method == "fields" and not method == "bucket":
                tmp_heads.append(method)
                if "as_field" in value:
                    result["heads"].append(value["as_field"])
                    result["y_arr"].append(value["as_field"])
                else:
                    result["heads"].append(method)
                    result["y_arr"].append(method)

        # print result["heads"]
        for item in stats:
            val = {}
            for key in tmp_heads:
                if key == "eval" or key == "fields":
                    for (k, v) in item[key].items():
                        val[k] = format_num(v, 8)
                else:
                    if "as_field" in item[key]:
                        val[item[key]["as_field"]] = format_num(item[key]["value"], 8)
                    else:
                        val[key] = format_num(item[key]["value"], 8)
            result["list"].append(val)
    else:
        result = {
            "heads": [],
            "by": [],
            "x_arr": [],
            "y_arr": [],
            "list": [],
            "method": "bucket",
            "method_cnt": 1
        }
    re_logger.info("result returned by build_stats: %s", result)
    return result


def build_stats_new(res, param):
    re_logger.info("data passed to build_stats_new: %s", len(str(res)))
    result = {
        "heads": [],
        "by": [],
        "x_arr": [],
        "y_arr": [],
        "list": [],
        "total": 0
    }
    if "sheets" in res:
        for item in res["sheets"].get("_field_infos_", []):
            result["heads"].append(item["name"])
        result["list"] = res["sheets"]["rows"]
        result["total"] = res["sheets"].get("total", len(result["list"]) if (type(result["list"]) is list) else 0)
    result["by"] = param.get("cur_ByFields", [])
    result["x_arr"] = param.get("xField", [])
    result["y_arr"] = param.get("yField", [])
    re_logger.info("result returned from build_stats_new: %s", len(str(result)))
    return result


def format_num(n, point):
    if isinstance(n, float):
        format = '%.' + str(point) + 'f'
        return float(format % n)
    else:
        return n


class RunCmd(threading.Thread):
    def __init__(self, cmd, timeout):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.timeout = timeout

    def run(self):
        self.p = subprocess.Popen(self.cmd, shell=True)
        self.p.wait()

    def Run(self):
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            self.p.terminate()      #use self.p.kill() if process needs a kill -9
            self.join()
