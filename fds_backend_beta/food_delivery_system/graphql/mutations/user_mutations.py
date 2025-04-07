import logging
import time
import jwt

from django.contrib.auth.hashers import make_password

import graphene
import graphql_jwt
from graphene_django.types import DjangoObjectType
from django.contrib.auth import get_user_model
from food_delivery_system.middleware import QueryProfilerMiddleware
from silk.profiling.profiler import silk_profile

from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from graphql_jwt.shortcuts import get_token, get_refresh_token
# from graphql_jwt.utils import get_payload, get_user_by_payload, jwt_decode, DoesNotExist, DecodeError, ExpiredSignatureError, InvalidTokenError
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidTokenError,
)

logger = logging.getLogger("user_mutations.log")

from food_delivery_system.utils.utilities import RBACPermissionManager
from food_delivery_system.restaurant.models import Restaurant
from food_delivery_system.orders.models import Staff
from food_delivery_system.utils.utilities import UserPermissions
from food_delivery_system import settings

from food_delivery_system.graphql.permissions import BaseMutation
from food_delivery_system.graphql.utilities.utils import UserAuthentication

user_auth = UserAuthentication()
rbac_permissions = RBACPermissionManager()
user_authorization = UserPermissions().get_user_authorization
User = get_user_model()



# Define CustomUser Type
class CustomUserType(DjangoObjectType):
    class Meta:
        model = User
        # fields = ("id", "username", "email", "is_active", "is_staff", "is_restaurant", "is_manager", "is_delivery_personnel")
        fields = '__all__'
        # exclude = ('password',)  # Exclude password from response


# Mutation for creating users
class CreateUser(BaseMutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        phone_number = graphene.String(required=False)
        address = graphene.String(required=False)
        role = graphene.String(required=False)
        restaurant_name = graphene.String(required=False)
        restaurant_address = graphene.String(required=False)
        token = graphene.String(required=True) 

    success = graphene.Boolean()
    user_id = graphene.Int()

    user = graphene.Field(CustomUserType)
    role = graphene.String()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        # Since the above decorator is not compatible with a profiler, hence declaring an internal silk profiler.
        from silk.profiling.profiler import silk_profile
        with silk_profile(name="GraphQL - Create User"):
            # request = info.context
            # user = request.user
            token = kwargs.get("token", None)
            try:
                user_authentication = user_auth.get_user_authentication(token)
                if not user_authentication:
                    raise GraphQLError(f"Authentication is required. Please check if the token is valid.")

                # Extract fields dynamically
                user_data = {field: kwargs[field] for field in kwargs if kwargs[field] is not None}
                username = user_data.get("username")
                email = user_data.get("email")
                password = user_data.get("password")
                restaurant_roles = ["manager", "chef", "delivery_personnel"]
                user_role_tags = {
                                    "manager": "is_manager",
                                    "chef": "is_chef",
                                    "delivery_personnel": "is_delivery_personnel",
                                    "restaurant": "is_restaurant",
                                    "admin": "is_admin",
                                }

                # Check if user already exists dynamically
                unique_fields = ["username", "email", "phone_number", "address"]
                for field in unique_fields:
                    if field in user_data and User.objects.filter(**{field: user_data[field]}).exists():
                        logger.error(f"{field.replace('_', ' ').capitalize()} '{user_data[field]}' already exists.")
                        raise Exception(f"{field.replace('_', ' ').capitalize()} '{user_data[field]}' already exists.")

                # Create the user
                # Set password using set_password to hash it
                # Note: Django's User model requires the password to be set using set_password
                # to ensure it's hashed properly.
                # This is important for security reasons
                password = make_password(password)  # Hash password
                user = User(
                    username=username,
                    email=email,
                    phone_number = user_data.get("phone_number"),
                    password=password,
                    address=user_data.get("address", None),
                )
                user.save()

                logger.info(f"User '{username}' created successfully. Continuing to create restaurant and staff...")

                # Assign user to a group based on its role
                group = None
                role = user_data.get("role")
                if role in rbac_permissions.role_permissions_map:
                    group_name = rbac_permissions.role_permissions_map[role]["group"]
                    # group, created = Group.objects.get_or_create(name=group_name)
                    rbac_permissions.assign_role_permissions(user, role)
                    logger.info(f"User '{username}' assigned to group '{group_name}' with role '{role}'.")
                
                # Create a restaurant and a Staff object if role exists.
                # Create a related restaurant atomically if the user is a restaurant owner
                if user_data.get("role") == "restaurant":
                    restaurant, restaurant_created = Restaurant.objects.get_or_create(
                        owner = user,
                        name = user_data.get("restaurant_name", None),
                        address = user_data.get("restaurant_address", None),
                        phone = user_data.get("phone_number", None),
                    )

                    logger.info(f"Restaurant '{user_data.get('restaurant_name', None)}' created successfully. owner of the restaurant is: '{user.username}'")
                    if restaurant_created:
                        user.is_restaurant = True
                        user.save()
                        logger.info(f"User '{user.username}' is now a restaurant owner. 'is_restaurant' set to True.")
                    
                    # Create the Staff object
                    staff, staff_created = Staff.objects.get_or_create(
                        user=user,
                        restaurant=restaurant,
                        role=role,
                    )
                    if staff_created:
                        staff.role = role
                        staff.save()
                    logger.info(f"Staff object created for user '{user.username}'.")
                elif role in restaurant_roles:
                    restaurant_name = user_data.get("restaurant_name", None)
                    if not restaurant_name:
                        raise ValidationError(f"A restaurant must be associated with the role '{role}'")

                    try:
                        restaurant, created = Restaurant.objects.get_or_create(
                                                                    owner=None,
                                                                    phone=user.phone_number,
                                                                    name=user_data.get("restaurant_name", None),
                                                                    address=user_data.get("restaurant_address", None),
                                                                    )
                        if created:
                            user.is_restaurant = True
                            user.save()
                    except Restaurant.DoesNotExist:
                        raise ValidationError("The specified restaurant does not exist.")

                    staff, staff_created = Staff.objects.get_or_create(user=user, restaurant=restaurant, role=role)
                    if staff_created:
                        staff.role = role
                        staff.save()
                        logger.info(f"Staff object created for user '{user.username}'.")
                        if role in user_role_tags:
                            setattr(user, user_role_tags[role], True)
                            user.save()
                            logger.info(f"User '{user.username}' updated with role '{role}'.")
                        
                else:
                    # Create the Staff object for other roles
                    staff, staff_created = Staff.objects.get_or_create(user=user, restaurant=None, role=request.data.get("role", ""))
                    if staff_created:
                        staff.role = role
                        staff.save()
                        logger.info(f"Staff object created for user '{user.username}'.")
                        if role in user_role_tags:
                            setattr(user, user_role_tags[role], True)
                            user.save()
                            logger.info(f"User '{user.username}' updated with role '{role}'.")

                return CreateUser(user=user, role=role, message="User created successfully!")
            except jwt.exceptions.DecodeError:
                raise GraphQLError("Invalid token: Signature decode error.")
            except jwt.exceptions.ExpiredSignatureError:
                raise GraphQLError("Token has expired.")
            except jwt.exceptions.InvalidTokenError as e:
                raise GraphQLError(f"Invalid token: {str(e)}")
            except User.DoesNotExist:
                raise GraphQLError("User in token does not exist.")
            except Exception as e:
                raise GraphQLError(f"error: {str(e)}")

