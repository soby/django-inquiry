from django.contrib import admin
from . import models

class OrgAdmin(admin.ModelAdmin):
    list_display = ('name','subdomain')
    search_fields = ('name','subdomain')

class UserAdmin(admin.ModelAdmin):
    pass
     
admin.site.register(models.Org, OrgAdmin)
admin.site.register(models.User, UserAdmin)
