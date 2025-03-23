from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from food_delivery_system.orders.models import Order, OrderItem
from food_delivery_system.users.factories import CustomUserFactory, RestaurantFactory
from food_delivery_system.orders.factories import OrderFactory, OrderItemFactory


class OrderViewSetTestCase(TestCase):
    def setUp(self):
        """Set up test data and API client."""
        self.client = APIClient()

        # Create a customer
        self.customer = CustomUserFactory()
        self.client.force_authenticate(user=self.customer)

        # Create another user who is not the owner of the order
        self.other_user = CustomUserFactory()

        # Create a user who is not a customer (e.g., a staff user)
        self.staff_user = CustomUserFactory(is_staff=True)

        # Create a restaurant and an order
        self.restaurant = RestaurantFactory()
        self.order = OrderFactory(customer=self.customer, restaurant=self.restaurant)

        # Endpoints
        self.order_list_url = "/api/orders/"    # list all orders
        self.order_detail_url = f"/api/orders/{self.order.id}/"     # list a specific order details
        self.item_detail_url = f"/api/get-order-items/"    # list all order items

    def test_create_order(self):
        """Test creating a new order."""
        payload = {
            "restaurant": self.restaurant.id,
            "items": [
                {"menu_item": "Pizza", "quantity": 2},
                {"menu_item": "Burger", "quantity": 1},
            ],
        }
        response = self.client.post(self.order_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)  # Existing(order created above in the setUp method) + new order
        self.assertEqual(Order.objects.last().customer, self.customer)

    def test_retrieve_order(self):
        """Test retrieving an order."""
        response = self.client.get(self.order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.order.id)

    def test_update_order(self):
        """Test updating an order."""
        payload = {"status": "completed"}
        response = self.client.patch(self.order_detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "completed")

    def test_delete_order(self):
        """Test deleting an order."""
        response = self.client.delete(self.order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_neither_authenticated_nor_authorized(self):
        """Test that unauthenticated and unauthorized users cannot access endpoints."""
        self.client.force_authenticate(user=None)  # No authentication

        # Test create
        payload = {
            "restaurant": self.restaurant.id,
            "items": [{"menu_item": "Pizza", "quantity": 2}],
        }
        response = self.client.post(self.order_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test update
        payload = {"status": "completed"}
        response = self.client.patch(self.order_detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test delete
        response = self.client.delete(self.order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_but_not_authenticated(self):
        """Test that authenticated but unauthorized users cannot access endpoints."""
        self.client.force_authenticate(user=self.other_user)
        self.client.logout()    # logout the user to ensure he is not authenticated.

        # Test create
        payload = {
            "restaurant": self.restaurant.id,
            "items": [{"menu_item": "Pizza", "quantity": 2}],
        }
        response = self.client.post(self.order_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test update
        payload = {"status": "completed"}
        response = self.client.patch(self.order_detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test delete
        response = self.client.delete(self.order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_but_not_authorized(self):
        """Test that unauthenticated but authorized users cannot access endpoints."""
        # Simulate a scenario where the user is authenticated but not authorized
        # This is not a valid scenario in DRF, but we can simulate it by not authenticating the user
        self.client.force_authenticate(user=self.staff_user)  # Authenticated

        # Test create
        payload = {
            "restaurant": self.restaurant.id,
            "items": [{"menu_item": "Pizza", "quantity": 2}],
        }
        response = self.client.post(self.order_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test update
        payload = {"status": "completed"}
        response = self.client.patch(self.order_detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test delete
        response = self.client.delete(self.order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



class OrderItemViewSetTestCase(TestCase):
    def setUp(self):
        """Set up test data and API client."""
        self.client = APIClient()

        # Create a restaurant owner and a chef
        self.owner = CustomUserFactory(is_restaurant=True)
        self.chef = CustomUserFactory()

        # Create a restaurant, order, and order item
        self.restaurant = RestaurantFactory(owner=self.owner)
        self.order = OrderFactory(restaurant=self.restaurant)
        self.order_item = OrderItemFactory(order=self.order)

        # Endpoints
        self.order_item_list_url = "/api/orders/order-items/"
        self.order_item_detail_url = f"/api/orders/order-items/{self.order_item.id}/"

    def test_retrieve_order_item(self):
        """Test retrieving an order item."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.order_item_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.order_item.id)

    def test_update_order_item(self):
        """Test updating an order item."""
        self.client.force_authenticate(user=self.owner)
        payload = {"quantity": 5}
        response = self.client.patch(self.order_item_detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order_item.refresh_from_db()
        self.assertEqual(self.order_item.quantity, 5)

    def test_delete_order_item(self):
        """Test deleting an order item."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.order_item_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(OrderItem.objects.filter(id=self.order_item.id).exists())

    def test_permission_denied_for_non_owner(self):
        """Test that non-owners cannot update or delete order items."""
        self.client.force_authenticate(user=self.chef)

        # Test update
        payload = {"quantity": 5}
        response = self.client.patch(self.order_item_detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test delete
        response = self.client.delete(self.order_item_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

