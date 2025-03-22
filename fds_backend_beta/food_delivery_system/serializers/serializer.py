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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone_number", "address", "is_restaurant"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'phone_number', 'address', 'is_restaurant']
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password is write-only
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  # Ensures password is hashed
        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)  # Hash the password
        return super().update(instance, validated_data)

    def validate_phone_number(self, value):
        if value == "":
            return None  # Treat empty string as NULL
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)  # Nesting customer details
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "customer", "restaurant", "status", "total_price", "created_at", "updated_at", "items"]
        read_only_fields = ['status', 'created_at', 'updated_at']

    def get_items(self, obj):
        return OrderItemSerializer(obj.order_items.all(), many=True).data


class RestaurantSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

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
    user = UserSerializer(read_only=True)
    restaurant = RestaurantSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'user', 'restaurant', 'role', 'date_joined']

