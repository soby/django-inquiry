import logging
LOGGER = logging.getLogger(__name__)

from rest_framework import serializers
from django.contrib.auth import models as auth_models
from django.contrib.auth import get_user_model

from .... import models
from .base import BaseModelSerializer, FieldRestrictingMixin


class GroupDisplayField(serializers.StringRelatedField):
    """
        Read-only field to show pretty names for group but not accept updates
    """
    def to_representation(self, value):
        return {'id': value.id, 'name': value.name.split('_')[-1]}


class UserSerializer(FieldRestrictingMixin, BaseModelSerializer):
    _QUERYSET_RESTRICTIONS = {'groups': models.Group}

    groups = GroupDisplayField(many=True, read_only=True)
    
    def validate(self, attrs, *args, **kwargs):
        if self.data.get('id'):
            # No changing the username after create
            if attrs.has_key('username'):
                del attrs['username']
        return super(UserSerializer,self).validate(attrs, *args, **kwargs)

    class Meta:
        model = models.User
        fields = ('id', 'username', 'email', 'first_name', 'last_name' , 
                  'phone', 'group', 'title', 'is_active', 'groups')
        read_only_fields = ['id', 'groups']


class GroupNameDisplayField(serializers.StringRelatedField):
    """
        Read-only field to show pretty names for group but not accept updates.
        Similar to above but gets the value from a different place
    """
    def to_representation(self, value):
        return value.split('_')[-1]


class GroupSerializer(FieldRestrictingMixin, BaseModelSerializer):
    _QUERYSET_RESTRICTIONS = {'user_set': get_user_model()}

    name = GroupNameDisplayField()

    class Meta:
        model = auth_models.Group
        fields = ('id', 'name', 'user_set')
        # Name is implied
        read_only_fields = ['id', 'name']
