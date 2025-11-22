from django.contrib import admin
from .models import RecyclingCenter, AcceptedMaterial

class AcceptedMaterialInline(admin.TabularInline):
    model = AcceptedMaterial
    extra = 1

@admin.register(RecyclingCenter)
class RecyclingCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone_number', 'capacity', 'current_load', 'availability_percentage', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'address', 'phone_number', 'email')
    readonly_fields = ('created_at', 'updated_at', 'availability_percentage')
    inlines = [AcceptedMaterialInline]
    
    def availability_percentage(self, obj):
        return f"{obj.availability_percentage:.1f}%"
    availability_percentage.short_description = 'Availability'

@admin.register(AcceptedMaterial)
class AcceptedMaterialAdmin(admin.ModelAdmin):
    list_display = ('recycling_center', 'material_type', 'description')
    list_filter = ('material_type',)
    search_fields = ('recycling_center__name', 'material_type')