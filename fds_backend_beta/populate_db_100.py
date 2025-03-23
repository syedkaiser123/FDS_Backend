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
    # Check if there are existing users in the database
    last_user = CustomUser.objects.order_by('-id').first()
    start_id = last_user.id + 1 if last_user else 1  # Start from (last user ID + 1) or 1 if no users exist
    end_id = start_id + 100  # Create 100 users

    # Create a list to hold user objects
    batch_size = 10
    users_to_create = []

    # Create 100 users
    for i in range(start_id, end_id):
        username = f"user{i}"
        email = f"user{i}@example.com"
        password = "password123"

        # Add user to the list (use `set_password` to hash the password)
        user = CustomUser(username=username, email=email)
        user.set_password(password)  # Hash the password
        users_to_create.append(user)
    
        # Bulk create users when the batch is full
        if len(users_to_create) == batch_size or i == end_id - 1:
            CustomUser.objects.bulk_create(users_to_create)
            print(f"Created users {i - len(users_to_create) + 1} to {i} in bulk.")
            users_to_create = []  # Clear the batch for the next set of users

    # Create restaurants, staff, categories, and other related data for every 10th user
    users_to_create = CustomUser.objects.filter(id__gte=start_id, id__lt=end_id)  # Get the created users
    for i, user in enumerate(users_to_create, start=start_id):
        # Create a restaurant for every 10th user
        if i % 10 == 0:
            restaurant = Restaurant.objects.create(
                owner=user,
                name=f"Restaurant {i}",
                address=f"Address {i}",
                phone=f"123-456-78{i}",
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
            print(f"Created restaurant: {restaurant.name}")

            
            # Assign a single role to the user
            # Create staff for the restaurant
            staff_roles = ['manager', 'chef', 'delivery']
            role = random.choice(staff_roles)
            staff = Staff.objects.create(
                user=user,
                restaurant=restaurant,
                role=role,
                date_joined=timezone.now(),
            )
            print(f"Assigned role '{role}' to user {user.username} for restaurant {restaurant.name}")
            print(f"Created staff roles {staff_roles} for restaurant {restaurant.name}")

            # Create categories for the restaurant
            categories_to_create = []
            for j in range(1, 4):  # Create 3 categories per restaurant
                category = Category(
                    restaurant=restaurant,
                    name=f"Category {j} for {restaurant.name}",
                )
                categories_to_create.append(category)

            # Bulk create categories
            created_categories = Category.objects.bulk_create(categories_to_create)
            print(f"Created {len(created_categories)} categories for restaurant {restaurant.name}")

            # Create menu items for the restaurant
            menu_items_to_create = []
            for category in created_categories:
                for j in range(1, 6):  # Create 5 menu items per category
                    menu_item = MenuItem(
                        category=category,
                        name=f"Menu Item {j} for {category.name}",
                        description=f"Description for Menu Item {j} of {category.name}",
                        price=random.uniform(5.0, 50.0),
                        available=True,
                        created_at=timezone.now(),
                    )
                    menu_items_to_create.append(menu_item)

            # Bulk create menu items
            MenuItem.objects.bulk_create(menu_items_to_create)
            print(f"Created {len(menu_items_to_create)} menu items for restaurant {restaurant.name}")

        else:
            restaurant = Restaurant.objects.order_by('?').first()  # Assign a random existing restaurant

        # Create orders for every user
        orders_to_create = []
        for j in range(1, 4):  # 3 orders per user
            order = Order(
                customer=user,
                restaurant=restaurant,  # Always assign a restaurant
                status=random.choice(['pending', 'preparing', 'delivered', 'canceled', 'completed']),
                total_price=random.uniform(20.0, 200.0),
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
            orders_to_create.append(order)

        # Bulk create orders
        created_orders = Order.objects.bulk_create(orders_to_create)
        print(f"Created {len(created_orders)} orders for user {user.username}")

        # Create order items for each order
        order_items_to_create = []
        for order in created_orders:
            for k in range(1, 4):  # 3 items per order
                menu_item = MenuItem.objects.order_by('?').first()  # Random menu item
                if menu_item:
                    order_item = OrderItem(
                        order=order,
                        menu_item=menu_item,
                        quantity=random.randint(1, 5),
                        price=menu_item.price,
                    )
                    order_items_to_create.append(order_item)

        # Bulk create order items
        OrderItem.objects.bulk_create(order_items_to_create)
        print(f"Created {len(order_items_to_create)} order items for user {user.username}")


if __name__ == "__main__":
    create_sample_data()



