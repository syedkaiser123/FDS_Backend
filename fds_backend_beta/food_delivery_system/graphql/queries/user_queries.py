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


logger = logging.getLogger("user_queries.log")

from food_delivery_system.utils.utilities import RBACPermissionManager
from food_delivery_system.restaurant.models import Restaurant
from food_delivery_system.orders.models import Staff
from food_delivery_system.utils.utilities import UserPermissions
from food_delivery_system import settings

from food_delivery_system.graphql.permissions import BaseMutation
from food_delivery_system.graphql.utilities.utils import UserAuthentication

rbac_permissions = RBACPermissionManager()
user_authorization = UserPermissions().get_user_authorization
User = get_user_model()

user_auth = UserAuthentication()



# Define CustomUser Type
class CustomUserType(DjangoObjectType):
    class Meta:
        model = User
        # fields = ("id", "username", "email", "is_active", "is_staff", "is_restaurant", "is_manager", "is_delivery_personnel")
        fields = '__all__'
        # exclude = ('password',)  # Exclude password from response

# Query for fetching users
class UserQueries(graphene.ObjectType):
    all_users = graphene.List(CustomUserType, token=graphene.String(required=True))
    current_user = graphene.Field(CustomUserType, token=graphene.String(required=True))
    user_by_id = graphene.Field(CustomUserType, id=graphene.Int(required=True), token=graphene.String(required=True))

    @silk_profile(name="GraphQL - Fetch All Users")
    def resolve_all_users(self, root, token):
        user = user_auth.get_user_authentication(token)
        if not user:
            raise GraphQLError(f"User '{user}' not found.")
        return get_user_model().objects.all()

    def resolve_user_by_id(self, root, info, id, token):
        return get_user_model().objects.get(pk=id)
    
    def resolve_current_user(self, root, info, token):
        user = info.context.user
        if not user.is_authenticated:
            return None  # Explicitly handle unauthenticated users
        return user
    
    # @login_required
    # def resolve_current_user(self, info):
    #     import ipdb;ipdb.set_trace()
    #     return info.context.user  # Should return the authenticated user


