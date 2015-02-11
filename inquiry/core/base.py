from django.db import models
from django.conf import settings
from . import querysets

class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
            abstract = True

class OrgOwnedModel(BaseModel):
    org = models.ForeignKey(settings.AUTH_ORG_MODEL)
    
    class Meta:
        abstract = True

class UserOwnedModel(OrgOwnedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                              related_name='%(app_label)s_%(class)s_owner_set')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                        blank=True,
                        related_name='%(app_label)s_%(class)s_created_by_set')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    null=True,blank=True,
                        related_name='%(app_label)s_%(class)s_modified_by_set')
    
    objects = models.Manager()
    manager = querysets.UserOwnerQuerySet.as_manager()
    
    class Meta:
        abstract = True