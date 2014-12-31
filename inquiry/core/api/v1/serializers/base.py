from django.contrib.auth import get_user_model

from rest_framework import serializers

import logging
LOGGER = logging.getLogger(__name__)

ORG_OWNED_READ_ONLY_FIELDS = ['id','created','modified']
ORG_OWNED_QUERYSET_RESTRICTIONS = {}

USER_OWNED_READ_ONLY_FIELDS = ORG_OWNED_READ_ONLY_FIELDS +\
                              ['created_by','owner','modified_by']                         
USER_OWNED_QUERYSET_RESTRICTIONS = {'created_by':get_user_model(),
                                    'owner':get_user_model()}                              


class CreateOnlyFieldsMixin(object):
    
    def to_internal_value(self,data):
        res = super(CreateOnlyFieldsMixin,self).to_internal_value(data)
        
        if not self.instance or not getattr(self.Meta,'create_only_fields',[]):
            return res
        
        for field in self.Meta.create_only_fields:
            if field in res.keys():
                # make sure they're the same value and we're not trying to
                # change it
                del res[field]
        return res            
             
        
        
class BaseModelSerializer(CreateOnlyFieldsMixin, serializers.ModelSerializer):
    pass


class FieldRestrictingMixin(object):
    """
        This mixin restricts the querysets available for read/writing at
        runtime based on the user. To use, set the field names that are exposed
        by the serializer and the associated model class. It expects the model
        class to have a manager called "manager" that has a queryset
        restriction function called for_user(user)
    """
    # in child class set like: {fieldName: ModelClass}
    _QUERYSET_RESTRICTIONS = None

    def get_fields(self, *args, **kwargs):
        fields = super(FieldRestrictingMixin, self).get_fields(*args, **kwargs)
        if not self._QUERYSET_RESTRICTIONS:
            return fields

        request = getattr(self, 'context', {}).get('request')
        if not request:
            LOGGER.error('No request in context for serializer {0}'
                            .format(self), extra={'request': request})

        for fieldName, modelCls in self._QUERYSET_RESTRICTIONS.items():
            if not request:
                fields[fieldName].queryset = modelCls.objects.none()
                if hasattr(fields[fieldName], 'child_relation'):
                    fields[fieldName].child_relation.queryset = \
                                                modelCls.objects.none()
            else:
                try:
                    fields[fieldName].queryset = \
                                    modelCls.manager.for_user(request.user)
                    if hasattr(fields[fieldName], 'child_relation'):
                        fields[fieldName].child_relation.queryset = \
                                        modelCls.manager.for_user(request.user)
                except AttributeError as e:
                    LOGGER.critical('Likely missing a manager.for_user() on '
                                    'cls {0}: {1}'.format(modelCls,e))
                    #TODO: raise ImplentationError or something
                    raise
                except Exception as e:
                    LOGGER.critical('Unknown exception setting ' 
                                    'user.for_user() on cls {0}: {1}'
                                    .format(modelCls, e))
                    raise
        return fields
