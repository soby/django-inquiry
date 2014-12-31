import json
from datetime import datetime

from rest_framework.test import APIClient
from rest_framework import mixins

from django.core.urlresolvers import reverse, NoReverseMatch
from  django.core.files import File

from .....utils.test import data as core_data
from .....utils.auth import make_perm, make_global_perm
from .....models import UserOwnedModel

# Used by other tests to ignore certain fields and check for
# things not changing during bad updates
USER_OWNED_META_FIELDS = ['created_by', 'created', 'modified_by',
                          'modified', 'owner' ]


class ViewSetBaseTestMixin(object):
    # set these dammit
    viewset = None
    named_view_base = None

    # This doesn't work yet in DRF
    namespace = None

    # this should be a valid object for details
    obj = None

    def __init__(self,*args,**kwargs):
        if not (self.named_view_base and self.viewset):
            raise Exception('named_view_base and viewset must be set')

        super(ViewSetBaseTestMixin,self).__init__(*args,**kwargs)

    def test_noauth_detail(self):
        client = APIClient()
        try:
            url = reverse(self.named_view_base+'-detail',kwargs=
                          {'pk':self.obj.id},current_app=self.namespace)
        except NoReverseMatch:
            return
        res = client.get(url)
        self.assertEqual(403,res.status_code)

    def test_noauth_create(self):
        client = APIClient()
        try:
            url = reverse(self.named_view_base+'-list',
                          current_app=self.namespace)
        except NoReverseMatch:
            return
        res = client.post(url)
        self.assertEqual(403,res.status_code)

    def test_noauth_list(self):
        client = APIClient()
        try:
            url = reverse(self.named_view_base+'-list',
                          current_app=self.namespace)
        except NoReverseMatch:
            return
        res = client.get(url)
        self.assertEqual(403,res.status_code)

    def test_noauth_update(self):
        client = APIClient()
        try:
            url = reverse(self.named_view_base+'-detail',
                          kwargs={'pk':self.obj.id},current_app=self.namespace)
        except NoReverseMatch:
            return
        res = client.put(url)
        self.assertEqual(403,res.status_code)

    def test_noauth_partial_update(self):
        client = APIClient()
        try:
            url = reverse(self.named_view_base+'-detail',
                          kwargs={'pk':self.obj.id},current_app=self.namespace)
        except NoReverseMatch:
            return
        res = client.patch(url)
        self.assertEqual(403,res.status_code)

    def test_noauth_delete(self):
        client = APIClient()
        try:
            url = url = reverse(self.named_view_base+'-detail',
                                kwargs={'pk':self.obj.id},
                                current_app=self.namespace)
        except NoReverseMatch:
            return
        res = client.delete(url)
        self.assertEqual(403,res.status_code)

    def test_create(self):
        if issubclass(self.viewset,mixins.CreateModelMixin):
            raise Exception("implement or override me")
    def test_list(self):
        if issubclass(self.viewset,mixins.ListModelMixin):
            raise Exception("implement me or override me")
    def test_detail(self):
        if issubclass(self.viewset,mixins.RetrieveModelMixin):
            raise Exception("implement me or override me")
    def test_update(self):
        if issubclass(self.viewset,mixins.UpdateModelMixin):
            raise Exception("implement me or override me")
    def test_partial_update(self):
        if issubclass(self.viewset,mixins.UpdateModelMixin):
            raise Exception("implement me or override me")
    def test_delete(self):
        if issubclass(self.viewset,mixins.DestroyModelMixin):
            raise Exception("implement me or override me")

    # should we try to enumerate the supported methods and mandate that a 
    # test case exists for each?

class UserTestMixin(object):
    
    def setUp(self):
        orgsAndUsers = core_data.UserCreator().create_users_and_orgs(2,3)
        self.org1 = orgsAndUsers.keys()[0]
        self.org1_users = orgsAndUsers[self.org1]
        self.org1_admin = orgsAndUsers[self.org1][0]
        self.org1_user = orgsAndUsers[self.org1][1]
        self.org2 = orgsAndUsers.keys()[1]
        self.org2_users = orgsAndUsers[self.org2]
        self.org2_admin = orgsAndUsers[self.org2][0]
        self.org2_user = orgsAndUsers[self.org2][1]
        super(UserTestMixin,self).setUp()

def refetch(obj):
    return obj.__class__.objects.get(pk=obj.pk)

class AutoTestMixin(object):
    TARG_USER = None
    FIELDS = []
    UPDATE_FIELDS = []
    CREATE_ONLY_FIELDS = []
    REQUIRE_ADMIN = False
    M2M_FIELDS = []
    FK_FIELDS = [] # FKs serialized to just an ID
    CREATOR_CLASS = None
    
    def setUp(self):
        super(AutoTestMixin,self).setUp()
        self.org1_records = []
        self.org2_records = []
        d = self.CREATOR_CLASS().create_for_users( self.org1_users[1:]+
                                                       self.org2_users, 2)
        for user in d:
            if user in self.org1_users:
                self.org1_records.extend(d[user])
            else:
                self.org2_records.extend(d[user])
                
        # Base test needs this
        self.obj = self.org1_records[0]
    
    def create_object(self, user):
        return self.CREATOR_CLASS().create_for_users( 
                                      [user,],
                                      1,
                                      save=False).values()[0][0]
    
    def get_list_count(self, user):
        return len(self.obj.__class__.manager.for_user(user))
    
    def get_extra_data(self, user):
        return {'created_by': user, 
                'owner': user 
                }
    
    def get_target_user(self):
        if not self.REQUIRE_ADMIN:
            if isinstance(self.obj,UserOwnedModel):
                return self.obj.owner
            
            return self.org1_user
        
        return self.org1_admin
    
    def get_unauthorized_user(self, obj):
        return self.org1_users[2]
    
    def get_cross_org_user(self):
        if not self.REQUIRE_ADMIN:
            return self.org2_user
        return self.org2_admin

    def get_target_object(self):
        return self.obj
    
    def get_fields(self):
        if not self.FIELDS:
            raise Exception('Must declare FIELDS')
        return self.FIELDS

    def get_update_fields(self):
        if not self.UPDATE_FIELDS:
            raise Exception('Must declare UPDATE_FIELDS')
        return self.UPDATE_FIELDS

    def get_create_only_fields(self):
        if not hasattr(self, 'CREATE_ONLY_FIELDS'):
            raise Exception('Must declare CREATE_ONLY_FIELDS')
        return self.CREATE_ONLY_FIELDS

    def get_data(self,new_obj):
        data = {}
        for f in self.get_fields():
            if f in self.FK_FIELDS:
                data[f] = getattr(new_obj,f).pk
            elif f in self.M2M_FIELDS:
                if not new_obj.pk:
                    # we can't use M2M on unsaved
                    continue
                data[f] = [x.pk for x in getattr(new_obj,f)]
            else:
                data[f] = getattr(new_obj,f)
        return data
        
    def get_update_data(self,existing, new_obj, full=True):
        data = {}
        for f in self.get_update_fields():
            if f in self.FK_FIELDS:
                data[f] = getattr(new_obj,f).pk
            elif f in self.M2M_FIELDS:
                if not new_obj.pk:
                    # can't use M2M on unsaved
                    continue
                data[f] = [x.pk for x in getattr(new_obj,f).all()]
            else:
                data[f] = getattr(new_obj,f)
        
        if full:
            # This is a PUT so we need all fields. The rest should be
            # from the existing object though
            for f in self.get_fields():
                if f in data.keys():
                    # already there, skip
                    continue
                if f in self.FK_FIELDS:
                    data[f] = getattr(existing,f).pk
                elif f in self.M2M_FIELDS:
                    if not existing.pk:
                        # can't use M2M on unsaved
                        continue
                    data[f] = [x.pk for x in getattr(existing,f).all()]
                else:
                    data[f] = getattr(existing,f)
                
        return data

    def get_create_only_data(self, existing, new_obj):
        data = {}
        for f in self.get_create_only_fields():
            if f in self.FK_FIELDS:
                data[f] = getattr(new_obj,f).pk
            elif f in self.M2M_FIELDS:
                if not new_obj.pk:
                    # can't use M2M on unsaved
                    continue
                data[f] = [x.pk for x in getattr(new_obj,f)]
            else:
                data[f] = getattr(new_obj,f)
        return data
    
    def _file_compare(self, field, fileObj, stringOrFile):
        # TODO: some sort of compare
        # stringOrFile can apparently be a URL with a different
        # pattern than fileObj.url()
        return 
    
        if isinstance(stringOrFile,basestring):
            self.assertEqual(fileObj.read(), stringOrFile,
                                 msg="Files differ for field {0}"\
                                 .format(field))
        else:
            g1 = fileObj.chunks()
            g2 = stringOrFile.chunks()
            for piece in g1:
                comp = g2.next()
                self.assertEqual(piece,comp,
                                 msg="Files differ for field {0}"\
                                 .format(field))
    
    def _datetime_compare(self, field, obj1, obj2):
        if isinstance(obj1,datetime):
            obj1 = obj1.isoformat().replace('Z','+00:00')
        else:
            if obj1 is not None:
                obj1 = obj1.replace('Z','+00:00')
        if isinstance(obj2,datetime):
            obj2 = obj2.isoformat().replace('Z','+00:00')
        else:
            if obj2 is not None:
                obj2 = obj2.replace('Z','+00:00')
        self.assertEqual(obj1, obj2,
                         msg="Values differ for field {0}:\n{1}\n{2}"\
                                 .format(field, obj1, obj2))
                                 
    def compare_field(self, field, naive, obj):
        if isinstance(naive,File) or isinstance(getattr(obj,field), File):
            self._file_compare(field, naive, getattr(obj,field))
        elif isinstance(naive,datetime) or\
                isinstance(getattr(obj,field), datetime):
            self._datetime_compare(field, naive, getattr(obj,field))
        elif field in self.FK_FIELDS:
            self.assertEqual(naive,getattr(obj,field).pk,
                             msg="Values differ for field {0}:\n{1}\n{2}"\
                                 .format(field, naive, getattr(obj,field).pk))
        elif field in self.M2M_FIELDS:
            m = [x.pk for x in getattr(obj,field).all()]
            self.assertEqual(naive, m,
                             msg="Values differ for field {0}:\n{1}\n{2}"\
                                 .format(field, naive, m))
        else:
            self.assertEqual(naive,getattr(obj,field),
                             msg="Values differ for field {0}:\n{1}\n{2}"\
                                 .format(field, naive, getattr(obj,field)))
    
    def compare_field_with_dicts(self, field, naive, naive2):
        if isinstance(naive,File) or isinstance(naive2, File):
            self._file_compare(field, naive, naive2)
        elif isinstance(naive,datetime) or\
                isinstance(naive2, datetime):
            self._datetime_compare(field, naive, naive2)
        else:
            self.assertEqual(naive,naive2,
                msg="Values differ for field {0}:\n{1}\n{2}"\
                                 .format(field, naive, naive2))
    
    def compare_field_with_objs(self, field, obj1, obj2):
        if isinstance(getattr(obj1,field),File) or\
                isinstance(getattr(obj2,field),File):
            self._file_compare(field, getattr(obj1,field), 
                               getattr(obj2,field))
        elif isinstance(getattr(obj1,field),datetime) or\
                isinstance(getattr(obj2,field), datetime):
            self._datetime_compare(field, getattr(obj1,field),
                                   getattr(obj2,field))
        elif field in self.FK_FIELDS:
            self.assertEqual(getattr(obj1,field).pk,getattr(obj1,field).pk,
                             msg="Values differ for field {0}:\n{1}\n{2}"\
                                 .format(field, getattr(obj1,field).pk,
                                         getattr(obj2,field).pk))
        elif field in self.M2M_FIELDS:
            m1 = [x.pk for x in getattr(obj1,field).all()]
            m2 = [x.pk for x in getattr(obj2,field).all()]
            self.assertEqual(m1, m2,
                             msg="Values differ for field {0}:\n{1}\n{2}"\
                                 .format(field, m1, m2))
        else:
            self.assertEqual(getattr(obj1,field),getattr(obj2,field),
                             msg="Values differ for field {0}:\n{1}\n{2}"\
                                 .format(field, getattr(obj1,field),
                                         getattr(obj2,field)))
            
    def test_create(self):
        TARG_USER=self.get_target_user()
        new_obj = self.create_object(TARG_USER)
        DATA = self.get_data(new_obj)
        EXTRA_DATA = self.get_extra_data(TARG_USER)
        
        self.client.force_authenticate(user=TARG_USER)
        url = reverse(self.named_view_base+'-list',current_app=self.namespace)
        self.assertTrue(TARG_USER.has_perm(make_global_perm(new_obj,
                                                            'add')))
        kwargs = {}
        for val in DATA.values():
            if isinstance(val,File):
                kwargs['format'] = 'multipart'
        res = self.client.post(url,data=DATA,**kwargs)
        self.assertEqual(201,res.status_code)
        resJson = json.loads(res.content)
        u = new_obj.__class__.objects.get(pk=resJson['id'])
        self.addCleanup(u.delete)
        for field in DATA:
            self.compare_field(field,DATA[field],u)
        
        for field in EXTRA_DATA:
            self.compare_field(field,EXTRA_DATA[field],u)
            
        self.assertEqual(u.org_id,self.obj.org_id)
        
        url = reverse(self.named_view_base+'-detail',kwargs={'pk':u.id},
                      current_app=self.namespace)
        res = self.client.get(url)
        
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        for field in DATA:
            self.compare_field_with_dicts(field, DATA[field], resJson[field])

    def test_create_bad_cross_org_owner(self):
        TARG_USER=self.get_target_user()
        new_obj = self.create_object(TARG_USER)
        DATA = self.get_data(new_obj)
        EXTRA_DATA = self.get_extra_data(TARG_USER)
        DATA.update({'owner':self.get_cross_org_user().pk,
                     'created_by':self.get_cross_org_user().pk})
        
        self.client.force_authenticate(user=TARG_USER)
        url = reverse(self.named_view_base+'-list',current_app=self.namespace)
        kwargs = {}
        for val in DATA.values():
            if isinstance(val,File):
                kwargs['format'] = 'multipart'
        res = self.client.post(url,data=DATA, **kwargs)
        self.assertEqual(201,res.status_code)
        resJson = json.loads(res.content)
        u = new_obj.__class__.objects.get(pk=resJson['id'])
        self.addCleanup(u.delete)
        for field in DATA:
            if field == 'owner' or field == 'created_by': continue
            self.compare_field(field,DATA[field],u)
        for field in EXTRA_DATA:
            self.compare_field(field,EXTRA_DATA[field],u)
        self.assertEqual(u.org_id,self.obj.org_id)
    
    def test_list(self):
        TARG_USER=self.get_target_user()
        self.client.force_authenticate(user=TARG_USER)
        url = reverse(self.named_view_base+'-list',current_app=self.namespace)
        res = self.client.get(url)
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        
        self.assertEqual(self.get_list_count(TARG_USER),len(resJson))
        
    def test_detail(self):
        TARG_USER=self.get_target_user()
        TARG_OBJ = self.get_target_object()
        self.client.force_authenticate(user=TARG_USER)
        url = reverse(self.named_view_base+'-detail',
                      kwargs={'pk':TARG_OBJ.pk},
                      current_app=self.namespace)
        res = self.client.get(url)
        self.assertEqual(200,res.status_code)
        resJson = json.loads(res.content)
        for field in self.get_fields():
            self.compare_field(field,resJson[field],TARG_OBJ)
    
    def test_update(self):
        TARG_USER=self.get_target_user()
        new_obj = self.create_object(TARG_USER)
        TARG_OBJ = self.get_target_object()
        DATA = self.get_update_data(TARG_OBJ, new_obj, full=True)
        
        self.client.force_authenticate(user=TARG_USER)
        self.assertTrue(TARG_USER.has_perm(make_perm(new_obj.__class__,
                                                            'change'),
                                           TARG_OBJ
                                           )
                        )
        url = reverse(self.named_view_base+'-detail',
                      kwargs={'pk':TARG_OBJ.pk},
                      current_app=self.namespace)
        kwargs = {}
        for val in DATA.values():
            if isinstance(val,File):
                kwargs['format'] = 'multipart'
        res = self.client.put(url,data=DATA, **kwargs)
        self.assertEqual(200,res.status_code)
        
        u = refetch(TARG_OBJ)
        for field in DATA:
            self.compare_field(field,DATA[field],u)
        extra = self.get_extra_data(TARG_OBJ.owner)
        for field in extra:
            self.compare_field(field,extra[field],u)
        
    def test_update_cross_org_bad(self):
        TARG_USER=self.get_cross_org_user()
        new_obj = self.create_object(TARG_USER)
        TARG_OBJ = self.get_target_object()
        
        self.client.force_authenticate(user=TARG_USER)
        self.assertFalse(TARG_USER.has_perm(make_perm(new_obj.__class__,
                                                            'change'),
                                           TARG_OBJ
                                           )
                        )
        url = reverse(self.named_view_base+'-detail',
                      kwargs={'pk':TARG_OBJ.pk},
                      current_app=self.namespace)
        DATA = self.get_update_data(TARG_OBJ, new_obj, full=True)
        kwargs = {}
        for val in DATA.values():
            if isinstance(val,File):
                kwargs['format'] = 'multipart'
        res = self.client.put(url,data=DATA, **kwargs)
        self.assertEqual(404,res.status_code)
        rf = refetch(TARG_OBJ)
        self.assertEqual(TARG_OBJ.modified,rf.modified)
        self.assertEqual(TARG_OBJ.modified_by,rf.modified_by)
        
    def test_partial_update(self):
        TARG_USER=self.get_target_user()
        new_obj = self.create_object(TARG_USER)
        TARG_OBJ = self.get_target_object()
        DATA = self.get_update_data(TARG_OBJ, new_obj)
        
        self.client.force_authenticate(user=TARG_USER)
        self.assertTrue(TARG_USER.has_perm(make_perm(new_obj.__class__,
                                                            'change'),
                                           TARG_OBJ
                                           )
                        )
        url = reverse(self.named_view_base+'-detail',
                      kwargs={'pk':TARG_OBJ.pk},
                      current_app=self.namespace)
        kwargs = {}
        for val in DATA.values():
            if isinstance(val,File):
                kwargs['format'] = 'multipart'
        
        res = self.client.patch(url,data=DATA, **kwargs)
        self.assertEqual(200,res.status_code)
        
        u = refetch(TARG_OBJ)
        for field in DATA:
            self.compare_field(field,DATA[field],u)
        EXTRA_DATA = self.get_extra_data(TARG_OBJ.owner)
        for field in EXTRA_DATA:
            self.compare_field(field,EXTRA_DATA[field],u)
    
    def test_partial_update_cross_org_bad(self):
        TARG_USER=self.get_cross_org_user()
        new_obj = self.create_object(TARG_USER)
        TARG_OBJ = self.get_target_object()
        DATA = self.get_update_data(TARG_OBJ, new_obj)
        
        self.client.force_authenticate(user=TARG_USER)
        self.assertFalse(TARG_USER.has_perm(make_perm(TARG_OBJ,
                                                            'change'),
                                           TARG_OBJ
                                           )
                        )
        url = reverse(self.named_view_base+'-detail',
                      kwargs={'pk':TARG_OBJ.pk},
                      current_app=self.namespace)
        kwargs = {}
        for val in DATA.values():
            if isinstance(val,File):
                kwargs['format'] = 'multipart'
        res = self.client.put(url, data=DATA, **kwargs)
        self.assertEqual(404,res.status_code)
        rf = refetch(TARG_OBJ)
        self.assertEqual(TARG_OBJ.modified,rf.modified)
        self.assertEqual(TARG_OBJ.modified_by,rf.modified_by)
    
    def test_partial_update_bad_read_only_field(self):
        TARG_USER=self.get_target_user()
        new_obj = self.create_object(TARG_USER)
        TARG_OBJ = self.get_target_object()
        DATA = self.get_create_only_data(TARG_OBJ, new_obj)
        
        self.client.force_authenticate(user=TARG_USER)
        self.assertTrue(TARG_USER.has_perm(make_perm(new_obj.__class__,
                                                            'change'),
                                           TARG_OBJ
                                           )
                        )
        url = reverse(self.named_view_base+'-detail',
                      kwargs={'pk':TARG_OBJ.pk},
                      current_app=self.namespace)
        kwargs = {}
        for val in DATA.values():
            if isinstance(val,File):
                kwargs['format'] = 'multipart'
        res = self.client.patch(url, data=DATA, **kwargs)
        self.assertEqual(400,res.status_code)
        self.assertTrue('no fields' in str(res.content).lower())
        
        u = refetch(TARG_OBJ)
        for field in DATA:
            self.compare_field_with_objs(field, TARG_OBJ, u)
        if isinstance(TARG_OBJ, UserOwnedModel):
            for field in USER_OWNED_META_FIELDS:
                self.compare_field_with_objs(field, TARG_OBJ, u)
            
    def test_delete(self):
        TARG_USER=self.get_target_user()
        TARG_OBJ = self.get_target_object()
        self.client.force_authenticate(user=TARG_USER)
        self.assertTrue(TARG_USER.has_perm(make_perm(TARG_OBJ,
                                                            'delete'),
                                           TARG_OBJ
                                           )
                        )
        url = reverse(self.named_view_base+'-detail',
                      kwargs={'pk':TARG_OBJ.pk},
                      current_app=self.namespace)
        res = self.client.delete(url)
        
        self.assertEqual(204,res.status_code)
        self.assertRaises(TARG_OBJ.__class__.DoesNotExist,
                          refetch, TARG_OBJ)
    
    def test_delete_user_bad(self):
        TARG_OBJ = self.get_target_object()
        TARG_USER=self.get_unauthorized_user(TARG_OBJ)
        
        self.client.force_authenticate(user=TARG_USER)
        self.assertFalse(TARG_USER.has_perm(make_perm(TARG_OBJ,
                                                            'delete'),
                                           TARG_OBJ
                                           )
                        )
        url = reverse(self.named_view_base+'-detail',
                      kwargs={'pk':TARG_OBJ.pk},
                      current_app=self.namespace)
        res = self.client.delete(url)
        # If the other user can't even see it then this is a 404
        try:
            self.assertEqual(403,res.status_code)
        except AssertionError:
            self.assertEqual(404,res.status_code)
        self.assertTrue(refetch(TARG_OBJ))
    
    def test_delete_cross_org_bad(self):
        TARG_OBJ = self.get_target_object()
        TARG_USER=self.get_cross_org_user()
        
        self.client.force_authenticate(user=TARG_USER)
        self.assertFalse(TARG_USER.has_perm(make_perm(TARG_OBJ,
                                                            'delete'),
                                           TARG_OBJ
                                           )
                        )
        url = reverse(self.named_view_base+'-detail',
                      kwargs={'pk':TARG_OBJ.pk},
                      current_app=self.namespace)
        res = self.client.delete(url)
        self.assertEqual(404,res.status_code)
        self.assertTrue(refetch(TARG_OBJ))
        