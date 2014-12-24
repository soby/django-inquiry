from django.test import TestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from urlparse import parse_qs, urlparse

import mock
import re

from ...auth import social



class TestFuncs(TestCase):
    def test_associate_by_email_and_allowed_org_user_fail(self):
        # No idea why this is desired by it was in the code i copied
        # If you give this pipeline function a user, it should return None
        self.assertEqual(social.associate_by_email_and_allowed_org('blah',{},'SomeUser'),None)
    def test_associate_by_email_and_allowed_org_unsupported_backend_fail(self):
        backend = mock.Mock()
        backend.name = 'asdf'
        self.assertEqual(social.associate_by_email_and_allowed_org(backend(),{}),None)
    def test_associate_by_email_and_allowed_org_no_mapping_fail(self):
        backend = mock.Mock()
        backend.name = social.ConfigurableRedirectGoogleOauth2Backend.name
        backend.strategy.storage.user.user_model.return_value.objects.filter.return_value=[]

        self.assertEqual(social.associate_by_email_and_allowed_org(backend,{'email':'blah'}),None)
        self.assertTrue(backend.strategy.storage.user.user_model.return_value.objects.filter.called_with(username__iexact='blah',is_active=True,org__preference_auth_google_oauth2=True))
    def test_associate_by_email_and_allowed_org_too_many_mappings_fail(self):
        backend = mock.Mock()
        backend.name = social.ConfigurableRedirectGoogleOauth2Backend.name
        backend.strategy.storage.user.user_model.return_value.objects.filter.return_value=[1,2]

        self.assertRaises(social.AuthException,social.associate_by_email_and_allowed_org,backend,{'email':'blah'})
        self.assertTrue(backend.strategy.storage.user.user_model.return_value.objects.filter.called_with(username__iexact='blah',is_active=True,org__preference_auth_google_oauth2=True))
    def test_associate_by_email_and_allowed_org_good(self):
        user = mock.Mock()
        user.username = 'blahuser'

        backend = mock.Mock()
        backend.name = social.ConfigurableRedirectGoogleOauth2Backend.name
        backend.strategy.storage.user.user_model.return_value.objects.filter.return_value=[user]

        self.assertEqual(social.associate_by_email_and_allowed_org(backend,{'email':'blah'}),{'user':user})
        self.assertTrue(backend.strategy.storage.user.user_model.return_value.objects.filter.called_with(username__iexact='blah',is_active=True,org__preference_auth_google_oauth2=True))
        
    def test_user_details_noop(self):
        # make sure nothing happen without a user
        self.assertEqual(social.user_details('blahstrategy',{},None),None)

    def test_user_details_nochange(self):
        user = mock.Mock()
        strategy = mock.Mock()
        social.user_details(strategy,{},user)     
        self.assertFalse(strategy.storage.user.changed.mock_calls)

    def test_user_details_unsafe_skip(self):
        user = mock.Mock()
        strategy = mock.Mock()
        strategy.setting.return_value=['blah']
        social.user_details(strategy,{'other':123},user)        
        self.assertFalse(strategy.storage.user.changed.mock_calls)
        self.assertNotEqual(user.other,'blah')

    def test_user_details_safe_apply(self):
        user = mock.Mock()
        user.parse_user = None
        strategy = mock.Mock()
        strategy.setting.return_value=['blah']
        social.user_details(strategy,{'other':123,'blah':456},user)        
        self.assertTrue(strategy.storage.user.changed.mock_calls)
        self.assertNotEqual(user.other,'blah')
        self.assertEqual(user.blah,456)

class ConfigurableRedirectGoogleOauth2BackendTest(TestCase):
    def setUp(self):
        self.backend = social.ConfigurableRedirectGoogleOauth2Backend()

    def test_get_subdomain(self):
        self.assertEqual(self.backend._get_subdomain('http://blah.stuff.com/asdf'),'blah')
        self.assertEqual(self.backend._get_subdomain('http://stuff.com/asdf'),None)
        self.assertEqual(self.backend._get_subdomain('http://stuff/asdf'),None)
        self.assertEqual(self.backend._get_subdomain('http://moo.blah.stuff.com/asdf'),'moo')
        self.assertEqual(self.backend._get_subdomain('http://moo.blah.stuff.com'),'moo')

    def test_state_token_normal(self):
        setting = mock.Mock()
        setting.return_value = False
        strategy = mock.Mock()
        strategy.random_string.return_value = '12345'
        self.backend.strategy = strategy
        self.backend.setting = setting
        self.assertEqual(self.backend.state_token(),'12345')

    def test_state_token_override(self):
        setting = mock.Mock()
        setting.return_value = True
        strategy = mock.Mock()
        strategy.random_string.return_value = '12345'
        self.backend.strategy = strategy
        self.backend.setting = setting
        self.backend.redirect_uri = 'http://blah.stuff.com/alskdf/asfd'
        self.assertEqual(self.backend.state_token(),'12345|blah')

    def test_get_redirect_uri_normal(self):
        self.backend.get_redirect_uri = lambda x: 'http://stuff.blah.com/asf'
        setting = mock.Mock()
        setting.return_value = None
        self.assertEqual(self.backend.get_redirect_uri('asdf'),'http://stuff.blah.com/asf')

    def test_get_redirect_uri_missing_redirector_name(self):
        self.backend.redirect_uri = 'http://stuff.blah.com/asf'
        setting = mock.Mock()
        # do override
        def x(setting,default=None):
            if setting == 'OVERRIDE_REDIRECT_URI_SUBDOMAIN':
                return 'id'
            else:
                return None #'auth/social/bounce'

        setting.side_effect = x
        self.backend.setting = setting
        self.assertRaises(Exception,self.backend.get_redirect_uri,'asdf')

    def test_get_redirect_uri_no_sub(self):
        self.backend.redirect_uri = 'http://blah.com/some/asf'
        setting = mock.Mock()
        # do override
        def x(setting,default=None):
            if setting == 'OVERRIDE_REDIRECT_URI_SUBDOMAIN':
                return 'id'
            else:
                return 'auth/social/bounce'

        setting.side_effect = x
        self.backend.setting = setting
        redir_path = reverse('auth/social/bounce',kwargs={'target_uri':'/some/asf'})
        self.assertEqual(self.backend.get_redirect_uri('asdf|stuff'),'http://id.blah.com'+redir_path)

    def test_get_redirect_uri_normal_override(self):
        self.backend.redirect_uri = 'http://stuff.blah.com/some/asf'
        setting = mock.Mock()
        # do override
        def x(setting,default=None):
            if setting == 'OVERRIDE_REDIRECT_URI_SUBDOMAIN':
                return 'id'
            else:
                return 'auth/social/bounce'

        setting.side_effect = x
        self.backend.setting = setting
        redir_path = reverse('auth/social/bounce',kwargs={'target_uri':'/some/asf'})
        self.assertEqual(self.backend.get_redirect_uri('asdf|stuff'),'http://id.blah.com'+redir_path)

    def test_get_original_subdomain_from_params_normal(self):
        params = {'state':'blah'}
        self.assertEqual(self.backend.get_original_subdomain_from_params(params),None)
    def test_get_original_subdomain_from_params_with_sub(self):
        params = {'state':'blah|stuff'}
        self.assertEqual(self.backend.get_original_subdomain_from_params(params),'stuff')
    def test_get_original_subdomain_from_params_invalid(self):
        params = {'state':'blah|stuff|more'}
        self.assertEqual(self.backend.get_original_subdomain_from_params(params),None)
    def test_get_original_subdomain_from_params_no_state(self):
        params = {'statezzzzz':'blah'}
        self.assertEqual(self.backend.get_original_subdomain_from_params(params),None)
    def test_name(self):
        self.assertEqual(self.backend.name,'google-oauth2-inquiry')

    @override_settings(SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_OVERRIDE_REDIRECT_URI_SUBDOMAIN='id',
                       SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_OVERRIDE_REDIRECT_URI_REDIRECTOR_NAME='auth/social/bounce')
    def test_client_good_nosubdom(self):
        res = self.client.get(reverse('social:begin',kwargs={'backend':'google-oauth2-inquiry'}))
        self.assertEqual(res.status_code,302)
        redir = res['Location']
        params = parse_qs(urlparse(redir).query, keep_blank_values=True)
        uri = params['redirect_uri'][0]
        goal = '{0}{1}'.format('http://id.testserver',reverse('auth/social/bounce',kwargs={'target_uri':reverse('social:complete',kwargs={'backend':'google-oauth2-inquiry'})}))
        self.assertEqual(uri,goal)
        state = params['state'][0]
        self.assertTrue(state.endswith('|'))

    @override_settings(SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_OVERRIDE_REDIRECT_URI_SUBDOMAIN='id',
                       SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_OVERRIDE_REDIRECT_URI_REDIRECTOR_NAME='auth/social/bounce')
    def test_client_good_subdom(self):
        res = self.client.get(reverse('social:begin',kwargs={'backend':'google-oauth2-inquiry'}),HTTP_HOST='blah.stuff.com')
        self.assertEqual(res.status_code,302)
        redir = res['Location']
        params = parse_qs(urlparse(redir).query, keep_blank_values=True)
        uri = params['redirect_uri'][0]
        goal = '{0}{1}'.format('http://id.stuff.com',reverse('auth/social/bounce',kwargs={'target_uri':reverse('social:complete',kwargs={'backend':'google-oauth2-inquiry'})}))
        self.assertEqual(uri,goal)
        state = params['state'][0]
        self.assertTrue('|blah' in state)

    @override_settings(SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_OVERRIDE_REDIRECT_URI_SUBDOMAIN='id',
                       SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_OVERRIDE_REDIRECT_URI_REDIRECTOR_NAME='auth/social/bounce')
    def test_client_good_secure(self):
        res = self.client.get(reverse('social:begin',kwargs={'backend':'google-oauth2-inquiry'}),secure=True,HTTP_HOST='blah.stuff.com')
        self.assertEqual(res.status_code,302)
        redir = res['Location']
        params = parse_qs(urlparse(redir).query, keep_blank_values=True)
        uri = params['redirect_uri'][0]
        goal = '{0}{1}'.format('https://id.stuff.com',reverse('auth/social/bounce',kwargs={'target_uri':reverse('social:complete',kwargs={'backend':'google-oauth2-inquiry'})}))
        self.assertEqual(uri,goal)
        state = params['state'][0]
        self.assertTrue('|blah' in state)

    @override_settings(SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_OVERRIDE_REDIRECT_URI_SUBDOMAIN=None,
                       SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_OVERRIDE_REDIRECT_URI_REDIRECTOR_NAME=None)
    def test_client_off_good_subdom(self):
        res = self.client.get(reverse('social:begin',kwargs={'backend':'google-oauth2-inquiry'}),HTTP_HOST='blah.stuff.com')
        self.assertEqual(res.status_code,302)
        redir = res['Location']
        params = parse_qs(urlparse(redir).query, keep_blank_values=True)
        uri = params['redirect_uri'][0]
        goal = '{0}{1}'.format('http://blah.stuff.com',reverse('social:complete',kwargs={'backend':'google-oauth2-inquiry'}))
        self.assertEqual(uri,goal)
        state = params['state'][0]
        self.assertFalse('|' in state)

    @override_settings(SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_OVERRIDE_REDIRECT_URI_SUBDOMAIN=None,
                       SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_OVERRIDE_REDIRECT_URI_REDIRECTOR_NAME=None)
    def test_client_off_no_subdom(self):
        res = self.client.get(reverse('social:begin',kwargs={'backend':'google-oauth2-inquiry'}),HTTP_HOST='localhost')
        self.assertEqual(res.status_code,302)
        redir = res['Location']
        params = parse_qs(urlparse(redir).query, keep_blank_values=True)
        uri = params['redirect_uri'][0]
        goal = '{0}{1}'.format('http://localhost',reverse('social:complete',kwargs={'backend':'google-oauth2-inquiry'}))
        self.assertEqual(uri,goal)
        state = params['state'][0]
        self.assertFalse('|' in state)

    @override_settings(SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_OVERRIDE_REDIRECT_URI_SUBDOMAIN='id',
                       SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_OVERRIDE_REDIRECT_URI_REDIRECTOR_NAME='auth/social/bounce')
    def test_client_bad(self):
        res = self.client.get(reverse('social:begin',kwargs={'backend':'google-oauth2'}))
        self.assertEqual(res.status_code,404)
        

class SavedSubdomainInStateRedirectorViewTest(TestCase):
    def setUp(self):
        self.social_complete =reverse('social:complete',kwargs={'backend':'google-oauth2-inquiry'})
    def _get_action(self,response):
        r = re.search('''action="(.*?)"''',response.content)
        if not r:
            return None
        else:
            return r.groups()[0]

    def test_post_bad(self):
        url = reverse('auth/social/bounce',kwargs={'target_uri':self.social_complete})
        res = self.client.post(url,data={'state':'asdfasf|blah'})
        self.assertEqual(res.status_code,405)

    def test_normal(self):
        url = reverse('auth/social/bounce',kwargs={'target_uri':self.social_complete})
        res = self.client.get(url,data={'state':'asdfasf|blah'})
        self.assertEqual(res.status_code,200)
        self.assertEqual(self._get_action(res),'http://blah.testserver'+self.social_complete)

    def test_normal_secure(self):
        url = reverse('auth/social/bounce',kwargs={'target_uri':self.social_complete})
        res = self.client.get(url,data={'state':'asdfasf|blah'},secure=True)
        self.assertEqual(res.status_code,200)
        self.assertEqual(self._get_action(res),'https://blah.testserver'+self.social_complete)

    def test_normal_with_sub(self):
        url = reverse('auth/social/bounce',kwargs={'target_uri':self.social_complete})
        res = self.client.get(url,data={'state':'asdfasf|blah'},HTTP_HOST='zap.stuff.com')
        self.assertEqual(res.status_code,200)
        self.assertEqual(self._get_action(res),'http://blah.stuff.com'+self.social_complete)

    def test_no_state_relative(self):
        url = reverse('auth/social/bounce',kwargs={'target_uri':self.social_complete})
        res = self.client.get(url,data={'state':'asdfasf'})
        self.assertEqual(res.status_code,200)
        self.assertEqual(self._get_action(res),self.social_complete)

    def test_no_state2_relative(self):
        url = reverse('auth/social/bounce',kwargs={'target_uri':self.social_complete})
        res = self.client.get(url,data={'state':'asdfasf|'})
        self.assertEqual(res.status_code,200)
        self.assertEqual(self._get_action(res),self.social_complete)
    def test_no_state3_relative(self):
        url = reverse('auth/social/bounce',kwargs={'target_uri':self.social_complete})
        res = self.client.get(url,data={'state':'asdfasf|  '})
        self.assertEqual(res.status_code,200)
        self.assertEqual(self._get_action(res),self.social_complete)
    def test_normal_with_sub_no_state_strip_sub(self):
        url = reverse('auth/social/bounce',kwargs={'target_uri':self.social_complete})
        res = self.client.get(url,data={'state':'asdfasf'},HTTP_HOST='zap.stuff.com')
        self.assertEqual(res.status_code,200)
        self.assertEqual(self._get_action(res),'http://stuff.com'+self.social_complete)

    def test_bad_state(self):
        url = reverse('auth/social/bounce',kwargs={'target_uri':self.social_complete})
        res = self.client.get(url,data={'state':'sadf|<blah>'},HTTP_HOST='zap.stuff.com')
        self.assertEqual(res.status_code,200)
        self.assertEqual(self._get_action(res),'http://&lt;blah&gt;.stuff.com'+self.social_complete)