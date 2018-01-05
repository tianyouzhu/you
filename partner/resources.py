# -*- coding: utf-8 -*-
# wangqiushi (wang.qiushi@yottabyte.cn)
# 2014/12/26
# Copyright 2014 Yottabyte
# file description : resources.py
__author__ = 'wangqiushi'
import hashlib
import json
import logging
import base64
import requests

log = logging.getLogger('django.request')


class ThirdPartnerAuth():
    def __init__(self):
        pass

    @staticmethod
    def auth(token):
        if token:
            params = {
                "AccessToken": "",
                "Action": "GetUserInfo",
            }
            SecretKey = "1440510369000162274218"
            private_key = "175c2e3f098ef2b25c04292afc98484908e9230a"
            # private_key = "a6043d20568d1e539f50f1179eb3408e631a33fe"


            decode_token = parseSignedToken(token, private_key)
            if not decode_token:
                return False
            else:
                params["AccessToken"] = decode_token

            try:
                sign = _verify_ac(private_key, params)
                url = "https://api.ucloud.cn/"
                # url = "http://114.119.38.96/api/"
                data = {
                    "AccessToken": params["AccessToken"],
                    "Action": "GetUserInfo",
                    "Signature": sign
                }
                res = requests.get(url, params=data)
                log.info('get_user_info_ucloud: %s', res.url)
            except Exception, e:
                print "auth error:", e
                return False
            result = res.json()
            log.info(result)
            return result.get('DataSet',[{}])[0]
        return False


def _verify_ac(secret_key, params):
    items=params.items()
    # 请求参数串
    items.sort()
    # 将参数串排序
    params_data = ""
    for key, value in items:
        params_data = params_data + str(key) + str(value)
    params_data = params_data + secret_key
    sign = hashlib.sha1()
    sign.update(params_data)
    signature = sign.hexdigest()
    return signature


def parseSignedToken(token, secret):
    encoded_sig, encoded_token = token.split(".")
    sig = base64.b64decode(encoded_sig)
    new_token = base64.b64decode(encoded_token)
    param = new_token+secret
    expected_sig = hashlib.sha1(param).hexdigest()
    # $expected_sig = sha1($token.$client_secret);
    return new_token if sig.lower() == expected_sig.lower() else False
