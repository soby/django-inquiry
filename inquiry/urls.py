from django.conf.urls import patterns, include, url
from django.contrib import admin

from inquiry.core.auth.social import SavedSubdomainInStateRedirectorView
from inquiry.core.api.v1 import urls as apicore_v1_urls
from inquiry.survey.api.v1 import urls as apisurvey_v1_urls

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    
    # Social auth login. Uses python-social-auth
    url(r'^auth/social/bounce(?P<target_uri>/.*)$', SavedSubdomainInStateRedirectorView.as_view(),name="auth/social/bounce"),
    url(r'^auth/social/login/', include('social.apps.django_app.urls', namespace='social')),
    
    url(r'^api/v1/core/',include(apicore_v1_urls)),
    url(r'^api/v1/survey/',include(apisurvey_v1_urls)),
)
