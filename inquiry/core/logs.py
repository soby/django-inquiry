from django.conf import settings
import logging


class ExtraDataFilter(logging.Filter):
    def filter(self, record):
        record.app_name = settings.APP_NAME
        if hasattr(record, 'user'):
            record.user = record.user
            if not hasattr(record, 'org'):
                record.org = getattr(record.user, 'org', None)
        elif hasattr(record, 'request'):
            user = getattr(record.request, 'user', None)
            record.user = user
            if not hasattr(record, 'org'):
                if user:
                    record.org = getattr(user, 'org', None)
                else:
                    record.org = None
        else:
            record.user = 'no_user'
            record.org = 'no_org'

        return True
