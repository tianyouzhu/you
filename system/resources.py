# wangqiushi (@yottabyte.cn)
# 2014/07/30
# Copyright 2014 Yottabyte
# file description : resources.py.
from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.variable.resources import MyVariable
from binascii import a2b_base64
import logging
import os
import json
import ConfigParser
import fileinput
import re
import subprocess
from shutil import copyfile

__author__ = 'wangqiushi, mayangguang'
err_data = ContributeErrorData()

req_logger = logging.getLogger("django.request")

class SystemResource(Resource):
    class Meta:
        resource_name = 'system'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/custom/$" % self._meta.resource_name,
                self.wrap_view('system_custom'), name="api_system_custom"),
            url(r"^(?P<resource_name>%s)/custom/logo/reset/$" % self._meta.resource_name,
                self.wrap_view('logo_reset'), name="api_logo_reset"),
            url(r"^(?P<resource_name>%s)/custom/applications/$" % (self._meta.resource_name),
                self.wrap_view('applications'), name="api_step"),
            url(r"^(?P<resource_name>%s)/custom/applications/new/$" % (self._meta.resource_name),
                self.wrap_view('applications_new'), name="api_step"),
            url(r"^(?P<resource_name>%s)/custom/applications/(?P<aid>[\w\d]+)/$" % (self._meta.resource_name),
                self.wrap_view('applications_update'), name="api_step"),
            url(r"^(?P<resource_name>%s)/custom/applications/del/(?P<aid>[\w\d]+)/$" % (self._meta.resource_name),
                self.wrap_view('applications_delete'), name="api_step"),
            url(r"^(?P<resource_name>%s)/custom/tables/$" % (self._meta.resource_name),
                self.wrap_view('tables'), name="api_step"),
            url(r"^(?P<resource_name>%s)/custom/tables/new/$" % (self._meta.resource_name),
                self.wrap_view('tables_new'), name="api_step"),
            url(r"^(?P<resource_name>%s)/custom/tables/(?P<aid>[\w\d]+)/$" % (self._meta.resource_name),
                self.wrap_view('tables_update'), name="api_step"),
            url(r"^(?P<resource_name>%s)/custom/tables/del/(?P<aid>[\w\d]+)/$" % (self._meta.resource_name),
                self.wrap_view('tables_delete'), name="api_step"),
            url(r"^(?P<resource_name>%s)/custom/dashboards/$" % (self._meta.resource_name),
                self.wrap_view('dashboards'), name="api_step"),
            url(r"^(?P<resource_name>%s)/custom/dashboards/new/$" % (self._meta.resource_name),
                self.wrap_view('dashboards_new'), name="api_step"),
            url(r"^(?P<resource_name>%s)/custom/dashboards/(?P<did>[\w\d]+)/$" % (self._meta.resource_name),
                self.wrap_view('dashboards_update'), name="api_step"),
            url(r"^(?P<resource_name>%s)/custom/dashboards/del/(?P<did>[\w\d]+)/$" % (self._meta.resource_name),
                self.wrap_view('dashboards_delete'), name="api_step"),
            url(r"^(?P<resource_name>%s)/custom/themes/change/$" % self._meta.resource_name,
                self.wrap_view('themes_change'), name="api_step"),
            url(r"^(?P<resource_name>%s)/custom/themes/color/$" % self._meta.resource_name,
                self.wrap_view('themes_color'), name="api_step"),
            url(r"^(?P<resource_name>%s)/custom/themes/restore/$" % self._meta.resource_name,
                self.wrap_view('themes_restore'), name="api_step"),
            url(r"^application/(?P<resource_name>%s)/(?P<sid>[\w\d]+)/steps/$" % (self._meta.resource_name),
                self.wrap_view('steps'), name="api_step"),

        ]

    def system_custom(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            imgString = request.POST.get('img', '')
            logoType = request.POST.get('type', '')
            data = imgString.split('base64,').pop()
            binary_data = a2b_base64(data)

            try:
                cf = ConfigParser.ConfigParser()
                real_path = os.getcwd() + '/config'
                cf.read(real_path + "/yottaweb.ini")
                navLogoSmallPathName = cf.get('logo', 'nav_logo_path_name')
                navLogoSmallPathNameBk = cf.get('logo', 'nav_logo_path_name_bk')
                navLogoLargePathName = cf.get('logo', 'login_logo_path_name')
                navLogoLargePathNameBk = cf.get('logo', 'login_logo_path_name_bk')

                if logoType == 'small':
                    if not os.path.isfile(navLogoSmallPathNameBk):
                        os.rename(navLogoSmallPathName, navLogoSmallPathNameBk)
                    with open(navLogoSmallPathName, 'wb') as f:
                        f.write(binary_data)
                elif logoType == 'large':
                    if not os.path.isfile(navLogoLargePathNameBk):
                        os.rename(navLogoLargePathName, navLogoLargePathNameBk)
                    with open(navLogoLargePathName, 'wb') as f:
                        f.write(binary_data)

                dummy_data["status"] = "1"
            except Exception, e:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "get error!"
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "get error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def logo_reset(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            logoType = request.POST.get('type', '')

            try:
                cf = ConfigParser.ConfigParser()
                real_path = os.getcwd() + '/config'
                cf.read(real_path + "/yottaweb.ini")
                navLogoSmallPathName = cf.get('logo', 'nav_logo_path_name')
                navLogoSmallPathNameBk = cf.get('logo', 'nav_logo_path_name_bk')
                navLogoLargePathName = cf.get('logo', 'login_logo_path_name')
                navLogoLargePathNameBk = cf.get('logo', 'login_logo_path_name_bk')

                if logoType == 'small':
                    if os.path.isfile(navLogoSmallPathNameBk):
                        os.remove(navLogoSmallPathName)
                        os.rename(navLogoSmallPathNameBk, navLogoSmallPathName)
                elif logoType == 'large':
                    if os.path.isfile(navLogoLargePathNameBk):
                        os.remove(navLogoLargePathName)
                        os.rename(navLogoLargePathNameBk, navLogoLargePathName)

                dummy_data["status"] = "1"
            except Exception, e:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "get error!"
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "get error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def applications(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            try:
                real_path = config_path + '/apps.json'
                with open(real_path, 'r') as f:
                    config = json.load(f)
                apps = config.get("apps", [])

            except Exception, e:
                print e
                apps = []
            dummy_data["status"] = "1"
            dummy_data["apps"] = apps
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "get error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def applications_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            post_data = json.loads(request.POST.get("data"))

            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            real_file = config_path + '/apps.json'
            try:
                if not os.path.exists(config_path):
                    os.makedirs(config_path)

                with open(real_file, 'rw') as f:
                    config = json.load(f)
                f.close()
                apps = config.get("apps", [])

            except Exception, e:
                print e
                apps = []

            apps.append(post_data)

            app_content = {
                "apps": apps
            }
            try:
                with open(real_file, 'w') as f:
                    json.dump(app_content, f)
                f.close()
                dummy_data["status"] = "1"
                dummy_data["url"] = "/system/custom/application/"
            except Exception, e:
                print e
                dummy_data["status"] = "0"
                dummy_data["msg"] = "create custom app error!"
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "create custom app auth error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def applications_update(self, request, **kwargs):
        self.method_check(request, allowed=['post', 'get'])
        dummy_data = {}
        id = kwargs.get("aid", "")
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            real_file = config_path + '/apps.json'

            if request.method == "POST":
                post_data = json.loads(request.POST.get("data"))

                try:
                    with open(real_file, 'r') as f:
                        config = json.load(f)
                    f.close()
                    apps = config.get("apps", [])

                except Exception, e:
                    print e
                    apps = []

                cur_id = -1
                for i in range(len(apps)):
                    if apps[i]["id"] == id:
                        cur_id = i
                if cur_id > -1:
                    apps[cur_id] = post_data

                app_content = {
                    "apps": apps
                }
                try:
                    with open(real_file, 'w') as f:
                        json.dump(app_content, f)
                    f.close()
                    dummy_data["status"] = "1"
                    dummy_data["url"] = "/system/custom/application/"
                except Exception, e:
                    print e
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "update custom app error!"
            else:
                try:
                    with open(real_file, 'r') as f:
                        config = json.load(f)
                    f.close()
                    apps = config.get("apps", [])
                    dummy_data["status"] = "0"
                    for item in apps:
                        if item["id"] == id:
                            dummy_data["status"] = "1"
                            dummy_data["app"] = item
                    if dummy_data["status"] == "0":
                        dummy_data["msg"] = "update custom app error!"
                except Exception, e:
                    print e
                    apps = []
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "update custom app error!"
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "update custom app auth error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def applications_delete(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        id = kwargs.get("aid", "")
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            real_file = config_path + '/apps.json'

            try:
                with open(real_file, 'r') as f:
                    config = json.load(f)
                f.close()
                apps = config.get("apps", [])

            except Exception, e:
                print e
                apps = []

            cur_id = -1
            for i in range(len(apps)):
                if apps[i]["id"] == id:
                    cur_id = i
            try:
                if cur_id > -1:
                    del(apps[cur_id])
            except Exception, e:
                print e

            app_content = {
                "apps": apps
            }
            try:
                with open(real_file, 'w') as f:
                    json.dump(app_content, f)
                f.close()
                dummy_data["status"] = "1"
                dummy_data["apps"] = apps
            except Exception, e:
                print e
                dummy_data["status"] = "0"
                dummy_data["msg"] = "delete custom app error!"
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "delete custom app auth error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def tables(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            try:
                real_path = config_path + '/tables.json'
                with open(real_path, 'r') as f:
                    config = json.load(f)
                tables = config.get("tables", [])

            except Exception, e:
                print e
                tables = []
            dummy_data["status"] = "1"
            dummy_data["tables"] = tables
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "get error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def tables_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            post_data = json.loads(request.POST.get("data"))

            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            real_file = config_path + '/tables.json'
            try:
                if not os.path.exists(config_path):
                    os.makedirs(config_path)

                with open(real_file, 'rw') as f:
                    config = json.load(f)
                f.close()
                tables = config.get("tables", [])

            except Exception, e:
                print e
                tables = []

            tables.append(post_data)

            app_content = {
                "tables": tables
            }
            try:
                with open(real_file, 'w') as f:
                    json.dump(app_content, f)
                f.close()
                dummy_data["status"] = "1"
                dummy_data["url"] = "/system/custom/table/"
            except Exception, e:
                print e
                dummy_data["status"] = "0"
                dummy_data["msg"] = "create custom table error!"
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "create custom table auth error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def tables_update(self, request, **kwargs):
        self.method_check(request, allowed=['post', 'get'])
        dummy_data = {}
        id = kwargs.get("aid", "")
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            real_file = config_path + '/tables.json'

            if request.method == "POST":
                post_data = json.loads(request.POST.get("data"))

                try:
                    with open(real_file, 'r') as f:
                        config = json.load(f)
                    f.close()
                    tables = config.get("tables", [])

                except Exception, e:
                    print e
                    tables = []

                cur_id = -1
                for i in range(len(tables)):
                    if tables[i]["id"] == id:
                        cur_id = i
                if cur_id > -1:
                    tables[cur_id] = post_data

                app_content = {
                    "tables": tables
                }
                try:
                    with open(real_file, 'w') as f:
                        json.dump(app_content, f)
                    f.close()
                    dummy_data["status"] = "1"
                    dummy_data["url"] = "/system/custom/table/"
                except Exception, e:
                    print e
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "update custom app error!"
            else:
                try:
                    with open(real_file, 'r') as f:
                        config = json.load(f)
                    f.close()
                    apps = config.get("tables", [])
                    dummy_data["status"] = "0"
                    for item in apps:
                        if item["id"] == id:
                            dummy_data["status"] = "1"
                            dummy_data["table"] = item
                    if dummy_data["status"] == "0":
                        dummy_data["msg"] = "update custom app error!"
                except Exception, e:
                    print e
                    apps = []
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "update custom app error!"
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "update custom app auth error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def tables_delete(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        id = kwargs.get("aid", "")
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            real_file = config_path + '/tables.json'

            try:
                with open(real_file, 'r') as f:
                    config = json.load(f)
                f.close()
                tables = config.get("tables", [])

            except Exception, e:
                print e
                tables = []

            cur_id = -1
            for i in range(len(tables)):
                if tables[i]["id"] == id:
                    cur_id = i
            try:
                if cur_id > -1:
                    del(tables[cur_id])
            except Exception, e:
                print e

            app_content = {
                "tables": tables
            }
            try:
                with open(real_file, 'w') as f:
                    json.dump(app_content, f)
                f.close()
                dummy_data["status"] = "1"
                dummy_data["tables"] = tables
            except Exception, e:
                print e
                dummy_data["status"] = "0"
                dummy_data["msg"] = "delete custom app error!"
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "delete custom app auth error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def dashboards(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            real_file = config_path + '/dashboard.json'
            try:
                with open(real_file, 'r') as f:
                    config = json.load(f)
                f.close()
            except Exception, e:
                print e
                config = []
            dummy_data["status"] = "1"
            dummy_data["dashboards"] = config
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "get error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def dashboards_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            post_data = json.loads(request.POST.get("data"))
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            real_file = config_path + '/dashboard.json'
            try:
                if not os.path.exists(config_path):
                    os.makedirs(config_path)
                with open(real_file, 'r') as f:
                    config = json.load(f)
                f.close()
                if not config:
                    config = []

            except Exception, e:
                print e
                config = []

            config.append(post_data)

            try:
                with open(real_file, 'w') as f:
                    json.dump(config, f)
                f.close()
                dummy_data["status"] = "1"
                dummy_data["url"] = "/system/custom/dashboard/"
            except Exception, e:
                print e
                dummy_data["status"] = "0"
                dummy_data["msg"] = "create custom dashboard error!"
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "create custom dashboard auth error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def dashboards_update(self, request, **kwargs):
        self.method_check(request, allowed=['post', 'get'])
        dummy_data = {}
        id = kwargs.get("did", "")
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            real_file = config_path + '/dashboard.json'
            if request.method == "POST":
                post_data = json.loads(request.POST.get("data"))

                try:
                    with open(real_file, 'r') as f:
                        config = json.load(f)
                    f.close()
                    if not config:
                        config = []

                except Exception, e:
                    print e
                    config = []

                cur_id = -1
                for i in range(len(config)):
                    if config[i]["custom_config_id"] == id:
                        cur_id = i
                if cur_id > -1:
                    config[cur_id] = post_data

                    try:
                        with open(real_file, 'w') as f:
                            json.dump(config, f)
                        f.close()
                        dummy_data["status"] = "1"
                        dummy_data["url"] = "/system/custom/dashboard/"
                    except Exception, e:
                        print e
                        dummy_data["status"] = "0"
                        dummy_data["msg"] = "update custom dashboard error!"
                else:
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "Can't find dashboard by id"+id+" !"
            else:
                try:
                    with open(real_file, 'r') as f:
                        config = json.load(f)
                    f.close()
                    if not config:
                        config = []
                    dummy_data["status"] = "0"
                    for item in config:
                        if item["custom_config_id"] == id:
                            dummy_data["status"] = "1"
                            dummy_data["dashboard"] = item
                    if dummy_data["status"] == "0":
                        dummy_data["msg"] = "Can't find dashboard by id"+id+" !"
                except Exception, e:
                    print e
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "get custom dashboard error!"
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "get custom dashboard auth error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def dashboards_delete(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        id = kwargs.get("did", "")
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            config_path = data_path + "custom"
            real_file = config_path + '/dashboard.json'
            try:
                with open(real_file, 'r') as f:
                    config = json.load(f)
                f.close()
                if not config:
                    config = []

            except Exception, e:
                print e
                config = []

            cur_id = -1
            for i in range(len(config)):
                if config[i]["custom_config_id"] == id:
                    cur_id = i
            if cur_id > -1:
                del(config[cur_id])
                try:
                    with open(real_file, 'w') as f:
                        json.dump(config, f)
                    f.close()
                    dummy_data["status"] = "1"
                    dummy_data["dashboards"] = config
                except Exception, e:
                    print e
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "delete custom dashboard error!"
            else:
                dummy_data["status"] = "0"
                dummy_data["msg"] = "Can't find dashboard by id"+id+" !"
        else:
            dummy_data["status"] = "0"
            dummy_data["msg"] = "delete custom app auth error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp
    
    def themes_change(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        path = os.path.dirname(os.path.realpath(__file__))
        if es_check:
            dummy_data["status"] = "1"
            dist_path = json.loads(request.POST.get('DISTPATH'))
            main_color = request.POST.get('mainColor')
            main_color_hover = request.POST.get('mainColorHover')
            left_nav = request.POST.get('leftNav')
            dashboard_color = request.POST.get('dashboard')
            icon_color = request.POST.get('icon')
            
            scssfile_check = os.path.isfile(path + '/../../static/scss/var.scss')
            backfile_check = os.path.isfile(path + '/../../static/scss/var.scss.back')
            if scssfile_check is False:
                if backfile_check is False:
                    req_logger.error("no scss file and backup file")
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "no scss file and backup file"
                else:
                    copyfile(path + '/../../static/scss/var.scss.back', path + '/../../static/scss/var.scss.prev')
                    copyfile(path + '/../../static/scss/var.scss.back', path + '/../../static/scss/var.scss')
            else:
                copyfile(path + '/../../static/scss/var.scss', path + '/../../static/scss/var.scss.prev')
            if scssfile_check is True or backfile_check is True:
                for line in fileinput.input(path + '/../../static/scss/var.scss', inplace=True):
                    # main_color
                    line = re.sub(r'\$yw-bg-btn-blue: #?[a-zA-Z0-9]+;', '$yw-bg-btn-blue: #' + main_color + ';', line.rstrip())
                    line = re.sub(r'\$yw-border-btn-blue: #?[a-zA-Z0-9]+;', '$yw-border-btn-blue: #' + main_color + ';', line.rstrip())
                    line = re.sub(r'\$yw-bg-topnav-blue: #?[a-zA-Z0-9]+;', '$yw-bg-topnav-blue: #' + main_color + ';', line.rstrip())
                    line = re.sub(r'\$yw-font-blue: #?[a-zA-Z0-9]+;', '$yw-font-blue: #' + main_color + ';', line.rstrip())
                    line = re.sub(r'\$yw-border-blue: #?[a-zA-Z0-9]+;', '$yw-border-blue: #' + main_color + ';', line.rstrip())
                    # main_color_hover
                    line = re.sub(r'\$yw-bg-btn-blue-hover: #?[a-zA-Z0-9]+;', '$yw-bg-btn-blue-hover: #' + main_color_hover + ';', line.rstrip())
                    line = re.sub(r'\$yw-border-btn-blue-hover: #?[a-zA-Z0-9]+;', '$yw-border-btn-blue-hover: #' + main_color_hover + ';', line.rstrip())
                    # left_nav
                    line = re.sub(r'\$yw-bg-leftnav-blue: #?[a-zA-Z0-9]+;', '$yw-bg-leftnav-blue: #' + left_nav + ';', line.rstrip())
                    # dashboard_color
                    line = re.sub(r'\$yw-bg-dashboard-night: #?[a-zA-Z0-9]+;', '$yw-bg-dashboard-night: #' + dashboard_color + ';', line.rstrip())
                    # icon_color
                    line = re.sub(r'\$yw-icon-info: #?[a-zA-Z0-9]+;', '$yw-icon-info: #' + icon_color + ';', line.rstrip())
                    print line
                fileinput.close()

                sass_path = path + "/../../../services/node-sass/bin/"
                node_path = path + "/../../../services/node/bin/"
                for filename in dist_path:
                    cmd = node_path + 'node ' + sass_path + 'node-sass ' + path + dist_path[filename][0] + ' ' + path + dist_path[filename][1]
                    try:
                        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        p.wait()
                        output = p.communicate()[0]
                        if p.returncode != 0:
                            req_logger.error("subprocess error: %d %s" % (p.returncode, output))
                            dummy_data["status"] = "0"
                            dummy_data["msg"] = "subprocess error: %d %s" % (p.returncode, output)
                            break
                    except Exception, e:
                        req_logger.error("subprocess error: %s", e)
                        dummy_data["status"] = "0"
                        dummy_data["msg"] = "subprocess error: " + e
        else:
            req_logger.error("auth error")
            dummy_data["status"] = "0"
            dummy_data["msg"] = "get error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def themes_color(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        path = os.path.dirname(os.path.realpath(__file__))
        if es_check:
            dummy_data["status"] = "1"
            dummy_data["color"] = {
                "mainColor": "329BE6",
                "mainColorHover": "3282F5",
                "leftNav": "1C2237",
                "dashboard": "16191C",
                "icon": "9BB4C8"
            }

            scssfile_check = os.path.isfile(path + '/../../static/scss/var.scss')
            backfile_check = os.path.isfile(path + '/../../static/scss/var.scss.back')
            prevfile_check = os.path.isfile(path + '/../../static/scss/var.scss.prev')
            if scssfile_check is False:
                if prevfile_check is False:
                    if backfile_check is False:
                        req_logger.error("no any scss files")
                        dummy_data["status"] = "0"
                        dummy_data["msg"] = "no any scss files, please contact the service provider"
                    else:
                        copyfile(path + '/../../static/scss/var.scss.back', path + '/../../static/scss/var.scss')
                else:
                    copyfile(path + '/../../static/scss/var.scss.prev', path + '/../../static/scss/var.scss')
            if scssfile_check is True or backfile_check is True or prevfile_check is True:
                for line in fileinput.input(path + '/../../static/scss/var.scss'):
                    match_main = re.search(r'\$yw-bg-btn-blue: #?(?P<hex>[a-zA-Z0-9]+);', line.rstrip())
                    if match_main is not None:
                        dummy_data["color"]["mainColor"] = match_main.group('hex')

                    match_main_hover = re.search(r'\$yw-bg-btn-blue-hover: #?(?P<hex>[a-zA-Z0-9]+);', line.rstrip())
                    if match_main_hover is not None:
                        dummy_data["color"]["mainColorHover"] = match_main_hover.group('hex')
                    
                    match_nav = re.search(r'\$yw-bg-leftnav-blue: #?(?P<hex>[a-zA-Z0-9]+);', line.rstrip())
                    if match_nav is not None:
                        dummy_data["color"]["leftNav"] = match_nav.group('hex')
                    
                    match_dashboard = re.search(r'\$yw-bg-dashboard-night: #?(?P<hex>[a-zA-Z0-9]+);', line.rstrip())
                    if match_dashboard is not None:
                        dummy_data["color"]["dashboard"] = match_dashboard.group('hex')
                    
                    match_icon = re.search(r'\$yw-icon-info: #?(?P<hex>[a-zA-Z0-9]+);', line.rstrip())
                    if match_icon is not None:
                        dummy_data["color"]["icon"] = match_icon.group('hex')
                    
                fileinput.close()
        else:
            req_logger.error("auth error")
            dummy_data["status"] = "0"
            dummy_data["msg"] = "get error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def themes_restore(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        path = os.path.dirname(os.path.realpath(__file__))
        if es_check:
            restore_type = request.POST.get('type')
            dist_path = json.loads(request.POST.get('DISTPATH'))
            backfile = 'var.scss.prev' if restore_type == 'rollback' else 'var.scss.back'
            backfile_check = os.path.isfile(path + '/../../static/scss/' + backfile)
            scssfile_check = os.path.isfile(path + '/../../static/scss/var.scss')
            if backfile_check:
                dummy_data["status"] = "1"
                if scssfile_check:
                    os.rename(path + '/../../static/scss/var.scss', path + '/../../static/scss/var.scss.del')
                try:
                    copyfile(path + '/../../static/scss/' + backfile, path + '/../../static/scss/var.scss')
                    if scssfile_check:
                        os.remove(path + '/../../static/scss/var.scss.del')

                    sass_path = path + "/../../../services/node-sass/bin/"
                    node_path = path + "/../../../services/node/bin/"
                    for filename in dist_path:
                        cmd = node_path + 'node ' +sass_path + 'node-sass ' + path + dist_path[filename][0] + ' ' + path + dist_path[filename][1]
                        try:
                            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                            p.wait()
                            output = p.communicate()[0]
                            if p.returncode != 0:
                                req_logger.error("subprocess error: %d %s" % (p.returncode, output))
                                dummy_data["status"] = "0"
                                dummy_data["msg"] = "subprocess error: %d %s" % (p.returncode, output)
                                break
                        except Exception, e:
                            req_logger.error("subprocess error: %s", e)
                            dummy_data["status"] = "0"
                            dummy_data["msg"] = "subprocess error: " + e
                except Exception, e:
                    req_logger.error("backup file copy error")
                    dummy_data["status"] = "0"
                    dummy_data["msg"] = "backup file copy error"   
            else:
                req_logger.error("backup file does not exist")
                dummy_data["status"] = "0"
                dummy_data["msg"] = "backup file does not exist"
        else:
            req_logger.error("auth error")
            dummy_data["status"] = "0"
            dummy_data["msg"] = "get error!"
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp
