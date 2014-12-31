from django.db import models
from django.contrib.auth.models import AbstractBaseUser, Group, PermissionsMixin
from django.contrib.auth.models import UserManager as auth_usermanager
from django.utils.translation import ugettext_lazy as _
from django.core import validators
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

from guardian.models import UserObjectPermissionBase
from guardian.models import GroupObjectPermissionBase

import logging
LOGGER = logging.getLogger(__name__)

class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
            abstract = True
        
class OrgQuerySet(models.QuerySet):
    def for_user(self,user):
        return self.filter(id=user.org_id)
    def for_admin(self,user):
        return self.filter(id=user.org_id)
    
class Org(BaseModel):
    name = models.CharField(max_length=512)
    subdomain = models.CharField(max_length=256,null=True,blank=True,unique=True)

    ##### Preferences
    ## Auth
    preference_auth_google_oauth2 = models.BooleanField(default=False,help_text="Allow Google OAuth2 login")
    preference_auth_email_autocreate_domains = models.CharField(
                                                max_length=2048,
                                                null=True,
                                                blank=True)


    objects = models.Manager()
    manager = OrgQuerySet.as_manager()

    def __str__(self):
        return self.__unicode__().encode('utf-8')
    def __unicode__(self):
        return u'%s (%s)' % (self.name,self.subdomain)

# We use these so django-guardian doesn't use generic foreign keys
class OrgUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(settings.AUTH_ORG_MODEL)
class OrgGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(settings.AUTH_ORG_MODEL)

class OrgOwnedModel(BaseModel):
    org = models.ForeignKey(settings.AUTH_ORG_MODEL)
    
    class Meta:
        abstract = True
    
class SameOrgQuerySet(models.QuerySet):
    def for_user(self,user):
        return self.filter(org_id=user.org_id)
    def for_admin(self,user):
        return self.filter(org_id=user.org_id)
    
class User(AbstractBaseUser,PermissionsMixin, OrgOwnedModel):
    username = models.CharField(_('username'), max_length=128, unique=True,
        help_text=_('Required. 100 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$',
                                      _('Enter a valid username. '
                                        'This value may contain only letters, numbers '
                                        'and @/./+/-/_ characters.'), 'invalid'),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        })

    phone = models.CharField(max_length=64,null=True,blank=True)
    # This is business unit, not django groups
    group = models.CharField(max_length=128,null=True,blank=True)
    title = models.CharField(max_length=128,null=True,blank=True)

    first_name = models.CharField(_('first name'), max_length=128, blank=True)
    last_name = models.CharField(_('last name'), max_length=128, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.NullBooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = auth_usermanager()
    manager = SameOrgQuerySet.as_manager()

    """ This is all copied from django's BaseUser. We have to do it to extend
        the length of the username field
    """
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def save(self,*args,**kwargs):
        if self.first_name is None:
            self.first_name = ''
        if self.last_name is None:
            self.last_name = ''
            
        if self.username:
            self.username = self.username.lower()
        return super(User,self).save(*args,**kwargs)


class UserUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(settings.AUTH_USER_MODEL,
                                       related_name='userpermission')
class UserGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(settings.AUTH_USER_MODEL)

class UserOwnerQuerySet(models.QuerySet):
    def for_user(self,user):
        return self.filter(owner_id=user.pk)
    def for_admin(self,user):
        return self.filter(org_id=user.org_id)
    
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
    manager = UserOwnerQuerySet.as_manager()
    
    class Meta:
        abstract = True
        
class GroupQuerySet(models.QuerySet):
    def for_user(self,user):
        return self.filter(name__startswith='org_{0}_'.format(user.org_id))

# Dirty monkey patch
Group.add_to_class('manager',GroupQuerySet.as_manager()) #@UndefinedVariable
    



