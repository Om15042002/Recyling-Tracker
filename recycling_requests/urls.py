from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_request, name='create_request'),
    path('<int:request_id>/', views.request_detail, name='request_detail'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('staff/', views.staff_requests, name='staff_requests'),
    path('<int:request_id>/approve/', views.approve_request, name='approve_request'),
    path('<int:request_id>/complete/', views.complete_request, name='complete_request'),
    path('<int:request_id>/reject/', views.reject_request, name='reject_request'),
    path('<int:request_id>/mark-in-progress/', views.mark_in_progress, name='mark_in_progress'),
    path('bulk-action/', views.bulk_action, name='bulk_action'),
]