#https://github.com/rdegges/django-sslify/blob/master/sslify/middleware.py

from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class SSLifyMiddleware(object):

    def process_request(self, request):
        if not any([settings.ALLOW_NON_SSL,request.is_secure(),request.META.get("HTTP_X_FORWARDED_PROTO", "") == 'https']):
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace('http://', 'https://')
            return HttpResponsePermanentRedirect(secure_url)