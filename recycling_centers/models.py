from django.db import models
from accounts.models import UserProfile

class RecyclingCenter(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True)
    opening_hours = models.TextField(help_text="Operating hours information")
    capacity = models.IntegerField(default=100, help_text="Daily capacity")
    current_load = models.IntegerField(default=0)
    staff_members = models.ManyToManyField(UserProfile, blank=True, limit_choices_to={'user_type': 'staff'})
    image = models.ImageField(upload_to='centers/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def availability_percentage(self):
        if self.capacity == 0:
            return 0
        return ((self.capacity - self.current_load) / self.capacity) * 100

class AcceptedMaterial(models.Model):
    MATERIAL_TYPES = (
        ('plastic', 'Plastic'),
        ('glass', 'Glass'),
        ('paper', 'Paper'),
        ('metal', 'Metal'),
        ('electronic', 'Electronic'),
        ('organic', 'Organic'),
        ('textile', 'Textile'),
        ('battery', 'Battery'),
        ('other', 'Other'),
    )
    
    recycling_center = models.ForeignKey(RecyclingCenter, on_delete=models.CASCADE, related_name='accepted_materials')
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES)
    description = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('recycling_center', 'material_type')
    
    def __str__(self):
        return f"{self.recycling_center.name} - {self.material_type}"