from django.db import models
from django.contrib.auth.models import Group

class OrgQuerySet(models.QuerySet):
    def for_user(self,user):
        return self.filter(id=user.org_id)
    def for_admin(self,user):
        return self.filter(id=user.org_id)

class SameOrgQuerySet(models.QuerySet):
    def for_user(self,user):
        return self.filter(org_id=user.org_id)
    def for_admin(self,user):
        return self.filter(org_id=user.org_id)

class UserOwnerQuerySet(models.QuerySet):
    def for_user(self,user):
        return self.filter(owner_id=user.pk)
    def for_admin(self,user):
        return self.filter(org_id=user.org_id)

class GroupQuerySet(models.QuerySet):
    def for_user(self,user):
        return self.filter(name__startswith='org_{0}_'.format(user.org_id))

# Dirty monkey patch
Group.add_to_class('manager',GroupQuerySet.as_manager()) #@UndefinedVariable