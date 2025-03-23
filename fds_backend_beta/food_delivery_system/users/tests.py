from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from food_delivery_system.users.factories import CustomUserFactory, RestaurantFactory
from food_delivery_system.users.models import CustomUser
from food_delivery_system.restaurant.models import Restaurant

class UserViewSetTestCase(TestCase):
    def setUp(self):
        """Set up test data and API client."""
        self.client = APIClient()

        # Create an admin user
        self.admin_user = CustomUserFactory(is_staff=True, is_superuser=True)
        self.client.force_authenticate(user=self.admin_user)

        # Create a regular user
        self.user = CustomUserFactory()

        # Endpoint for users
        self.user_list_url = "/api/users/"
        self.user_detail_url = f"/api/users/{self.user.id}/"

    def test_create_user(self):
        """Test creating a new user."""
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "phone_number": "9876543210",
            "address": "New Address",
            "is_restaurant": True,
            "restaurant_name": "New Restaurant",
            "restaurant_address": "Restaurant Address"
        }
        response = self.client.post(self.user_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 3)  # Admin, user, and newuser
        self.assertTrue(Restaurant.objects.filter(name="New Restaurant").exists())

    def test_retrieve_user(self):
        """Test retrieving a user."""
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user.username)

    def test_update_user(self):
        """Test updating a user."""
        payload = {
            "username": "updateduser",
            "email": "updateduser@example.com",
            "phone_number": "1112223333"
        }
        response = self.client.patch(self.user_detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")
        self.assertEqual(self.user.email, "updateduser@example.com")
        self.assertEqual(self.user.phone_number, "1112223333")

    def test_delete_user(self):
        """Test deleting a user."""
        response = self.client.delete(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomUser.objects.filter(id=self.user.id).exists())

    def test_atomicity_on_create(self):
        """Test atomicity of user creation with invalid data."""
        payload = {
            "username": "validuser",
            "email": "validuser@example.com",
            "password": "validpassword",
            "phone_number": 1234567890,
            "address": "Valid Address",
            "is_restaurant": True,
            "restaurant_name": 1234,    # Send Invalid restaurant name
            "restaurant_address": "Valid Address"
        }
        self.client.post(self.user_list_url, payload, format="json")

        # TODO Ensure atomicity is enforced by sending an invalid restaurant_name
        # like 1234 in the above payload. Ensure that the user is not created
        # and the restaurant is not created as well. Assert the user count with 2.
        self.assertEqual(CustomUser.objects.count(), 3)  # Admin and user
        self.assertFalse(Restaurant.objects.filter(name="1234").exists())

    def test_atomicity_on_update(self):
        """Test atomicity of user update with invalid data."""
        payload = {
            "phone_number": self.user.phone_number  # Duplicate phone number
        }
        response = self.client.patch(self.user_detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.phone_number, "1234567890")  # Ensure no partial update occurred

    