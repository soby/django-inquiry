import json
import mock
import re
import random
import string

from . import base

from .....api.v1.views import user
from .....utils.test.objects import remove_fields, compare_dict_lists
from .....utils.auth import make_perm, make_global_perm

from ..... import models

from rest_framework.test import APITestCase,APIRequestFactory,APIClient

from django.core.urlresolvers import reverse
from django.conf import settings 
from django.contrib.sessions.models import Session
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

def randomword(length):
    return ''.join(random.choice(string.lowercase+string.digits) for i in range(length)) #@UnusedVariable

class UserViewSetTest(base.ViewSetBaseTestMixin,APITestCase):
    named_view_base = 'api/core/v1/user'
    namespace = None
    viewset = user.UserViewSet

    def setUp(self):
        self.o = models.Org(name='blah')
        self.o.save()
        self.addCleanup(self.o.delete)
        self.obj = get_user_model()(username='user1',org=self.o)
        self.obj.save()
        self.obj2 = get_user_model()(username='regular_user1',org=self.o)
        self.obj2.save()

        self.addCleanup(self.obj.delete)
        self.addCleanup(self.obj2.delete)

        self.o2 = models.Org(name='uninvolved')
        self.o2.save()
        self.o2u2 = get_user_model()(username='user2',org=self.o2)
        self.o2u2.save()
        self.addCleanup(self.o2u2.delete)
        self.addCleanup(self.o2.delete)
        self.uninvolved = get_user_model()(username='uninvolved',org=self.o2)
        self.uninvolved.save()
        self.addCleanup(self.uninvolved.delete)

    def test_create(self):
        self.client.force_authenticate(user=self.obj)
        url = reverse(self.named_view_base+'-list',current_app=self.namespace)
        res = self.client.post(url,data={'username':'stuff'})
        self.assertEqual(201,res.status_code)
        resJson = json.loads(res.content)
        u = get_user_model().objects.get(pk=resJson['id'])
        self.addCleanup(u.delete)
        self.assertEqual(u.username,'stuff')
        self.assertEqual(u.org_id,self.obj.org_id)
        # Django thing. first_name is blank=True but not null=True
        self.assertEqual(u.first_name,u'')
        # This is a custom field
        self.assertEqual(u.title,None)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':u.id},current_app=self.namespace)
        res = self.client.get(url)
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)

        self.assertEqual({u"username": u"stuff", u"email": u'', u"first_name": u'', u"last_name": u'', u"title":None, u"group":None, u"phone":None, u"is_active": True, u"groups": [{u"name": u"users"}]},remove_fields(['id'],resJson))

    def test_create_cross_org_deny(self):
        self.client.force_authenticate(user=self.obj)
        url = reverse(self.named_view_base+'-list',current_app=self.namespace)

        org2 = models.Org(name='other')
        org2.save()
        self.addCleanup(org2.delete)

        res = self.client.post(url,data={'username':'stuff','org':org2.pk,'org_id':org2.pk})
        self.assertEqual(201,res.status_code)
        resJson = json.loads(res.content)
        u = get_user_model().objects.get(pk=resJson['id'])
        self.addCleanup(u.delete)
        
        self.assertEqual(u.org_id,self.obj2.org_id)

    def test_list(self):
        self.client.force_authenticate(user=self.obj2)
        url = reverse(self.named_view_base+'-list',current_app=self.namespace)
        res = self.client.get(url)
        self.assertEqual(200,res.status_code)
        expected = [{"username": "user1", "email": "", "first_name": "", "last_name": "", "title":None,"group":None,"phone":None,"is_active": True, "groups": [{"name": "users"}, {"name": "administrators"}]}, {"username": "regular_user1", "email": "", "first_name": "", "last_name": "", "title":None,"group":None,"phone":None,"is_active": True, "groups": [{"name": "users"}]}]
        self.assertEqual(([],[]),compare_dict_lists(expected,
                         json.loads(res.content),lambda x: remove_fields(['id','groups'],x))
                        )
        resJson = json.loads(res.content)
        for i in xrange(0,len(expected)):
            self.assertEqual(([],[]),
                             compare_dict_lists(expected[i]['groups'],
                                                resJson[i]['groups'],
                                                lambda x: remove_fields(['id'],x))
                            )

    def test_my(self):
        self.client.force_authenticate(user=self.obj)
        url = reverse(self.named_view_base+'-my',current_app=self.namespace)
        res = self.client.get(url)
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        self.assertEqual(resJson['id'],self.obj.id)

    def test_my_regular_user(self):
        self.client.force_authenticate(user=self.obj2)
        url = reverse(self.named_view_base+'-my',current_app=self.namespace)
        res = self.client.get(url)
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        self.assertEqual(resJson['id'],self.obj2.id)

    def test_detail(self):
        self.client.force_authenticate(user=self.obj2)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':self.obj2.id},current_app=self.namespace)
        res = self.client.get(url)
        self.assertEqual(200,res.status_code)

    def test_detail_bad_cross_org(self):
        self.client.force_authenticate(user=self.obj)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':self.uninvolved.id},current_app=self.namespace)
        res = self.client.get(url)
        self.assertEqual(404,res.status_code)

    def test_self_update_by_admin(self):
        self._self_update_by_admin('put')

    def _self_update_by_admin(self,method,token=None):
        if token is None:
            token = randomword(10)

        self.assertTrue(self.obj.has_perm(make_perm(self.obj,'change'),self.obj))
        self.assertTrue(self.obj.has_perm(make_global_perm(self.obj,'change')))
        data = {'username':'asdf{0}'.format(token),'email':'stuff{0}@stuff.com'.format(token),"first_name": "first{0}".format(token), "last_name": "last{0}".format(token), "is_active": False}
        self.client.force_authenticate(user=self.obj)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':self.obj.id},current_app=self.namespace)
        if method == 'put':
            res = self.client.put(url,data=data)
        else:
            res = self.client.patch(url,data=data)

        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        u = get_user_model().objects.get(pk=self.obj.id)
        self.addCleanup(u.delete)

        # shouldn't change
        self.assertEqual(u.username,self.obj.username)
        self.assertEqual(u.org_id,self.obj.org_id)
        self.assertEqual(resJson['username'],self.obj.username)

        # should change
        self.assertEqual(u.email,data['email'])
        self.assertEqual(u.first_name,data['first_name'])
        self.assertEqual(u.last_name,data['last_name'])
        self.assertEqual(u.is_active,data['is_active'])
        self.assertEqual(resJson['email'],data['email'])
        self.assertEqual(resJson['first_name'],data['first_name'])
        self.assertEqual(resJson['last_name'],data['last_name'])
        self.assertEqual(resJson['is_active'],data['is_active'])

    def test_self_update(self):
        self._self_update('put')

    def test_multiple_self_updates(self):
        self._self_update('put')
        self._self_update('put')
        self._self_update('patch')
        self._self_update('patch')

    def _self_update(self,method,token=None):
        if token is None:
            token = randomword(10)

        self.assertTrue(self.obj2.has_perm(make_perm(self.obj2,'change'),self.obj2))
        self.assertTrue(self.obj2.has_perm(make_global_perm(self.obj2,'change')))
        data = {'username':'asdf{0}'.format(token),'email':'stuff{0}@stuff.com'.format(token),"first_name": "first{0}".format(token), "last_name": "last{0}".format(token), "is_active": False}
        self.client.force_authenticate(user=self.obj2)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':self.obj2.id},current_app=self.namespace)
        if method == 'put':
            res = self.client.put(url,data=data)
        else:
            res = self.client.patch(url,data=data)
            
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        u = get_user_model().objects.get(pk=self.obj2.id)
        self.addCleanup(u.delete)

        # shouldn't change
        self.assertEqual(u.username,self.obj2.username)
        self.assertEqual(u.org_id,self.obj2.org_id)
        self.assertEqual(resJson[u'username'],self.obj2.username)

        # should change
        self.assertEqual(u.email,data['email'])
        self.assertEqual(u.first_name,data['first_name'])
        self.assertEqual(u.last_name,data['last_name'])
        self.assertEqual(u.is_active,data['is_active'])
        self.assertEqual(resJson[u'email'],data['email'])
        self.assertEqual(resJson[u'first_name'],data['first_name'])
        self.assertEqual(resJson[u'last_name'],data['last_name'])
        self.assertEqual(resJson[u'is_active'],data['is_active'])

    def test_bad_update_by_user(self):
        self._bad_update_by_user('put')

    def _bad_update_by_user(self,method):
        self.assertFalse(self.obj2.has_perm(make_perm(self.obj,'change'),self.obj))
        
        data = {'username':'asdf','email':'stuff@stuff.com',"first_name": "first", "last_name": "last", "is_active": False}
        self.client.force_authenticate(user=self.obj2)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':self.obj.id},current_app=self.namespace)
        if method == 'put':
            res = self.client.put(url,data=data)
        else:
            res = self.client.patch(url,data=data)
            
        self.assertEqual(403,res.status_code)

    def test_bad_cross_org_update_by_admin(self):
        self._bad_cross_org_update_by_admin('put')

    def _bad_cross_org_update_by_admin(self,method):
        self.assertFalse(self.obj.has_perm(make_perm(self.obj,'change'),self.uninvolved))
        
        data = {'username':'asdf','email':'stuff@stuff.com',"first_name": "newfirst", "last_name": "last", "is_active": False}
        self.client.force_authenticate(user=self.obj)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':self.uninvolved.id},current_app=self.namespace)
        if method == 'put':
            res = self.client.put(url,data=data)
        else:
            res = self.client.patch(url,data=data)
            

        # With a PUT, this actually results in a create in the caller's org, probably due to a strange side
        # effect of get_object() returning nothing with the restricted querysets 
        if method == 'put':
            self.assertEqual(404,res.status_code)
            u = get_user_model().objects.get(pk=self.uninvolved.id)
            self.assertNotEqual(u.first_name,'newfirst')
        else:
            self.assertEqual(404,res.status_code)

    def test_self_partial_update_by_admin(self):
        self._self_update_by_admin('partial')
    def test_self_partial_update(self):
        self._self_update('patch')
    def test_bad_partial_update_by_user(self):
        self._bad_update_by_user('patch')
    def test_bad_cross_org_partial_update_by_admin(self):
        self._bad_cross_org_update_by_admin('patch')

    def test_update(self):
        pass # covered above
    def test_partial_update(self):
        pass # covered above

    def test_delete(self):
        self.assertTrue(self.obj.has_perm(make_perm(self.obj,'delete'),self.obj2))
        self.assertTrue(self.obj.has_perm(make_global_perm(self.obj,'delete')))
        self.client.force_authenticate(user=self.obj)
        deactiveMock = mock.Mock()

        url = reverse(self.named_view_base+'-detail',kwargs={'pk':self.obj2.id},current_app=self.namespace)
        res = self.client.delete(url)

        u = get_user_model().objects.get(pk=self.obj2.id)
        self.assertNotEqual(self.obj2.is_active,u.is_active)
        self.assertFalse(u.is_active)
        self.assertEqual([],[x for x in u.groups.all()])
        self.assertFalse(deactiveMock.called)

        self.assertEqual(204,res.status_code)

    def test_bad_delete_by_user(self):
        self.assertFalse(self.obj2.has_perm(make_perm(self.obj,'delete'),self.obj))
        self.assertFalse(self.obj2.has_perm(make_global_perm(self.obj,'delete')))
        self.client.force_authenticate(user=self.obj2)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':self.obj.id},current_app=self.namespace)
        res = self.client.delete(url)

        u = get_user_model().objects.get(pk=self.obj.id)
        self.assertEqual(self.obj.is_active,u.is_active)
        self.assertTrue(u.is_active)

        self.assertEqual(403,res.status_code)

    def test_bad_delete_cross_org(self):
        self.assertFalse(self.obj.has_perm(make_perm(self.obj,'delete'),self.uninvolved))
        self.client.force_authenticate(user=self.obj)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':self.uninvolved.id},current_app=self.namespace)
        res = self.client.delete(url)

        u = get_user_model().objects.get(pk=self.uninvolved.id)
        self.assertEqual(self.uninvolved.is_active,u.is_active)
        self.assertTrue(u.is_active)

        self.assertEqual(404,res.status_code)

    def test_login(self):
        self.obj2.set_password('blah')
        self.obj2.save()
        url = reverse(self.named_view_base+'-login')
        res = self.client.get(url,data={'username':self.obj2.username,'password':'blah'})
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        self.assertEqual(self.obj2.username,resJson.get('user',{}).get('username'))
        session = resJson.get('session',{}).get('id')
        self.assertTrue(session)
        dbSession = self._get_valid_session(session)
        self.assertTrue(dbSession)
        self.assertEqual(self.obj2.id,dbSession.get_decoded().get('_auth_user_id'))

        csrf = resJson.get('csrf')
        self.assertTrue(csrf)
    
    def _get_valid_session(self,val):
        try:
            return Session.objects.get(session_key=val)
        except:
            return None

    def test_login_bad_password(self):
        self.obj2.set_password('blah')
        self.obj2.save()
        url = reverse(self.named_view_base+'-login')
        res = self.client.get(url,data={'username':self.obj2.username,'password':'wrong'})
        self.assertEqual(403,res.status_code)
        resJson = json.loads(res.content)
        self.assertEqual({"detail": "invalid login"},resJson)

    def test_login_unknown_user(self):
        self.obj2.set_password('blah')
        self.obj2.save()
        url = reverse(self.named_view_base+'-login')
        res = self.client.get(url,data={'username':'asdf234@lkasjdfau5.com','password':'wrong'})
        self.assertEqual(403,res.status_code)
        resJson = json.loads(res.content)
        self.assertEqual({"detail": "invalid login"},resJson)
        
    def test_logout(self):
        self.client.force_authenticate(user=self.obj2)
        url = reverse(self.named_view_base+'-logout',kwargs={'pk':self.obj2.id})
        res = self.client.patch(url)
        self.assertEqual(204,res.status_code)

    def test_logout_bad_other_user(self):
        self.client.force_authenticate(user=self.obj2)
        url = reverse(self.named_view_base+'-logout',kwargs={'pk':self.obj.id})
        res = self.client.patch(url)
        self.assertEqual(403,res.status_code)

    def test_multi(self):
        self.obj2.set_password('blah')
        self.obj2.save()
        url = reverse(self.named_view_base+'-login')
        res = self.client.get(url,data={'username':self.obj2.username,'password':'blah'})
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        self.assertEqual(self.obj2.username,resJson.get('user',{}).get('username'))
        session = resJson.get('session',{}).get('id')
        self.assertTrue(session)
        dbSession = self._get_valid_session(session)
        self.assertTrue(dbSession)
        self.assertEqual(self.obj2.id,dbSession.get_decoded().get('_auth_user_id'))

        url = reverse(self.named_view_base+'-logout',kwargs={'pk':self.obj2.id})
        # clean slate
        self.client = APIClient()
        res = self.client.patch(url,HTTP_AUTHORIZATION='session '+session)
        self.assertEqual(204,res.status_code)

        self.assertFalse(self._get_valid_session(session))

    def test_change_password(self):
        self.obj2.set_password('blah')
        self.obj2.save()
        self.client.force_authenticate(user=self.obj2)
        url = reverse(self.named_view_base+'-change-password',kwargs={'pk':self.obj2.id})
        res = self.client.patch(url,data={'oldpassword':'blah','newpassword':'stuff'})
        self.assertEqual(204,res.status_code)
        u = get_user_model().objects.get(pk=self.obj2.id)
        self.assertTrue(u.check_password('stuff'))

    def test_change_password_bad(self):
        self.obj2.set_password('blah')
        self.obj2.save()
        self.client.force_authenticate(user=self.obj2)
        url = reverse(self.named_view_base+'-change-password',kwargs={'pk':self.obj2.id})
        res = self.client.patch(url,data={'oldpassword':'blah2','newpassword':'stuff'})
        self.assertEqual(401,res.status_code)
        u = get_user_model().objects.get(pk=self.obj2.id)
        self.assertTrue(u.check_password('blah'))

    def test_change_password_wrong_user(self):
        self.obj2.set_password('blah')
        self.obj2.save()
        self.client.force_authenticate(user=self.obj)
        url = reverse(self.named_view_base+'-change-password',kwargs={'pk':self.obj2.id})
        res = self.client.patch(url,data={'oldpassword':'blah','newpassword':'stuff'})
        self.assertEqual(403,res.status_code)
        u = get_user_model().objects.get(pk=self.obj2.id)
        self.assertTrue(u.check_password('blah'))

    def test_reset_password_for_username_anon(self):
        email_send_mock = mock.Mock(spec=self.viewset._send_password_reset_email)
        with mock.patch.object(user.UserViewSet,'_send_password_reset_email',email_send_mock): #@UndefinedVariable
            url = reverse(self.named_view_base+'-reset-password-for-username')
            res = self.client.post(url, {'username': self.obj2.username})
        self.assertEqual(200,res.status_code)
        firstCall = email_send_mock.call_args[0]
        self.assertEqual(firstCall[1].pk,self.obj2.id)

    def test_reset_password_for_username_auth_same_user(self):
        email_send_mock = mock.Mock(spec=self.viewset._send_password_reset_email)
        self.client.force_authenticate(user=self.obj2)
        with mock.patch.object(user.UserViewSet,'_send_password_reset_email',email_send_mock): #@UndefinedVariable
            url = reverse(self.named_view_base+'-reset-password-for-username')
            res = self.client.post(url, {'username': self.obj2.username})
        self.assertEqual(200,res.status_code,)
        firstCall = email_send_mock.call_args[0]
        self.assertEqual(firstCall[1].pk,self.obj2.id)

    def test_reset_password_for_username_auth_admin(self):
        email_send_mock = mock.Mock(spec=self.viewset._send_password_reset_email)
        self.client.force_authenticate(user=self.obj)
        with mock.patch.object(user.UserViewSet,'_send_password_reset_email',email_send_mock): #@UndefinedVariable
            url = reverse(self.named_view_base+'-reset-password-for-username')
            res = self.client.post(url, {'username': self.obj2.username})
        self.assertEqual(200,res.status_code)
        firstCall = email_send_mock.call_args[0]
        self.assertEqual(firstCall[1].pk,self.obj2.id)

    def test_reset_password_for_username_bad_auth_user_to_admin(self):
        email_send_mock = mock.Mock(spec=self.viewset._send_password_reset_email)
        self.client.force_authenticate(user=self.obj2)
        with mock.patch.object(user.UserViewSet,'_send_password_reset_email',email_send_mock): #@UndefinedVariable
            url = reverse(self.named_view_base+'-reset-password-for-username')
            res = self.client.post(url, {'username': self.obj.username})
        self.assertEqual(403,res.status_code)
        self.assertFalse(email_send_mock.called)

    def test_reset_password_for_username_bad_no_username(self):
        email_send_mock = mock.Mock(spec=self.viewset._send_password_reset_email)
        with mock.patch.object(user.UserViewSet,'_send_password_reset_email',email_send_mock): #@UndefinedVariable
            url = reverse(self.named_view_base+'-reset-password-for-username')
            res = self.client.post(url)
        self.assertEqual(400,res.status_code)
        self.assertFalse(email_send_mock.called)

    def test_reset_password_for_username_bad_anon_not_found(self):
        # We don't tell anon that the user doesn't exist
        email_send_mock = mock.Mock(spec=self.viewset._send_password_reset_email)
        with mock.patch.object(user.UserViewSet,'_send_password_reset_email',email_send_mock): #@UndefinedVariable
            url = reverse(self.named_view_base+'-reset-password-for-username')
            res = self.client.post(url, {'username': 'asdfasdfas@dflkajsd.com'})
        self.assertEqual(200,res.status_code)
        self.assertFalse(email_send_mock.called)

    def test_reset_password_for_username_bad_anon_inactive(self):
        # We don't tell anon about bad requests
        self.obj2.is_active=False
        self.obj2.save()
        email_send_mock = mock.Mock(spec=self.viewset._send_password_reset_email)
        with mock.patch.object(user.UserViewSet,'_send_password_reset_email',email_send_mock): #@UndefinedVariable
            url = reverse(self.named_view_base+'-reset-password-for-username')
            res = self.client.post(url, {'username': 'asdfasdfas@dflkajsd.com'})
        self.assertEqual(200,res.status_code)
        self.assertFalse(email_send_mock.called)

    def test_reset_password_for_username_bad_anon_good_bad_message_same(self):
        # We don't tell anon about bad requests
        email_send_mock = mock.Mock(spec=self.viewset._send_password_reset_email)
        with mock.patch.object(user.UserViewSet,'_send_password_reset_email',email_send_mock): #@UndefinedVariable
            url = reverse(self.named_view_base+'-reset-password-for-username')
            badRes = self.client.post(url, {'username': 'asdfasdfas@dflkajsd.com'})
            goodRes = self.client.post(url, {'username': self.obj2.username})
        self.assertEqual(badRes.status_code,goodRes.status_code)
        self.assertEqual(badRes.content,goodRes.content)

    def test_reset_password_for_username_bad_auth_not_found(self):
        email_send_mock = mock.Mock(spec=self.viewset._send_password_reset_email)
        self.client.force_authenticate(user=self.obj2)
        with mock.patch.object(user.UserViewSet,'_send_password_reset_email',email_send_mock): #@UndefinedVariable
            url = reverse(self.named_view_base+'-reset-password-for-username')
            res = self.client.post(url, {'username': 'asdf@asdfasdfad.com'})
        self.assertEqual(404,res.status_code)
        self.assertFalse(email_send_mock.called)        

    def test_reset_password_for_username_bad_auth_not_active(self):
        self.obj2.is_active=False
        self.obj2.save()
        email_send_mock = mock.Mock(spec=self.viewset._send_password_reset_email)
        self.client.force_authenticate(user=self.obj)
        with mock.patch.object(user.UserViewSet,'_send_password_reset_email',email_send_mock): #@UndefinedVariable
            url = reverse(self.named_view_base+'-reset-password-for-username')
            res = self.client.post(url, {'username': self.obj2.username})
        self.assertEqual(400,res.status_code)
        self.assertFalse(email_send_mock.called)

    def test_reset_password_for_username_bad_auth_wrong_org(self):
        email_send_mock = mock.Mock(spec=self.viewset._send_password_reset_email)
        self.client.force_authenticate(user=self.obj)
        with mock.patch.object(user.UserViewSet,'_send_password_reset_email',email_send_mock): #@UndefinedVariable
            url = reverse(self.named_view_base+'-reset-password-for-username')
            res = self.client.post(url, {'username': self.uninvolved.username})
        self.assertEqual(404,res.status_code)
        self.assertFalse(email_send_mock.called)

    def test_send_password_reset_email(self):
        url = reverse(self.named_view_base+'-reset-password-for-username')
        request = self.client.post(url, {'username': self.obj2.username}) #@UnusedVariable
        self.obj2.email = 'blah234@blah.com'
        self.obj2.save()

        sendEmailMock = mock.Mock(spec=user.send_mail)
        with mock.patch.object(user,'send_mail',sendEmailMock): #@UndefinedVariable
            factory = APIRequestFactory()
            # the method is expecting a request and we're testing it directly
            request = factory.post(url)
            self.viewset()._send_password_reset_email(request,self.obj2)

        self.assertTrue(sendEmailMock.called)
        paramRegex = re.compile('uid=(?P<uid>.+?)&token=.+')
        txtCall = sendEmailMock.call_args[0]
        def check(self,call):
            ghetto_version = u'{0}'.format(call)
            self.assertTrue(settings.PASSWORD_RESET_CONFIRM_URL in ghetto_version)
            m = paramRegex.search(ghetto_version)
            self.assertTrue(m)
            self.assertEqual(urlsafe_base64_decode(m.groupdict().get('uid','')),str(self.obj2.pk))
            return ghetto_version
        
        ghetto_version = check(self,txtCall)
        self.assertTrue(self.obj2.email in ghetto_version)
        htmlCall = sendEmailMock.call_args[1]
        check(self,htmlCall)

    def test_reset_password_with_token(self,client=None):
        token = default_token_generator.make_token(self.obj2)
        uid = urlsafe_base64_encode(force_bytes(self.obj2.pk))
        url = reverse(self.named_view_base+'-reset-password-with-token')
        c = client
        if not c:
            c = self.client
        res = c.post(url,data={'uid':uid,'token':token,'newpassword':'qwer','newpassword_confirm':'qwer'})
        self.assertEqual(200,res.status_code)
        u2 = get_user_model().objects.get(pk=self.obj2.pk)
        self.assertTrue(u2.check_password('qwer'))

    def test_rest_password_with_token_authd(self):
        self.client.force_authenticate(self.obj2)
        self.test_reset_password_with_token(self.client)

    def test_reset_password_with_token_bad_no_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.obj2.pk))
        url = reverse(self.named_view_base+'-reset-password-with-token')
        res = self.client.post(url,data={'uid':uid,'newpassword':'qwer','newpassword_confirm':'qwer'})
        self.assertEqual(400,res.status_code)
        self.assertFalse(get_user_model().objects.get(pk=self.obj2.pk).check_password('qwer'))

    def test_reset_password_with_token_bad_no_uid(self):
        token = default_token_generator.make_token(self.obj2)
        url = reverse(self.named_view_base+'-reset-password-with-token')
        res = self.client.post(url,data={'token':token,'newpassword':'qwer','newpassword_confirm':'qwer'})
        self.assertEqual(400,res.status_code)
        self.assertFalse(get_user_model().objects.get(pk=self.obj2.pk).check_password('qwer'))

    def test_reset_password_with_token_bad_uid_not_b64(self):
        token = default_token_generator.make_token(self.obj2)
        url = reverse(self.named_view_base+'-reset-password-with-token')
        res = self.client.post(url,data={'uid':'invalid','token':token,'newpassword':'qwer','newpassword_confirm':'qwer'})
        self.assertEqual(400,res.status_code)
        self.assertFalse(get_user_model().objects.get(pk=self.obj2.pk).check_password('qwer'))

    def test_reset_password_with_token_bad_user_not_found(self):
        token = default_token_generator.make_token(self.obj2)
        url = reverse(self.named_view_base+'-reset-password-with-token')
        res = self.client.post(url,data={'uid':'NTAwMDAw','token':token,'newpassword':'qwer','newpassword_confirm':'qwer'})
        self.assertEqual(400,res.status_code)
        self.assertFalse(get_user_model().objects.get(pk=self.obj2.pk).check_password('qwer'))

    def test_reset_password_with_token_bad_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.obj2.pk))
        url = reverse(self.named_view_base+'-reset-password-with-token')
        res = self.client.post(url,data={'uid':uid,'token':'whatever','newpassword':'qwer','newpassword_confirm':'qwer'})
        self.assertEqual(400,res.status_code)
        self.assertFalse(get_user_model().objects.get(pk=self.obj2.pk).check_password('qwer'))

    def test_reset_password_with_token_bad_pwd_match(self):
        token = default_token_generator.make_token(self.obj2)
        uid = urlsafe_base64_encode(force_bytes(self.obj2.pk))
        url = reverse(self.named_view_base+'-reset-password-with-token')
        res = self.client.post(url,data={'uid':uid,'token':token,'newpassword':'qwer','newpassword_confirm':'somethingdifferent'})
        self.assertEqual(400,res.status_code)
        self.assertFalse(get_user_model().objects.get(pk=self.obj2.pk).check_password('qwer'))

    def test_set_groups(self):
        url = reverse(self.named_view_base+'-set-groups',kwargs={'pk':self.obj.id})
        # all but the first
        groupPks = [x.id for x in self.obj.groups.all()[1:]]
        self.assertTrue(len(groupPks))
        self.client.force_authenticate(user=self.obj)
        res = self.client.put(url,data={'groups':groupPks})
        self.assertEqual(204,res.status_code)
        self.assertEqual(groupPks,[x.id for x in self.obj.groups.all()])

    def test_set_groups_bad_no_list_json(self):
        url = reverse(self.named_view_base+'-set-groups',kwargs={'pk':self.obj.id})
        # all but the first
        self.client.force_authenticate(user=self.obj)
        res = self.client.put(url,data={'groups':'2'},format='json')
        self.assertEqual(400,res.status_code)
        resJson = json.loads(res.content)
        self.assertTrue('must be a list or multivalue post' in resJson['detail'])

    def test_set_groups_no_list_urlencoded(self):
        # apparently it coverts this to a list all the time by virtue of getlist()

        url = reverse(self.named_view_base+'-set-groups',kwargs={'pk':self.obj.id})
        # all but the first
        self.client.force_authenticate(user=self.obj)
        res = self.client.put(url,data={'groups':'2'})
        self.assertEqual(400,res.status_code)

    def test_set_groups_bad_no_param(self):
        url = reverse(self.named_view_base+'-set-groups',kwargs={'pk':self.obj.id})
        self.client.force_authenticate(user=self.obj)
        res = self.client.put(url)
        self.assertEqual(400,res.status_code)
        resJson = json.loads(res.content)
        self.assertTrue('groups parameter not provided' in resJson['detail'])

    def test_set_groups_bad_no_perms_cross_org(self):
        url = reverse(self.named_view_base+'-set-groups',kwargs={'pk':self.obj.id})
        groupPks = [x.id for x in self.o2u2.groups.all()]
        self.assertTrue(len(groupPks))
        self.client.force_authenticate(user=self.obj)
        res = self.client.put(url,data={'groups':groupPks})
        self.assertEqual(400,res.status_code)
        resJson = json.loads(res.content)
        self.assertTrue('Could not find' in resJson['detail'])

    def test_set_groups_bad_no_perms(self):
        self.assertTrue(self.obj.has_perm(make_perm(self.obj2,'change'),self.obj2))
        url = reverse(self.named_view_base+'-set-groups',kwargs={'pk':self.obj2.id})
        groupPks = [x.id for x in self.obj2.groups.all()]
        self.assertTrue(len(groupPks))
        self.client.force_authenticate(user=self.obj2)
        res = self.client.put(url,data={'groups':groupPks})
        self.assertEqual(403,res.status_code)
        resJson = json.loads(res.content)
        self.assertTrue('Access denied to change' in resJson['detail'])

    def test_set_groups_bad_some_not_found(self):
        url = reverse(self.named_view_base+'-set-groups',kwargs={'pk':self.obj.id})
        # all but the first
        groupPks = [x.id for x in self.obj.groups.all()[1:]]
        groupPks.append(888)
        self.client.force_authenticate(user=self.obj)
        res = self.client.put(url,data={'groups':groupPks})
        self.assertEqual(400,res.status_code)
        resJson = json.loads(res.content)
        self.assertTrue('Could not find requested number of groups' in resJson['detail'])