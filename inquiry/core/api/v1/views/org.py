from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route
from . import base
from ..serializers import org

class OrgViewSet(base.BaseAPIViewMixin,viewsets.ReadOnlyModelViewSet):
    serializer_class = org.OrgSerializer
    queryset = serializer_class.Meta.model.objects.none()  # Required for DjangoObjectPermissions

    @list_route(methods=['get'])
    def my(self, request, pk=None):
        return Response(self.get_serializer(instance=request.user.org).data)