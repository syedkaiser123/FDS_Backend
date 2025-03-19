"""
URL configuration for food_delivery_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


from food_delivery_system.views import homepage

urlpatterns = [
    path("", homepage),
    path("admin/", admin.site.urls),
    path('api/login/gettoken/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Now explicitly under /api/login
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),     # Now explicitly under /api/login
    path("api/orders/", include('food_delivery_system.orders.urls')),  # Include the orders app URLs under 'api/orders'.
    path("api/users/", include('food_delivery_system.users.urls')),     # Include the users app URLs under 'api/users'.
]

