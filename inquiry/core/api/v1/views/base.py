import inspect

from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework import status
from rest_framework.exceptions import ValidationError

from ....utils.auth import get_org_model
from ....auth.permissions import OwnedModelPermissions
from ....models import OrgOwnedModel, UserOwnedModel

import logging
LOGGER = logging.getLogger(__name__)

Org = get_org_model()

def is_sub(classOrInstance,superclass):
    if inspect.isclass(classOrInstance):
        return issubclass(classOrInstance,superclass)
    else:
        return isinstance(classOrInstance,superclass)


class OrderableViewMixin(object):

    @detail_route(methods=['patch'])
    def order_up(self, request, pk=None):
        u = self.get_object()
        u.up()
        u = self.serializer_class.model.objects.get(pk=u.pk)
        serializer = self.get_serializer(u)
        return Response(serializer.data)
        
    @detail_route(methods=['patch'])
    def order_down(self, request, pk=None):
        u = self.get_object()
        u.down()
        u = self.serializer_class.model.objects.get(pk=u.pk)
        serializer = self.get_serializer(u)
        return Response(serializer.data)

    @detail_route(methods=['patch'])
    def order_top(self, request, pk=None):
        u = self.get_object()
        u.top()
        u = self.serializer_class.model.objects.get(pk=u.pk)
        serializer = self.get_serializer(u)
        return Response(serializer.data)
        
    @detail_route(methods=['patch'])
    def order_bottom(self, request, pk=None):
        u = self.get_object()
        u.bottom()
        u = self.serializer_class.model.objects.get(pk=u.pk)
        serializer = self.get_serializer(u)
        return Response(serializer.data)
    
    @detail_route(methods=['patch'])
    def order_to(self, request, pk=None):
        order = request.DATA.get('order')
        if not order:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':'order parameter not provided'})
        try:
            order = int(order)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':'order parameter invalid'})
            
        u = self.get_object()
        try:
            u.to(order)
        except Exception as e:
            LOGGER.error('Unable to change order for {0} to {1}: {2}'.\
                         format(u,order,e),extra={'user':request.user})
            
        u = self.serializer_class.model.objects.get(pk=u.pk)
        serializer = self.get_serializer(u)
        return Response(serializer.data)
    
    @detail_route(methods=['patch'])
    def order_above(self, request, pk=None):
        target_id = request.DATA.get('target_id')
        if not target_id:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':
                                      'target_id parameter not provided'})
        try:
            target = self.get_queryset().get(pk=target_id)
        except self.serializer_class.model.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':'target not found'})
            
        u = self.get_object()
        try:
            u.above(target)
        except Exception as e:
            LOGGER.error('Unable to change order for {0} above {1}: {2}'.\
                         format(u,target,e),extra={'user':request.user})
            
        u = self.serializer_class.model.objects.get(pk=u.pk)
        serializer = self.get_serializer(u)
        return Response(serializer.data)
    
    @detail_route(methods=['patch'])
    def order_below(self, request, pk=None):
        target_id = request.DATA.get('target_id')
        if not target_id:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':
                                      'target_id parameter not provided'})
        try:
            target = self.get_queryset().get(pk=target_id)
        except self.serializer_class.model.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':'target not found'})
            
        u = self.get_object()
        try:
            u.below(target)
        except Exception as e:
            LOGGER.error('Unable to change order for {0} below {1}: {2}'.\
                         format(u,target,e),extra={'user':request.user})
            
        u = self.serializer_class.model.objects.get(pk=u.pk)
        serializer = self.get_serializer(u)
        return Response(serializer.data)


class BaseAPIViewMixin(object):
    #http://www.django-rest-framework.org/api-guide
    #    /permissions#djangomodelpermissions
    queryset = Org.objects.none()  # Required for DjangoObjectPermissions

    def perform_create(self, serializer, *args, **kwargs):
        if not serializer.validated_data:
            raise ValidationError(detail='No fields for creation')
        
        if hasattr(self,'request') and hasattr(self.request, 'user'):
            if is_sub(serializer.Meta.model,OrgOwnedModel):
                # I think this is a DRF bug. You have to set it here and not 
                # .data for it to persist
                serializer.validated_data['org_id'] = self.request.user.org_id
            if is_sub(serializer.Meta.model,UserOwnedModel):
                serializer.validated_data['owner_id'] =\
                    self.request.user.pk
                serializer.validated_data['created_by_id'] =\
                    self.request.user.pk
                    
        try:
            res = super(BaseAPIViewMixin, self).perform_create(serializer, 
                                                               *args, **kwargs)
        except AttributeError:
            # super() is only possible when we're mixed in. 
            # This is probably a direct usage in testing
            if self.__class__.__name__ != 'BaseAPIViewMixin':
                raise
            else:
                return None
        # I also think this is a bug in DRF. Created object ID isn't 
        # serialized back out
        # Build _data cache
        serializer.data
        # Set value in underlying object
        serializer._data['id'] = serializer.instance.id
        return res

    def perform_update(self, serializer, *args, **kwargs):
        if not serializer.validated_data:
            raise ValidationError(detail='No fields for update')
        
        if hasattr(self,'request') and hasattr(self.request, 'user'):
            if isinstance(serializer.Meta.model, UserOwnedModel):
                serializer.validated_data['modified_by_id'] =\
                    self.request.user.pk
        try:
            res = super(BaseAPIViewMixin, self).perform_update(serializer, 
                                                               *args, **kwargs)
        except AttributeError:
            # super() is only possible when we're mixed in. 
            # This is probably a direct usage in testing
            if self.__class__.__name__ != 'BaseAPIViewMixin':
                raise
            else:
                return None
        return res

    def check_object_permissions(self, request, obj):
        """
            Modified to check for the use of our ParentOwnedPermission. It
            needs to check the permission on the parent object instead of
            the target object itself
        """
        for permission in self.get_permissions():
            if isinstance(permission, OwnedModelPermissions):
                parent = getattr(obj, permission.parent_key, None)
                if not permission.has_object_permission(request, self, parent):
                    self.permission_denied(request)
            else:
                if not permission.has_object_permission(request, self, obj):
                    self.permission_denied(request)
                
    def get_queryset(self):
        return self.serializer_class.Meta.model.manager\
                                                .for_user(self.request.user)