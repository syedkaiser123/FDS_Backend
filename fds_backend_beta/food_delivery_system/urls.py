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
from graphene_django.views import GraphQLView



from food_delivery_system.views import homepage
from .views import CustomTokenRefreshView, CustomTokenObtainPairView
from food_delivery_system.graphql.schema import schema
from food_delivery_system.middleware import QueryProfilerMiddleware


urlpatterns = [
    path("", homepage),
    path("admin/", admin.site.urls),
    # path('api/login/gettoken/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Now explicitly under /api/login
    path("api/login/gettoken/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),     # override default TokenObtainPairView

    # path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),     # Now explicitly under /api/login
    path('api/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),      # Override default TokenRefreshView

    path("api/orders/", include('food_delivery_system.orders.urls')),  # Include the orders app URLs under 'api/orders'.
    path("api/users/", include('food_delivery_system.users.urls')),     # Include the users app URLs under 'api/users'.
    path("api/restaurant/", include('food_delivery_system.restaurant.urls')),     # Include the users app URLs under 'api/restaurant'.

    # GraphQL viewsets
    path("graphql/", GraphQLView.as_view(graphiql=True, schema=schema)),

    # Silk Urls
    path('silk/', include('silk.urls', namespace='silk')),



]

