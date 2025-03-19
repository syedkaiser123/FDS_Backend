from django.contrib import admin
from food_delivery_system.restaurant.models import Restaurant

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'address', 'phone', 'created_at')  # Fields to display in the list view
    search_fields = ('name', 'owner__username', 'address')  # Enable search by name, owner username, and address
    list_filter = ('created_at',)  # Add a filter for the creation date

