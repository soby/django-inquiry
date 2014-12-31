from rest_framework.test import APITestCase

from ......core.tests.api.v1.views import base
from .....api.v1.views import survey
from .....utils.test import data


class StatusViewSetTest(base.UserTestMixin, base.AutoTestMixin, 
                        base.ViewSetBaseTestMixin, APITestCase):
    named_view_base = 'api/survey/v1/status'
    namespace = None
    viewset = survey.StatusViewSet
    
    FIELDS = ['name', 'label', 'help_text', 'closed_state']
    UPDATE_FIELDS = ['name', 'label', 'help_text', 'closed_state']
    REQUIRE_ADMIN = True
    CREATOR_CLASS = data.StatusCreator
    
        
class TypeViewSetTest(base.UserTestMixin, base.AutoTestMixin, 
                        base.ViewSetBaseTestMixin, APITestCase):
    named_view_base = 'api/survey/v1/type'
    namespace = None
    viewset = survey.TypeViewSet
    
    FIELDS = ['name', 'statuses', 'initial_status']
    UPDATE_FIELDS = ['name', 'statuses', 'initial_status']
    REQUIRE_ADMIN = True
    M2M_FIELDS = ['statuses']
    FK_FIELDS = ['initial_status']
    CREATOR_CLASS = data.TypeCreator
    
    def get_update_data(self,*args,**kwargs):
        # The way we get update data is to use an unsaved object
        # M2M can't be set on those
        dt = super(TypeViewSetTest,self).get_update_data(*args,**kwargs)
        statuses = data.StatusCreator()\
                    .create_for_users([self.org1_admin,],3)\
                    .values()[0]
        dt['statuses'] = [x.pk for x in statuses]
        dt['initial_status'] = statuses[0].pk
        return dt
    
    def get_data(self,*args,**kwargs):
        # The way we get update data is to use an unsaved object
        # M2M can't be set on those
        dt = super(TypeViewSetTest,self).get_data(*args,**kwargs)
        statuses = data.StatusCreator()\
                    .create_for_users([self.org1_admin,],3)\
                    .values()[0]
        dt['statuses'] = [x.pk for x in statuses]
        dt['initial_status'] = statuses[0].pk
        return dt


class SurveyViewSetTest(base.UserTestMixin, base.AutoTestMixin, 
                        base.ViewSetBaseTestMixin, APITestCase):
    named_view_base = 'api/survey/v1/survey'
    namespace = None
    viewset = survey.SurveyViewSet
    
    FIELDS = ['name', 'description', 'survey_type']
    UPDATE_FIELDS = ['name', 'description', ]
    FK_FIELDS = ['survey_type']
    CREATOR_CLASS = data.SurveyCreator


class SectionViewSetTest(base.UserTestMixin, base.AutoTestMixin, 
                        base.ViewSetBaseTestMixin, APITestCase):
    named_view_base = 'api/survey/v1/section'
    namespace = None
    viewset = survey.SectionViewSet
    
    FIELDS = ['name', 'description', 'parent']
    UPDATE_FIELDS = ['name', 'description', 'parent']
    FK_FIELDS = ['parent']
    CREATOR_CLASS = data.SectionCreator


class ResourceViewSetTest(base.UserTestMixin, base.AutoTestMixin, 
                        base.ViewSetBaseTestMixin, APITestCase):
    named_view_base = 'api/survey/v1/resource'
    namespace = None
    viewset = survey.ResourceViewSet

    FIELDS = ['name', 'description', 'resource', 'resource_type',
              'section', 'section']
    UPDATE_FIELDS = ['name', 'description', 'section', 'resource',
                     'resource_type']
    FK_FIELDS = ['section']
    CREATOR_CLASS = data.ResourceCreator


class QuestionViewSetTest(base.UserTestMixin, base.AutoTestMixin, 
                            base.ViewSetBaseTestMixin, APITestCase):
    named_view_base = 'api/survey/v1/question'
    namespace = None
    viewset = survey.QuestionViewSet
    
    FIELDS = ['question', 'question_type', 'section']
    UPDATE_FIELDS = ['question', 'question_type', 'section']
    FK_FIELDS = ['section']
    CREATOR_CLASS = data.QuestionCreator
    

class QuestionChoiceViewSetTest(base.UserTestMixin, base.AutoTestMixin, 
                                base.ViewSetBaseTestMixin, APITestCase):
    named_view_base = 'api/survey/v1/questionchoice'
    namespace = None
    viewset = survey.QuestionChoiceViewSet

    FIELDS = ['question', 'name', 'value', 'help_text']
    UPDATE_FIELDS = ['question', 'name', 'value', 'help_text']
    FK_FIELDS = ['question']
    CREATOR_CLASS = data.QuestionChoiceCreator


class QuestionResourceViewSetTest(base.UserTestMixin, base.AutoTestMixin, 
                                    base.ViewSetBaseTestMixin, APITestCase):
    named_view_base = 'api/survey/v1/questionresource'
    namespace = None
    viewset = survey.QuestionResourceViewSet

    FIELDS = ['question', 'name', 'description', 'resource', 'resource_type' ]
    UPDATE_FIELDS = ['question', 'name', 'description', 'resource',
                     'resource_type']
    FK_FIELDS = ['question']
    CREATOR_CLASS = data.QuestionResourceCreator


class ResponseViewSetTest(base.UserTestMixin, base.AutoTestMixin, 
                            base.ViewSetBaseTestMixin, APITestCase):
    named_view_base = 'api/survey/v1/response'
    namespace = None
    viewset = survey.ResponseViewSet
    
    FIELDS = ['survey', 'user', 'status', 'due_date']
    UPDATE_FIELDS = ['survey', 'user', 'status']
    FK_FIELDS = ['survey', 'user','status']
    CREATOR_CLASS = data.ResponseCreator


class ResponseSectionViewSetTest(base.UserTestMixin, base.AutoTestMixin, 
                                base.ViewSetBaseTestMixin, APITestCase):
    named_view_base = 'api/survey/v1/responsesection'
    namespace = None
    viewset = survey.ResponseSectionViewSet

    FIELDS = ['response', 'survey_section' ]
    UPDATE_FIELDS = ['response', 'survey_section' ]
    FK_FIELDS = ['response', 'survey_section' ]
    CREATOR_CLASS = data.ResponseSectionCreator


class QuestionResponseViewSetTest(base.UserTestMixin, base.AutoTestMixin, 
                                    base.ViewSetBaseTestMixin, APITestCase):
    named_view_base = 'api/survey/v1/questionresponse'
    namespace = None
    viewset = survey.QuestionResponseViewSet

    FIELDS = ['section', 'answer', 'question']
    UPDATE_FIELDS = ['section', 'answer', 'question']
    FK_FIELDS = ['section', 'question' ]
    CREATOR_CLASS = data.QuestionResponseCreator
    
    
class QuestionResponseResourceViewSetTest(base.UserTestMixin,
                                    base.AutoTestMixin, 
                                    base.ViewSetBaseTestMixin, APITestCase):
    named_view_base = 'api/survey/v1/questionresponseresource'
    namespace = None
    viewset = survey.QuestionResponseResourceViewSet

    FIELDS = ['question_response', 'name', 'description', 'resource',
              'resource_type' ]
    UPDATE_FIELDS = ['question_response', 'name', 'description', 'resource',
              'resource_type' ]
    FK_FIELDS = ['question_response']
    CREATOR_CLASS = data.QuestionResponseResourceCreator