import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Order, OrderItem
from food_delivery_system.serializers.serializer import OrderSerializer, OrderItemSerializer
from food_delivery_system.permissions.permission import IsRestaurantOwner, IsRestaurantManagerOrOwner, IsCustomer, IsChef, IsDeliveryPersonnel


from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from django.utils import timezone
from django.db import transaction
from food_delivery_system.restaurant.models import Restaurant
from food_delivery_system.serializers.serializer import RestaurantSerializer
from food_delivery_system.utils.pagination import CustomPagination


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_permissions(self):
        # import ipdb;ipdb.set_trace()
        if self.action in ['create', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [IsCustomer()]
        return super().get_permissions()

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Save the order with the authenticated user as the customer.
        """
        if not self.request.user.is_authenticated:
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


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
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

