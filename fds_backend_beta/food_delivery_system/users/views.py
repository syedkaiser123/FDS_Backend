from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


from food_delivery_system.serializers.serializer import UserSerializer, UserRegistrationSerializer
from food_delivery_system.users.models import CustomUser
from food_delivery_system.utils.pagination import CustomPagination


# class LoginView(APIView):
#     def post(self, request):
#         username = request.data.get("username")
#         password = request.data.get("password")
#
#         import ipdb;ipdb.set_trace()
#         user = authenticate(username=username, password=password)
#         if user:
#             # Get or create a token for the user
#             token, created = Token.objects.get_or_create(user=user)
#             return Response({"token": token.key}, status=status.HTTP_200_OK)
#
#         return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class UserViewSet(viewsets.ModelViewSet):
    """
    User management with robust error handling & custom pagination.

    list: Retrieve all users with pagination.
    retrieve: Retrieve a single user.
    create: Create a new user.
    update: Update user details.
    destroy: Delete a user.
    """
    
    queryset = CustomUser.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        """Use UserRegistrationSerializer for user creation (registration)."""
        if self.action in ['create', 'update', 'partial_update']:
            return UserRegistrationSerializer
        return UserSerializer

    def list(self, request, *args, **kwargs):
        """Retrieve all users with pagination."""
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            return Response(self.get_serializer(queryset, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a single user, handling potential errors."""
        try:
            instance = self.get_object()
            self.check_object_permissions(request, instance)  # Ensure the user has access
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({"error": "You do not have permission to view this user."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        """Create a new user with validation checks."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response({"message": "User created successfully.", "results": UserSerializer(user).data}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"error": "User with this information already exists."}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """Update user details with permission check."""
        try:
            instance = self.get_object()
            if not request.user.is_staff and request.user != instance:
                raise PermissionDenied("You can only update your own profile.")

            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "User updated successfully.", "results": serializer.data}, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """Delete a user with safety checks."""
        try:
            instance = self.get_object()
            if not request.user.is_staff and request.user != instance:
                raise PermissionDenied("You do not have permission to delete this user.")
            
            instance.delete()
            return Response({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

