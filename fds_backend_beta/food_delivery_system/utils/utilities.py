
from django.contrib.auth.models import Permission, Group
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, permissions, status


from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from food_delivery_system.permissions.permission import (
                                                        IsRestaurantOwner, IsRestaurantManagerOrOwner,
                                                        IsCustomer, IsChef, IsDeliveryPersonnel,
                                                        CanMarkDeliveredPermission
                                                        )

class UserPermissions:
    """
    Mixin class to assign permissions based on the action and user type.
    """

    def get_permissions(self, view):
        """
        Assign permissions based on the action and user type, leveraging role-based access from the Staff model.
        """
        # Deny access to the `create` endpoint for non-customers
        if view.action == 'create':
            # Ensure the user is authenticated and is a customer
            if not self.request.user or not self.request.user.is_authenticated:
                raise PermissionDenied("You must be logged in to create an order.")

            # Check if the user is a staff member with a specific role (e.g., manager, chef, etc.)
            staff = getattr(self.request.user, 'staff', None)  # Reverse relationship from Staff to CustomUser
            if ((staff and staff.role in ['manager', 'chef', 'delivery'])) or not self.request.user.is_superuser:
                raise PermissionDenied("Staff members, managers, and restaurant owners cannot create orders.")

            # Apply `IsCustomer` permission for customers and admin.
            return [permissions.IsAuthenticated(), IsCustomer()]

        # # Allow admin users to bypass specific permissions for other actions
        # if self.request.user and self.request.user.is_superuser:
        #     return [permissions.IsAuthenticated()]  # Admins only need to be authenticated

        # Assign `IsCustomer` permission for specific actions
        if view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsCustomer()]

        return super().get_permissions()
    

    @login_required
    def mark_order_delivered(request, order_id):
        if not request.user.has_perm('orders.can_mark_delivered'):
            return HttpResponseForbidden("You do not have permission to mark this order as delivered.")
        
        # Logic to mark the order as delivered
        return HttpResponse("Order marked as delivered.")


class RBACPermissionManager:
    """
    A utility class to manage permissions for users and groups.
    """

    # Global role-to-permissions mapping
    role_permissions_map = {
        "restaurant": {
            "permissions": ["can_manage_categories", "can_manage_menuitems", "can_manage_restaurant", "can_view_analytics", "can_manage_staff"],
            "group": "Restaurant Owners",
        },
        "manager": {
            "permissions": ["can_manage_categories", "can_manage_menuitems", "can_update_order_status", "can_manage_staff"],
            "group": "Managers",
        },
        "chef": {
            "permissions": ["can_manage_menuitems", "can_mark_unavailable", "can_update_order_status"],
            "group": "Chefs",
        },
        "delivery": {
            "permissions": ["can_mark_delivered"],
            "group": "Delivery Personnel",
        },
        "customer": {
            "permissions": ["can_cancel_order"],
            "group": "Customers",
        },
    }

    @staticmethod
    def assign_permissions_to_user(user, permissions_list):
        """
        Assign a list of permissions to a specific user.

        Args:
            user (CustomUser): The user to whom permissions will be assigned.
            permissions_list (list): A list of permission codenames to assign.

        Raises:
            ObjectDoesNotExist: If a permission does not exist.
        """
        for codename in permissions_list:
            try:
                permission = Permission.objects.get(codename=codename)
                user.user_permissions.add(permission)
            except ObjectDoesNotExist:
                raise ObjectDoesNotExist(f"Permission with codename '{codename}' does not exist.")

    @staticmethod
    def assign_permissions_to_group(group_name, permissions_list):
        """
        Assign a list of permissions to a specific group.

        Args:
            group_name (str): The name of the group to which permissions will be assigned.
            permissions_list (list): A list of permission codenames to assign.

        Raises:
            ObjectDoesNotExist: If a permission or group does not exist.
        """
        try:
            group, created = Group.objects.get_or_create(name=group_name)
            for codename in permissions_list:
                try:
                    permission = Permission.objects.get(codename=codename)
                    group.permissions.add(permission)
                except ObjectDoesNotExist:
                    raise ObjectDoesNotExist(f"Permission with codename '{codename}' does not exist.")
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"Group '{group_name}' does not exist.")

    @staticmethod
    def assign_user_to_group(user, group_name):
        """
        Assign a user to a specific group.

        Args:
            user (CustomUser): The user to assign to the group.
            group_name (str): The name of the group.

        Raises:
            ObjectDoesNotExist: If the group does not exist.
        """
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"Group '{group_name}' does not exist.")

    @classmethod
    def assign_role_permissions(cls, user, role_key):
        """
        Assign permissions and group to a user based on their role.

        Args:
            user (CustomUser): The user to whom permissions and group will be assigned.
            role_key (str): The role key (e.g., "is_restaurant", "is_manager").

        Raises:
            KeyError: If the role_key is not found in the role_permissions_map.
        """
        if role_key not in cls.role_permissions_map:
            raise KeyError(f"Role '{role_key}' is not defined in the role_permissions_map.")

        role_config = cls.role_permissions_map[role_key]
        cls.assign_permissions_to_user(user, role_config["permissions"])
        cls.assign_user_to_group(user, role_config["group"])


