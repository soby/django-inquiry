from django.apps import AppConfig


class CoreAppConfig(AppConfig):
    name = 'inquiry.core'
    verbose_name = 'inquiry.core'

    def ready(self):
        # import signal handlers
        from .signals import permissions #@UnusedImport
        type(permissions) # for flake8
