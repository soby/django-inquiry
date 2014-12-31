import copy

from django.test import TestCase
from .....api.v1.serializers import org
from .....utils.test.objects import remove_fields
from .....utils.auth import get_org_model

Org = get_org_model()


class OrgSerializerTest(TestCase):
    def setUp(self):
        self.data = {'name': 'blah',
                     'subdomain': 'stuff',
                     'preference_auth_google_oauth2': True,
                     'preference_auth_email_autocreate_domains': 'acme.com',
                     }
        self.o = Org(**self.data)
        self.o.save()
        self.addCleanup(self.o.delete)

    def test_expected_data_serialized(self):
        ser = org.OrgSerializer(instance=self.o, context={})
        self.assertEqual(self.data, remove_fields(['id'], ser.data,
                                                  onCopy=False)
                         )

    def test_no_updates(self):
        newdata = copy.deepcopy(self.data)
        for k, v in newdata.items():
            if not isinstance(v, bool):
                newdata[k] = v + '1'
            else:
                newdata[k] = not v
        ser = org.OrgSerializer(instance=self.o, data=newdata)
        self.assertTrue(ser.is_valid())
        obj = ser.data
        for k, v in self.data.items():
            self.assertEqual(obj.get(k), v)
