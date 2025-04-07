import jwt
import graphene
from graphql import GraphQLError
from graphql_jwt.utils import get_payload, get_user_by_payload, jwt_decode
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidTokenError,
)

from django.contrib.auth import get_user_model

from food_delivery_system import settings


User = get_user_model()


class UserAuthentication():
    """
    Enforce JWT token based authentication on graphql requests.
    """
    def get_user_authentication(self, token):
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
                raise GraphQLError("Authentication required to view users.")
            
            return user_from_token
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