from rest_framework import authentication
from rest_framework import exceptions

from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model

from django.core.urlresolvers import resolve


class SessionAuthorizationHeaderAuthentication(
                 authentication.BaseAuthentication):
    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()

        if not auth or auth[0].lower() != u'session':
            return None
        if len(auth) == 1:
            msg = 'Invalid authorization session header. '\
                    'No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid authorization session header. '\
                    'Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        res = self.authenticate_credentials(auth[1])
        if isinstance(res, tuple):
            user, session_key = res #@UnusedVariable

            # Logout needs this to work properly. Possibly when the user has
            # both a cookie-based session and an Authorization header
            request.session._session_key = session_key
        return res

    def authenticate_credentials(self, key):
        try:
            session = Session.objects.get(session_key=key)
        except Session.DoesNotExist:
            return None
        session_data = session.get_decoded()
        uid = session_data.get('_auth_user_id')
        User = get_user_model()
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return None
        return (user, key)


class SessionAuthentication(authentication.SessionAuthentication):
    def enforce_csrf(self, request):
        """
        Enforce CSRF validation for session based authentication.
        Respect csrf_exempt dammit!
        """

        func, args, kwargs = resolve(request.path_info) #@UnusedVariable
        if getattr(func, 'csrf_exempt', None):
            return

        reason = authentication.CSRFCheck().process_view(request, None, (), {})
        if reason:
            # CSRF failed, bail with explicit error message
            raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)
