from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.compat import get_model_name

class OwnedModelPermissions(DjangoObjectPermissions):
    parent_key = 'parent'
    
    # Since we're essentially deferring to access on a parent object, 
    # we're considering add and delete to be changes to the parent
    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        #'POST': ['%(app_label)s.add_%(model_name)s'],
        'POST': ['%(app_label)s.change_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        #'DELETE': ['%(app_label)s.delete_%(model_name)s'
        'DELETE': ['%(app_label)s.change_%(model_name)s'],
    }
    
    def get_required_object_permissions(self, method, model_cls):
        
        parent_model = model_cls._meta.get_field(self.parent_key).rel.to
        kwargs = {
                  
            'app_label': parent_model._meta.app_label,
            'model_name': get_model_name(parent_model)
        }
        return [perm % kwargs for perm in self.perms_map[method]] 