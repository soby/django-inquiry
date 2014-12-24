from django.test import TestCase
from django.contrib.auth import get_user_model

from ...auth import model
from ... import models

class ModelBackendTest(TestCase):
    def setUp(self):
        self.USERNAME = 'asdf@skdjf.com'
        self.PASSWORD = 'blahblahblah'
        self.org = models.Org(subdomain='asdf',name='stuff')
        self.org.save()
        self.user = get_user_model()(username=self.USERNAME,org=self.org)
        self.user.set_password(self.PASSWORD)
        self.user.is_active=True
        self.user.save()

    def test_authenticate(self):
        u = model.ModelBackend().authenticate(username=self.USERNAME,password=self.PASSWORD)
        self.assertEqual(self.user,u)
    
    def test_authenticate_bad_inactive(self):
        self.user.is_active=False
        self.user.save()
        u = model.ModelBackend().authenticate(username=self.USERNAME,password=self.PASSWORD)
        self.assertEqual(None,u)