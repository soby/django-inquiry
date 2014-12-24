from django.apps import AppConfig


class SurveyAppConfig(AppConfig):
    name = 'inquiry.survey'
    verbose_name = 'inquiry.survey'

    def ready(self):
        # import signal handlers
        from . import signals #@UnusedImport
        type(signals) # for flake8
