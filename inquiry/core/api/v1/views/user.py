from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.permissions import AllowAny

from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.template import loader
from django.core.mail import send_mail
from django.conf import settings
from django.http import QueryDict

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from django_mailgun import MailgunAPIError

from ..serializers import user
from . import base
from ....utils.auth import make_perm

import logging
LOGGER = logging.getLogger(__name__)

class UserViewSet(base.BaseAPIViewMixin,ModelViewSet):
    serializer_class = user.UserSerializer
    queryset = serializer_class.Meta.model.objects.none()  # Required for DjangoObjectPermissions
    search_fields = ('username','email','first_name','last_name')

    def _get_subdomain(self):
        fqdn = self.request.META.get('HTTP_HOST','')
        subdomain = fqdn
        if subdomain:
            try:
                subdomain = subdomain.split('.')[0]
            except:
                pass
        if (subdomain.startswith('localhost') or fqdn.endswith('herokuapp.com')) and settings.DEVELOPMENT_MODE:
            subdomain = 'demo'
        return subdomain

    def get_queryset(self,*args,**kwargs):
        qs = super(UserViewSet,self).get_queryset()
        if not self.request.data.has_key('is_active'):
            # default option
            return qs.filter(is_active=True)
        else:
            return qs

    def perform_create(self, serializer, *args, **kwargs):
        """
            Hooks into the create operation to send reset email
        """
        super(UserViewSet,self).perform_create(serializer, *args, **kwargs)
        self._send_password_reset_email(self.request,serializer.instance)

    def perform_update(self, serializer, *args, **kwargs):
        super(UserViewSet,self).perform_update(serializer, *args, **kwargs)
        
        # I think this is a DRF bug, it uses a pre-update version of the data. This refreshes it
        del serializer._data
        pass
        
    def perform_destroy(self, request, *args, **kwargs):
        """
            Soft delete
        """
        obj = self.get_object()
        obj.is_active=False
        obj.groups.clear()
        obj.save()

    @list_route(methods=['get'],permission_classes=[AllowAny])
    def login(self, request, pk=None):
        username = self.request.GET.get('username')
        password = self.request.GET.get('password')
        
        subdomain = self._get_subdomain()
        usr= authenticate(username=username, password=password,subdomain=subdomain)
        if usr is not None:
            if usr.is_active:
                login(request, usr)
                userData = self.get_serializer(instance=usr).data
                LOGGER.info('Login success for user {0}'.format(usr),extra={'request':request})
                return Response({'user':userData,'session':{'id':request.session._session_key},'csrf':get_token(request)})
            else:
                LOGGER.warn('Login failure for disabled user {0}'.format(usr),extra={'request':request})
                raise AuthenticationFailed("disabled account")
        else:
            LOGGER.warn('Login failure for user {0}'.format(usr),extra={'request':request})
            raise AuthenticationFailed("invalid login")

    @list_route(methods=['get'])
    def my(self,request,pk=None):
        return Response(self.get_serializer(instance=request.user).data)

    @detail_route(methods=['patch'])
    def logout(self, request, pk=None):
        u = self.get_object()
        if u.id != request.user.id:
            LOGGER.warn('Logout attempt against different user {0}'.format(u),extra={'request':request})
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'detail':'This function must be performed on the same user that is logged in'})

        logout(request)
        LOGGER.info('Logout success',extra={'request':request})
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['put'])
    def set_groups(self,request,pk=None):
        u = self.get_object()
        if not request.DATA.has_key('groups'):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':'groups parameter not provided'})

        if isinstance(request.data,QueryDict):
            groupPks = request.DATA.getlist('groups',[])
        else:
            groupPks = request.DATA.get('groups',[])

        if not isinstance(groupPks,tuple) and not isinstance(groupPks,list):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':'groups parameter must be a list or multivalue post'})
        groups = Group.manager.for_user(self.request.user).filter(pk__in=groupPks) #@UndefinedVariable
        for g in groups:
            if not request.user.has_perm(make_perm(Group,'change'),g):
                LOGGER.warn('Access denied to change group {0} when setting groups for user {1}'.format(g,u),extra={'request':request})
                return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'detail':'Access denied to change one or more provided groups'})
        if len(groupPks) != len(groups):
            LOGGER.warn('Unable to find all requested groups {0} to set for user {1}'.format(groupPks,u),extra={'request':request})
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'detail':'Could not find requested number of groups'})
        u.groups.clear()
        u.groups.add(*groups)

        LOGGER.info('User {0} added to groups {1}'.format(u,groups),extra={'request':request})
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['patch'])
    def change_password(self, request, pk=None):
        # given the current password, change it
        u = self.get_object()
        if u.id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'detail':'This function must be performed on the same user that is logged in'})

        oldpassword = request.DATA.get('oldpassword')
        newpassword = request.DATA.get('newpassword')
        # TODO: lockouts, etc
        if not request.user.check_password(oldpassword):
            LOGGER.warn('Password change attempt with wrong password',extra={'request':request})
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'detail':'Invalid password'})

        request.user.set_password(newpassword)
        
        request.user.save()
        LOGGER.warn('Passwword change success for user {0}'.format(u),extra={'request':request})
        return Response(status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=['post'],permission_classes=[AllowAny])
    def reset_password_for_username(self, request, pk=None):
        """
            This is a pre or post authentication password reset function. Give it a 
            username and it will send the user an email to reset their password
            If you're authenticated, it will only search your users. If you're not 
            authenticated, it will search all users. At some point, there will probably
            be a CAPTCHA or something on the unauthenticated flow
        """
        username = request.DATA.get('username')
        if not username:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':'username parameter not provided'})

        userModel = get_user_model()
        
        if request.user and request.user.pk != settings.ANONYMOUS_USER_ID:
            # Authenticated version. They can only retrieve their own users
            try:
                usr = userModel.manager.for_user(request.user).get(username=username)
            except userModel.DoesNotExist:
                LOGGER.warn('Password reset attempt, authorized but user {0} not found for caller'.format(username),extra={'request':request})
                return Response(status=status.HTTP_404_NOT_FOUND,
                                data={'detail':'User not found'})

            if not request.user.has_perm(make_perm(usr,'change'),usr):
                LOGGER.warn('Password reset attempt, access denied to change user {0} for authorized user'.format(usr),extra={'request':request})
                raise PermissionDenied()

            if not usr.is_active:
                LOGGER.warn('Password reset attempt, inactive user by authenticated user {0}'.format(usr),extra={'request':request})
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':'User is not active'})

            LOGGER.warn('Password reset success, successful reset by authenticated caller for {0}'.format(usr),extra={'request':request})
            self._send_password_reset_email(request,usr)

        else:
            try:
                usr = userModel.objects.get(is_active=True,username=username)
            except userModel.DoesNotExist:
                # This use doesn't exist. Of course, we can't tell them that 
                # since that would give away the existance of users, which customers
                # will flag as user enumeration
                LOGGER.warn('Password reset attempt, user {0} not found for anonymous caller'.format(username),extra={'request':request})
            else:
                LOGGER.warn('Password reset success, successful reset by anonymous caller for {0}'.format(usr),extra={'request':request})
                self._send_password_reset_email(request,usr)

        return Response(data={'detail':'A password reset email has been sent to the address on file'})

    @list_route(methods=['post'],permission_classes=[AllowAny])
    def reset_password_with_token(self, request, pk=None,token_generator=default_token_generator):
        """
            This is a pre or post authentication password reset finishing function. The token
            generated in reset_password_for_username() is validated and the password is reset
        """
        token = request.DATA.get('token')
        if not token:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':'token parameter not provided'})
        uidb64 = request.DATA.get('uid')
        if not token:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':'uid parameter not provided'})

        userModel = get_user_model()
        try:
            uid = int(urlsafe_base64_decode(uidb64))
            usr = userModel._default_manager.get(pk=uid)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':'invalid uid parameter'})
        
        if not token_generator.check_token(usr, token):
            LOGGER.error('Password reset with token error, bad token {0} for user {1}'.format(token,usr),extra={'request':request})
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':'invalid token'})

        newpassword = request.DATA.get('newpassword')
        newpassword_confirm = request.DATA.get('newpassword_confirm')

        if not newpassword == newpassword_confirm:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':'Passwords do not match'})

        usr.set_password(newpassword)
        
        usr.save()
        LOGGER.info('Password reset with token success for user {0}'.format(usr),extra={'request':request})
        
        # auto login users after resetting password
        subdomain = self._get_subdomain()
        
        usr = authenticate(username=usr.username, password=newpassword,subdomain=subdomain)
        login(request, usr)
        return Response(data={'detail':'Password updated'})

    def _send_password_reset_email(self,
                                   request,
                                   usr,
                                   email_template_name='registration/password_reset_email.txt',
                                   subject_template_name='registration/password_reset_subject.txt',
                                   token_generator=default_token_generator,
                                   from_email=settings.EMAIL_FROM_ADDRESS,
                                   html_email_template_name='registration/password_reset_email.html'):
        """ 
            Mostly copied from django's PasswordResetForm. I just don't like how it does password
            resets by lookups based off of email and then iterating through the hits
        """

        domain = request.get_host()
        c = {
                'email': usr.email,
                'domain': domain,
                'site_name': settings.SITE_NAME,
                'uid': urlsafe_base64_encode(force_bytes(usr.pk)),
                'user': usr,
                'token': token_generator.make_token(usr),
                'protocol': 'https' if request.is_secure() else 'http',
                'password_reset_confirm_url': settings.PASSWORD_RESET_CONFIRM_URL,
            }

        subject = loader.render_to_string(subject_template_name, c)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        email = loader.render_to_string(email_template_name, c)

        if html_email_template_name:
            html_email = loader.render_to_string(html_email_template_name, c)
        else:
            html_email = None

        try:
            send_mail(subject, email, from_email, [usr.email], html_message=html_email)
        except MailgunAPIError as e:
            LOGGER.error('Error sending mail for user {0}: {1}'.format(usr,e.message.content),extra={'request':request})
        except Exception as e:
            LOGGER.error('Error sending mail for user {0}: {1}'.format(usr,e),extra={'request':request})


class GroupViewSet(base.BaseAPIViewMixin, ModelViewSet):
    serializer_class = user.GroupSerializer
    queryset = serializer_class.Meta.model.objects.none()  # Required for DjangoObjectPermissions

    @detail_route(methods=['patch'])
    def add_user(self,request,pk=None):
        
        grp = self.get_object()
        userModel = get_user_model()
        uid = request.DATA.get('userId')
        try:
            user = userModel.manager.for_user(request.user).get(pk=uid)
        except userModel.DoesNotExist:
            LOGGER.warn('User {0} not found to be added to group {1}'.format(uid,grp),extra={'request':request})
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':'user not found'})

        grp.user_set.add(user)
        LOGGER.info('User {0} added to group {1}'.format(user,grp),extra={'request':request})

        return Response(data={'detail':'User added to group'})

    @detail_route(methods=['patch'])
    def remove_user(self,request,pk=None):
        
        grp = self.get_object()
        userModel = get_user_model()
        uid = request.DATA.get('userId')
        try:
            user = userModel.manager.for_user(request.user).get(pk=uid)
        except userModel.DoesNotExist:
            LOGGER.warn('User {0} not found when trying to remove from group {1}'.format(uid,grp),extra={'request':request})
            return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'detail':'user not found'})
        grp.user_set.remove(user)
        LOGGER.info('User {0} removed from group {1}'.format(user,grp),extra={'request':request})
        
        return Response(data={'detail':'User removed from group'})        