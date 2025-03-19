import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_delivery_system.settings')  # Replace with your settings module
django.setup()

import random
from django.utils import timezone
# from django.contrib.auth import get_user_model
from food_delivery_system.users.models import CustomUser
from food_delivery_system.orders.models import Order, OrderItem, Category, MenuItem, Staff
from food_delivery_system.restaurant.models import Restaurant

# Get the CustomUser model
User = CustomUser

def create_sample_data():
    # Create a default user to own the default restaurant
    default_user = User.objects.create_user(username="default_user", email="default@example.com", password="password123")
    print(f"Created default user: {default_user.username}")

    # Create a default restaurant owned by the default user
    default_restaurant = Restaurant.objects.create(
        owner=default_user,  # Assign the default user as the owner
        name="Default Restaurant",
        address="Default Address",
        phone="123-456-7890",
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )
    print(f"Created default restaurant: {default_restaurant.name}")

    # Create 100 users
    for i in range(1, 101):
        username = f"user{i}"
        email = f"user{i}@example.com"
        password = "password123"
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        print(f"Created user: {username}")

        # Create a restaurant for every 10th user
        if i % 10 == 0:
            restaurant = Restaurant.objects.create(
                owner=user,
                name=f"Restaurant {i}",
                address=f"Address {i}",
                phone=f"123-456-78{i % 10}",
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
            print(f"Created restaurant: {restaurant.name}")
        else:
            restaurant = default_restaurant  # Assign the default restaurant

        # Create orders for every user
        for j in range(1, 4):  # 3 orders per user
            order = Order.objects.create(
                customer=user,
                restaurant=restaurant,  # Always assign a restaurant
                status=random.choice(['pending', 'preparing', 'delivered', 'canceled']),
                total_price=random.uniform(20.0, 200.0),
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
            print(f"Created order: {order.id} for user {user.username}")

            # Create order items for the order
            for k in range(1, 4):  # 3 items per order
                menu_item = MenuItem.objects.order_by('?').first()  # Random menu item
                if menu_item:
                    order_item = OrderItem.objects.create(
                        order=order,
                        menu_item=menu_item,
                        quantity=random.randint(1, 5),
                        price=menu_item.price,
                    )
                    print(f"Created order item: {order_item.id} for order {order.id}")

if __name__ == "__main__":
    create_sample_data()

