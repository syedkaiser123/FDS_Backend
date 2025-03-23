from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from food_delivery_system.orders.views import OrderViewSet, OrderItemViewSet

urlpatterns = [
    # OrderViewSet endpoints
    path('', OrderViewSet.as_view({'get': 'list', 'post': 'create'}), name='order-list'),  # List and Create
    path('<int:pk>/', OrderViewSet.as_view({'get': 'retrieve', 'patch': 'update', 'delete': 'destroy'}), name='order-detail'),  # Retrieve, Update, Destroy orders

    # OrderItemViewSet endpoints
    path('get-order-items/', OrderItemViewSet.as_view({'get': 'list'}), name='orderitem-list'),  # List
    path('get-order-items/<int:pk>/', OrderItemViewSet.as_view({'get': 'retrieve', 'patch': 'update', 'delete': 'destroy'}), name='orderitem-detail'),  # Retrieve, Update, Destroy order-items
]

