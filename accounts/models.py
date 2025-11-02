from django.db import models
from django.contrib.auth.models import AbstractUser
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
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    
    # Recycling statistics
    total_items_recycled = models.IntegerField(default=0)
    total_weight_recycled = models.FloatField(default=0.0)
    recycling_level = models.IntegerField(default=1)
    recycling_level_progress = models.IntegerField(default=0)
    co2_saved = models.FloatField(default=0.0)
    trees_saved = models.FloatField(default=0.0)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    newsletter = models.BooleanField(default=True)
    
    # Privacy settings
    public_profile = models.BooleanField(default=False)
    location_sharing = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
