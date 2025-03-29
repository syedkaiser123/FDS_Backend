from django.http import HttpResponse

import logging
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger("app_logs_with_token_info")


def homepage(request):
    return HttpResponse("<h1>Welcome to Food Delivery System API</h1>")


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        print(f"Incoming request data:\n{request.data}")  # Debugging print
        logger.info(f"Incoming request data: {request.data}")  # Logs request data
        response = super().post(request, *args, **kwargs)
        return response


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view to handle token obtain requests with logging.
    """

    def post(self, request, *args, **kwargs):
        # Log incoming request data
        logger.info(f"Login attempt: {request.data}")
        print(f"\nLogin attempt:\n{request.data}")
        # logging.getLogger().handlers[0].flush()  # Force flush

        # Call the original token obtain functionality
        response = super().post(request, *args, **kwargs)
        # logging.getLogger().handlers[0].flush()  # Force flush


        # Log the response data (excluding sensitive info)
        if response.status_code == 200:
            logger.info("Login successful")
            print(f"\nLogin successful")
        else:
            logger.warning(f"Login failed: {response.data}")

        return response


