import factory
from factory.django import DjangoModelFactory
from food_delivery_system.orders.models import Category, MenuItem, Order, OrderItem, Staff
from food_delivery_system.restaurant.models import Restaurant
from food_delivery_system.users.models import CustomUser


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    restaurant = factory.SubFactory("food_delivery_system.restaurant.factories.RestaurantFactory")
    name = factory.Faker("word")  # Generates a random word for the category name


class MenuItemFactory(DjangoModelFactory):
    class Meta:
        model = MenuItem

    category = factory.SubFactory(CategoryFactory)
    name = factory.Faker("word")  # Generates a random word for the menu item name
    description = factory.Faker("sentence")  # Generates a random sentence for the description
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)  # Random price
    available = factory.Faker("boolean")  # Randomly sets availability to True or False
    created_at = factory.Faker("date_time_this_year")  # Random timestamp within the current year


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    customer = factory.SubFactory("food_delivery_system.users.factories.CustomUserFactory")
    restaurant = factory.SubFactory("food_delivery_system.restaurant.factories.RestaurantFactory")
    status = factory.Iterator(['pending', 'preparing', 'picked up', 'delivered', 'canceled'])  # Random status
    total_price = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)  # Random total price
    created_at = factory.Faker("date_time_this_year")  # Random timestamp within the current year
    updated_at = factory.Faker("date_time_this_year")  # Random timestamp within the current year


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    menu_item = factory.SubFactory(MenuItemFactory)
    quantity = factory.Faker("random_int", min=1, max=10)  # Random quantity between 1 and 10
    price = factory.LazyAttribute(lambda obj: obj.menu_item.price * obj.quantity)  # Calculate price dynamically


class StaffFactory(DjangoModelFactory):
    class Meta:
        model = Staff

    user = factory.SubFactory("food_delivery_system.users.factories.CustomUserFactory")
    restaurant = factory.SubFactory("food_delivery_system.restaurant.factories.RestaurantFactory")
    role = factory.Iterator(['manager', 'chef', 'delivery'])  # Random role from ROLE_CHOICES
    date_joined = factory.Faker("date_time_this_year")  # Random timestamp within the current year


