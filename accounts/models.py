from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_TYPES = (
        ('normal', 'Normal User'),
        ('admin', 'Admin'),
        ('staff', 'Recycling Center Staff'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='normal')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
