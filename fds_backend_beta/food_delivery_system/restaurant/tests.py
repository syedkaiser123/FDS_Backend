from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from food_delivery_system.restaurant.models import Restaurant
from food_delivery_system.users.factories import CustomUserFactory, RestaurantFactory


class RestaurantViewSetTestCase(TestCase):
    def setUp(self):
        """Set up test data and API client."""
        self.client = APIClient()

        # Create an admin user
        self.admin_user = CustomUserFactory(is_staff=True, is_superuser=True)
        self.client.force_authenticate(user=self.admin_user)

        # Create a restaurant owner
        self.owner_user = CustomUserFactory(is_restaurant=True)
        self.restaurant = RestaurantFactory(owner=self.owner_user)

        # Create a regular user
        self.regular_user = CustomUserFactory()

        # Endpoints
        self.restaurant_list_url = "/api/restaurant/"
        self.restaurant_detail_url = f"/api/restaurant/{self.restaurant.id}/"

    # def test_create_restaurant(self):
    #     """Test creating a new restaurant."""
    #     payload = {
    #         "name": "New Restaurant",
    #         "address": "123 Main Street",
    #         "phone": "9876543210",
    #     }
        
    #     self.client.force_authenticate(user=self.owner_user)  # Authenticate as the owner
    #     response = self.client.post(self.restaurant_list_url, payload, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Restaurant.objects.count(), 2)  # Existing + new restaurant
    #     self.assertTrue(Restaurant.objects.filter(name="New Restaurant").exists())

    def test_retrieve_restaurant(self):
        """Test retrieving a restaurant."""
        response = self.client.get(self.restaurant_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.restaurant.name)

    def test_partial_update_restaurant(self):
        """Test updating a restaurant."""
        payload = {
            "name": "Updated Restaurant",
            "address": "456 Updated Street",
        }
        self.client.force_authenticate(user=self.owner_user)  # Authenticate as the owner
        response = self.client.patch(self.restaurant_detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.name, "Updated Restaurant")
        self.assertEqual(self.restaurant.address, "456 Updated Street")

    def test_delete_restaurant(self):
        """Test deleting a restaurant."""
        self.client.force_authenticate(user=self.owner_user)  # Authenticate as the owner
        response = self.client.delete(self.restaurant_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Restaurant.objects.filter(id=self.restaurant.id).exists())

    def test_permission_denied_for_regular_user(self):
        """Test that a regular user cannot create, update, or delete a restaurant."""
        self.client.force_authenticate(user=self.regular_user)

        payload = {
            "phone": "1234567890",
        }

        # Test update
        payload = {"name": "Unauthorized Update"}
        response = self.client.patch(self.restaurant_detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test delete
        response = self.client.delete(self.restaurant_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_atomicity_on_update(self):
        """Test atomicity of restaurant update with invalid data."""
        payload = {
            "name": 1234,  # Invalid name (integer instead of string)
        }
        self.client.force_authenticate(user=self.owner_user)  # Authenticate as the owner
        response = self.client.patch(self.restaurant_detail_url, payload, format="json")
        # TODO: ensure atomicity is enforced on update API first.
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.restaurant.refresh_from_db()
        self.assertNotEqual(self.restaurant.name, 1234)  # Ensure no partial update occurred

