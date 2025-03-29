import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth import get_user_model
from food_delivery_system.middleware import QueryProfilerMiddleware
from silk.profiling.profiler import silk_profile


# Define CustomUser Type
class CustomUserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        # fields = ("id", "username", "email", "is_active", "is_staff", "is_restaurant", "is_manager", "is_delivery_personnel", "role")
        fields = '__all__'

# Query for fetching users
class Query(graphene.ObjectType):
    all_users = graphene.List(CustomUserType)
    user_by_id = graphene.Field(CustomUserType, id=graphene.Int(required=True))

    @silk_profile(name="GraphQL - Fetch All Users")
    def resolve_all_users(self, info):
        return get_user_model().objects.all()

    @silk_profile(name="GraphQL - Fetch a single User")
    def resolve_user_by_id(self, info, id):
        return get_user_model().objects.get(pk=id)

# Mutation for creating users
class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        is_restaurant = graphene.Boolean(required=False)
        is_chef = graphene.Boolean(required=False)
        is_delivery_personnel = graphene.Boolean(required=False)
        is_active = graphene.Boolean(required=False)
        is_staff = graphene.Boolean(required=False)


    user = graphene.Field(CustomUserType)

    def mutate(self, info, username, email, password, is_restaurant=False, is_chef=False, is_delivery_personnel=False, is_active=True, is_staff=False):
        # Check if user already exists
        if get_user_model().objects.filter(username=username).exists():
            raise Exception("Username already exists")
        if get_user_model().objects.filter(email=email).exists():
            raise Exception("Email already exists")
        # Create the user
        user = get_user_model()(username=username, email=email, is_restaurant=is_restaurant, is_chef=is_chef, is_delivery_personnel=is_delivery_personnel, is_active=is_active, is_staff=is_staff, role=role)
        # Set password using set_password to hash it
        # Note: Django's User model requires the password to be set using set_password
        # to ensure it's hashed properly.
        # This is important for security reasons
        user.set_password(password)
        user.save()
        return CreateUser(user=user)


# Mutation Root
class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()

# Define Schema
schema = graphene.Schema(query=Query, mutation=Mutation)

