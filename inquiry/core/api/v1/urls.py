from django.conf.urls import patterns

from rest_framework.routers import DefaultRouter
router = DefaultRouter()

from .views import user as user_views
from .views import org as org_views


urlpatterns = patterns('',)

router.register(r'user', user_views.UserViewSet, base_name='api/core/v1/user')
router.register(r'group', user_views.GroupViewSet,
                base_name='api/core/v1/group')
router.register(r'org', org_views.OrgViewSet, base_name='api/core/v1/org')

urlpatterns = router.urls
