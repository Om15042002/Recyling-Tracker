from django.contrib import admin
from .models import RecyclingRequest, RequestTracking

class RequestTrackingInline(admin.TabularInline):
    model = RequestTracking
    extra = 0
    readonly_fields = ('timestamp',)

@admin.register(RecyclingRequest)
class RecyclingRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'recycling_center', 'material_type', 'status', 'priority', 'created_at', 'approved_at')
    list_filter = ('status', 'priority', 'material_type', 'created_at', 'approved_at')
    search_fields = ('user__username', 'recycling_center__name', 'item_description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [RequestTrackingInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'recycling_center', 'approved_by')

@admin.register(RequestTracking)
class RequestTrackingAdmin(admin.ModelAdmin):
    list_display = ('request', 'status', 'timestamp', 'updated_by')
    list_filter = ('status', 'timestamp')
    search_fields = ('request__user__username', 'description')
    readonly_fields = ('timestamp',)