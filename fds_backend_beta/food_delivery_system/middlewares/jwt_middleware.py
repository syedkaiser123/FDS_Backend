import logging
from django.contrib.auth.models import AnonymousUser
from graphql import GraphQLError
# from graphql_jwt.authentication import JSONWebTokenAuthentication
from graphql_jwt.backends import JSONWebTokenBackend
from django.conf import settings

logger = logging.getLogger("data.log")

class CustomJWTMiddleware:
    """
    Custom GraphQL JWT Middleware to authenticate requests,
    attach user to context, and support fallback/logging.
    """

    def __init__(self, get_response=None):
        self.get_response = get_response
        logger.info("CustomJWTMiddleware initialized")

    def resolve(self, next, root, info, **kwargs):
        request = info.context

        import ipdb;ipdb.set_trace()
        auth_header = request.headers.get("Authorization", "")
        is_bearer = auth_header.startswith("Bearer ")

        headers = request.headers
        logger.info(f"[JWT AUTH] Headers: {headers}")
        
        token = headers.get("Authorization", None)
        if not token:
            logger.error("No Authorization header provided!!!, Authentication required!")
            raise GraphQLError("No Authorization header provided")

        if is_bearer:
            token = auth_header[len("Bearer "):].strip()

            if not token:
                raise GraphQLError("Authorization header is provided but token is missing.")

            try:
                user = JSONWebTokenBackend().authenticate(request)
                if user:
                    request.user = user
                    logger.info(f"[JWT AUTH] Authenticated user: {user}")
                else:
                    logger.warning("[JWT AUTH] Invalid JWT token.")
                    raise GraphQLError("Invalid or expired JWT token.")
            except Exception as e:
                logger.error(f"[JWT AUTH] Exception while authenticating: {e}")
                raise GraphQLError("Failed to authenticate user from token.")
        
        else:
            # If Authorization header is not provided at all
            if not hasattr(request, "user") or request.user.is_anonymous:
                request.user = AnonymousUser()
                logger.info("[JWT AUTH] No auth header provided. Proceeding as AnonymousUser.")

        return next(root, info, **kwargs)

