import mock
from django.test import TestCase

from .....api.v1.serializers import base

class holder(object):
    def __init__(self,val):
        self.val = val
    def get_fields(self,*args,**kwargs):
        return self.val
    
class testclass(base.FieldRestrictingMixin,holder):
    pass

class FieldRestrictingMixinTest(TestCase):
    def test_get_fields_empty(self):
        a = testclass({})
        self.assertEqual({},a.get_fields())
    def test_get_fields_inactive(self):
        a = testclass({'blah':'stuff'})
        self.assertEqual({'blah':'stuff'},a.get_fields())
    def test_get_fields_no_request(self):
        fieldMock = mock.Mock()
        modelMock = mock.Mock()
        a = testclass({'blah':fieldMock})

        a.context = {}
        a._QUERYSET_RESTRICTIONS = {'blah':modelMock}
        
        res = a.get_fields()
        self.assertEqual({'blah':fieldMock},res)
        self.assertTrue(modelMock.objects.none.called)
        self.assertEqual(res['blah'].queryset,modelMock.objects.none.return_value)

    def test_get_fields_no_manager(self):
        fieldMock = mock.Mock()
        modelMock = mock.Mock()
        class TestException(Exception): pass
        def raisesomething(*args,**kwargs):
            raise AttributeError(args)
        modelMock.manager.for_user.side_effect = raisesomething
        userMock = mock.Mock(spec=[])
        a = testclass({'blah':fieldMock})

        a.context = {'request':userMock}
        a._QUERYSET_RESTRICTIONS = {'blah':modelMock}
        
        self.assertRaises(AttributeError,a.get_fields)

    def test_get_fields_normal(self):
        fieldMock = mock.Mock()
        modelMock = mock.Mock()
        userMock = mock.Mock()
        a = testclass({'blah':fieldMock})

        a.context = {'request':userMock}
        a._QUERYSET_RESTRICTIONS = {'blah':modelMock}
        res = a.get_fields()
        self.assertTrue(modelMock.manager.for_user.called_with(userMock))
        self.assertEqual(res['blah'].queryset,modelMock.manager.for_user.return_value)