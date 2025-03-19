import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from food_delivery_system.serializers.serializer import RestaurantSerializer
from food_delivery_system.permissions.permission import IsRestaurantOwner, IsRestaurantManagerOrOwner, IsCustomer, IsChef, IsDeliveryPersonnel


from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from django.utils import timezone
from food_delivery_system.restaurant.models import Restaurant


class RestaurantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Restaurant CRUD operations.
    """
    queryset = Restaurant.objects.all().order_by('-created_at')
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Define custom permissions for different actions.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsRestaurantOwner() or IsRestaurantManagerOrOwner()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Automatically set the owner of the restaurant during creation.
        """
        user = self.request.user
        user.is_restaurant = True  # Set the is_restaurant flag to True
        user.save()
        serializer.save(owner=user, created_at=timezone.now(), updated_at=timezone.now())

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single restaurant with error handling.
        """
        try:
            instance = self.get_object()
            self.check_object_permissions(request, instance)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except PermissionDenied:
            return Response({'error': 'You do not have permission to view this restaurant.'}, status=status.HTTP_403_FORBIDDEN)
        except NotFound:
            return Response({'error': 'Restaurant not found.'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        """
        Update a restaurant with permission checks.
        """
        try:
            instance = self.get_object()
            self.check_object_permissions(request, instance)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(updated_at=timezone.now())
            return Response({"message": "Restaurant updated successfully.", "results": serializer.data}, status=status.HTTP_200_OK)
        except PermissionDenied:
            return Response({'error': 'You do not have permission to update this restaurant.'}, status=status.HTTP_403_FORBIDDEN)
        except NotFound:
            return Response({'error': 'Restaurant not found.'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a restaurant with permission checks.
        """
        try:
            instance = self.get_object()
            self.check_object_permissions(request, instance)
            instance.delete()
            return Response({"message": "Restaurant deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except PermissionDenied:
            return Response({'error': 'You do not have permission to delete this restaurant.'}, status=status.HTTP_403_FORBIDDEN)
        except NotFound:
            return Response({'error': 'Restaurant not found.'}, status=status.HTTP_404_NOT_FOUND)


