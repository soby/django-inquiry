from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from . import models

class StatusAdmin(admin.ModelAdmin): pass
class TypeAdmin(admin.ModelAdmin): pass
class SurveyAdmin(admin.ModelAdmin): pass
class SectionAdmin(admin.ModelAdmin): pass
class ResourceAdmin(admin.ModelAdmin): pass
class QuestionAdmin(admin.ModelAdmin): pass
class QuestionChoiceAdmin(admin.ModelAdmin): pass
class QuestionResourceAdmin(admin.ModelAdmin): pass
class ResponseAdmin(admin.ModelAdmin): pass
class ResponseSectionAdmin(OrderedModelAdmin): pass
class QuestionResponseAdmin(OrderedModelAdmin):
    list_display = ('question', 'order','move_up_down_links')
class QuestionResponseResourceAdmin(admin.ModelAdmin): pass
     
admin.site.register(models.Status, StatusAdmin)
admin.site.register(models.Type, TypeAdmin)
admin.site.register(models.Survey, SurveyAdmin)
admin.site.register(models.Section, SectionAdmin)
admin.site.register(models.Resource, ResourceAdmin)
admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.QuestionChoice, QuestionChoiceAdmin)
admin.site.register(models.QuestionResource, QuestionResourceAdmin)
admin.site.register(models.Response, ResponseAdmin)
admin.site.register(models.ResponseSection, ResponseSectionAdmin)
admin.site.register(models.QuestionResponse, QuestionResponseAdmin)
admin.site.register(models.QuestionResponseResource, QuestionResponseResourceAdmin)
