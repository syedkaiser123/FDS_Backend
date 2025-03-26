from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set up groups and assign permissions"

    def handle(self, *args, **kwargs):
        # Define groups and their permissions
        role_permissions_map = {
            "Restaurant Owners": [
                                    "can_manage_categories", "can_manage_menuitems",
                                    "can_manage_restaurant", "can_view_analytics",
                                    "can_manage_staff"
                                ],
            "Managers": [
                            "can_manage_categories", "can_manage_menuitems",
                            "can_update_order_status", "can_manage_staff"
                        ],
            "Chefs": [
                        "can_manage_menuitems", "can_mark_unavailable",
                        "can_update_order_status"
                    ],
            "Delivery Personnel": [
                                    "can_mark_delivered"
                                ],
            "Customers": [
                            "can_cancel_order"
                        ],
        }

        # Create groups and assign permissions
        for group_name, permissions in role_permissions_map.items():
            group, created = Group.objects.get_or_create(name=group_name)
            for codename in permissions:
                try:
                    permission = Permission.objects.get(codename=codename)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Permission '{codename}' does not exist."))
            self.stdout.write(self.style.SUCCESS(f"Group '{group_name}' created/updated successfully."))

        self.stdout.write(self.style.SUCCESS("Groups and permissions setup completed."))


