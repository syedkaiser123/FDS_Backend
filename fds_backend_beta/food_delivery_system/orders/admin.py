from django.contrib import admin
from food_delivery_system.orders.models import Category, MenuItem, Order, OrderItem, Staff

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant')
    search_fields = ('name', 'restaurant__name')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'available')
    list_filter = ('available', 'category')
    search_fields = ('name', 'category__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'restaurant', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'restaurant')
    search_fields = ('customer__username', 'restaurant__name')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'price')
    search_fields = ('order__id', 'menu_item__name')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'role', 'date_joined')
    list_filter = ('role', 'restaurant')
    search_fields = ('user__username', 'restaurant__name')


