from django.test import TestCase
from ... import models

from ...utils import auth
class TestUtility(TestCase):
    def test_group_for_org(self):
        o = models.Org(name='asdf')
        o.save()
        self.addCleanup(o.delete)
        self.assertEqual('org_{0}_users'.format(o.pk),auth.group_for_org(o,'users'))

    def test_make_perm(self):
        o = models.Org(name='asdf')
        self.assertEqual('change_org',auth.make_perm(o,'change'))
        self.assertEqual('change_org',auth.make_perm(models.Org,'change'))

    def test_make_global_perm(self):
        o = models.Org(name='asdf')
        self.assertEqual('core.change_org',auth.make_global_perm(o,'change'))
        self.assertEqual('core.change_org',auth.make_global_perm(models.Org,'change'))