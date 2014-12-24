from django.test import TestCase
from .....api.v1.views import base
from ..... import models
from django.contrib.auth import get_user_model

import mock


class BaseAPIViewMixinTest(TestCase):
    def test_queryset_exists(self):
        #http://www.django-rest-framework.org/api-guide/permissions#djangomodelpermissions
        # Required for DjangoObjectPermissions
        self.assertTrue(hasattr(base.BaseAPIViewMixin,'queryset'))

    def test_get_queryset(self):
        obj = base.BaseAPIViewMixin()
        obj.request = mock.Mock()
        obj.serializer_class = mock.Mock()
        obj.get_queryset()
        self.assertTrue(obj.serializer_class.Meta.model.manager.for_user.called_with(obj.request.user))

    def test_perform_create(self):
        obj = base.BaseAPIViewMixin()
        obj.queryset = get_user_model().objects.all()
        obj.request = mock.Mock()
        objMock = mock.Mock()
        objMock.Meta.model = get_user_model()
        objMock.validated_data={}
        objMock._data={}
        obj.perform_create(objMock)
        self.assertEqual(objMock.validated_data.get('org_id'),obj.request.user.org_id)

    def test_perform_create_no_user(self):
        # probably shouldn't ever happen
        obj = base.BaseAPIViewMixin()
        objMock = mock.Mock()
        objMock.validated_data={}
        objMock._data={}
        obj.perform_create(objMock)
        self.assertEqual(None, objMock.validated_data.get('org_id'))