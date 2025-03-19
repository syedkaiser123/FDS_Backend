from django.urls import path, include
from rest_framework.routers import DefaultRouter
from food_delivery_system.restaurant.views import RestaurantViewSet

router = DefaultRouter()
router.register(r'', RestaurantViewSet, basename='restaurant')

urlpatterns = [
    path('', include(router.urls)),
]

