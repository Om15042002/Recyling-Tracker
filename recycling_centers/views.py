from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import RecyclingCenter, AcceptedMaterial
import math
import json

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2) * math.sin(dlat/2) + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2) * math.sin(dlon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def recycling_centers_list(request):
    centers = RecyclingCenter.objects.filter(is_active=True)
    
    # Filter by material type
    material_type = request.GET.get('material_type')
    if material_type:
        centers = centers.filter(accepted_materials__material_type=material_type)
    
    # Search by name or address
    search = request.GET.get('search')
    if search:
        centers = centers.filter(
            Q(name__icontains=search) | 
            Q(address__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Sort by distance if user location is provided
    user_lat = request.GET.get('lat')
    user_lon = request.GET.get('lon')
    
    centers_list = []
    for center in centers:
        center_data = {
            'id': center.id,
            'name': center.name,
            'description': center.description,
            'address': center.address,
            'latitude': center.latitude,
            'longitude': center.longitude,
            'phone_number': center.phone_number,
            'email': center.email,
            'website': center.website,
            'opening_hours': center.opening_hours,
            'availability_percentage': center.availability_percentage,
            'image_url': center.image.url if center.image else None,
            'accepted_materials': [
                {
                    'type': material.material_type,
                    'description': material.description
                } for material in center.accepted_materials.all()
            ]
        }
        
        # Calculate distance if user location is provided
        if user_lat and user_lon:
            try:
                distance = calculate_distance(
                    float(user_lat), float(user_lon),
                    center.latitude, center.longitude
                )
                center_data['distance'] = round(distance, 2)
            except (ValueError, TypeError):
                center_data['distance'] = None
        
        centers_list.append(center_data)
    
    # Sort by distance if available
    if user_lat and user_lon:
        centers_list.sort(key=lambda x: x['distance'] if x['distance'] is not None else float('inf'))
    
    return render(request, 'recycling_centers/list.html', {
        'centers': centers_list,
        'material_types': AcceptedMaterial.MATERIAL_TYPES,
        'selected_material': material_type,
        'search_query': search,
    })

def recycling_center_detail(request, center_id):
    center = get_object_or_404(RecyclingCenter, id=center_id, is_active=True)
    
    context = {
        'center': center,
        'accepted_materials': center.accepted_materials.all(),
    }
    
    return render(request, 'recycling_centers/detail.html', context)

def recycling_centers_map(request):
    centers = RecyclingCenter.objects.filter(is_active=True)
    
    # Filter by material type
    material_type = request.GET.get('material_type')
    if material_type:
        centers = centers.filter(accepted_materials__material_type=material_type)
    
    centers_data = []
    for center in centers:
        centers_data.append({
            'id': center.id,
            'name': center.name,
            'address': center.address,
            'latitude': center.latitude,
            'longitude': center.longitude,
            'phone_number': center.phone_number,
            'availability_percentage': center.availability_percentage,
            'accepted_materials': [material.material_type for material in center.accepted_materials.all()]
        })
    
    return render(request, 'recycling_centers/map.html', {
        'centers_json': json.dumps(centers_data),
        'material_types': AcceptedMaterial.MATERIAL_TYPES,
        'selected_material': material_type,
    })

def centers_api(request):
    """API endpoint for map markers"""
    centers = RecyclingCenter.objects.filter(is_active=True)
    
    material_type = request.GET.get('material_type')
    if material_type:
        centers = centers.filter(accepted_materials__material_type=material_type)
    
    centers_data = []
    for center in centers:
        centers_data.append({
            'id': center.id,
            'name': center.name,
            'address': center.address,
            'latitude': center.latitude,
            'longitude': center.longitude,
            'phone_number': center.phone_number,
            'availability_percentage': center.availability_percentage,
            'accepted_materials': [material.material_type for material in center.accepted_materials.all()]
        })
    
    return JsonResponse({'centers': centers_data})