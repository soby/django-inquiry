from .....core.api.v1.serializers import base
from .... import models

SECTION_OWNED_READ_ONLY_FIELDS = base.USER_OWNED_READ_ONLY_FIELDS +\
    ['parent']
SECTION_OWNED_QUERYSET_RESTRICTIONS =\
    dict(base.USER_OWNED_QUERYSET_RESTRICTIONS,
         parent=models.Survey)

RESPONSE_OWNED_READ_ONLY_FIELDS = base.USER_OWNED_READ_ONLY_FIELDS +\
    ['survey']
RESPONSE_OWNED_QUERYSET_RESTRICTIONS =\
    dict(base.USER_OWNED_QUERYSET_RESTRICTIONS,
         survey=models.Survey,
         response=models.Response)
    
RESPONSE_SECTION_OWNED_READ_ONLY_FIELDS = \
    RESPONSE_OWNED_READ_ONLY_FIELDS + ['response']
RESPONSE_SECTION_OWNED_QUERYSET_RESTRICTIONS =\
    dict(RESPONSE_OWNED_QUERYSET_RESTRICTIONS,
         section=models.ResponseSection)