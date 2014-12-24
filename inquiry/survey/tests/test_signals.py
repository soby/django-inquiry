from django.test import TestCase
from django.apps import apps
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from ...core.utils.auth import group_for_org, make_global_perm
from ...core.utils.auth import get_org_model
from ..models import Status

class TestOrgSignals(TestCase):
    def test_create_default_survey_statuses(self):
        o = get_org_model()(name='blah', subdomain='stuff')
        o.save()
        statuses = Status.objects.all()
        self.assertEqual(['open', 'closed'],
                         [x.name for x in statuses])
    
    def test_basic_crud_permissions(self):
        o = get_org_model()(name='blah', subdomain='stuff')
        o.save()
        # first user is an admin
        adminu = get_user_model()(username='blah',org=o)
        adminu.save()
        useru = get_user_model()(username='blah2',org=o)
        useru.save()
        config = apps.get_app_config('survey')
        
        for model in config.get_models():
            self.assertTrue(adminu.has_perm(
                                    make_global_perm(model, 'add')))
            self.assertTrue(adminu.has_perm(
                                    make_global_perm(model, 'change')))
            self.assertTrue(adminu.has_perm(
                                    make_global_perm(model, 'delete')))
        
        for model in config.get_models():
            if model == Status:
                continue
            
            self.assertTrue(useru.has_perm(
                                    make_global_perm(model, 'add')))
            self.assertTrue(useru.has_perm(
                                    make_global_perm(model, 'change')))
            self.assertTrue(useru.has_perm(
                                    make_global_perm(model, 'delete')))
            
            
        