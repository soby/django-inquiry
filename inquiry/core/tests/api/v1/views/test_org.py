import json

from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from .....utils.test.objects import remove_fields
from django.core.urlresolvers import reverse

from . import base
from .....api.v1.views import org
from ..... import models


class OrgViewSetTest(base.ViewSetBaseTestMixin,APITestCase):
    named_view_base = 'api/core/v1/org'
    namespace = None
    viewset = org.OrgViewSet

    def setUp(self):
        self.obj = models.Org(name='blah',subdomain='blah')
        self.obj.save()
        self.u1 = get_user_model()(username='user1',org=self.obj)
        self.u1.save()
        self.u2 = get_user_model()(username='user2',org=self.obj)
        self.u2.save()

        self.addCleanup(self.obj.delete)
        self.addCleanup(self.u1.delete)
        self.addCleanup(self.u2.delete)

        self.org2 = models.Org(name='blah2',subdomain='blah2')
        self.org2.save()
        self.o2u1 = get_user_model()(username='o2u1',org=self.org2)
        self.o2u1.save()
        self.o2u2 = get_user_model()(username='o2u2',org=self.org2)
        self.o2u2.save()

        self.addCleanup(self.org2.delete)
        self.addCleanup(self.o2u1.delete)
        self.addCleanup(self.o2u2.delete)

    def test_my(self):
        self.client.force_authenticate(user=self.u1)
        url = reverse(self.named_view_base+'-my',current_app=self.namespace)
        res = self.client.get(url)
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        self.assertEqual(resJson['id'],self.obj.id)

    def test_my_regular_user(self):
        self.client.force_authenticate(user=self.u2)
        url = reverse(self.named_view_base+'-my',current_app=self.namespace)
        res = self.client.get(url)
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        self.assertEqual(resJson['id'],self.obj.id)

    def test_detail(self):
        self.client.force_authenticate(user=self.u1)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':self.obj.id},current_app=self.namespace)
        res = self.client.get(url)
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        self.assertEqual(resJson['id'],self.obj.id)

    def test_detail_regular_user(self):
        self.client.force_authenticate(user=self.u2)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':self.obj.id},current_app=self.namespace)
        res = self.client.get(url)
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        self.assertEqual(resJson['id'],self.obj.id)

    def test_detail_bad_cross_org(self):
        self.client.force_authenticate(user=self.u1)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':self.org2.id},current_app=self.namespace)
        res = self.client.get(url)
        self.assertEqual(404,res.status_code)

    def test_list(self):
        self.client.force_authenticate(user=self.u1)
        url = reverse(self.named_view_base+'-list',current_app=self.namespace)
        res = self.client.get(url)
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        self.assertEqual([{u'preference_auth_google_oauth2': False, u'subdomain': u'blah', u'name': u'blah'}],remove_fields(['id'],resJson))

    def test_partial_update_bad(self):
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':self.obj.id},current_app=self.namespace)
        self.client.force_authenticate(user=self.u1)
        res = self.client.patch(url,data={'name':'blahblah'})
        self.assertEqual(403,res.status_code)
        org = models.Org.objects.get(pk=self.obj.id)
        self.assertEqual(self.obj.name,org.name)