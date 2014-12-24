from django.db.models import signals
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from ..utils.auth import get_org_model

from guardian.shortcuts import assign_perm

from ..utils.auth import group_for_org,make_perm,make_global_perm


#
# Functions that do all of the work
# 
# org post_save
def create_org_groups(sender, instance, created, **kwargs):
    """
        Orgs won't really be edited often so we don't bother checking to see
        if they've just been created or not. The advantage to this is we can
        just add new groups here and existing orgs will have them created during
        their next save
    """

    users,ucreated = Group.objects.get_or_create( #@UnusedVariable
                                name=group_for_org(instance,'users'))
    admins,acreated = Group.objects.get_or_create( #@UnusedVariable
                                name=group_for_org(instance,'administrators'))

    #
    # GLOBAL CRUD PERMS
    #

    #
    # Admins
    #

    # user
    assign_perm(make_global_perm(get_user_model(), 'add'), admins)
    assign_perm(make_global_perm(get_user_model(), 'change'), admins)
    assign_perm(make_global_perm(get_user_model(), 'delete'), admins)

    # group
    assign_perm(make_global_perm(Group, 'change'), admins)

    # specific groups
    assign_perm(make_perm(Group, 'change'), admins, admins)
    assign_perm(make_perm(Group, 'change'), admins, users)


    #
    # Users
    #

    # user
    assign_perm(make_global_perm(get_user_model(), 'change'), users)


# user post_save
def first_user_is_admin_group(sender, instance, created, **kwargs):
    if instance.org.user_set.all().count() == 1:
        g = Group.objects.get(name=group_for_org(instance.org,
                                                 'administrators')
                              )
        instance.groups.add(g)

# user post_save
def add_to_users_group(sender, instance, created, **kwargs):
    if created:
        g = Group.objects.get(name=group_for_org(instance.org, 'users'))
        instance.groups.add(g)

# user post_save
def assign_user_perms(sender, instance, created, **kwargs):
    if created:
        admins = Group.objects.get(name=group_for_org(instance.org,
                                                      'administrators')
                                   )
        # admins can edit and "delete" users
        assign_perm(make_perm(instance, 'change'), admins, instance)
        assign_perm(make_perm(instance, 'delete'), admins, instance)

        # user can edit themselves (restrict fields in views)
        assign_perm(make_perm(instance, 'change'), instance, instance)


#
# Registration functions
#
@receiver(signals.post_save, sender=get_org_model())
def org_post_save_signals(sender, instance, created, **kwargs):
    create_org_groups(sender, instance, created, **kwargs)

@receiver(signals.post_save, sender=get_user_model())
def user_post_save_signals(sender, instance, created, **kwargs):
    first_user_is_admin_group(sender, instance, created, **kwargs)
    add_to_users_group(sender, instance, created, **kwargs)
    assign_user_perms(sender, instance, created, **kwargs)
