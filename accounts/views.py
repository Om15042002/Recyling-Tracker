from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import UserProfile
from recycling_requests.models import RecyclingRequest
from recycling_centers.models import RecyclingCenter, AcceptedMaterial
from django.db.models import Count, Q
import json

def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Redirect to next page if specified, otherwise to dashboard
            next_page = request.GET.get('next', 'dashboard')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        user_type = request.POST.get('user_type', 'normal')
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                user_type=user_type,
                phone_number=request.POST.get('phone_number', ''),
                address=request.POST.get('address', '')
            )
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update user information
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Update profile information
        user_profile.phone_number = request.POST.get('phone_number', '')
        user_profile.address = request.POST.get('address', '')
        user_profile.city = request.POST.get('city', '')
        user_profile.postal_code = request.POST.get('postal_code', '')
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']
        user_profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    # Get user statistics
    requests = RecyclingRequest.objects.filter(user=request.user)
    context = {
        'user_profile': user_profile,
        'total_requests': requests.count(),
        'completed_requests': requests.filter(status='completed').count(),
        'pending_requests': requests.filter(status='pending').count(),
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def dashboard(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Route to appropriate dashboard based on user type
    if user_profile.user_type == 'admin':
        return admin_dashboard(request)
    elif user_profile.user_type == 'staff':
        return staff_dashboard(request)
    else:
        return normal_user_dashboard(request)

@login_required
def normal_user_dashboard(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    # Get user's recycling requests statistics
    requests = RecyclingRequest.objects.filter(user=request.user)
    
    stats = {
        'total_requests': requests.count(),
        'pending_requests': requests.filter(status='pending').count(),
        'approved_requests': requests.filter(status='approved').count(),
        'completed_requests': requests.filter(status='completed').count(),
        'total_items_recycled': user_profile.total_items_recycled,
    }
    
    # Get material type distribution
    material_stats = requests.values('material_type').annotate(
        count=Count('material_type')
    ).order_by('-count')
    
    # Recent requests
    recent_requests = requests.order_by('-created_at')[:5]
    
    # Nearby recycling centers
    nearby_centers = RecyclingCenter.objects.filter(is_active=True)[:5]
    
    context = {
        'user_profile': user_profile,
        'stats': stats,
        'material_stats': list(material_stats),
        'recent_requests': recent_requests,
        'nearby_centers': nearby_centers,
        'dashboard_type': 'normal',
    }
    
    return render(request, 'accounts/dashboard.html', context)

@login_required
def admin_dashboard(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    # Admin statistics
    stats = {
        'total_users': User.objects.count(),
        'normal_users': UserProfile.objects.filter(user_type='normal').count(),
        'staff_users': UserProfile.objects.filter(user_type='staff').count(),
        'admin_users': UserProfile.objects.filter(user_type='admin').count(),
        'total_centers': RecyclingCenter.objects.count(),
        'active_centers': RecyclingCenter.objects.filter(is_active=True).count(),
        'total_requests': RecyclingRequest.objects.count(),
        'pending_requests': RecyclingRequest.objects.filter(status='pending').count(),
    }
    
    # Recent users
    recent_users = User.objects.select_related('userprofile').order_by('-date_joined')[:10]
    
    # Recent requests
    recent_requests = RecyclingRequest.objects.select_related('user', 'recycling_center').order_by('-created_at')[:10]
    
    # Recycling centers
    centers = RecyclingCenter.objects.all()[:10]
    
    context = {
        'user_profile': user_profile,
        'stats': stats,
        'recent_users': recent_users,
        'recent_requests': recent_requests,
        'centers': centers,
        'dashboard_type': 'admin',
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
def staff_dashboard(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type != 'staff':
        messages.error(request, 'Access denied. Staff privileges required.')
        return redirect('dashboard')
    
    # Get centers assigned to this staff member
    assigned_centers = RecyclingCenter.objects.filter(staff_members=user_profile)
    
    if not assigned_centers.exists():
        # Staff not assigned to any center
        context = {
            'user_profile': user_profile,
            'no_assignment': True,
            'dashboard_type': 'staff',
        }
        return render(request, 'accounts/staff_dashboard.html', context)
    
    # Get requests for assigned centers
    center_requests = RecyclingRequest.objects.filter(
        recycling_center__in=assigned_centers
    ).order_by('-created_at')
    
    # Statistics for staff dashboard
    stats = {
        'assigned_centers': assigned_centers.count(),
        'total_requests': center_requests.count(),
        'pending_requests': center_requests.filter(status='pending').count(),
        'approved_requests': center_requests.filter(status='approved').count(),
        'completed_requests': center_requests.filter(status='completed').count(),
        'rejected_requests': center_requests.filter(status='rejected').count(),
    }
    
    # Recent requests for assigned centers
    recent_requests = center_requests[:10]
    
    # Pending requests that need attention
    pending_requests = center_requests.filter(status='pending')[:10]
    
    context = {
        'user_profile': user_profile,
        'stats': stats,
        'assigned_centers': assigned_centers,
        'recent_requests': recent_requests,
        'pending_requests': pending_requests,
        'dashboard_type': 'staff',
    }
    
    return render(request, 'accounts/staff_dashboard.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return redirect('profile')

@login_required
def update_settings(request):
    if request.method == 'POST':
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Update notification preferences
        user_profile.email_notifications = 'email_notifications' in request.POST
        user_profile.sms_notifications = 'sms_notifications' in request.POST
        user_profile.newsletter = 'newsletter' in request.POST
        
        # Update privacy settings
        user_profile.public_profile = 'public_profile' in request.POST
        user_profile.location_sharing = 'location_sharing' in request.POST
        
        user_profile.save()
        messages.success(request, 'Settings updated successfully!')
    
    return redirect('profile')

@login_required
def manage_users(request):
    """Admin view to manage all users"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    # Get all users with their profiles
    users_list = User.objects.select_related('userprofile').order_by('-date_joined')
    
    # Filter by user type if specified
    user_type_filter = request.GET.get('user_type')
    if user_type_filter and user_type_filter != 'all':
        users_list = users_list.filter(userprofile__user_type=user_type_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        users_list = users_list.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(users_list, 20)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    context = {
        'users': users,
        'user_type_filter': user_type_filter,
        'search_query': search_query,
        'user_types': UserProfile.USER_TYPES,
    }
    
    return render(request, 'accounts/manage_users.html', context)

@login_required
def manage_centers(request):
    """Admin view to manage recycling centers"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    centers_list = RecyclingCenter.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        centers_list = centers_list.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(centers_list, 10)
    page_number = request.GET.get('page')
    centers = paginator.get_page(page_number)
    
    context = {
        'centers': centers,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/manage_centers.html', context)

@login_required
def create_center(request):
    """Admin view to create new recycling center"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Create new recycling center
        center = RecyclingCenter.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            address=request.POST.get('address'),
            latitude=float(request.POST.get('latitude', 0)),
            longitude=float(request.POST.get('longitude', 0)),
            phone_number=request.POST.get('phone_number'),
            email=request.POST.get('email'),
            website=request.POST.get('website', ''),
            opening_hours=request.POST.get('opening_hours'),
            capacity=int(request.POST.get('capacity', 100)),
        )
        
        # Handle image upload
        if 'image' in request.FILES:
            center.image = request.FILES['image']
            center.save()
        
        # Add accepted materials
        selected_materials = request.POST.getlist('materials')
        for material in selected_materials:
            AcceptedMaterial.objects.create(
                recycling_center=center,
                material_type=material
            )
        
        messages.success(request, f'Recycling center "{center.name}" created successfully!')
        return redirect('manage_centers')
    
    context = {
        'material_types': AcceptedMaterial.MATERIAL_TYPES,
    }
    
    return render(request, 'accounts/create_center.html', context)

@login_required
def assign_staff(request, center_id):
    """Admin view to assign staff to recycling center"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    center = get_object_or_404(RecyclingCenter, id=center_id)
    
    if request.method == 'POST':
        # Get selected staff members
        selected_staff = request.POST.getlist('staff_members')
        
        # Clear existing assignments
        center.staff_members.clear()
        
        # Add new assignments
        for staff_id in selected_staff:
            staff_profile = UserProfile.objects.get(id=staff_id)
            center.staff_members.add(staff_profile)
        
        messages.success(request, f'Staff assignments updated for {center.name}!')
        return redirect('manage_centers')
    
    # Get all staff members
    staff_members = UserProfile.objects.filter(user_type='staff').select_related('user')
    assigned_staff = center.staff_members.all()
    
    context = {
        'center': center,
        'staff_members': staff_members,
        'assigned_staff': assigned_staff,
    }
    
    return render(request, 'accounts/assign_staff.html', context)

@login_required
def approve_request(request, request_id):
    """Staff view to approve recycling request"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type != 'staff':
        messages.error(request, 'Access denied. Staff privileges required.')
        return redirect('dashboard')
    
    recycling_request = get_object_or_404(RecyclingRequest, id=request_id)
    
    # Check if staff is assigned to this center
    if not recycling_request.recycling_center.staff_members.filter(id=user_profile.id).exists():
        messages.error(request, 'You are not authorized to manage requests for this center.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            recycling_request.status = 'approved'
            recycling_request.save()
            messages.success(request, 'Request approved successfully!')
        elif action == 'reject':
            recycling_request.status = 'rejected'
            recycling_request.rejection_reason = request.POST.get('rejection_reason', '')
            recycling_request.save()
            messages.success(request, 'Request rejected.')
        
        return redirect('dashboard')
    
    context = {
        'recycling_request': recycling_request,
    }
    
    return render(request, 'accounts/approve_request.html', context)

def logout_view(request):
    """Handle user logout"""
    auth_logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')
