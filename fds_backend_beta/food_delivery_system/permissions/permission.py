from rest_framework import permissions


class IsRestaurantOwner(permissions.BasePermission):
    """Allows access only to restaurant owners or admin users."""

    def has_object_permission(self, request, view, obj):
        # Allow access if the user is an admin
        if request.user.is_staff or request.user.is_superuser:
            return True
        # Otherwise, check if the user is the owner
        return request.user == obj.owner


class IsRestaurantManagerOrOwner(permissions.BasePermission):
    """Allows access to restaurant managers, owners, or admin users."""

    def has_object_permission(self, request, view, obj):
        # Allow access if the user is an admin
        if request.user.is_staff or request.user.is_superuser:
            return True
        # Otherwise, check if the user is the owner or a manager
        return request.user == obj.owner or obj.staff.filter(user=request.user, role='manager').exists()


class IsCustomer(permissions.BasePermission):
    """Allows access only to customers for their own orders."""

    def has_object_permission(self, request, view, obj):
        return request.user == obj.customer


class IsChef(permissions.BasePermission):
    """Allows access only to chefs of the restaurant."""

    def has_object_permission(self, request, view, obj):
        return obj.restaurant.staff.filter(user=request.user, role='chef').exists()


class IsDeliveryPersonnel(permissions.BasePermission):
    """Allows access only to delivery personnel of the restaurant."""

    def has_object_permission(self, request, view, obj):
        return obj.restaurant.staff.filter(user=request.user, role='delivery').exists()

