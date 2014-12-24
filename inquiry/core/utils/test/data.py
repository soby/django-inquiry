from django.conf import settings
from model_mommy import mommy
import random

class Creator(object):
    def make(self, *args, **kwargs):
        save = kwargs.pop('save')
        if save:
            return mommy.make(*args,**kwargs)
        else:
            return mommy.prepare(*args,**kwargs)
        
class OrgCreator(Creator):
    def create_orgs(self, count, save=True):
        return self.make(settings.AUTH_ORG_MODEL,
                          _quantity=count,
                          _fill_optional=bool(random.getrandbits(1)),
                          save=save
                          )
        

class UserCreator(Creator):
    def create_users_for_orgs(self, orgs, count, save=True):
        res = {}
        for org in orgs:
            res[org] = self.make(settings.AUTH_USER_MODEL,
                                  org=org,
                                  is_active=True,
                                  is_staff=False,
                                  is_superuser=False,
                                  _quantity=count,
                                  _fill_optional=bool(random.getrandbits(1)),
                                  save=save
                                  )
        return res
        
    def create_users_and_orgs(self, orgCount, usersPerOrg, save=True):
        orgs = OrgCreator().create_orgs(orgCount, save=save)
        return self.create_users_for_orgs(orgs, usersPerOrg, save=save)
    
    