import factory
from factory.django import DjangoModelFactory
from food_delivery_system.users.models import CustomUser
from food_delivery_system.restaurant.models import Restaurant

class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "password123")
    phone_number = factory.Faker("numerify", text="###########")  # Generate a 10-digit phone number
    address = factory.Faker("address")
    is_staff = False
    is_superuser = False

class RestaurantFactory(DjangoModelFactory):
    class Meta:
        model = Restaurant

    owner = factory.SubFactory(CustomUserFactory)
    name = factory.Faker("company")
    address = factory.Faker("address")
    phone = factory.Faker("numerify", text="##########")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Validate that the 'name' field is a string
        name = kwargs.get("name")
        if not isinstance(name, str):
            raise TypeError("The 'name' field must be a string.")
        return super()._create(model_class, *args, **kwargs)

