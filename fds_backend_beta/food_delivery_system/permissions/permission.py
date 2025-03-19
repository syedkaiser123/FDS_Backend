from rest_framework import permissions


class IsRestaurantOwner(permissions.BasePermission):
    """Allows access only to restaurant owners."""

    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner


class IsRestaurantManagerOrOwner(permissions.BasePermission):
    """Allows access to restaurant managers and owners."""

    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or obj.staff.filter(user=request.user, role='manager').exists()


class IsCustomer(permissions.BasePermission):
    """Allows access only to customers for their own orders."""

    def has_object_permission(self, request, view, obj):
        import pdb; pdb.set_trace()
        return request.user == obj.customer


class IsChef(permissions.BasePermission):
    """Allows access only to chefs of the restaurant."""

    def has_object_permission(self, request, view, obj):
        return obj.restaurant.staff.filter(user=request.user, role='chef').exists()


class IsDeliveryPersonnel(permissions.BasePermission):
    """Allows access only to delivery personnel of the restaurant."""

    def has_object_permission(self, request, view, obj):
        return obj.restaurant.staff.filter(user=request.user, role='delivery').exists()

