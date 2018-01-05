__author__ = 'wangqiushi'
from django.test import TestCase
from tastypie.test import ResourceTestCase
from yottaweb.apps.auth.resources import AuthResource


class AuthResourceTest(ResourceTestCase):

    def setUp(self):
        super(AuthResourceTest, self).setUp()
        self.testData = {
            "username": "",
            "fullname": '', 
            "company": '', 
            "email": '', 
            "phone": '', 
            "domain": '', 
            "server": '',
            "password": '', 
            "repassword": ''
        }

    def test_auth_register(self):
        # check error situation
        resp = self.api_client.post('/api/v0/auth/register', format='json', data=self.testData)
        self.assertValidJSONResponse(resp)
        original_data = self.deserialize(resp)
        new_data = original_data.copy()
        self.assertEqual(new_data['status'], '0', 'error status should be 0:')
        self.assertEqual(new_data['msg'], 'parameter required error', 'required parameter test:')
        self.assertEqual(new_data['err_code'], '2', 'error_code test')
        # password not equal test

        # check normal situation
        normal_data = {
            "username": "aaa",
            "fullname": 'asdf',
            "company": 'qqdfda',
            "email": 'a@bc.com',
            "phone": '12341234',
            "domain": 'aaa',
            "server": 'fadsfds',
            "password": 'qwerqwer',
            "repassword": 'qwerqwer'
        }
        resp_new = self.client.post('/api/v0/auth/register', data=normal_data)
        self.assertValidJSONResponse(resp_new)
        org_normal_data = self.deserialize(resp_new)
        new_normal_data = org_normal_data.copy()
        self.assertEqual(new_normal_data['status'], '1', 'status should be 1:')
        self.assertEqual(new_normal_data['location'], 'http://localhost:8080/dashboard/', 'location test')

    def test_auth_register_password(self):
        normal_data = {
            "username": "aaa",
            "fullname": 'asdf',
            "company": 'qqdfda',
            "email": 'a@bc.com',
            "phone": '12341234',
            "domain": 'aaa',
            "server": 'fadsfds',
            "password": 'qwerqwer',
            "repassword": '123123'
        }
        resp_new = self.client.post('/api/v0/auth/register', data=normal_data)
        self.assertValidJSONResponse(resp_new)
        org_normal_data = self.deserialize(resp_new)
        new_normal_data = org_normal_data.copy()
        self.assertEqual(new_normal_data['status'], '0', 'status should be 0:')
        self.assertEqual(new_normal_data['err_code'], '1', 'password not equal')

    def test_auth_login(self):
        test_data = {
            "username": "u",
            "password": "p"
        }

        resp = self.client.post('/api/v0/auth/login',  format='json', data=test_data)
        self.assertValidJSONResponse(resp)
        org_normal_data = self.deserialize(resp)
        new_normal_data = org_normal_data.copy()
        self.assertEqual(new_normal_data['status'], '1', 'status should be 1')
        self.assertEqual(new_normal_data['location'], '/dashboard', 'location should be /dashboard')

        test_data = {
            "username": "",
            "password": "p"
        }

        resp = self.client.post('/api/v0/auth/login',  format='json', data=test_data)
        self.assertValidJSONResponse(resp)
        org_normal_data = self.deserialize(resp)
        new_normal_data = org_normal_data.copy()
        self.assertEqual(new_normal_data['status'], '0', 'status should be 0')
        self.assertEqual(new_normal_data['err_code'], '1', 'error code should 1')

        test_data = {
            "username": "u",
            "password": ""
        }

        resp = self.client.post('/api/v0/auth/login',  format='json', data=test_data)
        self.assertValidJSONResponse(resp)
        org_normal_data = self.deserialize(resp)
        new_normal_data = org_normal_data.copy()
        self.assertEqual(new_normal_data['status'], '0', 'status should be 0')
        self.assertEqual(new_normal_data['err_code'], '1', 'error code should 1')

        data_inValid3 = {
            "username": "",
            "password": ""
        }

        resp = self.client.post('/api/v0/auth/login',  format='json', data=test_data)
        self.assertValidJSONResponse(resp)
        org_normal_data = self.deserialize(resp)
        new_normal_data = org_normal_data.copy()
        self.assertEqual(new_normal_data['status'], '0', 'status should be 0')
        self.assertEqual(new_normal_data['err_code'], '1', 'error code should 1')