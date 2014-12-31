import logging
LOGGER = logging.getLogger(__name__)

from django.contrib.auth import get_user_model

from .....core.api.v1.serializers.base import (
    BaseModelSerializer, FieldRestrictingMixin,
    USER_OWNED_READ_ONLY_FIELDS, USER_OWNED_QUERYSET_RESTRICTIONS)
from .....core.api.v1.serializers.user import UserSerializer

from . import base
from .... import models

class SectionOwnedMixin(object):
    def validate(self,data):
        super(SectionOwnedMixin, self).validate(data)
        if data.has_key('section'):
            if not data.get('parent'):
                data['parent'] = data.get('section').parent
        return data

class ResponseOwnedMixin(object):
    def validate(self,data):
        super(ResponseOwnedMixin, self).validate(data)
        if data.has_key('response'):
            if not data.get('survey'):
                data['survey'] = data.get('response').survey
        return data
    
class StatusSerializer(FieldRestrictingMixin, BaseModelSerializer):
    _QUERYSET_RESTRICTIONS = USER_OWNED_QUERYSET_RESTRICTIONS
    
    class Meta:
        model = models.Status
        fields = USER_OWNED_READ_ONLY_FIELDS + ['name','label','help_text',
                                                'closed_state']
        read_only_fields = USER_OWNED_READ_ONLY_FIELDS


class TypeSerializer(FieldRestrictingMixin, BaseModelSerializer):
    _QUERYSET_RESTRICTIONS = USER_OWNED_QUERYSET_RESTRICTIONS
    
    class Meta:
        model = models.Type
        fields = USER_OWNED_READ_ONLY_FIELDS + ['name','statuses',
                                                'initial_status']
        read_only_fields = USER_OWNED_READ_ONLY_FIELDS


class SurveySerializer(FieldRestrictingMixin, BaseModelSerializer):
    _QUERYSET_RESTRICTIONS = dict(USER_OWNED_QUERYSET_RESTRICTIONS,
                                  survey_type=models.Type)
    
    class Meta:
        model = models.Survey
        fields = USER_OWNED_READ_ONLY_FIELDS + ['name','description',
                                                'survey_type']
        read_only_fields = USER_OWNED_READ_ONLY_FIELDS
        create_only_fields = ['survey_type', ]
        
class SectionSerializer(FieldRestrictingMixin, BaseModelSerializer):
    _QUERYSET_RESTRICTIONS = dict(USER_OWNED_QUERYSET_RESTRICTIONS,
                                  parent=models.Survey)
    
    class Meta:
        model = models.Section
        fields = USER_OWNED_READ_ONLY_FIELDS + ['name','description',
                                                'parent','order']
        read_only_fields = USER_OWNED_READ_ONLY_FIELDS+['order']


class ResourceSerializer(SectionOwnedMixin, FieldRestrictingMixin, BaseModelSerializer):
    _QUERYSET_RESTRICTIONS = base.SECTION_OWNED_QUERYSET_RESTRICTIONS
    
    class Meta:
        model = models.Resource
        fields = base.SECTION_OWNED_READ_ONLY_FIELDS +\
            ['name', 'description', 'section', 'resource', 'resource_type',
             'content_type','size']
        read_only_fields = base.SECTION_OWNED_READ_ONLY_FIELDS+\
            ['parent', 'content_type', 'size']


class QuestionSerializer(SectionOwnedMixin, FieldRestrictingMixin, BaseModelSerializer):
    _QUERYSET_RESTRICTIONS = base.SECTION_OWNED_QUERYSET_RESTRICTIONS
    
    class Meta:
        model = models.Question
        fields = base.SECTION_OWNED_READ_ONLY_FIELDS +\
            ['section', 'question','question_type','order']
        read_only_fields = base.SECTION_OWNED_READ_ONLY_FIELDS+\
            ['order']
   

class QuestionChoiceSerializer(SectionOwnedMixin, FieldRestrictingMixin, 
                                     BaseModelSerializer):
    _QUERYSET_RESTRICTIONS =\
        dict(base.SECTION_OWNED_QUERYSET_RESTRICTIONS,
             question=models.Question)
    
    def validate(self,data):
        if data.has_key('question'):
            if not data.get('section'):
                data['section'] = data.get('question').section
        super(QuestionChoiceSerializer, self).validate(data)
        return data
    
    class Meta:
        model = models.QuestionChoice
        fields = base.SECTION_OWNED_READ_ONLY_FIELDS +\
            ['section', 'question', 'name', 'value', 'help_text', 'order']
        read_only_fields = base.SECTION_OWNED_READ_ONLY_FIELDS+\
            ['section', 'order']
            

class QuestionResourceSerializer(SectionOwnedMixin, FieldRestrictingMixin, 
                                       BaseModelSerializer):
    _QUERYSET_RESTRICTIONS =\
        dict(base.SECTION_OWNED_QUERYSET_RESTRICTIONS,
             question=models.Question)
    
    def validate(self,data):
        if data.has_key('question'):
            if not data.get('section'):
                data['section'] = data.get('question').section
        super(QuestionResourceSerializer, self).validate(data)
        return data
    
    class Meta:
        model = models.QuestionResource
        fields = base.SECTION_OWNED_READ_ONLY_FIELDS +\
            ['section', 'name', 'description', 'resource', 'resource_type',
             'content_type', 'size', 'question']
        read_only_fields = base.SECTION_OWNED_READ_ONLY_FIELDS+\
            ['section', 'content_type',' size']


class ResponseSerializer(FieldRestrictingMixin, BaseModelSerializer):
    _QUERYSET_RESTRICTIONS =\
        dict(USER_OWNED_QUERYSET_RESTRICTIONS,
             survey=models.Survey, user=get_user_model())
    
    class Meta:
        model = models.Response
        fields = USER_OWNED_READ_ONLY_FIELDS +\
            ['survey', 'user', 'passed', 'score', 'status', 'completed_date',
             'due_date']
        read_only_fields = USER_OWNED_READ_ONLY_FIELDS +\
           ['passed', 'score', 'completed_date', 'due_date']
            

class ResponseSectionSerializer(ResponseOwnedMixin, FieldRestrictingMixin, 
                                      BaseModelSerializer):
    _QUERYSET_RESTRICTIONS =\
        dict(base.RESPONSE_OWNED_QUERYSET_RESTRICTIONS,
             survey_section=models.Section)
    
    def validate(self,data):
        if data.has_key('response'):
            if not data.get('survey'):
                data['survey'] = data.get('response').survey
        super(ResponseSectionSerializer, self).validate(data)
        return data
    
    class Meta:
        model = models.ResponseSection
        fields = base.RESPONSE_OWNED_READ_ONLY_FIELDS +\
            ['response', 'survey_section']
        read_only_fields = base.RESPONSE_OWNED_READ_ONLY_FIELDS


class QuestionResponseSerializer(ResponseOwnedMixin, FieldRestrictingMixin, 
                                      BaseModelSerializer):
    _QUERYSET_RESTRICTIONS =\
        dict(base.RESPONSE_SECTION_OWNED_QUERYSET_RESTRICTIONS,
             question=models.Question)
    
    def validate(self,data):
        if data.has_key('section'):
            if not data.get('response'):
                data['response'] = data.get('section').response
        super(QuestionResponseSerializer, self).validate(data)
        return data
    
    class Meta:
        model = models.QuestionResponse
        fields = base.RESPONSE_SECTION_OWNED_READ_ONLY_FIELDS +\
            ['section', 'question', 'answer']
        read_only_fields =\
            base.RESPONSE_SECTION_OWNED_READ_ONLY_FIELDS +\
            []


class QuestionResponseResourceSerializer(ResponseOwnedMixin, 
                                         FieldRestrictingMixin, 
                                         BaseModelSerializer):
    _QUERYSET_RESTRICTIONS =\
        dict(base.RESPONSE_SECTION_OWNED_QUERYSET_RESTRICTIONS,
             question_response=models.QuestionResponse)
    
    def validate(self,data):
        if data.has_key('question_response'):
            if not data.get('section'):
                data['section'] = data.get('question_response').section
                data['response'] = data.get('question_response').response
        super(QuestionResponseResourceSerializer, self).validate(data)
        return data
    
    class Meta:
        model = models.QuestionResponseResource
        fields = base.RESPONSE_SECTION_OWNED_READ_ONLY_FIELDS +\
            ['section', 'question_response', 'name', 'description',
             'resource', 'resource_type', 'content_type', 'size']
        read_only_fields =\
            base.RESPONSE_SECTION_OWNED_READ_ONLY_FIELDS +\
                ['section', 'content_type', 'size']
