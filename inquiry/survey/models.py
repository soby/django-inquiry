from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ordered_model.models import OrderedModel
from ..core import models as core_models

from guardian.models import UserObjectPermissionBase
from guardian.models import GroupObjectPermissionBase
from guardian.shortcuts import get_objects_for_user

from inquiry.core.utils.auth import make_perm

import logging
LOGGER = logging.getLogger(__name__)

RESOURCE_TYPE_FILE = 'file'
RESOURCE_TYPE_IMAGE = 'image'
RESOURCE_TYPE_FLASH = 'flash'
RESOURCE_TYPE_MOVIE = 'movie'
RESOURCE_TYPE_CHOICES = (
    [RESOURCE_TYPE_FILE,_('File')],
    [RESOURCE_TYPE_IMAGE,_('Image')],
    [RESOURCE_TYPE_FLASH,_('Flash Movie')],
    [RESOURCE_TYPE_MOVIE,_('Movie')],
)


class ParentOwnedPermissionQuerySet(models.QuerySet):
    """
        Returns of queryset based on which parent objects referenced by
        the "parent" foreign key the user has an explicit view perm
    """
    parent_key = 'parent'
    
    def for_admin(self,user):
        return self.filter(id=user.org_id)
    
    def for_user(self,user):
        cls = self.model._meta.get_field(self.parent_key).rel.to
        qs = get_objects_for_user(user,make_perm(cls,'view'),klass=cls)
        ids = qs.values_list('id', flat=True)
        return self.filter(**{'{0}__in'.format(self.parent_key):ids})
  
    
class ResourceMixin(models.Model):
    name = models.CharField(max_length=1024, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    resource = models.FileField()
    resource_type = models.CharField(max_length=1024,
                                     choices=RESOURCE_TYPE_CHOICES)
    content_type = models.CharField(max_length=1024, null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)
    
    class Meta:
        abstract = True

class Status(core_models.UserOwnedModel):
    name = models.CharField(max_length=1024)
    label = models.CharField(max_length=1024, null=True, blank=True)
    help_text = models.CharField(max_length=1024, null=True, blank=True)
    closed_state = models.BooleanField(default=False,
                                       help_text=_('This is a final state'))
    
    objects = models.Manager()
    manager = core_models.SameOrgQuerySet.as_manager()
    
    class Meta:
        unique_together = [ ('name', 'org'), ]


class StatusObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(Status,
                                       related_name='statuspermission')
    
    
class StatusGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(Status)
    
    
class Type(core_models.UserOwnedModel):
    name = models.CharField(max_length=1024)
    statuses = models.ManyToManyField(Status)
    initial_status = models.ForeignKey(Status,
                                    related_name='surveytype_initial_statuses')

    objects = models.Manager()
    manager = core_models.SameOrgQuerySet.as_manager()

class TypeObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(Type,
                                       related_name='typepermission')
    
    
class TypeGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(Type)
    
    
class Survey(core_models.UserOwnedModel):
    name = models.CharField(max_length=1024)
    description = models.TextField()
    survey_type = models.ForeignKey(Type)
    
    class Meta:
        # add view permission
        default_permissions = ('add', 'change', 'delete', 'view')

class SurveyObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(Survey, related_name='surveypermission')
    
    
class SurveyGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(Survey)

    
class Section(core_models.UserOwnedModel, OrderedModel):
    parent = models.ForeignKey(Survey)
    name = models.CharField(max_length=1024)
    description = models.TextField()


class SectionOwnedModel(core_models.UserOwnedModel):
    parent = models.ForeignKey(Survey)
    section = models.ForeignKey(Section)
    
    objects = models.Manager()
    manager = ParentOwnedPermissionQuerySet.as_manager()
    
    class Meta:
        abstract = True


class Resource(ResourceMixin, SectionOwnedModel):
    pass


class Question(SectionOwnedModel,OrderedModel):
    TYPE_BOOLEAN = 'boolean'
    TYPE_CHOICE = 'choice'
    TYPE_MULTICHOICE = 'multiple choice'
    TYPE_TEXT = 'text'
    TYPE_TEXTAREA = 'textarea'
    TYPE_FILE = 'file'
    
    QUESTION_TYPES = (
        [TYPE_BOOLEAN,_('Boolean')],
        [TYPE_CHOICE,_('Choice')],
        [TYPE_MULTICHOICE,_('Multiple Choice')],
        [TYPE_TEXT,_('Text')],
        [TYPE_TEXTAREA,_('Text Area')],
        [TYPE_FILE,_('File')],
        
    )
    
    question = models.TextField()
    question_type = models.CharField(max_length=1024, choices=QUESTION_TYPES)


class QuestionChoice(SectionOwnedModel, OrderedModel):
    question = models.ForeignKey(Question)
    
    name = models.CharField(max_length=1024)
    value = models.CharField(max_length=1024)
    help_text = models.CharField(max_length=1024, null=True, blank=True)


class QuestionResource(ResourceMixin,SectionOwnedModel):
    question = models.ForeignKey(Question)


class Response(core_models.UserOwnedModel):
    survey = models.ForeignKey(Survey)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    
    passed = models.NullBooleanField(blank=True)
    score = models.IntegerField(null=True, blank=True)
    status = models.ForeignKey(Status)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        # add view permission
        default_permissions = ('add', 'change', 'delete', 'view')


class SRObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(Response,
                                       related_name='responsepermission')


class SRGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(Response)


class ResponseOwnedPermissionQuerySet(ParentOwnedPermissionQuerySet):
    # Similar to parent but uses a different key
    parent_key = 'response'
    
    
class ResponseOwnedModel(core_models.UserOwnedModel):
    survey   = models.ForeignKey(Survey)
    response = models.ForeignKey(Response)
    
    objects = models.Manager()
    manager = ResponseOwnedPermissionQuerySet.as_manager()
    
    class Meta:
        abstract = True


class ResponseSection(ResponseOwnedModel):
    survey_section = models.ForeignKey(Section)


class ResponseSectionOwnedModel(ResponseOwnedModel):
    section = models.ForeignKey(ResponseSection)
    
    class Meta:
        abstract = True
    
    
class QuestionResponse(ResponseSectionOwnedModel):
    question = models.ForeignKey(Question)
    answer = models.TextField()


class QuestionResponseResource(ResourceMixin, ResponseSectionOwnedModel):
    question_response = models.ForeignKey(QuestionResponse)
