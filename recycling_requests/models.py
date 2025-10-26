from django.db import models
from django.contrib.auth.models import User
from recycling_centers.models import RecyclingCenter, AcceptedMaterial

class RecyclingRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recycling_requests')
    recycling_center = models.ForeignKey(RecyclingCenter, on_delete=models.CASCADE, related_name='requests')
    material_type = models.CharField(max_length=20, choices=AcceptedMaterial.MATERIAL_TYPES)
    item_description = models.TextField()
    quantity = models.IntegerField(default=1)
    estimated_weight = models.FloatField(help_text="Weight in kg")
    item_image = models.ImageField(upload_to='requests/')
    additional_images = models.JSONField(default=list, blank=True)  # Store additional image paths
    pickup_address = models.TextField()
    pickup_latitude = models.FloatField(null=True, blank=True)
    pickup_longitude = models.FloatField(null=True, blank=True)
    preferred_pickup_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    notes = models.TextField(blank=True)
    staff_notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requests')
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.material_type} - {self.status}"

class RequestTracking(models.Model):
    TRACKING_STATUS = (
        ('submitted', 'Request Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('pickup_scheduled', 'Pickup Scheduled'),
        ('picked_up', 'Item Picked Up'),
        ('processing', 'Processing'),
        ('completed', 'Recycling Completed'),
        ('rejected', 'Request Rejected'),
    )
    
    request = models.ForeignKey(RecyclingRequest, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=20, choices=TRACKING_STATUS)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.request} - {self.status}"