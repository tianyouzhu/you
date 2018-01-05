# -*- coding:utf-8 -*-
from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest

__author__ = 'wangqiushi, mayangguang'
err_data = ContributeErrorData()


class UsageResource(Resource):

    class Meta:
        resource_name = 'usage'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search/$" % self._meta.resource_name,
                self.wrap_view('search_usage'), name="api_search_usage"),

        ]

    def search_usage(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        dummy_data = {}
        req_data = request.POST
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            sg_param = {
                'account': es_check['i'],
                'token': es_check['t'],
                'opeator': es_check['u'],
                'from': req_data.get("from", ""),
                'to': req_data.get("to", ""),
                # "source_group": req_data.get("source_group", "all")
            }
            sg_res = BackendRequest.get_search_stats(sg_param)
            if sg_res["result"]:
                dummy_data["status"] = "1"
                a_list = []
                for item in sg_res["tokens"]:
                    item["name"] = item["account_name"]
                    a_list.append(item)
                dummy_data["stats"] = a_list
                dummy_data["total"] = len(sg_res["tokens"])
            else:
                dummy_data = err_data.build_error(sg_res)
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp
