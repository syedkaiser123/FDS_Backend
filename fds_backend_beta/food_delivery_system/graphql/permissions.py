import graphene
from graphql import GraphQLError

from food_delivery_system.utils.utilities import UserPermissions
from rest_framework.exceptions import PermissionDenied, NotFound


class BaseMutation(graphene.Mutation):
    def mutate(self, info, **kwargs):
        pass

    @classmethod
    def check_permissions(cls, info):
        request = info.context
        try:
            UserPermissions.get_permissions(cls, request)
        except PermissionDenied as e:
            raise GraphQLError(str(e))


