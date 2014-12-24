from django.test import TestCase
from ... import models

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from guardian.core import ObjectPermissionChecker

from ...utils import auth

class TestOrgSignals(TestCase):
    def setUp(self):
        self.o = models.Org(name='asdf')
        self.o.save()
        self.addCleanup(self.o.delete)

    def test_create_org_groups(self):
        grps = Group.objects.filter(name__startswith='org_{0}_'.format(self.o.id))
        self.assertEqual(2,len(grps))
        expected = set(['org_{0}_users'.format(self.o.id),'org_{0}_administrators'.format(self.o.id)])
        for i in grps:
            self.assertTrue(i.name in expected)
            expected.remove(i.name)
        self.assertEqual(0,len(expected))

    def test_admins_control_groups(self):
        grps = Group.objects.filter(name__startswith='org_{0}_'.format(self.o.id))
        admins = Group.objects.get(name='org_{0}_administrators'.format(self.o.id))
        checker = ObjectPermissionChecker(admins)
        for grp in grps:
            self.assertTrue(checker.has_perm(auth.make_perm(grp,'change'), grp))

    def test_admins_global_create_perms(self):
        admins = Group.objects.get(name='org_{0}_administrators'.format(self.o.id))

        adminPermNames = ['{0}.{1}'.format(x.content_type.app_label,x.codename) for x in admins.permissions.all()]
        
        userCreatePerm = auth.make_global_perm(models.User,'add')
        self.assertTrue(userCreatePerm in adminPermNames)


class TestUserSignals(TestCase):
    def setUp(self):
        self.o = models.Org(name='asdf')
        self.o.save()
        self.addCleanup(self.o.delete)
        self.u = get_user_model()(username='adf8a7sdf98',org=self.o)
        self.u.save()
        self.addCleanup(self.u.delete)

    def test_first_user_is_admin_group(self):
        grps = self.u.groups.all()
        self.assertEqual(2,len(grps))
        expected = set(['org_{0}_users'.format(self.o.id),'org_{0}_administrators'.format(self.o.id)])
        for i in grps:
            self.assertTrue(i.name in expected)
            expected.remove(i.name)
        self.assertEqual(0,len(expected))

    def test_add_to_users_group(self):
        u = get_user_model()(username='adf',org=self.o)
        u.save()
        self.addCleanup(u.delete)
        grps = u.groups.all()
        self.assertEqual(1,len(grps))
        expected = set(['org_{0}_users'.format(self.o.id)])
        for i in grps:
            self.assertTrue(i.name in expected)
            expected.remove(i.name)
        self.assertEqual(0,len(expected))

    def test_assign_user_perms(self):
        User = get_user_model()
        u = get_user_model()(username='adf',org=self.o)
        u.save()
        self.addCleanup(u.delete)

        # via admins
        self.assertTrue(self.u.has_perm(auth.make_global_perm(User,'add')))
        self.assertTrue(self.u.has_perm(auth.make_global_perm(User,'delete')))
        self.assertTrue(self.u.has_perm(auth.make_global_perm(User,'change')))

        self.assertTrue(self.u.has_perm(auth.make_perm(u,'delete'),u))
        self.assertTrue(self.u.has_perm(auth.make_perm(u,'change'),u))

        # via users
        self.assertTrue(u.has_perm(auth.make_global_perm(User,'change')))

        # via self (u not self.u)
        self.assertTrue(u.has_perm(auth.make_perm(u,'change'),u))


        unrelated = get_user_model()(username='adf2',org=self.o)
        unrelated.save()
        self.addCleanup(unrelated.delete)
        self.assertFalse(unrelated.has_perm(auth.make_perm(u,'delete'),u))
        self.assertFalse(unrelated.has_perm(auth.make_perm(u,'change'),u))
        self.assertFalse(u.has_perm(auth.make_perm(unrelated,'delete'),unrelated))
        self.assertFalse(u.has_perm(auth.make_perm(unrelated,'change'),unrelated))

    def test_other_admins_no_perms(self):
        o2 = models.Org(name='org2')
        o2.save()
        u2 = get_user_model()(username='adf',org=o2)
        u2.save()
        self.addCleanup(u2.delete)
        self.addCleanup(o2.delete)

        self.assertFalse(u2.has_perm(auth.make_perm(self.u,'delete'),self.u))
        self.assertFalse(u2.has_perm(auth.make_perm(self.u,'change'),self.u))
        self.assertFalse(self.u.has_perm(auth.make_perm(u2,'delete'),u2))
        self.assertFalse(self.u.has_perm(auth.make_perm(u2,'change'),u2))