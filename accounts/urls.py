from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('change-password/', views.change_password, name='change_password'),
    path('update-settings/', views.update_settings, name='update_settings'),
    
    # Admin views
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-centers/', views.manage_centers, name='manage_centers'),
    path('create-center/', views.create_center, name='create_center'),
    path('assign-staff/<int:center_id>/', views.assign_staff, name='assign_staff'),
    
    # Staff views
    path('approve-request/<int:request_id>/', views.approve_request, name='approve_request'),
]