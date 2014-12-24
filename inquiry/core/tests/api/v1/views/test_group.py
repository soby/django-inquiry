import json

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework.test import APITestCase

from ..... import models
from .....api.v1.views import user

from . import base
from .....utils.test.objects import remove_fields, compare_dict_lists

class GroupViewSetTest(base.ViewSetBaseTestMixin,APITestCase):
    named_view_base = 'api/core/v1/group'
    namespace = None
    viewset = user.GroupViewSet

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
        self.addCleanup(self.o2.delete)
        self.uninvolved = get_user_model()(username='uninvolved',org=self.o2)
        self.uninvolved.save()
        self.addCleanup(self.uninvolved.delete)

    def _add_user_to(self,grpName):
        grp = Group.objects.get(name=grpName)
        self.assertFalse(grp.user_set.filter(pk=self.obj2.pk).exists())
        url = reverse(self.named_view_base+'-add-user',kwargs={'pk':grp.id},current_app=self.namespace)
        self.client.force_authenticate(user=self.obj)
        res = self.client.patch(url,data={'userId':self.obj2.pk})
        self.assertEqual(200,res.status_code)
        self.assertTrue('added' in res.content)
        self.assertTrue(grp.user_set.filter(pk=self.obj2.pk).exists())
        
    def test_create(self):
        # TODO: Test
        pass

    def test_delete(self):
        # TODO: Test
        pass
    
    def test_add_user_to_admins(self):
        grpName = 'org_{0}_administrators'.format(self.o.id)
        self._add_user_to(grpName)

    def test_add_user_to_admin_bad_not_allowed(self):
        grpName = 'org_{0}_administrators'.format(self.o.id)
        grp = Group.objects.get(name=grpName)
        self.assertFalse(grp.user_set.filter(pk=self.obj2.pk).exists())
        url = reverse(self.named_view_base+'-add-user',kwargs={'pk':grp.id},current_app=self.namespace)
        self.client.force_authenticate(user=self.obj2)
        res = self.client.patch(url,data={'userId':self.obj2.pk})
        self.assertEqual(403,res.status_code)
        self.assertFalse(grp.user_set.filter(pk=self.obj2.pk).exists())

    def test_add_user_to_admin_cross_org_user_added(self):
        grpName = 'org_{0}_administrators'.format(self.o.id)
        grp = Group.objects.get(name=grpName)
        self.assertFalse(grp.user_set.filter(pk=self.obj2.pk).exists())
        url = reverse(self.named_view_base+'-add-user',kwargs={'pk':grp.id},current_app=self.namespace)
        self.client.force_authenticate(user=self.obj)
        res = self.client.patch(url,data={'userId':self.uninvolved.pk})
        self.assertEqual(400,res.status_code)
        self.assertFalse(grp.user_set.filter(pk=self.uninvolved.pk).exists())

    def test_detail(self):
        grpName = 'org_{0}_administrators'.format(self.o.id)
        grp = Group.objects.get(name=grpName)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':grp.id},current_app=self.namespace)
        self.client.force_authenticate(user=self.obj2)
        res = self.client.get(url)
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        self.assertEqual({"name": "administrators", "user_set": [self.obj.id]},remove_fields(['id'],resJson))

    def test_detail_bad_cross_org(self):
        grpName = 'org_{0}_administrators'.format(self.o2.id)
        grp = Group.objects.get(name=grpName)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':grp.id},current_app=self.namespace)
        self.client.force_authenticate(user=self.obj)
        res = self.client.get(url)
        self.assertEqual(404,res.status_code)


    def test_list(self):
        url = reverse(self.named_view_base+'-list',current_app=self.namespace)
        self.client.force_authenticate(user=self.obj2)
        res = self.client.get(url)
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        self.assertEqual(([],[]),compare_dict_lists([{"name": "users", "user_set": [1, 2]}, {"name": "administrators", "user_set": [1]}],remove_fields(['id'],resJson)))
        
    def test_partial_update(self):
        # The only thing we can update is the user_set

        grpName = 'org_{0}_administrators'.format(self.o.id)
        grp = Group.objects.get(name=grpName)
        self.assertEqual([self.obj.pk],[x.pk for x in grp.user_set.all()])
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':grp.id},current_app=self.namespace)
        self.client.force_authenticate(user=self.obj)
        res = self.client.patch(url,data={'name':'blahblah','user_set':[self.obj2.pk]})
        self.assertEqual(200,res.status_code)
        grp2 = Group.objects.get(pk=grp.pk)
        self.assertEqual(grp.name,grp2.name)
        self.assertEqual([self.obj2.pk],[x.pk for x in grp2.user_set.all()])

    def test_partial_update_bad_regular_user_unauthorized(self):

        grpName = 'org_{0}_administrators'.format(self.o.id)
        grp = Group.objects.get(name=grpName)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':grp.id},current_app=self.namespace)
        self.client.force_authenticate(user=self.obj2)
        res = self.client.patch(url,data={'name':'blahblah','user_set':[self.obj2.pk]})
        self.assertEqual(403,res.status_code)

    def test_partial_update_bad_cross_org(self):
        
        grpName = 'org_{0}_administrators'.format(self.o2.id)
        grp = Group.objects.get(name=grpName)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':grp.id},current_app=self.namespace)
        self.client.force_authenticate(user=self.obj)
        res = self.client.patch(url,data={'name':'blahblah','user_set':[self.obj2.pk]})
        self.assertEqual(404,res.status_code)

    def test_partial_update_bad_cross_org_user_added(self):
        
        grpName = 'org_{0}_administrators'.format(self.o.id)
        grp = Group.objects.get(name=grpName)
        self.assertEqual(1,grp.user_set.all().count())
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':grp.id},current_app=self.namespace)
        self.client.force_authenticate(user=self.obj)
        res = self.client.patch(url,data={'name':'blahblah','user_set':[self.uninvolved.pk]})
        grp2 = Group.objects.get(pk=grp.pk)
        self.assertEqual(1,grp2.user_set.all().count())
        self.assertEqual(400,res.status_code)

    def test_update(self):
        # The only thing we can update is the user_set

        grpName = 'org_{0}_administrators'.format(self.o.id)
        grp = Group.objects.get(name=grpName)
        self.assertEqual(1,grp.user_set.all().count())
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':grp.id},current_app=self.namespace)
        self.client.force_authenticate(user=self.obj)
        res = self.client.patch(url,data={'name':'blahblah','user_set':[self.obj2.pk]})
        self.assertEqual(200,res.status_code)
        grp2 = Group.objects.get(pk=grp.pk)
        self.assertEqual(grp.name,grp2.name)
        self.assertEqual([self.obj2.pk],[x.pk for x in grp2.user_set.all()])

    def test_update_bad_regular_user_unauthorized(self):
        # There isn't really anything on group that we can update so we're testing that we can't update

        grpName = 'org_{0}_administrators'.format(self.o.id)
        grp = Group.objects.get(name=grpName)
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':grp.id},current_app=self.namespace)
        self.client.force_authenticate(user=self.obj2)
        res = self.client.put(url,data={'name':'blahblah','user_set':[self.obj2.pk]})
        self.assertEqual(403,res.status_code)