from django.urls import path
from . import views

urlpatterns = [
    path('', views.recycling_centers_list, name='recycling_centers_list'),
    path('<int:center_id>/', views.recycling_center_detail, name='recycling_center_detail'),
    path('map/', views.recycling_centers_map, name='recycling_centers_map'),
    path('api/centers/', views.centers_api, name='centers_api'),
]