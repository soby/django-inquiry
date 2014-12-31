from django.dispatch import receiver
from django.db.models import signals
from django.contrib.auth.models import Group
from django.apps import apps

from guardian.shortcuts import assign_perm

from ..core.utils.auth import group_for_org,make_global_perm, make_perm
from ..core.utils.auth import get_org_model
from ..core import models as core_models
from . import models

# org post save
def create_default_survey_statuses(sender, instance, created, **kwargs):
    """
        Post-save 
    """
    stat1,u = models.Status.objects.get_or_create( #@UnusedVariable
                                name='open',label='Open',org=instance)
    stat2,u = models.Status.objects.get_or_create( #@UnusedVariable
                                name='closed',label='Closed',closed_state=True,
                                org=instance)

# org post save
def assign_object_perms(sender, instance, created, **kwargs):
    admins,acreated = Group.objects.get_or_create( #@UnusedVariable
                                name=group_for_org(instance,'administrators'))
    users,ucreated = Group.objects.get_or_create( #@UnusedVariable
                                name=group_for_org(instance,'users'))
    
    assign_perm(make_global_perm(models.Survey,'view'), users)
    assign_perm(make_global_perm(models.Response,'view'), users)
    
    config = apps.get_app_config('survey')
    for model in config.get_models():
        # Assign basic CRUD to all models to admins
        assign_perm(make_global_perm(model, 'add'), admins)
        assign_perm(make_global_perm(model, 'change'), admins)
        assign_perm(make_global_perm(model, 'delete'), admins)
        
        if model != config.get_model('Status') and\
                model != config.get_model('Type'):
            assign_perm(make_global_perm(model, 'add'), users)
            assign_perm(make_global_perm(model, 'change'), users)
            assign_perm(make_global_perm(model, 'delete'), users)
    
# post-save on Survey to create the viewers group
@receiver(signals.post_save, sender=models.Survey)
def survey_viewers_group_and_view_perm(sender, instance, created, **kwargs):
    if created:
        grp = Group(
                    name=group_for_org(instance.org,
                                       'survey-{0}-viewers'.format(
                                                            instance.pk
                                                                    )
                                       )
                    )
        grp.save()
        assign_perm(make_perm(instance,'view'), grp, instance)
        
        if instance.owner:
            instance.owner.groups.add(grp)
        admins = Group.objects.get( 
                            name=group_for_org(instance.org,'administrators'))
        assign_perm(make_perm(instance,'view'), admins, instance)
        

# post-save on Response to create the viewers group
@receiver(signals.post_save, sender=models.Response)
def response_viewers_group_and_view_perm(sender, instance, created, **kwargs):
    if created:
        grp = Group(
                    name=group_for_org(instance.org,
                                       'response-{0}-viewers'.format(
                                                            instance.pk
                                                                    )
                                       )
                    )
        grp.save()
        assign_perm(make_perm(instance,'view'), grp, instance)
        
        if instance.owner:
            instance.owner.groups.add(grp)
        admins = Group.objects.get( 
                            name=group_for_org(instance.org,'administrators'))
        assign_perm(make_perm(instance,'view'), admins, instance)
        
# post-delete on Response to delete the viewers group
@receiver(signals.post_delete, sender=models.Response)
def delete_response_viewers_group_and_view_perm(sender, instance, **kwargs):
    try:
        grp = Group.objects.get(
                name=group_for_org(instance.org,
                                   'response-{0}-viewers'.format(
                                                        instance.pk
                                                                )
                                   )
                )
    except Group.DoesNotExist:
        # I guess we're done here
        pass
    else:
        grp.delete()
    
         
# all survey obj post-save
# generic admin permission assigner and user per assigner for user-owned
def assign_CRUD_to_admins_and_owner(sender, instance, created, **kwargs):
    if created:
        if not getattr(instance,'org',None):
            return 
        
        admins = Group.objects.get( 
                                name=group_for_org(instance.org,
                                                    'administrators'))
        
        
        assign_perm(make_perm(instance,'change'), admins, instance)
        assign_perm(make_perm(instance,'delete'), admins, instance)
        if isinstance(instance,core_models.UserOwnedModel):
            if getattr(instance,'owner',None):
                assign_perm(make_perm(instance,'change'), 
                            instance.owner, instance)
                assign_perm(make_perm(instance,'delete'), 
                            instance.owner, instance)       

# ####
# Actual wiring of the signals
# ####
@receiver(signals.post_save, sender=get_org_model())
def org_post_save_handler(sender, instance, created, **kwargs):
    assign_object_perms(sender, instance, created, **kwargs)
    create_default_survey_statuses(sender, instance, created, **kwargs)

config = apps.get_app_config('survey')
for model in config.get_models():
    if issubclass(model,core_models.BaseModel):
        signals.post_save.connect(assign_CRUD_to_admins_and_owner,model)
    