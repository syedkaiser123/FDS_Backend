from django.urls import path, include
from rest_framework.routers import DefaultRouter
from food_delivery_system.orders.views import OrderViewSet, OrderItemViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'get-order-items', OrderItemViewSet, basename='orderitem')

urlpatterns = [
    path('', include(router.urls)),
]

