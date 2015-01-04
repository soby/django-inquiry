from django.dispatch import receiver
from django.db.models import signals
from django.contrib.auth.models import Group
from django.apps import apps

from guardian.shortcuts import assign_perm, remove_perm, get_users_with_perms

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
        
        if instance.owner_id:
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
        
        if instance.owner_id:
            instance.owner.groups.add(grp)
        admins = Group.objects.get( 
                            name=group_for_org(instance.org,'administrators'))
        assign_perm(make_perm(instance,'view'), admins, instance)

# post-save on Response to remove change/delete rights on completion
@receiver(signals.post_save, sender=models.Response)
def response_remove_change_delete_for_complete(sender, instance, 
                                               created, **kwargs):
    if instance.status.closed_state:
        # This will return users with _any_ perms
        users = get_users_with_perms(instance, with_group_users=False)\
                    .only('id')
        for u in users:
            remove_perm(make_perm(instance,'change'), u, instance)
            remove_perm(make_perm(instance,'delete'), u, instance)

                    
        
        
        
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
            if getattr(instance,'owner_id',None):
                assign_perm(make_perm(instance,'change'), 
                            instance.owner, instance)
                assign_perm(make_perm(instance,'delete'), 
                            instance.owner, instance)  

# all survey obj pre-save
# check for new owner and assign change/delete. Remove from old owner
def assign_CRUD_to_new_owner(sender, instance, raw, **kwargs):
    if not instance.pk:
        # the post-save above will get this one
        return
    
    if isinstance(instance,core_models.UserOwnedModel):
        existing_owner = instance.__class__.objects.filter(pk=instance.pk)\
                                .only('owner')[0].owner
        if existing_owner != instance.owner_id:
            # owner change. Get to work! 
            new_owner = instance.owner
            if not existing_owner or (existing_owner and\
                    existing_owner.has_perm(
                                    make_perm(instance,'change'), instance)):
                if new_owner:
                    assign_perm(make_perm(instance,'change'), 
                                new_owner, instance)
                if existing_owner:
                    remove_perm(make_perm(instance,'change'), 
                                existing_owner, instance)
            
            if not existing_owner or (existing_owner and\
                    existing_owner.has_perm(
                                    make_perm(instance,'delete'), instance)):
                if new_owner:
                    assign_perm(make_perm(instance,'delete'), 
                                new_owner, instance)
                if existing_owner:
                    remove_perm(make_perm(instance,'delete'), 
                                existing_owner, instance)
                
    

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
        signals.post_save.connect(assign_CRUD_to_admins_and_owner, model)
        signals.pre_save.connect(assign_CRUD_to_new_owner, model)
    