from rest_framework import serializers
from django.apps import apps
from django.contrib.auth.hashers import make_password

from food_delivery_system.users.models import CustomUser

Restaurant = apps.get_model('restaurant', 'Restaurant')
Category = apps.get_model('orders', 'Category')
MenuItem = apps.get_model('orders', 'MenuItem')
Order = apps.get_model('orders', 'Order')
OrderItem = apps.get_model('orders', 'OrderItem')
Staff = apps.get_model('orders', 'Staff')


User = CustomUser


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ["id", "username", "email", "phone_number", "address", "is_restaurant"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.SerializerMethodField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'phone_number', 'address', 'is_restaurant', 'is_manager', 'is_chef', 'is_delivery_personnel', 'role']
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password is write-only
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  # Ensures password is hashed
        import ipdb;ipdb.set_trace()
        # user = super().create(validated_data)

        # Extract the role from the payload
        role = self.context['request'].data.get('role')

        if role == 'restaurant':
            validated_data['is_restaurant'] = True
        elif role == 'manager':
            validated_data['is_manager'] = True
        elif role == 'chef':
            validated_data['is_chef'] = True
        elif role == 'delivery':
            validated_data['is_delivery_personnel'] = True
        else:
            # Default all boolean fields to False if no role matches
            validated_data['is_restaurant'] = False
            validated_data['is_manager'] = False
            validated_data['is_chef'] = False
            validated_data['is_delivery_personnel'] = False
        
        user = super().create(validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)  # Hash the password
        return super().update(instance, validated_data)
    
    def get_role(self, obj):
        # Fetch the role from the related Staff model
        staff = Staff.objects.filter(user=obj).first()
        return staff.role if staff else None

    def validate_phone_number(self, value):
        if value == "":
            return None  # Treat empty string as NULL
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

class OrderSerializer(serializers.ModelSerializer):
    customer = UserRegistrationSerializer(read_only=True)  # Nesting customer details
    items = serializers.ListField(write_only=True)  # Accept items in the payload

    class Meta:
        model = Order
        fields = ["id", "customer", "status", "restaurant", "status", "total_price", "created_at", "updated_at", "items"]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        # Extract items from the payload
        items_data = validated_data.pop("items", [])
        order = super().create(validated_data)

        # Create OrderItem and MenuItem objects
        for item_data in items_data:
            menu_item_name = item_data.get("menu_item")
            quantity = item_data.get("quantity", 1)

            # Create or get the MenuItem
            menu_item, _ = MenuItem.objects.get_or_create(
                name=menu_item_name,
                defaults={"price": 0.00, "available": True}  # Default values for MenuItem
            )

            # Create the OrderItem
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                price=menu_item.price * quantity,
            )

        return order

    def to_representation(self, instance):
        # Add items to the serialized output
        representation = super().to_representation(instance)
        representation["items"] = OrderItemSerializer(instance.order_items.all(), many=True).data
        return representation

class RestaurantSerializer(serializers.ModelSerializer):
    owner = UserRegistrationSerializer(read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'owner', 'name', 'address', 'phone', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'restaurant', 'name']


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'category', 'name', 'description', 'price', 'available', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menu_item', 'quantity', 'price']


class StaffSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer(read_only=True)
    restaurant = RestaurantSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'user', 'restaurant', 'role', 'date_joined']

