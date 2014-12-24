from django.test import TestCase
import mock

from rest_framework.test import APIRequestFactory
from rest_framework import exceptions

from ...auth import drf_session as drf_session_header

class TestDrfSession(TestCase):
    def test_enforce_csrf(self):
        #TODO: real test
        self.assertTrue(True)
        # Any valid URL will work
        request = APIRequestFactory().get('/admin/',HTTP_AUTHORIZATION='session blah')
        drf_session_header.SessionAuthentication().enforce_csrf(request)
        
        
class TestDrfSessionHeader(TestCase):
    def setUp(self):
        self.obj = drf_session_header.SessionAuthorizationHeaderAuthentication()
        self.factory = APIRequestFactory()

    def test_authenticate(self):
        request = self.factory.get('/blah',HTTP_AUTHORIZATION='session blah')
        m = mock.Mock()
        self.obj.authenticate_credentials = m
        res = self.obj.authenticate(request)
        self.assertEqual( m('blah'),res)
        m.assertCalledWith(['blah'])

    def test_authentication_bad_no_header(self):
        m = mock.Mock()
        self.obj.authenticate_credentials = m
        request = self.factory.get('/blah')
        res = self.obj.authenticate(request)
        self.assertEqual(None,res)

        self.assertFalse(m.called)
    def test_authentication_bad_wrong_scheme(self):
        m = mock.Mock()
        self.obj.authenticate_credentials = m
        request = self.factory.get('/blah',HTTP_AUTHORIZATION='stuff blah')
        res = self.obj.authenticate(request)

        self.assertFalse(m.called)
    def test_authentication_bad_right_scheme_no_val(self):
        m = mock.Mock()
        self.obj.authenticate_credentials = m
        request = self.factory.get('/blah',HTTP_AUTHORIZATION='session')

        self.assertRaises(exceptions.AuthenticationFailed,self.obj.authenticate,request)

    def test_authentication_bad_right_scheme_too_many_vals(self):
        m = mock.Mock()
        self.obj.authenticate_credentials = m
        request = self.factory.get('/blah',HTTP_AUTHORIZATION='session blah stuff')
        self.assertRaises(exceptions.AuthenticationFailed,self.obj.authenticate,request)

        self.assertFalse(m.called)

    def test_authenticate_credentials(self):
        sessionMock = mock.Mock()
        userMock = mock.Mock()
        with mock.patch.object(drf_session_header,'Session',sessionMock):
            with mock.patch.object(drf_session_header,'get_user_model',userMock):
                res = self.obj.authenticate_credentials('blah')

        sessionMock.objects.get.assertCalledWith({'session_key':'blah'})
        gmock = sessionMock.objects.get(session_key='blah').get_decoded.get
        gmock.assertCalledWith(['_auth_user_id'])
        userMock().objects.get.assertCalledWith({'pk':gmock('_auth_user_id')})
        self.assertEqual((userMock().objects.get(),'blah'),res)

    def test_authenticate_credentials_bad_no_session(self):
        userMock = mock.Mock()

        with mock.patch.object(drf_session_header,'get_user_model',userMock):
            res = self.obj.authenticate_credentials('blah')

        self.assertEqual(None,res)
        self.assertFalse(userMock.called)