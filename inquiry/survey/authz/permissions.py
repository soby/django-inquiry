from ...core.auth.permissions import OwnedModelPermissions


class ResponseOwnedModelPermissions(OwnedModelPermissions):
    parent_key = 'response'