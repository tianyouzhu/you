from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest

__author__ = 'wangqiushi, mayangguang'
err_data = ContributeErrorData()


class TokenResource(Resource):
    # Just like a Django ``Form`` or ``Model``, we're defining all the
    # fields we're going to handle with the API here.

    class Meta:
        resource_name = 'tokens'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/lists/$" % self._meta.resource_name,
                self.wrap_view('token_list'), name="api_token_list"),
            url(r"^(?P<resource_name>%s)/retired/$" % self._meta.resource_name,
                self.wrap_view('token_retired_list'), name="api_token_list"),
            url(r"^(?P<resource_name>%s)/new/" % self._meta.resource_name,
                self.wrap_view('token_new'), name="api_token_list"),
            url(r"^(?P<resource_name>%s)/(?P<tid>[\w\d_.-]+)/" % self._meta.resource_name,
                self.wrap_view('token_update'), name="api_token_update"),
        ]

    def token_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        data = []
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_domain(param)
            if res['result']:
                for t in res['domain']['token']:
                    data.append({
                        'token': t,
                        "description": "",
                        "created": res['domain']['create_time'] * 1000,
                        "edit": "false"
                    })
                dummy_data["status"] = "1"
                dummy_data["totle"] = len(data)
                dummy_data["list"] = data
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

    def token_retired_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        data = [
            {"token": "01234kjhasak12j3l4lh3jh41lkh322j315kph12vasd", "description": "ddd",
             "created": "20140706", "edit": "false"},
            {"token": "31aaagghk12j3l4lh12k3jh41lkh322j315kph12vasd", "description": "ssssss",
             "created": "20140706", "edit": "false"},
            {"token": "aasdkvocinwj3l4lh12k3jh41lkh322j315kph12vasd", "description": "afffdsfadds",
             "created": "20140706", "edit": "false"}
        ]
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)

        if es_check:
            param = {
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_domain(param)
            if res['result']:
                list = []
                for a_domain in res['domain']:
                    list.append({
                        'token': a_domain['token'],
                        'created': a_domain['create_time'] * 1000
                    })
                data = res['domain']['token']
                dummy_data["status"] = "1"
                dummy_data["totle"] = len(data)
                dummy_data["list"] = list
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

    def token_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        req_data = request.POST
        description = req_data.get('description', ''),
        data = [
            {"token": "31234kjhk12j3l4lh12k3jh41lkh322j315kph12vasd", "description": "asdfasdfadsfa",
             "created": "20140706", "edit": "false"}
        ]
        data[0]['description'] = description

        dummy_data = {}
        es_check = True
        if es_check:
            dummy_data["status"] = "1"
            dummy_data["totle"] = "1"
            dummy_data["list"] = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def token_update(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        tokenId = kwargs['tid']
        req_data = request.POST
        description = req_data.get('description', ''),
        data = [
            {"token": "31234kjhk12j3l4lh12k3jh41lkh322j315kph12vasd", "description": "asdfasdfadsfa",
             "created": "20140706", "edit": "false"}
        ]
        if data[0]['token'] == tokenId:
            data[0]['description'] = description[0]

        dummy_data = {}
        es_check = True
        if es_check:
            dummy_data["status"] = "1"
            dummy_data["totle"] = "1"
            dummy_data["list"] = data
        else:
            data = err_data.build_error({}, "auth error!")
            data["location"] = "/auth/login/"
            dummy_data = data
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp
