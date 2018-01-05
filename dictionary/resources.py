from tastypie.resources import Resource
from django.conf.urls import url
from yottaweb.apps.basic.resources import MyBasicAuthentication
from yottaweb.apps.basic.resources import ContributeErrorData
from yottaweb.apps.backend.resources import BackendRequest
from yottaweb.apps.dictionary.forms import UploadFileForm
import os
import pymysql
import ConfigParser
import logging
import time
import numbers

__author__ = 'wangqiushi'
err_data = ContributeErrorData()
host = '192.168.1.88'
user = 'root'
pwd = 'rizhiyi&2014'
database = 'rizhiyi_system'

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


logger = logging.getLogger("django.request")

class DictionaryResource(Resource):
    # Just like a Django ``Form`` or ``Model``, we're defining all the
    # fields we're going to handle with the API here.

    class Meta:
        resource_name = 'dictionary'
        always_return_data = True
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/upload/$" % self._meta.resource_name,
                self.wrap_view('dict_upload'), name="api_dict_upload"),
            url(r"^(?P<resource_name>%s)/update/(?P<id>[\w]+)/$" % self._meta.resource_name,
                self.wrap_view('dict_update'), name="api_dict_upload"),
            url(r"^(?P<resource_name>%s)/lists/$" % self._meta.resource_name,
                self.wrap_view('dict_lists'), name="api_dict_upload"),
            url(r"^(?P<resource_name>%s)/lists/title/(?P<id>[\w]+)/$" % self._meta.resource_name,
                self.wrap_view('dict_lists_title'), name="api_dict_upload"),
            url(r"^(?P<resource_name>%s)/detail/(?P<id>[\w]+)/$" % self._meta.resource_name,
                self.wrap_view('dict_detail'), name="api_dict_detail"),
            url(r"^(?P<resource_name>%s)/delete/(?P<id>[\w]+)/$" % self._meta.resource_name,
                self.wrap_view('dict_delete'), name="api_dict_delete"),
            url(r"^(?P<resource_name>%s)/resourcegroup/filter/$" % self._meta.resource_name,
                self.wrap_view('reourcegroup_filter'), name="api_sourcegroups_rg_filter"),
            url(r"^(?P<resource_name>%s)/resourcegroup/list/assigned/(?P<did>[\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('get_resourcegroup_assigned_list'), name="api_get_resourcegroup_assigned_list"),
            url(r"^(?P<resource_name>%s)/resourcegroup/list/(?P<action>[\w_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('get_resourcegroup_list'), name="api_get_resourcegroup_list"),
            url(r"^(?P<resource_name>%s)/resourcegroup/ungrouped/$" % self._meta.resource_name,
                self.wrap_view('get_resourcegroup_ungrouped'), name="api_get_resourcegroup_ungrouped")
        ]


    ###########################################################################################################
    #   author: "Junwei Zhao"
    #   date: 10/24/2016
    #   module: Dictionary
    #   subject: Change code from directly manipulating database to calling Restful API provided by Frontend
    #   Modified APIs:
    #            1. dict_lists(self, request, **kwargs)
    #            2. dict_lists_title(self, request, **kwargs)
    #            3. dict_detail(self, request, **kwargs)
    #            4. dict_update(self, request, **kwargs)
    #            5. dict_upload(self, request, **kwargs)
    #            6. dict_delete(self, request, **kwargs)
    #   Returned error Codes and meanings:
    #            1. 000: authentication failed/error
    #            2. 001: file size is too large
    #            3. 002: not a csv file
    #            4. 003: file has already existed
    #            5. 004: file is not existed
    #            6. 010: unknow server error
    ###########################################################################################################
    @staticmethod
    def error_handler(res, authError):
        """
            Used to handle occured errors
            Error codes and meanings:
            000: authentication failed/error
            001: file size is too large
            002: not a csv file
            003: file has already existed
            004: file is not existed
            010: unknow server error
        """

        dummy = {}
        if authError:
            dummy = err_data.build_error({}, "auth error!")
            dummy["location"] = "/auth/login/"
            dummy['error_code'] = "000"
        else:
            errorCode = res.get('error_code', 500)
            error = res.get('error', None)

            if errorCode == 500:
                dummy = err_data.build_error({}, "Unknown server error")
                dummy['error_code'] = "010"
            elif errorCode == 560:
                dummy = err_data.build_error({}, "Dictionary size exceeds the maximum limit")
                dummy['error_code'] = "001"
            elif errorCode == 561:
                dummy = err_data.build_error({}, "Dictionary is not a 'csv' file")
                dummy['error_code'] = "002"
            elif errorCode == 562:
                dummy = err_data.build_error({}, "Dictionary has already existed")
                dummy['error_code'] = "003"
            elif errorCode == 563:
                dummy = err_data.build_error({}, "Dictionary is not existed")
                dummy['error_code'] = "004"
            else:
                dummy = err_data.build_error({})
                dummy['error_code'] = "010"

            dummy['error'] = str(error)

        return dummy


    @staticmethod
    def check_auth(request, **kwargs):
        """
            Used to check and return authentication result
        """

        my_auth = MyBasicAuthentication()
        return my_auth.is_authenticated(request, **kwargs)


    @staticmethod
    def generate_param(es_check, params={}):
        """
            Used to generate parameters dictionary passed to the Backend/Frontend carried in http's url.
            Default form will be passing two items: 'token' and 'operator'.
            If additional parameters are specified, then those specified params will be grouped with default and get passed.
        """

        default = {
            'token': es_check['t'],
            'operator': es_check['u']
        }

        if params:
            return dict(default, **params)

        return default


    @staticmethod
    def generate_response(objRef, data, request):
        """
            Used to generate response regards to the previous request.
        """

        bundle = objRef.build_bundle(obj=data, data=data, request=request)
        response_data = bundle
        resp = objRef.create_response(request, response_data)

        return resp


    @staticmethod
    def check_uploaded_file(file):
        """
            Used to check if uploaded file exceeds 10MB size limit or if it is not in 'csv' format
        """

        if file.size > 1024*1024*10:
            mock = {
                "result": False,
                "error_code": 560,
                "error": "Dictionary size exceeds the maximum limit 10MB"
            }
            result = DictionaryResource.error_handler(mock, False)
            return (False, result)
        elif file.name.split('.')[-1] != 'csv':
            mock = {
                "result": False,
                "error_code": 560,
                "error": "Dictionary is not a 'csv' file"
            }
            result = DictionaryResource.error_handler(mock, False)
            return (False, result)
        else:
            return (True,)


    @staticmethod
    def epoch_millisec_to_localtime(millisec):
        """
            Format upload time, incoming 'timestamp' field of every list item is epoch time in millisecond
            Chang it to localtime in Year-Month-Day Hour:Minute:Second form
        """

        if isinstance(millisec, numbers.Integral):
            # convert 'timestamp' from millisecond to second
            sec = millisec/1000
            # Get a time.struct_time object from epoch time using time.gmtime([sec]) or time.localtime([sec])
            # A time.struct_time object encapsulates all information about one specific time point.
            # If the sec argument is not provided, then time.time() is used
            struct_time = time.localtime(sec)
            # time.strftime(format[, t]) constructs a string representation of time from a time.struct_time object
            # If the t argument is not provided or None, the the time_struct object returned by time.localtime is used
            localtime = time.strftime('%Y-%m-%d %H:%M:%S', struct_time)
            return localtime


    @staticmethod
    def timestamp_format(dictList):
        """
            Format upload time, incoming 'timestamp' field is epoch time in millisecond
        """
        if len(dictList):
            for item in dictList:
                timestamp_millisec = item['timestamp']
                if isinstance(timestamp_millisec, numbers.Integral):
                    item['timestamp'] = DictionaryResource.epoch_millisec_to_localtime(timestamp_millisec)


    def dict_lists(self, request, **kwargs):
        """
            Used to get a list of all existing dictionaries.
        """

        self.method_check(request, allowed=['get'])
        dummy_data = {}

        es_check = DictionaryResource.check_auth(request, **kwargs)

        if es_check:
            param = DictionaryResource.generate_param(es_check)
            res = BackendRequest.get_dict_list(param)
            permits = []

            if res['result']:
                dummy_data["status"] = "1"
                data = res.get("list", [])
                dummy_data["list"] = data
                DictionaryResource.timestamp_format(dummy_data['list'])

                for i in data:
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "Dictionary",
                        "action": "Update"
                    })
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "Dictionary",
                        "action": "Delete"
                    })
                permits.append({
                    "target": "Dictionary",
                    "action": "Create"
                })
                permits.append({
                    "target": "DerelictResource",
                    "action": "Possess"
                })
                
                permit_param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_data = {
                    'permits': permits
                }
                permit_res = BackendRequest.batch_permit_can(permit_param, permit_data)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
            else:
                dummy_data = DictionaryResource.error_handler(res, False)
        else:
            dummy_data = DictionaryResource.error_handler(None, True)

        return DictionaryResource.generate_response(self, dummy_data, request)


    def dict_lists_title(self, request, **kwargs):
        """
        """

        self.method_check(request, allowed=['get'])
        dummy_data = {}

        es_check = DictionaryResource.check_auth(request, **kwargs)

        if es_check:
            param = DictionaryResource.generate_param(es_check, {'id': kwargs.get("id", "")})
            res = BackendRequest.get_dict_list_title(param)

            if res['result']:
                dummy_data["status"] = "1"
                # any need for data parsing?
                dummy_data["list"] = res.get("titles", [])
            else:
                dummy_data = DictionaryResource.error_handler(res, False)
        else:
            dummy_data = DictionaryResource.error_handler(None, True)

        return DictionaryResource.generate_response(self, dummy_data, request)


    def dict_update(self, request, **kwargs):
        """
            Used to update uploaded dictionary identified by its id.
        """

        self.method_check(request, allowed=['post'])
        dummy_data = {}

        es_check = DictionaryResource.check_auth(request, **kwargs)

        if es_check:
            uploaded_file = request.FILES['file']
            checked = DictionaryResource.check_uploaded_file(uploaded_file)

            if len(checked) == 2:
                dummy_data = checked[1]
            else:
                file_name = uploaded_file.name
                file_content = uploaded_file.read()

                param = DictionaryResource.generate_param(es_check,
                    {
                        'name': file_name,
                        'id': kwargs.get("id", ""),
                        'resource_group_ids': request.GET.get('ids', "")
                    }
                )
                res = BackendRequest.update_dict(param, file_content)

                if res['result']:
                    dummy_data['status'] = "1"
                else:
                    dummy_data = DictionaryResource.error_handler(res, False)
        else:
            dummy_data = DictionaryResource.error_handler(None, True)

        return DictionaryResource.generate_response(self, dummy_data, request)


    def dict_detail(self, request, **kwargs):
        """
            Used to get the data of small peek of given dictionary identified by its id.
        """

        self.method_check(request, allowed=['get'])
        dummy_data = {}

        es_check = DictionaryResource.check_auth(request, **kwargs)

        if es_check:
            param = DictionaryResource.generate_param(es_check, {'id': kwargs.get("id", "")})
            res = BackendRequest.get_dict_detail(param)

            if res['result']:

                dummy_data['status'] = "1"
                content_list = res.get("some_detail_lines", "")
                # format?
                content_str = "\n".join(content_list)
                dummy_data["content"] = content_str
            else:
                dummy_data = DictionaryResource.error_handler(res, False)
        else:
            dummy_data = DictionaryResource.error_handler(res, True)

        return DictionaryResource.generate_response(self, dummy_data, request)


    def dict_delete(self, request, **kwargs):
        """
            Used to delete the given dictionary identified by its id.
        """

        self.method_check(request, allowed=['post'])
        dummy_data = {}

        es_check = DictionaryResource.check_auth(request, **kwargs)

        if es_check:
            param = DictionaryResource.generate_param(es_check, {'id': kwargs.get("id", "")})
            res = BackendRequest.delete_dict(param)

            if res['result']:
                dummy_data['status'] = "1"
            else:
                dummy_data = DictionaryResource.error_handler(res, False)
        else:
            dummy_data = DictionaryResource.error_handler(res, True)

        return DictionaryResource.generate_response(self, dummy_data, request)


    def dict_upload(self, request, **kwargs):
        """
            Used to upload and create a new dictionary entry.
        """

        self.method_check(request, allowed=['post'])
        dummy_data = {}

        es_check = DictionaryResource.check_auth(request, **kwargs)

        if es_check:
            uploaded_file = request.FILES['file']
            checked = DictionaryResource.check_uploaded_file(uploaded_file)

            if len(checked) == 2:
                dummy_data = checked[1]
            else:
                file_name = uploaded_file.name
                file_content = uploaded_file.read()

                param = DictionaryResource.generate_param(es_check,
                    {
                    'name':file_name,
                    'resource_group_ids': request.GET.get('ids', ""),
                    }
                )

                if not BackendRequest.dict_exist(param):
                    res = BackendRequest.upload_dict(param, file_content)

                    if res['result']:
                        dummy_data['status'] = "1"
                    else:
                        dummy_data = DictionaryResource.error_handler(res, False)
                else:
                    mockRes = {
                        'result': False,
                        'error_code': 562,
                        'error': "Dictionary has already existed"
                    }
                    dummy_data = DictionaryResource.error_handler(mockRes, False)
                    print dummy_data
        else:
            dummy_data = DictionaryResource.error_handler(None, True)

        resp = DictionaryResource.generate_response(self, dummy_data, request)

        try:
            request.environ.get("HTTP_USER_AGENT","").index("MSIE 9.0")
            resp._headers.__setitem__("content-type",("CONTENT-TYPE", "text/plain"))
        except Exception, e:
            print e

        return resp


    def get_resourcegroup_list(self, request, **kwargs):
        """Get a list of available resource groups in aspect of current user.
        """

        self.method_check(request, allowed=['get'])
        dummy_data = {}

        es_check = DictionaryResource.check_auth(request, **kwargs)

        if es_check:
            # 'action' specifies what action is performed: Read, Assign
            # 'target' specifies what module is requesting
            param = {}
            if kwargs['action'].lower() == "read":
                param['action'] = "Read"
                param['category'] = "Dictionary"
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = "ResourceGroup"
            elif kwargs['action'].lower() == "assign":
                param['action'] = "Assign"
                param['token'] = es_check['t']
                param['operator'] = es_check['u']
                param['target'] = "Dictionary"

            res = BackendRequest.permit_list_resource_group(param)

            if res['result']:
                data = self.rebuild_resource_group_list(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["list"] = data
            else:
                dummy_data['status'] = 0
                dummy_data['msg'] = res.get('error', "Unknow server error")
        else:
            dummy_data['status'] = 0
            dummy_data['msg'] = "auth failed/error"

        return DictionaryResource.generate_response(self, dummy_data, request)


    def get_resourcegroup_assigned_list(self, request, **kwargs):
        """
        """

        self.method_check(request, allowed=['get'])
        dict_id = kwargs.get('did', "")
        dummy_data = {}

        es_check = DictionaryResource.check_auth(request, **kwargs)

        if es_check:
            param = DictionaryResource.generate_param(es_check, {'resource_id': dict_id, 'category': "Dictionary"})

            res = BackendRequest.list_assigned_resource_group(param)

            if res['result']:
                data = self.rebuild_resource_group_list(res['resource_groups'])
                dummy_data["status"] = "1"
                dummy_data["total"] = len(data)
                dummy_data["list"] = data
            else:
                dummy_data["status"] = 0
                dummy_data["msg"] = res.get('error', 'get source group history error!')
        else:
            dummy_data["status"] = "0"

        return DictionaryResource.generate_response(self, dummy_data, request)


    def reourcegroup_filter(self, request, **kwargs):
        """
        """

        self.method_check(request, allowed=['post'])

        req_data = request.POST
        ids = req_data.get('ids', "")
        dummy_data = {}

        es_check = DictionaryResource.check_auth(request, **kwargs)

        if es_check:
            # reource group ids is passed to frontend in string form which each id is separated by comma
            param = DictionaryResource.generate_param(es_check, {'ids': ids})

            res = BackendRequest.get_batch_dictionary(param)

            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["list"] = res['list']
                DictionaryResource.timestamp_format(dummy_data['list'])
                dummy_data["total"] = len(res['list'])

                permits = []
                for i in res['list']:
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "Dictionary",
                        "action": "Update"
                    })
                    permits.append({
                        "resource_id": int(i['id']),
                        "target": "Dictionary",
                        "action": "Delete"
                    })
                permits.append({
                    "target": "Dictionary",
                    "action": "Create"
                })
                permits.append({
                    "target": "DerelictResource",
                    "action": "Possess"
                })
                
                permit_param = {
                    'token': es_check['t'],
                    'operator': es_check['u']
                }
                permit_data = {
                    'permits': permits
                }
                permit_res = BackendRequest.batch_permit_can(permit_param, permit_data)
                if permit_res['result']:
                    dummy_data["permit_list"] = permit_res["short_permits"]
                else:
                    dummy_data["permit_list"] = []
            else:
                dummy_data['status'] = 0
                dummy_data['msg'] = res.get('error', "Unknow server error")
        else:
            dummy_data['status'] = 0
            dummy_data['msg'] = "auth failed/error"

        return DictionaryResource.generate_response(self, dummy_data, request)

    def get_resourcegroup_ungrouped(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        es_check = False
        my_auth = MyBasicAuthentication()
        es_check = my_auth.is_authenticated(request, **kwargs)
        if es_check:
            param = {
                'category': "Dictionary",
                'token': es_check['t'],
                'operator': es_check['u']
            }
            res = BackendRequest.list_derelict_resource_ids(param)
            if res['result']:
                dummy_data["status"] = "1"
                dummy_data["ids"] = res['resource_ids']
            else:
                dummy_data['status'] = 0
                dummy_data['msg'] = res.get('error', "Unknow server error")
        else:
            dummy_data["status"] = "0"

        return DictionaryResource.generate_response(self, dummy_data, request)

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


    ###############################################
    # Deprecated code starts here
    #
    ###############################################

    def handle_uploaded_file(self, f):
        path = os.path.dirname(os.path.realpath(__file__))
        filename = f.name
        with open(path + '/' + filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)