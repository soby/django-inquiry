import mock
import copy
import random
import string
from django.test import TestCase
from django.contrib.auth.models import Group
from .....api.v1.serializers import user
from ..... import models
from .....utils.test.objects import remove_fields, compare_dict_lists


def randomword(length):
    return ''.join(random.choice(string.lowercase + string.digits)
                        for i in range(length) #@UnusedVariable
                   )


class GroupDisplayFieldTest(TestCase):

    def test_to_native(self):
        class testObj(object):
            id = 'sdf'
            name = 'org_4_administrators'
        self.assertEqual({'id': 'sdf', 'name': 'administrators'},
                         user.GroupDisplayField(read_only=True)
                            .to_representation(testObj())
                        )


class UserSerializerTest(TestCase):

    def setUp(self):
        self.token = token = randomword(10)
        self.o = models.Org(name='blah')
        self.o.save()
        self.userData = {'username': u'blah{0}'.format(token),
                         'email': u'a{0}@b.com'.format(token),
                         'first_name': u'first{0}'.format(token),
                         'last_name': u'last{0}'.format(token),
                         'title': u'afs{0}'.format(token),
                         'group': u'asd{0}'.format(token),
                         'phone': u'4523423{0}'.format(token),
                         'is_active': True,
                         'groups': [{'name': u'users'},
                                    {'name': u'administrators'}
                                    ]
                         }
        d = copy.copy(self.userData)
        del d['groups']
        self.u = models.User(org=self.o, **d)
        self.u.save()
        self.addCleanup(self.u.delete)
        self.addCleanup(self.o.delete)

    def test_expected_data_serialized(self):
        ser = user.UserSerializer(instance=self.u, context={})
        self.assertEqual(remove_fields(['id', 'groups'], self.userData),
                         remove_fields(['id', 'groups'], dict(ser.data))
                        )
        self.assertEqual(([], []),
                         compare_dict_lists(self.userData['groups'],
                                            ser.data['groups'],
                                            lambda x: remove_fields(['id'],
                                                                    x)
                                            )
                         )

    def test_updates(self):
        grp = Group.objects.get(name='org_{0}_administrators'
                                .format(self.o.id))
        data = {
                    # not allowed
                    'id': '3',
                    'username': 'blah2{0}'.format(self.token),
                    'groups': {'id': grp.id, 'name': grp.name},

                    # the below are allowed
                    'email': 'legit{0}@legit.com'.format(self.token),
                    'first_name': 'blah{0}'.format(self.token),
                    'last_name': 'blah{0}'.format(self.token),
                    'is_active': False,
               }

        ser = user.UserSerializer(instance=self.u, data=data)
        self.assertTrue(ser.is_valid())
        ser.save()
        obj = ser.instance

        # Not allowed. Keep originals
        self.assertEqual(self.u.id, obj.id)
        self.assertEqual(self.userData['username'], obj.username)
        origGrps = [x['name'] for x in self.userData['groups']]
        for i in obj.groups.all():
            self.assertTrue(i.name.split('_')[-1] in origGrps)

        # allowed
        self.assertEqual(data['email'], obj.email)
        self.assertEqual(data['first_name'], obj.first_name)
        self.assertEqual(data['last_name'], obj.last_name)
        self.assertEqual(data['is_active'], obj.is_active)

    def test_create(self):
        data = {
                    'username': 'blah3{0}'.format(self.token),

                    # the below are allowed
                    'email': 'legit{0}@legit.com'.format(self.token),
                    'first_name': 'blah1{0}'.format(self.token),
                    'last_name': 'blah2{0}'.format(self.token),
               }
        ser = user.UserSerializer(data=data)
        self.assertTrue(ser.is_valid())
        obj = ser.data

        self.assertEqual(obj['username'], data['username'])
        self.assertEqual(obj['email'], data['email'])
        self.assertEqual(obj['first_name'], data['first_name'])
        self.assertEqual(obj['last_name'], data['last_name'])


class GroupNameDisplayFieldTest(TestCase):
    def test_to_representation(self):
        self.assertEqual('administrators',
                         user.GroupNameDisplayField()
                            .to_representation('org_4_administrators')
                        )


class GroupSerializerTest(TestCase):
    def setUp(self):
        self.o = models.Org(name='blah')
        self.o.save()
        self.u = models.User(username='blah2', org=self.o)
        self.u.save()
        self.u2 = models.User(username='blah3', org=self.o)
        self.u2.save()

        self.otherOrg = models.Org(name='blah2')
        self.otherOrg.save()
        self.uninvolved = models.User(username='blah4', org=self.otherOrg)
        self.uninvolved.save()

        self.addCleanup(self.u.delete)
        self.addCleanup(self.u2.delete)
        self.addCleanup(self.o.delete)
        self.addCleanup(self.uninvolved.delete)
        self.addCleanup(self.otherOrg.delete)

        self.grp = self.u.groups.get(name='org_{0}_administrators'
                                      .format(self.o.id))
    
    def test_expected_data_serialized(self):
        ser = user.GroupSerializer(instance=self.grp, context={})
        self.assertEqual({'name': u'administrators', 'user_set': [self.u.id]},
                          remove_fields(['id'], dict(ser.data)))

    def test_updates_with_user(self):
        """
            we're setting a context.request.user here so we should be able to
            change appropriate relationships with our allowed queryset
        """
        data = {
                    # not allowed
                    'name': 'stuff',
                    'id': '3',

                    # allowed
                    'user_set': [self.u.id, self.u2.id],
               }

        request = mock.Mock()
        request.user = self.u
        ser = user.GroupSerializer(instance=self.grp,
                                   data=data,
                                   context={'request': request})
        self.assertTrue(ser.is_valid())
        ser.save()
        obj = ser.instance

        # Not allowed. Keep originals
        self.assertEqual(self.grp.id, obj.id)
        self.assertEqual(self.grp.name, obj.name)

        # allowed
        self.assertEqual(data['user_set'], [x.id for x in obj.user_set.all()])

    def test_updates_no_user(self):
        """
            we're not setting a context.request.user here so we shouldn't
            be able to touch relationships since serializers filter on this
        """
        data = {
                    # not allowed
                    'name': 'stuff',
                    'id': '3',

                    # allowed
                    'user_set': [self.u.id, self.u2.id],
               }

        ser = user.GroupSerializer(instance=self.grp, data=data)
        self.assertFalse(ser.is_valid())
        self.assertRaises(AssertionError, ser.save)

    def test_updates_with_bad_user_for_relationship(self):
        """
            Our serializer restricts the valid querysets for user_set
            to those user this user is allowed to see. In this case, it's
            only users in their org so no update would be allowed for this
            field. They're only able to update this object at all through this
            serializer because the object-level update permission checking
            happens in the views
        """
        data = {
                    # not allowed
                    'name': 'stuff',
                    'id': '3',

                    # allowed, but not for the user we'll set in the context
                    'user_set': [self.u.id, self.u2.id],
               }

        request = mock.Mock()
        request.user = self.uninvolved
        ser = user.GroupSerializer(instance=self.grp, data=data,
                                   context={'request': request})
        self.assertFalse(ser.is_valid())
        self.assertRaises(AssertionError, ser.save)
