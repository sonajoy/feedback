from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Permission


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """
    Create default groups and assign permissions to them.
    """
    # Define group names and associated permissions
    group_permissions = {
        'end-user': [
            'add_feedback', 'change_feedback', 'view_feedback', 'delete_feedback'
        ],
        'auditor': [
            'view_feedback', 'change_feedback', 'delete_feedback'
        ],
        'admin': [
            'add_feedback', 'change_feedback', 'view_feedback', 'delete_feedback'
        ],
    }

    # Loop through group definitions
    for group_name, permissions in group_permissions.items():
        group, created = Group.objects.get_or_create(name=group_name)

        if created:
            print(f"Group '{group_name}' created.")
        else:
            print(f"Group '{group_name}' already exists.")

        # Fetch and assign permissions
        for perm_codename in permissions:
            try:
                perm = Permission.objects.get(codename=perm_codename)
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                print(f"Permission '{perm_codename}' does not exist. Skipping.")





# @receiver(post_migrate)
# def create_default_groups(sender, **kwargs):
#     """
#     Create default groups if they do not exist.
#     """
#     group_names = ['end-user', 'auditor', 'admin']
#     for group_name in group_names:
#         group, created = Group.objects.get_or_create(name=group_name)
#         if created:
#             print(f"Group '{group_name}' created.")
#         else:
#             print(f"Group '{group_name}' already exists.")



