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
from graphql_jwt.utils import get_payload, get_user_by_payload, jwt_decode




logger = logging.getLogger("data.log")

from food_delivery_system.utils.utilities import RBACPermissionManager
from food_delivery_system.restaurant.models import Restaurant
from food_delivery_system.orders.models import Staff
from food_delivery_system.utils.utilities import UserPermissions
from food_delivery_system import settings

from food_delivery_system.graphql.permissions import BaseMutation

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

# Query for fetching users
class Query(graphene.ObjectType):
    all_users = graphene.List(CustomUserType)
    current_user = graphene.Field(CustomUserType)
    user_by_id = graphene.Field(CustomUserType, id=graphene.Int(required=True))

    @silk_profile(name="GraphQL - Fetch All Users")
    def resolve_all_users(self, info):
        return get_user_model().objects.all()

    def resolve_user_by_id(self, info, id):
        return get_user_model().objects.get(pk=id)
    
    def resolve_current_user(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return None  # Explicitly handle unauthenticated users
        return user
    
    # @login_required
    # def resolve_current_user(self, info):
    #     import ipdb;ipdb.set_trace()
    #     return info.context.user  # Should return the authenticated user

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
                # manually decode the JWT token
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=["HS256"],  # Adjust this if you're using RS256 or others
                )
                username = payload.get("username")
                if not username:
                    raise GraphQLError("Token does not contain a valid username.")
                
                # Get the user from the token
                user_from_token = User.objects.get(username=username)

                if not user_from_token or not user_from_token.is_authenticated:
                    raise GraphQLError("Authentication credentials were not provided. If they are, then they must be wrong!")

                if user_from_token.is_anonymous:
                    raise GraphQLError("Authentication required to create a user.")

                # Extract fields dynamically
                user_data = {field: kwargs[field] for field in kwargs if kwargs[field] is not None}
                username = user_data.get("username")
                email = user_data.get("email")
                password = user_data.get("password")
                restaurant_roles = ["manager", "chef", "delivery_personnel"]

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
                else:
                    # Create the Staff object for other roles
                    staff, staff_created = Staff.objects.get_or_create(user=user, restaurant=None, role=request.data.get("role", ""))
                    if staff_created:
                        staff.role = role
                        staff.save()
                        logger.info(f"Staff object created for user '{user.username}'.")

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


# Custom Token Mutation to return both access & refresh tokens
class ObtainTokenPair(graphql_jwt.ObtainJSONWebToken):
    """
    Custom token authentication class to return both access and refresh tokens.
    """
    refresh_token = graphene.String()

    @classmethod
    def resolve(cls, root, info, **kwargs):

        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Invalid credentials")

        #TODO: add/update logic to return correct refresh token, currently it is returning an invaid refresh token.
        return cls(
            token=graphql_jwt.shortcuts.get_token(user),  # Access token
            refresh_token=get_refresh_token(user),  # Refresh token
        )


# Mutation Root
class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()  # Add CreateUser mutation
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()  # Custom login returning both tokens
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()  # This is the correct way to refresh tokens
    revoke_token = graphql_jwt.Revoke.Field()  # Optional: Logout by revoking refresh token

# Define Schema
schema = graphene.Schema(query=Query, mutation=Mutation)

