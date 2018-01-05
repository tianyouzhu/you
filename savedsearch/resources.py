# wangqiushi (wang.qiushi@yottabyte.cn)
# 2014/07/22
# Copyright 2014 Yottabyte
# file description : resources.py
from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
import time
import urllib
__author__ = 'wangqiushi'
err_data = ContributeErrorData()


class SavedSearchResource(Resource):
    # Just like a Django ``Form`` or ``Model``, we're defining all the
    # fields we're going to handle with the API here.

    class Meta:
        resource_name = 'savedsearches'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/$" % self._meta.resource_name,
                self.wrap_view('saved_list'), name="api_saved_list"),
            # url(r"^(?P<resource_name>%s)/retired/$" % self._meta.resource_name,
            #     self.wrap_view('_retired_list'), name="api_token_list"),
            url(r"^(?P<resource_name>%s)/detail/(?P<ssid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('saved_detail'), name="api_saved_detail"),
            url(r"^(?P<resource_name>%s)/new/" % self._meta.resource_name,
                self.wrap_view('saved_new'), name="api_saved_new"),
            url(r"^(?P<resource_name>%s)/(?P<ssid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('saved_update'), name="api_saved_update"),
            url(r"^(?P<resource_name>%s)/fav/(?P<ssid>[\w\d_.-]+)/(?P<fav>[\w]{1})/$" % self._meta.resource_name,
                self.wrap_view('saved_update_fav'), name="api_saved_delete"),
            url(r"^(?P<resource_name>%s)/del/(?P<ssid>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('saved_delete'), name="api_saved_delete"),
            url(r"^(?P<resource_name>%s)/resourcegroup/filter/$" % self._meta.resource_name,
                self.wrap_view('saved_rg_filter'), name="api_saved_rg_filter"),
            url(r"^(?P<resource_name>%s)/resourcegroup/ungrouped/$" % self._meta.resource_name,
                self.wrap_view('saved_rg_ungrouped'), name="api_saved_rg_filter"),
            url(r"^(?P<resource_name>%s)/resourcegroup/list/assigned/(?P<rid>[\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('saved_rg_assigned'), name="api_saved_rg_assigned"),
            url(r"^(?P<resource_name>%s)/resourcegroup/list/(?P<action>[\w_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('saved_rg_action'), name="api_saved_rg_action"),
        ]

    def saved_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            res = BackendRequest.get_all_saved_search({
                "token": es_check["t"],
                'operator': es_check['u']
            })
            saved_searches = []
            permits = []
            if res['result']:
                for i in res['items']:
                    anonymous = i.get('anonymous', False)
                    if anonymous:
                        continue
                    saved_searches.append({
                        'savedsearch_id': i['id'].encode('utf-8'),
                        'savedsearch_name': i['name'].encode('utf-8'),
                        "related_alert_num": i.get('alert_count', 0),
                        'query': i['query'].encode('utf-8'),
                        "sourcegroup": i['source_groups'].encode('utf-8'),
                        "owner": i.get('owner_name', "").encode('utf-8'),
                        "rg_ids": i.get("resource_group_ids", []),
                        "timerange": i.get('time_range', "").encode('utf-8'),
                        "filters": i.get('filters', "").encode('utf-8') if i.get('filters', "") else "",
                        "fav": 'yes' if i.get('like', True) else 'no'
                    })
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "SavedSearch",
                        "action": "Update"
                    })
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "SavedSearch",
                        "action": "Delete"
                    })
                permits.append({
                    "target": "SavedSearch",
                    "action": "Create"
                })
                permits.append({
                    "target": "DerelictResource",
                    "action": "Possess"
                })

                dummy_data["status"] = "1"
                dummy_data["totle"] = len(saved_searches)
                dummy_data["list"] = sorted(saved_searches, key=lambda x: x['fav'], reverse=True)
                param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_param = {
                    'permits': permits
                }
                permit_res = BackendRequest.batch_permit_can(param, permit_param)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
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


    def saved_detail(self, request, **kwargs):
        """ Get detailed data of a single saved search identified by its id """
        self.method_check(request, allowed=['get'])
        savedsearch_id = kwargs['ssid']
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                "token": es_check["t"],
                "operator": es_check["u"],
                "id": savedsearch_id
            }
            res = BackendRequest.get_saved_search(param)
            if res["result"]:
                dummy_data["status"] = "1"
                i = res["item"]
                dummy_data["savedsearch"] = {
                    'savedsearch_id': i['id'].encode('utf-8'),
                    'savedsearch_name': i['name'].encode('utf-8'),
                    "related_alert_num": i.get('alert_count', 0),
                    'query': i['query'].encode('utf-8'),
                    "sourcegroup": i['source_groups'].encode('utf-8'),
                    "owner": i.get('owner_name', "").encode('utf-8'),
                    "timerange": i.get('time_range', "").encode('utf-8'),
                    "filters": i.get('filters', "").encode('utf-8') if i.get('filters', "") else "",
                    "fav": 'yes' if i.get('like', True) else 'no',
                    "anonymous": i.get('anonymous', False)
                }
            else:
                if res["error_code"] == 60:
                    dummy_data = {
                        "status": "0",
                        "error_code": "60"
                    }
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


    def saved_new(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        req_data = request.POST
        query = req_data.get('query', '')
        timerange = req_data.get('time_range', '')
        sg = req_data.get('sourcegroup', 'all')
        sourcegroup = req_data.get('sourcegroupCn', '') if not sg == 'all' else 'all'
        filters = req_data.get('filters', '')
        name = req_data.get('name', '').encode('utf-8')
        confirm = req_data.get('confirm', 'false')
        ids = req_data.get('resource_group_ids')
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            res = BackendRequest.create_saved_search({
                "token": es_check["t"],
                "owner_name": es_check["u"],
                "operator": es_check['u'],
                "name": name,
                "query": query,
                "time_range": timerange,
                "source_groups": sourcegroup,
                "confirm": confirm,
                "filters": filters,
                'resource_group_ids': ids
            })
            if res["result"]:
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

    def saved_update_fav(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        savedsearch_id = kwargs['ssid']
        fav = 'yes' if kwargs['fav'] == '1' else 'no'
        post_data = request.POST
        print request
        rg_ids = post_data.get("rg_ids", "")
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            res = BackendRequest.update_saved_search({
                "token": es_check["t"],
                'operator': es_check['u'],
                "id": savedsearch_id,
                'resource_group_ids': rg_ids,
                "like": fav
            })
            if res["result"]:
                res_list = BackendRequest.get_all_saved_search({
                    "token": es_check["t"],
                    'operator': es_check['u']
                })
                saved_searches = []
                if res_list['result']:
                    for i in res_list['items']:
                        anonymous = i.get('anonymous', False)
                        if anonymous:
                            continue
                        saved_searches.append({
                            'savedsearch_id': i['id'].encode('utf-8'),
                            'savedsearch_name': i['name'].encode('utf-8'),
                            "related_alert_num": i.get('alert_count', 0),
                            'query': i['query'].encode('utf-8'),
                            "sourcegroup": i['source_groups'].encode('utf-8'),
                            "owner": i.get('owner_name', "").encode('utf-8'),
                            "timerange": i.get('time_range', "").encode('utf-8'),
                            "filters": i.get('filters', "").encode('utf-8'),
                            "fav": 'yes' if i.get('like', True) else 'no'
                        })
                dummy_data["status"] = "1"
                dummy_data["fav"] = fav
                dummy_data["list"] = saved_searches
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

    def saved_update(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        req_data = request.POST
        query = req_data.get('query', '')
        timerange = req_data.get('time_range', '')
        sg = req_data.get('sourcegroup', '')
        sourcegroup = req_data.get('sourcegroupCn', '') if not sg == 'all' else 'all'
        filters = req_data.get('filters', '')
        name = req_data.get('name', '')
        savedsearch_id = kwargs['ssid']
        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            res = BackendRequest.update_saved_search({
                "token": es_check["t"],
                "operator": es_check["u"],
                "id": savedsearch_id,
                "name": name,
                "query": query,
                "time_range": timerange,
                "source_groups": sourcegroup,
                "filters": filters
            })
            if res["result"]:
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

    def saved_delete(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        savedsearch_id = kwargs['ssid']

        dummy_data = {}
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            res = BackendRequest.delete_saved_search({
                "token": es_check["t"],
                "operator": es_check["u"],
                "id": savedsearch_id
            })
            if res["result"]:
                time.sleep(0.2)
                res_list = BackendRequest.get_all_saved_search({
                    "token": es_check["t"],
                    'operator': es_check['u']
                })
                saved_searches = []
                if res_list['result']:
                    for i in res_list['items']:
                        ana = i.get("anonymous", False)
                        if ana:
                            continue
                        saved_searches.append({
                            'savedsearch_id': i['id'].encode('utf-8'),
                            'savedsearch_name': i['name'].encode('utf-8'),
                            "related_alert_num": i.get('alert_count', 0),
                            'query': i['query'].encode('utf-8'),
                            "sourcegroup": i['source_groups'].encode('utf-8'),
                            "owner": i.get('owner_name', "").encode('utf-8'),
                            "timerange": i.get('time_range', "").encode('utf-8'),
                            "filters": i.get('filters', "").encode('utf-8'),
                            "fav": 'yes' if i.get('like', True) else 'no'
                        })
                dummy_data["status"] = "1"
                dummy_data["totle"] = len(saved_searches)
                dummy_data["list"] = saved_searches
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

    def saved_rg_filter(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        req_data = request.POST
        ids = req_data.get('ids', '')
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'ids': ids,
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.get_batch_saved_search(param)
            saved_searches = []
            permits = []
            if res['result']:
                for i in res['saved_searchs']:
                    anonymous = i.get('anonymous', False)
                    if anonymous:
                        continue
                    saved_searches.append({
                        'savedsearch_id': i['id'].encode('utf-8'),
                        'savedsearch_name': i['name'].encode('utf-8'),
                        "related_alert_num": i.get('alert_count', 0),
                        'query': i['query'].encode('utf-8'),
                        "sourcegroup": i['source_groups'].encode('utf-8'),
                        "owner": i.get('owner_name', "").encode('utf-8'),
                        "timerange": i.get('time_range', "").encode('utf-8'),
                        "filters": i.get('filters', "").encode('utf-8') if i.get('filters', "") else "",
                        "fav": 'yes' if i.get('like', True) else 'no'
                    })
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "SavedSearch",
                        "action": "Update"
                    })
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "SavedSearch",
                        "action": "Delete"
                    })
                permits.append({
                    "target": "SavedSearch",
                    "action": "Create"
                })
                permits.append({
                    "target": "DerelictResource",
                    "action": "Possess"
                })

                dummy_data["status"] = "1"
                dummy_data["total"] = len(saved_searches)
                dummy_data["list"] = sorted(saved_searches, key=lambda x: x['fav'], reverse=True)
                param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_param = {
                    'permits': permits
                }
                permit_res = BackendRequest.batch_permit_can(param, permit_param)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
            else:
                dummy_data["status"] = 0
                dummy_data["msg"] = res.get('error', 'get saved search filter error!')
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def saved_rg_action(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {}
            if kwargs['action'].lower() == "read":
                param['action'] = "Read"
                param['category'] = "SavedSearch"
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = "ResourceGroup"
            elif kwargs['action'].lower() == "assign":
                param['action'] = "Assign"
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = "SavedSearch"

            res = BackendRequest.permit_list_resource_group(param)
            if res['result']:
                data = self.rebuild_resource_group_list(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["rg_list"] = data
            else:
                dummy_data["status"] = 0
                dummy_data["msg"] = res.get('error', 'get saved rg action error!')
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def saved_rg_assigned(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        rid = kwargs['rid']
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'resource_id': rid,
                'category': "SavedSearch",
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.list_assigned_resource_group(param)
            if res['result']:
                data = self.rebuild_assigned_resource_group_list(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["rg_list"] = data
            else:
                dummy_data["status"] = 0
                dummy_data["msg"] = res.get('error', 'get saved rg assigned error!')
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    def saved_rg_ungrouped(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'category': 'SavedSearch',
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.list_derelict_resource_ids(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["ids"] = res['resource_ids']
            else:
                dummy_data["status"] = 0
                dummy_data["msg"] = res.get('error', 'get dashboards ungrouped rg error!')
        else:
            dummy_data["status"] = "0"

        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        response_data = bundle
        resp = self.create_response(request, response_data)
        return resp

    @staticmethod
    def rebuild_resource_group_list(data):
        res_list = []
        for item in data:
            final = {}
            final["type"] = item.get("category").encode('utf-8')
            final["rgname"] = item.get("name").encode('utf-8')
            final["memo"] = item.get("memo", "").encode('utf-8')
            final["domain_id"] = item.get("domain_id")
            final["creator_id"] = item.get("creator_id")
            final["rg_id"] = item.get("id")
            final["resource_ids"] = item.get("resource_ids", [])
            res_list.append(final)
        return res_list