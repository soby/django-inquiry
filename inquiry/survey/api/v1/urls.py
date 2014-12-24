from django.conf.urls import patterns

from rest_framework.routers import DefaultRouter
router = DefaultRouter()

from .views import survey


urlpatterns = patterns('',)

router.register(r'status', survey.StatusViewSet, 
                base_name='api/survey/v1/status')
router.register(r'type', survey.TypeViewSet, 
                base_name='api/survey/v1/type')
router.register(r'survey', survey.SurveyViewSet, 
                base_name='api/survey/v1/survey')
router.register(r'section', survey.SectionViewSet, 
                base_name='api/survey/v1/section')
router.register(r'resource', survey.ResourceViewSet, 
                base_name='api/survey/v1/resource')
router.register(r'question', survey.QuestionViewSet, 
                base_name='api/survey/v1/question')
router.register(r'questionchoice', survey.QuestionChoiceViewSet, 
                base_name='api/survey/v1/questionchoice')
router.register(r'questionresource', survey.QuestionResourceViewSet, 
                base_name='api/survey/v1/questionresource')
router.register(r'response', survey.ResponseViewSet, 
                base_name='api/survey/v1/response')
router.register(r'responsesection', survey.ResponseSectionViewSet, 
                base_name='api/survey/v1/responsesection')
router.register(r'questionresponse', 
                survey.QuestionResponseViewSet, 
                base_name='api/survey/v1/questionresponse')
router.register(r'questionresponseresource', 
                survey.QuestionResponseResourceViewSet, 
                base_name='api/survey/v1/questionresponseresource')

urlpatterns = router.urls

