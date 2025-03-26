from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from food_delivery_system.users.models import CustomUser


# Customize how CustomUser appears in admin panel
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'phone_number', 'is_restaurant', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('is_restaurant', 'is_staff', 'is_superuser')
    ordering = ('id',)

    # Optional: Customize fieldsets if needed
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'is_restaurant')}),
    )

# Register the CustomUser model with the admin panel
admin.site.register(CustomUser, CustomUserAdmin)

