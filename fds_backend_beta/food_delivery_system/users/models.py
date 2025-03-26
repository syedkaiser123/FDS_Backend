from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_restaurant = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_chef = models.BooleanField(default=False)
    is_delivery_personnel = models.BooleanField(default=False)

    # Fix the conflicts by setting unique related_name attributes
    groups = models.ManyToManyField(Group, related_name="customuser_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions_set", blank=True)

    def __str__(self):
        return self.username
