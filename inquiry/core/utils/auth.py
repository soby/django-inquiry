from django.db.models import Model
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
#
# Utility functions
# 
def group_for_org(org,groupName):
    return 'org_{0}_{1}'.format(org.id,groupName.lower())

def make_perm(obj,action):
    if isinstance(obj,Model):
        cls = obj.__class__
    elif issubclass(obj,Model):
        cls = obj
    else:
        raise Exception('Unknown model type: {0}'.format(obj))
    
    return '{0}_{1}'.format(action,cls.__name__.lower())

def make_global_perm(obj,action):
    if isinstance(obj,Model):
        cls = obj.__class__
    elif issubclass(obj,Model):
        cls = obj
    return '{0}.{1}_{2}'.format(cls._meta.app_label,action,cls.__name__.lower())

def get_org_model():
    """
    Returns the Org model that is active in this project.
    """
    try:
        return django_apps.get_model(settings.AUTH_ORG_MODEL)
    except ValueError:
        raise ImproperlyConfigured("AUTH_ORG_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "AUTH_ORG_MODEL refers to model '%s' that has not been installed" % settings.AUTH_ORG_MODEL
        )