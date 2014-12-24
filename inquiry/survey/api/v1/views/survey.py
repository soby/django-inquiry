from rest_framework.viewsets import ModelViewSet

from .....core.api.v1.views import base

from ..serializers import survey
from .....core.auth import permissions
from ....authz import permissions as survey_permissions


class StatusViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.StatusSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    

class TypeViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.TypeSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()


class SurveyViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.SurveySerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()


class SectionViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.SectionSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    permission_classes = [permissions.OwnedModelPermissions, ]        


class ResourceViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.ResourceSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    permission_classes = [permissions.OwnedModelPermissions, ]


class QuestionViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.QuestionSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    permission_classes = [permissions.OwnedModelPermissions, ]
    

class QuestionChoiceViewSet(base.BaseAPIViewMixin, ModelViewSet):
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
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()


class ResponseSectionViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.ResponseSectionSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    permission_classes = [survey_permissions.ResponseOwnedModelPermissions, ]


class QuestionResponseViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.QuestionResponseSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    permission_classes = [survey_permissions.ResponseOwnedModelPermissions, ]


class QuestionResponseResourceViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = survey.QuestionResponseResourceSerializer
    # Required for DjangoObjectPermissions
    queryset = serializer_class.Meta.model.objects.none()
    permission_classes = [survey_permissions.ResponseOwnedModelPermissions, ]
