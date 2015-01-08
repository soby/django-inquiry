# Django settings for web project.
import os
import sys

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
APP_NAME = os.environ.get('APP_NAME', 'unnamed_app')

DEBUG = os.environ.get('APP_MODE_DEBUG', '0') == '1'
DEVELOPMENT_MODE = os.environ.get('APP_MODE_DEVELOPMENT', '1') == '1'

SITE_ID = 1

# Branding mostly. Used in places like the password reset email
SITE_NAME = 'djangoinquiry.com'

# added for django guardian. Must be none since all users
# need org associations and anon would be missing that
ANONYMOUS_USER_ID = None

# The URL that password reset emails will use. It should end in
# a spot for the token like /#accounts/reset. It will end up looking like
# /#accounts/reset?uid=<base64Uid>&token=<token>
PASSWORD_RESET_CONFIRM_URL = '/#accounts/reset'

TEMPLATE_DEBUG = DEBUG
ALLOW_NON_SSL = os.environ.get('APP_SUPPORTS_SSL', '0') != '1'

AUTH_USER_MODEL = 'core.User'
AUTH_ORG_MODEL = 'core.Org'

ADMINS = []

if os.environ.get('APP_ADMIN_EMAIL'):
    ADMINS.append(['Admins', os.environ.get('APP_ADMIN_EMAIL')])


MANAGERS = ADMINS

# django 1.7 thing
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': PROJECT_DIR + '/../test.db',   
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        
    },
    'OPTIONS': {
        'timeout': 10,
    }
}

# Heroku stuff
import dj_database_url
prodDb = dj_database_url.config()
if prodDb:
    DATABASES['default'] = prodDb
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# #################################
# ### Begin Django Social Auth ####
# #################################
# python-social-auth and Heroku
SOCIAL_AUTH_REDIRECT_IS_HTTPS = not ALLOW_NON_SSL

SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_KEY = \
            os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_KEY', None)
SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_SECRET = \
            os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_SECRET', None)
#
SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_SCOPE = ['openid','profile','email']

SOCIAL_AUTH_FORCE_POST_DISCONNECT = True
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']

SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_OVERRIDE_REDIRECT_URI_SUBDOMAIN = \
            os.environ.get('APP_SOCIAL_LOGIN_REDIR_DOMAIN',None)
SOCIAL_AUTH_GOOGLE_OAUTH2_INQUIRY_OVERRIDE_REDIRECT_URI_REDIRECTOR_NAME = \
            'auth/social/bounce'

LOGIN_URL          = '/#/login'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/#/complete_login'
LOGIN_ERROR_URL    = '/#/login?error=1'

SOCIAL_AUTH_USER_MODEL = AUTH_USER_MODEL
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True

# List of fields we'll update from social auth provider. This 
# is custom to our pipeline module since the original one had a blacklist
SOCIAL_AUTH_SAFE_USER_FIELDS = ['first_name', 'last_name']

SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is were emails and domains whitelists are applied (if
    # defined).
    'social.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address and an org that allows 
    'inquiry.core.auth.social.associate_by_email_and_allowed_org',

    # Create a user account if we haven't found one yet.
    #'social.pipeline.user.create_user',
    'inquiry.core.auth.social.create_user',

    # Create the record that associated the social account with this user.
    'social.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social.pipeline.social_auth.load_extra_data',

    # Safer version with whitelist:
    # Update the user record with any changed info from the auth service.
    'inquiry.core.auth.social.user_details',
)
##################################
#### end Django Social Auth ###
##################################


# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['localhost', '.herokussl.com', '.herokuapp.com']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Etc/UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''


#
#
#  Email Settings - Mailgun
#
#
EMAIL_BACKEND = 'django_mailgun.MailgunBackend'
MAILGUN_ACCESS_KEY = os.environ.get('APP_MAILGUN_KEY')
MAILGUN_SERVER_NAME = APP_NAME
EMAIL_ENABLED = bool(MAILGUN_ACCESS_KEY)

EMAIL_FROM_ADDRESS = os.environ.get('APP_EMAIL_FROM_ADDRESS',
                                    'sobyx@hotmail.com')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_DIR,'collected_statics')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'bk5^(b=vv=+m1maasdfh(udbl$xm6s$5ha@rpt#&#v!b*6go'

MIDDLEWARE_CLASSES = (
    'inquiry.core.middleware.sslify.SSLifyMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
)

MIGRATION_MODULES = {
    # default is the final label on the social login app
    'default' : 'dependency_migrations.default',
    'guardian' : 'dependency_migrations.guardian',

}

ROOT_URLCONF = 'inquiry.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'inquiry.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'inquiry.core.context_processors.debug.debug',
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)
INSTALLED_APPS = (
    'inquiry.core',
    'inquiry.survey',
    'social.apps.django_app.default',
    'rest_framework',
    'guardian',
    'ordered_model',
    
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'debug_toolbar',    
)

AUTHENTICATION_BACKENDS = (
    'inquiry.core.auth.social.ConfigurableRedirectGoogleOauth2Backend',
    'inquiry.core.auth.model.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'extra_data': {
            '()':'inquiry.core.logs.ExtraDataFilter'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(pathname)s %(funcName)s %(lineno)d '\
                        '%(org)s %(user)s %(message)s'
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(pathname)s %(funcName)s %(lineno)d '\
                        '%(org)s %(user)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter':'verbose',
            'filters':['extra_data',],
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false','extra_data'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter':'verbose',
        }
    },
    'loggers': {},
    'root': {
        'handlers': ['console',],
        'level': os.environ.get('APP_LOG_LEVEL','INFO')
    }
}


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoObjectPermissions',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'inquiry.core.auth.drf_session.'\
            'SessionAuthorizationHeaderAuthentication',
        'inquiry.core.auth.drf_session.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT':'json',
}

from .core.utils.test import mommy
MOMMY_CUSTOM_FIELDS_GEN = {
    'django.db.models.fields.NullBooleanField': mommy.gen_null_boolean
}

if EMAIL_ENABLED:
    LOGGING['root']['handlers'].append('mail_admins')
