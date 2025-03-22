from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from food_delivery_system.orders.views import OrderViewSet, OrderItemViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'get-order-items', OrderItemViewSet, basename='orderitem')

urlpatterns = [
    path('', include(router.urls)),
]

# urlpatterns = [
#     re_path(r'^o.*s$', OrderViewSet.as_view({'get': 'list'}), name='order-list'),
#     re_path(r'^o.*s$', OrderViewSet.as_view({'post': 'create'}), name='order-list'),
#     re_path(r'^get-order-items$', OrderItemViewSet.as_view({'get': 'list'}), name='orderitem-list'),
# ]
