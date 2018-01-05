#  -*- coding: utf-8 -*-
from tastypie.resources import Resource
from django.conf.urls import url
from django.core.servers.basehttp import FileWrapper
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.variable.resources import MyVariable
import os
from django.http import HttpResponse
import mimetypes
from django.http import StreamingHttpResponse
from django.http import Http404
from django.utils.http import urlquote
import logging
import time
import json
__author__ = 'wangqiushi'
err_data = ContributeErrorData()

audit_logger = logging.getLogger('yottaweb.audit')

class DownloadsResource(Resource):
    # Just like a Django ``Form`` or ``Model``, we're defining all the
    # fields we're going to handle with the API here.

    class Meta:
        resource_name = 'downloads'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/list/$" % self._meta.resource_name,
                self.wrap_view('download_list'), name="api_download"),
            url(r"^(?P<resource_name>%s)/logs_download/(?P<fid>[\u4e00-\u9fa5\w\d_\.\-\\\/]+)/$" % self._meta.resource_name,
                self.wrap_view('logs_download'), name="api_download"),
            url(r"^(?P<resource_name>%s)/del/$" % self._meta.resource_name,
                self.wrap_view('delete_download'), name="api_download"),
            url(r"^(?P<resource_name>%s)/(?P<fid>[\w\d_.\-@]+)/$" % self._meta.resource_name,
                self.wrap_view('csv_download'), name="api_download"),
        ]

    def csv_download(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        data = []
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            file_name = kwargs['fid']
            root_path = os.getcwd()
            my_var = MyVariable()
            data_path = my_var.get_var('path', 'data_path')
            tmp_path = data_path + "yottaweb_tmp/" + es_check["d"] + "/" + es_check["u"] + "/"
            filename = tmp_path + file_name
            wrapper = FileWrapper(file(filename))
            resp = HttpResponse(wrapper, content_type='text/plain')

            # resp = self.create_response(request, wrapper)
            resp['Content-Length'] = os.path.getsize(filename)
            resp['Content-Encoding'] = 'utf-8'
            resp['Content-Disposition'] = 'attachment;filename=%s' % file_name
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            response_data = bundle
            resp = self.create_response(request, response_data)
        return resp

    def logs_download(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        data = []
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            domain = es_check['d']
            user_id = es_check['i']
            file_name = kwargs['fid']
            base_file_name = os.path.basename(file_name)
            to_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "action": "download",
                "module": "download",
                "user_name": es_check["u"],
                "user_id": es_check["i"],
                "domain": es_check["d"],
                "target": base_file_name,
                "result": "success"
            }
            pathArr = file_name.split('/')
            if domain == pathArr[-3] and user_id == int(pathArr[-2]):
                file_name = '/' + file_name
                chunk_size = 8192
                resp = StreamingHttpResponse(FileWrapper(open(file_name, 'rb'), chunk_size), content_type=mimetypes.guess_type(file_name)[0])
                resp['Content-Length'] = os.path.getsize(file_name)
                resp['Content-Encoding'] = 'utf-8'
                ua = request.META.get('HTTP_USER_AGENT', '')
                if ua and self.detectIE(ua):
                    resp['Content-Disposition'] = "attachment; filename=" + urlquote(base_file_name)
                else:
                    resp['Content-Disposition'] = "attachment; filename={0}".format(base_file_name.encode('utf8'))
                audit_logger.info(json.dumps(to_log))
            else:
                to_log["result"] = "error"
                to_log["msg"] = "domain or user_id does not match"
                audit_logger.info(json.dumps(to_log))
                raise Http404
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
            response_data = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
            resp = self.create_response(request, response_data)
        return resp

    def delete_download(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        post_data = request.POST
        file_name = post_data.get("file_name", "")
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        dummy_data = {}
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'file_name': file_name
            }
            res = BackendRequest.delete_download(param)
            if res['result']:
                dummy_data["status"] = "1"
            else:
                dummy_data = err_data.build_error(res)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def download_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'category': 'download'
            }
            res = BackendRequest.get_job_list(param)
            print res
            try:
                if res["rc"] == 0:
                    print res
                    if res["jobs"]:
                        dummy_data["status"] = "1"
                        dummy_data["list"] = res["jobs"]
                else:
                    dummy_data = err_data.build_error_new(error_code=res.get("rc", "1"), msg=res.get("error", ""), origin="spl")
            except Exception, e:
                dummy_data = err_data.build_error_new(res.get("rc", "1"))
        else:
            data = err_data.build_error_new(error_code="2", param={"location": "/auth/login/"})
            dummy_data = data
        response_data = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        return self.create_response(request, response_data)

    def detectIE(self, ua):
        # IE 10 or older
        msie = ua.find('MSIE ')
        if msie > 0:
            return True
        # IE 11
        trident = ua.find('Trident/')
        if trident > 0:
            return True
        # Edge (IE 12+)
        edge = ua.find('Edge/')
        if edge > 0:
            return True

        return False
