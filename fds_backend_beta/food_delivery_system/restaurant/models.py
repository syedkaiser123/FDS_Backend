from django.db import models
from django.utils import timezone
from food_delivery_system.users.models import CustomUser

User = CustomUser


class Restaurant(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="restaurant")
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.name


