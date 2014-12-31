from __future__ import absolute_import

import urlparse
import logging
LOGGER = logging.getLogger(__name__)

from django.views.generic.base import View,TemplateResponseMixin
from django.template import RequestContext
from django.http import HttpResponseBadRequest
from django.core.urlresolvers import reverse

from social.backends.google import GoogleOAuth2
from social.exceptions import AuthException

from ..utils.auth import get_org_model

# From https://github.com/omab/python-social-auth/blob/master/social/pipeline/social_auth.py
def associate_by_email_and_allowed_org(backend, details, user=None, *args, **kwargs):
    """
    Associate current auth with a user with the same email address in the DB.
    This pipeline entry is not 100% secure unless you know that the providers
    enabled enforce email verification on their side, otherwise a user can
    attempt to take over another user account by using the same (not validated)
    email address on some provider.  This pipeline entry is disabled by
    default.
    """
    if user:
        return None

    email = details.get('email')
    if email:
        # Try to associate accounts registered with the same email address,
        # only if it's a single object. AuthException is raised if multiple
        # objects are returned. The org must have the google oauth 2 preference
        # enabled
        if backend.name == ConfigurableRedirectGoogleOauth2Backend.name:
            backend_pref = 'org__preference_auth_google_oauth2'
        else:
            LOGGER.error('Unconfigured social oauth [%s] backend for mapping user "%s"' % (backend.name,email))
            return None

        users = list(backend.strategy.storage.user.user_model().objects.filter(username__iexact=email,is_active=True,**{backend_pref:True}))

        if len(users) == 0:
            LOGGER.error('No social user found for backend %s and email %s' % (backend.name,email))
            return None
        elif len(users) > 1:
            LOGGER.error('Multiple users found for backend %s and email %s' % (backend.name,email))
            raise AuthException(
                backend,
                'The given email address is associated with another account'
            )
        else:
            LOGGER.warn('Mapping %s social user %s to internal username %s and pk %s' % (backend.name,email,users[0].username,users[0].id))
            return {'user': users[0]}


#https://github.com/omab/python-social-auth/blob/master/social/pipeline/user.py#L71
# But with a whitelist
def user_details(strategy, details, user=None, *args, **kwargs):
    """Update user details using data from provider."""
    if user:
        changed = False  # flag to track changes
        safe_fields = strategy.setting('SAFE_USER_FIELDS', [])

        for name, value in details.items():
            if not name in safe_fields:
                continue

            if hasattr(user, name):
                if value and value != getattr(user, name, None):
                    try:
                        setattr(user, name, value)
                        changed = True
                    except AttributeError:
                        pass

        if changed:
            strategy.storage.user.changed(user)

# https://github.com/omab/python-social-auth/blob/master/social/pipeline/user.py#L56
# but with domain whitelisting
def create_user(strategy, details, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    fields = dict((name, kwargs.get(name) or details.get(name))
                        for name in strategy.setting('SAFE_USER_FIELDS',
                                                      []))
    if not fields:
        return
    
    email = details.get('email')
    if not email:
        return
    domain = ''.join(email.split('@')[1:])
    allowedOrg = None
    for org in get_org_model().objects.all():
        if not org.preference_auth_email_autocreate_domains:
            continue
        else:
            domains = [x.strip() for x in 
                       org.preference_auth_email_autocreate_domains.split(',')]
            if domain in domains:
                allowedOrg = org
    if not allowedOrg:
        return None
    
    fields['org'] = allowedOrg
    fields['username'] = email
    
    return {
        'is_new': True,
        'user': strategy.create_user(**fields)
    }
    
class ConfigurableRedirectGoogleOauth2Backend(GoogleOAuth2):
    """ Google is really anal about redirect_uri always being pre-configured. 
        Since we have a subdomain per customer, that doesn't really work for us.
        This backend allows for a setting to override the redirect URI and
        puts a hint about the original subdomain into the oauth strate
    """

    name = 'google-oauth2-inquiry'

    def _get_subdomain(self,url):
        """
            Anything 3 or more levels is considered to have a subdomain. Anything
            less than 3 levels is considered to be without a subdomain. This allows
            for localhost or localhost.domain
        """
        parts = urlparse.urlparse(url).netloc.split('.')
        if len(parts) >= 3:
            if parts[0]:
                return parts[0]
            else:
                return None
        else:
            return None

    def state_token(self): 
        """ Generate csrf token to include as state parameter.
            From https://github.com/omab/python-social-auth/blob/master/social/backends/oauth.py OAuthAuth
        """
        token = super(ConfigurableRedirectGoogleOauth2Backend,self).state_token().replace('|','A')

        if self.setting('OVERRIDE_REDIRECT_URI_SUBDOMAIN', None):
            # We need to add the current request subdomain so our external redirector
            # knows where to send the user. To do this, we'll yank it off of the 
            # parent's redirect URI (not our modified version)
            current_subdomain = self._get_subdomain(self.redirect_uri)
            token += '|{0}'.format(current_subdomain or '')
        return token

    def get_redirect_uri(self, state=None):
        """ Build redirect with redirect_state parameter.
            From https://github.com/omab/python-social-auth/blob/master/social/backends/oauth.py OAuthAuth
        """
        redirect_uri = super(ConfigurableRedirectGoogleOauth2Backend,self).get_redirect_uri(state)

        override = self.setting('OVERRIDE_REDIRECT_URI_SUBDOMAIN', None)
        if override:
            subdomain = self._get_subdomain(redirect_uri)
            parts = urlparse.urlparse(redirect_uri) 
            path = parts.path
            if not self.setting('OVERRIDE_REDIRECT_URI_REDIRECTOR_NAME',None):
                raise Exception('Must set SOCIAL_AUTH_<BACKEND_NAME>_OVERRIDE_REDIRECT_URI_REDIRECTOR_NAME to a reversible view name when using OVERRIDE_REDIRECT_URI_SUBDOMAIN')
            redirected_path = reverse(self.setting('OVERRIDE_REDIRECT_URI_REDIRECTOR_NAME'),kwargs={'target_uri':path})
            if subdomain:
                redirect_fqdn = parts.netloc.replace(subdomain,override,1)
            else:
                redirect_fqdn = '{0}.{1}'.format(override,parts.netloc)

            redirect_uri = '{0}://{1}{2}'.format(parts.scheme,redirect_fqdn,redirected_path)

        return redirect_uri

    @classmethod
    def get_original_subdomain_from_params(cls,params):
        """
            The state would look like <token>|subdomain
        """
        state = params.get('state','')
        parts = state.split('|')
        if len(parts) == 2:
            sub = parts[1].strip()
            if sub:
                return sub
            else:
                return None
        return None

class SavedSubdomainInStateRedirectorView(View,TemplateResponseMixin):
    template_name = 'core/auth/social/redirect.html'

    def get(self,request,*args, **kwargs):
        """
            The auth provider send the user back to soemthing like:
                /<this view's path>/<real target_uri>
            Urls.py should strip off this view's path and pass the rest in as
            target_uri. This view redirects the user to the subdomain in the state
            plus the target URI. It's essentially a simple redirector to allow us to
            configure Google's allowed redirect_uri's with a consistent URI
        """

        target_uri = self.kwargs.get('target_uri',None)
        if not target_uri:
            return HttpResponseBadRequest('No target_uri')

        if target_uri.startswith('//'):
            # arbitrary redirection attempt?
            return HttpResponseBadRequest('Bad target_uri: {0}'.format(target_uri))

        # Note that a subdomain of None will cause us to strip any current subdomain
        subdomain = ConfigurableRedirectGoogleOauth2Backend.get_original_subdomain_from_params(request.GET)

        requested_host = request.get_host()
        parts = requested_host.split('.')
        if subdomain:
            # Ok, we have a subdomain that we're going to replace
            if len(parts) >= 3:
                # replace
                new_fqdn = '{0}.{1}'.format(subdomain,'.'.join(parts[1:]))
            else:
                # we're likely using an unqualified hostname for testing (e.g. localhost)
                # Add the subdomain
                new_fqdn = '{0}.{1}'.format(subdomain,'.'.join(parts))
        else:
            # No subdomain. Strip the subdomain or leave it alone
            if len(parts) >= 3:
                # Strip
                new_fqdn = '.'.join(parts[1:])
            else:
                new_fqdn = requested_host

        if new_fqdn == requested_host:
            form_action = target_uri
        else:
            if request.is_secure():
                scheme = 'https://'
            else:
                scheme = 'http://'
            form_action = '{0}{1}{2}'.format(scheme,new_fqdn,target_uri)

        context = RequestContext(request,{'action':form_action,'form_params':request.GET})
        return self.render_to_response(context)
