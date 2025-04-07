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

from food_delivery_system.graphql.mutations.user_mutations import CreateUser


logger = logging.getLogger("user_auth.log")

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
class AuthMutations(graphene.ObjectType):
    create_user = CreateUser.Field()  # Add CreateUser mutation
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()  # Custom login returning both tokens
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()  # This is the correct way to refresh tokens
    revoke_token = graphql_jwt.Revoke.Field()  # Optional: Logout by revoking refresh token


