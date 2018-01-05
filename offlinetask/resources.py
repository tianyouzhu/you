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
__author__ = 'daibin'
err_data = ContributeErrorData()


class OfflinetaskResource(Resource):
    # Just like a Django ``Form`` or ``Model``, we're defining all the
    # fields we're going to handle with the API here.

    class Meta:
        resource_name = 'offlinetask'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/list/$" % self._meta.resource_name,
                self.wrap_view('offlinetask_list'), name="api_offlinetask"),
            url(r"^(?P<resource_name>%s)/del/$" % self._meta.resource_name,
                self.wrap_view('delete_offlinetask'), name="api_offlinetask")
        ]

    def offlinetask_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u'],
                'category': 'search'
            }
            res = BackendRequest.get_job_list(param)
            print res
            try:
                if res["rc"] == 0:
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

    def delete_offlinetask(self, request, **kwargs):
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
