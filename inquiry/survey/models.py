from uuid import uuid4

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
        
    def __unicode__(self):
        return '<{0}({1}):{2} {3}({4})>'.format(self.__class__.__name__, 
                    self.org_id, self.id, self.name, self.closed_state)
    def __str__(self):
        return self.__unicode__().encode('utf-8')


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
    
    def __unicode__(self):
        return '<{0}({1}):{2} {3}>'.format(self.__class__.__name__, 
                    self.org_id, self.id, self.name)
    def __str__(self):
        return self.__unicode__().encode('utf-8')

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
    
    def __unicode__(self):
        return '<{0}({1}):{2} {3}>'.format(self.__class__.__name__, 
                    self.org_id, self.id, self.name)
    def __str__(self):
        return self.__unicode__().encode('utf-8')

class SurveyObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(Survey, related_name='surveypermission')
    
    
class SurveyGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(Survey)

    
class Section(core_models.UserOwnedModel, OrderedModel):
    parent = models.ForeignKey(Survey)
    name = models.CharField(max_length=1024)
    description = models.TextField()

    def __unicode__(self):
        return '<{0}({1}):{2} {3}>'.format(self.__class__.__name__, 
                    self.org_id, self.id, self.parent.name)
    def __str__(self):
        return self.__unicode__().encode('utf-8')

class SectionOwnedModel(core_models.UserOwnedModel):
    parent = models.ForeignKey(Survey)
    section = models.ForeignKey(Section)
    
    objects = models.Manager()
    manager = ParentOwnedPermissionQuerySet.as_manager()
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return '<{0}({1}):{2} {3}>'.format(self.__class__.__name__, 
                    self.org_id, self.id, self.section.name)
    def __str__(self):
        return self.__unicode__().encode('utf-8')


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
    
    STATUS_ACTIVE='active'
    STATUS_DEPRECATED='deprecated'
    STATUSES = (
        [STATUS_ACTIVE,_('Active')],
        [STATUS_DEPRECATED,_('Deprecated')],
    )
    
    question = models.TextField()
    question_type = models.CharField(max_length=1024, choices=QUESTION_TYPES)
    
    status = models.CharField(max_length=256,choices=STATUSES, 
                              default=STATUS_ACTIVE)
    version = models.IntegerField(default=1)
    identifier = models.CharField(max_length=1024, null=True, blank=True)
    
    def save(self,*args,**kwargs):
        if not self.pk:
            self.identifier = uuid4().hex
        
        # TODO: check for references from QuestionResponse and refuse 
        # to save. Force clone_and_replace instead
        return super(Question, self).save(*args,**kwargs)
    
    def clone_and_replace(self):
        """
            In order to support versioning, changes are not allowed to 
            Questions that have been answered. 
             
        """
        self.status = self.STATUS_DEPRECATED
        self.save()
        return Question.objects.create(question=self.question,
                                       question_type=self.question_type,
                                       parent=self.parent,
                                       section=self.section,
                                       version=(self.version+1),
                                       identifier=self.identifier,
                                       owner=self.owner,
                                       created_by=self.created_by
                                      )
        

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
    
    due_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        # add view permission
        default_permissions = ('add', 'change', 'delete', 'view')
        
    def __unicode__(self):
        return '<{0}({1}):{2} {3}>'.format(self.__class__.__name__, 
                    self.org_id, self.id, self.survey.name)
    def __str__(self):
        return self.__unicode__().encode('utf-8')
    
    @classmethod
    def create_from_survey(cls, survey, user, owner=None, created_by=None, 
                           status=None, due_date=None):
        """
            Generate an open response, sections, and questions from a survey
        """
        status = status or survey.survey_type.initial_status
        owner = owner or user
        created_by = created_by or owner
        kwargs = {'survey': survey, 'status': status, 'owner': owner,
                  'user': user, 'created_by': created_by, 
                  'status': status, 'due_date': due_date, 
                  'org_id': owner.org_id}
        resp = Response.objects.create(**kwargs)
        for section in survey.section_set.all():
            sec = ResponseSection.create_from_section(section,
                                                survey=survey,
                                                response=resp,
                                                owner=owner,
                                                created_by=created_by
                                                )
            for question in survey.question_set.all():
                QuestionResponse.create_from_question(
                                        question,
                                        section=sec, 
                                        survey=survey,
                                        response=resp,
                                        owner=owner,
                                        created_by=created_by
                                        )
        return resp 



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
        
    def __unicode__(self):
        return '<{0}({1}):{2} {3}>'.format(self.__class__.__name__, 
                    self.org_id, self.id, self.survey.name)
    def __str__(self):
        return self.__unicode__().encode('utf-8')


class ResponseSection(ResponseOwnedModel):
    survey_section = models.ForeignKey(Section)
    
    @classmethod
    def create_from_section(cls, survey_section, survey, response, owner, 
                            created_by=None):
        created_by = created_by or owner
        return ResponseSection.objects.create(survey_section=survey_section,
                                              survey=survey,
                                              response=response, 
                                              owner=owner,
                                              created_by=created_by,
                                              org_id=owner.org_id
                                              )


class ResponseSectionOwnedModel(ResponseOwnedModel):
    section = models.ForeignKey(ResponseSection)
    
    class Meta:
        abstract = True
    
    
class QuestionResponse(ResponseSectionOwnedModel):
    question = models.ForeignKey(Question)
    answer = models.TextField()
    
    @classmethod
    def create_from_question(cls, question, section, survey, response, 
                             owner, created_by=None):
        created_by = created_by or owner
        return QuestionResponse.objects.create(question=question, 
                                               section=section,
                                               survey=survey, 
                                               response=response, 
                                               owner=owner, 
                                               created_by=created_by,
                                               org_id=owner.org_id
                                               )


class QuestionResponseResource(ResourceMixin, ResponseSectionOwnedModel):
    question_response = models.ForeignKey(QuestionResponse)
