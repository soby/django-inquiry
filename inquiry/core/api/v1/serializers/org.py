import logging
LOGGER = logging.getLogger(__name__)

from .base import BaseModelSerializer
from ....utils.auth import get_org_model

Org = get_org_model()


class OrgSerializer(BaseModelSerializer):
    class Meta:
        model = Org
        fields = ['id', 'name', 'subdomain', 'preference_auth_google_oauth2',
                  'preference_auth_email_autocreate_domains',]
