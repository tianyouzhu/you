# bindai (dai.bin@yottabyte.cn)
# 2016/06/01
# Copyright 2014-2016 Yottabyte
# file description : resources.py
__author__ = "bindai"

import time

class MyUtils():

    def getFromToDate(self, time_range=""):
        if not time_range:
            return ""
        timeranges = time_range.split(",")
        fromDate = timeranges[0]
        toDate = timeranges[1]
        now = int(round(time.time() * 1000))
        if fromDate == "now":
            fromDate = now
        elif len(fromDate) < 13:
            if fromDate[0] == "-":
                fromDate = now - self.getUnixTimeInterval(fromDate[1:])
        if toDate == "now":
            toDate = now
        elif len(toDate) < 13:
            if toDate[0] == "-":
                toDate = now - self.getUnixTimeInterval(toDate[1:])
        return {
            "fromDate": fromDate,
            "toDate": toDate
        }

    def getUnixTimeInterval(self, interval=""):
        if not interval:
            return ""
        number = interval[:-1]
        unit = interval[-1]
        if unit == "S":
            return int(number)
        if unit == "s":
            return int(number) * 1000
        if unit == "m":
            return int(number) * 1000 * 60
        if unit == "h":
            return int(number) * 1000 * 60 * 60
        if unit == "d":
            return int(number) * 1000 * 60 * 60 * 24
        if unit == "w":
            return int(number) * 1000 * 60 * 60 * 24 * 7
        if unit == "M":
            return int(number) * 1000 * 60 * 60 * 24 * 30
        if unit == "y":
            return int(number) * 1000 * 60 * 60 * 24 * 30 * 12
        return 0

    def convertNumericRangeToStringRange(self, range=""):
        if not range:
            return ""
        range = int(range)
        if range > 1000 * 60 * 60 * 24 * 30 * 12:
            number = range/(1000 * 60 * 60 * 24 * 30 * 12)
            unit = 'y'
        elif range > 1000 * 60 * 60 * 24 * 30:
            number = range/(1000 * 60 * 60 * 24 * 30)
            unit = 'M'
        elif range > 1000 * 60 * 60 * 24 * 7:
            number = range/(1000 * 60 * 60 * 24 * 7)
            unit = 'w'
        elif range > 1000 * 60 * 60 * 24:
            number = range/(1000 * 60 * 60 * 24)
            unit = 'd'
        elif range > 1000 * 60 * 60:
            number = range/(1000 * 60 * 60)
            unit = 'h'
        elif range > 1000 * 60:
            number = range/(1000 * 60)
            unit = 'm'
        elif range > 1000:
            number = range/1000
            unit = 's'
        else:
            number = range
            unit = 'S'
        return str(number) + unit

    def getSpan(self, range):
        rangeSpanMap = {
            "1y": "1M",
            "6M": "1w",
            "3M": "5d",
            "2M": "2d",
            "1M": "1d",
            "15d": "12h",
            "1w": "6h",
            "2d": "3h",
            "1d": "1h",
            "12h": "30m",
            "6h": "15m",
            "3h": "10m",
            "90m": "5m",
            "60m": "2m",
            "30m": "1m",
            "12m": "30s",
            "6m": "15s",
            "3m": "10s",
            "90s": "5s",
            "60s": "2s",
            "30s": "1s",
            "15000S": "500S",
            "7500S": "250S",
            "4500S": "150S",
            "3000S": "100S",
            "1500S": "50S",
            "750S": "25S",
            "300S": "10S",
            "150S": "5S",
            "60S": "2S",
            "30S": "1S"
        }
        span = ""
        range = int(range)
        if range > 1000 * 60 * 60 * 24 * 30 * 24:
            span = rangeSpanMap["1y"]
        elif range > 1000 * 60 * 60 * 24 * 30 * 6:
            span = rangeSpanMap["6M"]
        elif range > 1000 * 60 * 60 * 24 * 30 * 3:
            span = rangeSpanMap["3M"]
        elif range > 1000 * 60 * 60 * 24 * 30 * 2:
            span = rangeSpanMap["2M"]
        elif range > 1000 * 60 * 60 * 24 * 30 * 1:
            span = rangeSpanMap["1M"]
        elif range > 1000 * 60 * 60 * 24 * 15:
            span = rangeSpanMap["15d"]
        elif range > 1000 * 60 * 60 * 24 * 7:
            span = rangeSpanMap["1w"]
        elif range > 1000 * 60 * 60 * 24 * 2:
            span = rangeSpanMap["2d"]
        elif range > 1000 * 60 * 60 * 24 * 1:
            span = rangeSpanMap["1d"]
        elif range > 1000 * 60 * 60 * 12:
            span = rangeSpanMap["12h"]
        elif range > 1000 * 60 * 60 * 6:
            span = rangeSpanMap["6h"]
        elif range > 1000 * 60 * 60 * 3:
            span = rangeSpanMap["3h"]
        elif range > 1000 * 60 * 90:
            span = rangeSpanMap["90m"]
        elif range > 1000 * 60 * 60:
            span = rangeSpanMap["60m"]
        elif range > 1000 * 60 * 30:
            span = rangeSpanMap["30m"]
        elif range > 1000 * 60 * 12:
            span = rangeSpanMap["12m"]
        elif range > 1000 * 60 * 6:
            span = rangeSpanMap["6m"]
        elif range > 1000 * 60 * 3:
            span = rangeSpanMap["3m"]
        elif range > 1000 * 90:
            span = rangeSpanMap["90s"]
        elif range > 1000 * 60:
            span = rangeSpanMap["60s"]
        elif range > 1000 * 30:
            span = rangeSpanMap["30s"]
        elif range > 1000 * 15:
            span = rangeSpanMap["15000S"]
        elif range > 7500:
            span = rangeSpanMap["7500S"]
        elif range > 4500:
            span = rangeSpanMap["4500S"]
        elif range > 3000:
            span = rangeSpanMap["3000S"]
        elif range > 1500:
            span = rangeSpanMap["1500S"]
        elif range > 750:
            span = rangeSpanMap["750S"]
        elif range > 300:
            span = rangeSpanMap["300S"]
        elif range > 150:
            span = rangeSpanMap["150S"]
        elif range > 60:
            span = rangeSpanMap["60S"]
        elif range > 30:
            span = rangeSpanMap["1S"]
        else:
             span = "1S"
        return span

    def generateSPLQuery(self, name, obj):
        spl = ""
        if name == "SJJSTJ":
            stats = ""
            for item in obj["fields"]:
                statisType = "count" if item["isUnique"] == "false" else "dc"
                stats += " " + statisType + '(' + item["name"] + ') as ' + item["name"] + " ,"
            stats = stats[:-1]
            spl = "|bucket timestamp span=" + obj["span"] + " as ts |stats " + stats + " by ts"
        elif name == "SJSFDTJ_TIME":
            timeranges = ""
            for item in obj["times"]:
                timeranges += " (" + item["from"] + ", " + item["to"] + "),"
            timeranges = timeranges[:-1]
            spl = '|bucket timestamp timeranges=(' + timeranges + ') as tr |stats ' + obj["statisType"] + '(' + obj["field"] + ') as ct by tr'
        elif name == 'SJSFDTJ_VALUE':
            valueranges = ""
            for item in obj["values"]:
                valueranges += " (" + item["from"] + ", " + item["to"] + "),"
            valueranges = valueranges[:-1]
            spl = '|bucket ' + obj["field"] + ' ranges=(' + valueranges + ') as vs |stats count(' + obj["field"] + ') as ct by vs'
        elif name == 'ZFT_TIME':
            spl = '|bucket timestamp span=' + obj["interval"] + obj["unit"] + ' as ts |stats count(timestamp) as ct by ts'
        elif name == 'ZFT_VALUE':
            spl = '|bucket ' + obj["field"] + ' span=' + obj["interval"] + ' as ts |stats count(' + obj["field"] + ') as ct by ts'
        elif name == 'ZDFLTJ':
            if obj["type"] == 'data':
                spl = '|stats count(' + obj["field"] + ') as count_ by ' + obj["field"] + ' |sort by count_ |limit ' + str(obj["top"])
            elif obj["type"] == 'graph':
                spl = '|bucket timestamp span=' + obj["span"] + ' as ts |stats count(' + obj["field"] + ') as ct by ' + obj["field"] + ', ts'
        elif name == 'ZDSZTJ':
            spl = '|bucket timestamp span=' + obj["span"] + ' as ts |stats ' + obj["statisType"] + '(' + obj["yAxis"] + ') as ct by ' + obj["field"] + ', ts ' + '|join type=inner ' + obj["field"] + ' [[*|stats count(' + obj["field"] + ') as count_ by ' + obj["field"] + ' |sort by count_ |limit 5 ]]'
        elif name == 'LJBFB':
            if obj["reverse"] == 'true':
                spl = '|stats pct_ranks(' + obj["field"] + ', ' + obj["reValue"] + ')'
            else:
                spl = '|stats pct(' + obj["field"] + ', ' + obj["percents"] + ')'
        elif name == 'DJTJ':
            if obj["step"] == 'step1':
                if obj["chartType"] == 'bar' or obj["chartType"] == 'pie':
                    spl = '|stats count(' + obj["step_field"] + ') as count_ by ' + obj["step_field"] + ' |sort by count_'
                else:
                    spl = '|bucket timestamp span=' + str(obj["interval"]) + obj["unit"] + ' as ts |stats count(' + obj["step_field"] + ') as ct by ' + obj["step_field"] + ', ts' + '|join type=inner ' + obj["step_field"] + ' [[*|stats count(' + obj["step_field"] + ') as count_ by ' + obj["step_field"] + ' |sort by count_ |limit ' + str(obj["stat_top"]) + ']]'
            if obj["step"] == 'step2' or obj["step"] == 'step3':
                if obj["chartType"] == 'bar' or obj["chartType"] == 'pie':
                    spl = '|stats count(' + obj["step_field"] + ') as count_ by ' + obj["step_field"] + ' |sort by count_'
                else:
                    if obj["statisType"] == 'count':
                        spl = '|bucket timestamp span=' + str(obj["interval"]) + obj["unit"] + ' as ts |stats ' + obj["statisType"] + '(' + obj["step_field"] + ') as ct by ' + obj["step_field"] + ', ts'
                    else:
                        obj["statisType"] = "dc" if obj["statisType"] == "cardinality" else obj["statisType"]
                        spl = '|bucket timestamp span=' + str(obj["interval"]) + obj["unit"] + ' as ts |stats ' + obj["statisType"] + '(' + obj["step_field"] + ') as ct by ts'
        elif name == 'DLFB':
            spl = '|stats count(' + obj["field"] + ') as count_ by ' + obj["field"] + '|sort by count_ |limit ' + str(obj["top"])

        return spl
    
    # convert base64 string
    # the 2nd char swqp places with the last 7 and 8 chars
    # example a[b]cdefghijklmnopqrs[tu]vwxyz=  -->  a[tu]cdefghijklmnopqrs[b]vwxyz=
    def b64Encrypt(self, input_string):
        if input_string and isinstance(input_string, str) and len(input_string) > 10:
            _char_first_10 = input_string[:10]
            _char_last = input_string[-22:-2]
            _new_string = _char_last + input_string[10:-22] + _char_first_10 + input_string[-2:]
            return _new_string
        else:
            input_string

    # reconvert base64 string
    # the 2nd and 3rd chars swqp places with the last 7 chars
    # example a[tu]cdefghijklmnopqrs[b]vwxyz=  -->  a[b]cdefghijklmnopqrs[tu]vwxyz=
    def b64Decrypt(self, input_string):
        print str(input_string)
        if input_string and isinstance(input_string, str) and len(input_string) > 10:
            _char_first_20 = input_string[:20]
            _char_last = input_string[-12:-2]
            _new_string = _char_last + input_string[20:-12] + _char_first_20 + input_string[-2:]
            return _new_string
        else:
            input_string