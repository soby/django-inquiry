import json

from rest_framework.viewsets import ModelViewSet
from django_filters import MethodFilter
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework.decorators import detail_route
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission

from .....core.api.v1.views import base
from .....core.utils.auth import make_perm, make_global_perm
from .....core.utils import filters
from .....core.auth import permissions

from ..serializers import survey
from ....authz import permissions as survey_permissions
from .... import models


class StatusViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.StatusSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    

class TypeViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.TypeSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()


class SurveyFilter(filters.BaseFilterSet):
    no_responses_for = MethodFilter(action='exclude_response_user')

    class Meta:
        model = survey.SurveySerializer.Meta.model
        fields = ['no_responses_for', 'name', 'description', 'survey_type',
                  'owner']

    def exclude_response_user(self, queryset, value):
        return queryset.exclude(response__user_id=value)


class SurveyLauchPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm(
                make_global_perm(models.Response, 
                                 'add'))
    
    def has_object_permission(self, request, view, obj):
        return request.user.has_perm(make_perm(obj,'view'), obj)

            
class SurveyViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.SurveySerializer
    filter_class = SurveyFilter
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    
    @detail_route(methods=['post'],permission_classes=[SurveyLauchPermission,])
    def launch(self, request, pk=None):
        # given the current password, change it
        srvy = self.get_object()
        userPk = request.data.get('user')
        if not userPk:
            raise serializers.ValidationError(
                                    detail={'user': 'This field is required'})
        user = get_user_model().manager.for_user(request.user).get(pk=userPk)
        # Since they're assigning a Response to a user, we check change_user
        if not request.user.has_perm(make_perm(user,'change'),user):
            return Response(status=status.HTTP_403_FORBIDDEN,
                        data={'detail':'Access denied to modify target user'})
        
        if srvy.response_set.filter(user=user, status__closed_state=False):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'detail':'Target user already has an open'
                                       'response for this survey'})
        resp = models.Response.create_from_survey(srvy, user, owner=user,
                                                  created_by=request.user)
        return Response(survey.ResponseSerializer(resp).data) 
        
        
class SectionFilter(filters.BaseFilterSet):
    class Meta:
        model = survey.SectionSerializer.Meta.model
        fields = ['pk__in', 'parent', 'name', 'owner']

    
class SectionViewSet(base.BaseAPIViewMixin, base.OrderableViewMixin, ModelViewSet):
    serializer_class = survey.SectionSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    permission_classes = [permissions.OwnedModelPermissions, ] 
    filter_class = SectionFilter       


class ResourceViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.ResourceSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    permission_classes = [permissions.OwnedModelPermissions, ]


class QuestionFilter(filters.BaseFilterSet):
    class Meta:
        model = survey.QuestionSerializer.Meta.model
        fields = ['pk__in', 'parent', 'section', 'owner', 'question',
                  'question_type']
        

class QuestionViewSet(base.BaseAPIViewMixin, base.OrderableViewMixin,
                       ModelViewSet):
    serializer_class = survey.QuestionSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    permission_classes = [permissions.OwnedModelPermissions, ]
    filter_class = QuestionFilter
    

class QuestionChoiceFilter(filters.BaseFilterSet):
    question__in = MethodFilter(action="handle_question_in")
    
    class Meta:
        model = survey.QuestionChoiceSerializer.Meta.model
        fields = ['pk__in', 'question', 'question__in', 'name', 'value', 
                  'help_text', 'order', 'parent', 'section', 'owner']
        
    def handle_question_in(self, queryset, value):
        l = json.loads(value)
        if l:
            return queryset.filter(question__in=l)
        return queryset
        
class QuestionChoiceViewSet(base.BaseAPIViewMixin, base.OrderableViewMixin,
                             ModelViewSet):
    serializer_class = survey.QuestionChoiceSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    permission_classes = [permissions.OwnedModelPermissions, ]


class QuestionResourceViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.QuestionResourceSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    permission_classes = [permissions.OwnedModelPermissions, ]


class ResponseViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.ResponseSerializer
    filter_fields = ['survey', 'user', 'passed', 'score', 'passed', 'status',
                     'status__closed_state', 'completed_date']
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()


class ResponseSectionFilter(filters.BaseFilterSet):
    questionresponse__null_answer = MethodFilter(action='handle_no_answer')
    
    class Meta:
        model = survey.ResponseSectionSerializer.Meta.model
        fields = ['survey', 'response', 'survey_section',
                  'questionresponse__null_answer', 'pk__in']
    
    def handle_no_answer(self, queryset, value):
        if value == False or value == 'False':
            return queryset.exclude(Q(questionresponse__answer__isnull=True) |
                                    Q(questionresponse__answer=''))
        else:  
            return queryset.filter(Q(questionresponse__answer__isnull=True) |
                                    Q(questionresponse__answer=''))
    
    
        
            
class ResponseSectionViewSet(base.BaseAPIViewMixin, base.OrderableViewMixin,
                             ModelViewSet):
    serializer_class = survey.ResponseSectionSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    permission_classes = [survey_permissions.ResponseOwnedModelPermissions, ]
    filter_class = ResponseSectionFilter


class QuestionResponseFilter(filters.BaseFilterSet):
    null_answer = MethodFilter(action='handle_no_answer')
    
    class Meta:
        model = survey.QuestionResponseSerializer.Meta.model
        fields = ['survey', 'response', 'section',
                  'question', 'answer', 'null_answer']
    
    def handle_no_answer(self, queryset, value):
        if value == False or value == 'False':
            return queryset.exclude(Q(answer__isnull=True) |
                                    Q(answer=''))
        else:  
            return queryset.filter(Q(answer__isnull=True) |
                                    Q(answer=''))

    
class QuestionResponseViewSet(base.BaseAPIViewMixin, base.OrderableViewMixin,
                              ModelViewSet):
    serializer_class = survey.QuestionResponseSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    permission_classes = [survey_permissions.ResponseOwnedModelPermissions, ]
    filter_class = QuestionResponseFilter


class QuestionResponseResourceFilter(filters.BaseFilterSet):
    question_response__in = MethodFilter(action="handle_question_response_in")
    
    class Meta:
        model = survey.QuestionResponseResourceSerializer.Meta.model
        fields = ['name', 'description', 'resource_type', 'content_type',
                  'size', 'question_response', 'question_response__in',
                  'survey', 'response', 'section', 'owner']
        
    def handle_question_response_in(self, queryset, value):
        l = json.loads(value)
        if l:
            return queryset.filter(question_response__in=l)
        return queryset
    
class QuestionResponseResourceViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.QuestionResponseResourceSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    permission_classes = [survey_permissions.ResponseOwnedModelPermissions, ]
    filter_class = QuestionResponseResourceFilter
