import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Order, OrderItem, Staff, Category
from food_delivery_system.serializers.serializer import (OrderSerializer, OrderItemSerializer,
                                                        StaffSerializer, CategorySerializer
                                                        )
from food_delivery_system.permissions.permission import (
                                                        IsRestaurantOwner, IsRestaurantManagerOrOwner,
                                                        IsCustomer, IsChef, IsDeliveryPersonnel,
                                                        CanMarkDeliveredPermission
                                                        )


from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from django.utils import timezone
from django.db import transaction
from food_delivery_system.restaurant.models import Restaurant
from food_delivery_system.serializers.serializer import RestaurantSerializer
from food_delivery_system.utils.pagination import CustomPagination
from food_delivery_system.utils.utilities import UserPermissions


user_auth = UserPermissions()

class OrderViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        Override the get_queryset method to filter the orders based on the user role.
        """
        user = self.request.user
        import ipdb;ipdb.set_trace()
        # If the user is a not a customer, deny access to the orders.
        if hasattr(user, 'staff') and user.staff.role in ['manager', 'chef', 'delivery']:
            # Staff members should not access orders directly
            raise PermissionDenied("You do not have permission to access orders other than yours.")

        # If the user is a customer, return only their orders
        if not user.is_staff and not user.is_superuser:
            return Order.objects.filter(customer=user).order_by('-created_at')

        # Admins and superusers can access all orders
        return Order.objects.all().order_by('-created_at')

    def get_permissions(self):
        """
        Override the get_permissions method to use the custom UserPermissions logic.
        """
        # Use custom permissions logic
        custom_permissions = user_auth.get_permissions(self)

        # If no custom permissions are returned, fall back to the default DRF logic
        if not custom_permissions:
            return super().get_permissions()
        
        return custom_permissions  # run through custom permissions defined in utilities

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Save the order with the authenticated user as the customer.
        """
        if not self.request.user or not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to create an order.")

        serializer.save(customer=self.request.user, created_at=timezone.now(), updated_at=timezone.now())

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.check_object_permissions(request, instance)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except PermissionDenied:
            return Response({'error': 'You do not have permission to view this order.'}, status=status.HTTP_403_FORBIDDEN)
        except NotFound:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        Update an order(partial) with permission checks.
        """
        try:
            instance = self.get_queryset().select_for_update().get(pk=kwargs["pk"])  # Lock the row for update, to prevent race conditions.
            self.check_object_permissions(request, instance)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(updated_at=timezone.now())
            return Response({"message": "Order updated successfully.", "results": serializer.data}, status=status.HTTP_200_OK)
        except PermissionDenied:
            return Response({'error': 'You do not have permission to update this Order.'}, status=status.HTTP_403_FORBIDDEN)
        except NotFound:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # @action(detail=True, methods=['delete'])    # overriding the as_view method in orders/urls
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Delete an Order with permission checks.
        """
        try:
            instance = self.get_object()
            self.check_object_permissions(request, instance)
            instance.delete()
            return Response({"message": "Order deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except PermissionDenied:
            return Response({'error': 'You do not have permission to delete this Order.'}, status=status.HTTP_403_FORBIDDEN)
        except NotFound:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)



class OrderItemViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    queryset = OrderItem.objects.all().order_by('id')
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        Override the get_queryset method to filter the order items based on the user role.
        """
        user = self.request.user

        # If the user is a not a customer, deny access to the orders.
        if hasattr(user, 'staff') and user.staff.role in ['manager', 'chef', 'delivery']:
            # Staff members should not access orders directly
            raise PermissionDenied("You do not have permission to access orders other than yours.")

        # If the user is a customer, return only their orders
        if not user.is_staff and not user.is_superuser:
            return OrderItem.objects.filter(order__customer=user).order_by('-order_id')

        # Admins and superusers can access all orders
        return OrderItem.objects.all().order_by('-order_id')

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [IsRestaurantOwner(), IsRestaurantManagerOrOwner(), IsChef()]
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.check_object_permissions(request, instance)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except PermissionDenied:
            return Response({'error': 'You do not have permission to view this order item.'}, status=status.HTTP_403_FORBIDDEN)
        except NotFound:
            return Response({'error': 'Order item not found.'}, status=status.HTTP_404_NOT_FOUND)


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all().order_by('id')
    serializer_class = StaffSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_permissions(self):
        """
        Assign permissions based on the action and user type.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsRestaurantOwner(), IsRestaurantManagerOrOwner()]
        return super().get_permissions()

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Save the staff object with permission checks.
        """
        if not self.request.user or not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to create a staff member.")
        serializer.save(date_joined=timezone.now())

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.check_object_permissions(request, instance)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except PermissionDenied:
            return Response({'error': 'You do not have permission to view this staff member.'}, status=status.HTTP_403_FORBIDDEN)
        except NotFound:
            return Response({'error': 'Staff member not found.'}, status=status.HTTP_404_NOT_FOUND)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_permissions(self):
        """
        Assign permissions based on the action and user type.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsRestaurantOwner(), IsRestaurantManagerOrOwner()]
        return super().get_permissions()

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Save the category object with permission checks.
        """
        if not self.request.user or not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to create a category.")
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.check_object_permissions(request, instance)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except PermissionDenied:
            return Response({'error': 'You do not have permission to view this category.'}, status=status.HTTP_403_FORBIDDEN)
        except NotFound:
            return Response({'error': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)
    
