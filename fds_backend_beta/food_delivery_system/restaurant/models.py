from django.db import models
from django.utils import timezone
from food_delivery_system.users.models import CustomUser

User = CustomUser


class Restaurant(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="restaurant")
    name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)

    def save(self, *args, **kwargs):
        if self.name is not None and not isinstance(self.name, str):
            raise TypeError("The 'name' field must be a string.")
        super().save(*args, **kwargs)

    class Meta:
        permissions = [
            ("can_manage_restaurant", "Can manage restaurant"),     # For Restaurant Owners
            ("can_view_analytics", "Can view analytics"),   # For Restaurant Owners
        ]

    def __str__(self):
        return self.name


