from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import RecyclingRequest, RequestTracking
from recycling_centers.models import RecyclingCenter, AcceptedMaterial
from notifications.models import Notification
from accounts.models import UserProfile

@login_required
def create_request(request):
    if request.method == 'POST':
        center_id = request.POST.get('recycling_center')
        center = get_object_or_404(RecyclingCenter, id=center_id)
        
        # Create the recycling request
        recycling_request = RecyclingRequest.objects.create(
            user=request.user,
            recycling_center=center,
            material_type=request.POST.get('material_type'),
            item_description=request.POST.get('item_description'),
            quantity=int(request.POST.get('quantity', 1)),
            estimated_weight=float(request.POST.get('estimated_weight', 0)),
            item_image=request.FILES.get('item_image'),
            pickup_address=request.POST.get('pickup_address'),
            pickup_latitude=request.POST.get('pickup_latitude') or None,
            pickup_longitude=request.POST.get('pickup_longitude') or None,
            preferred_pickup_date=request.POST.get('preferred_pickup_date'),
            notes=request.POST.get('notes', ''),
        )
        
        # Create initial tracking entry
        RequestTracking.objects.create(
            request=recycling_request,
            status='submitted',
            description='Request submitted successfully',
            updated_by=request.user
        )
        
        # Notify staff members
        for staff_profile in center.staff_members.all():
            Notification.objects.create(
                user=staff_profile.user,
                title='New Recycling Request',
                message=f'New recycling request for {recycling_request.material_type} from {request.user.username}',
                notification_type='new_request',
                related_request=recycling_request
            )
        
        messages.success(request, 'Your recycling request has been submitted successfully!')
        return redirect('request_detail', request_id=recycling_request.id)
    
    # GET request
    centers = RecyclingCenter.objects.filter(is_active=True)
    material_types = AcceptedMaterial.MATERIAL_TYPES
    
    return render(request, 'recycling_requests/create.html', {
        'centers': centers,
        'material_types': material_types,
    })

@login_required
def request_detail(request, request_id):
    recycling_request = get_object_or_404(RecyclingRequest, id=request_id)
    
    # Check permissions
    user_profile = getattr(request.user, 'userprofile', None)
    is_owner = request.user == recycling_request.user
    is_staff = request.user.is_staff
    is_admin_or_staff = user_profile and user_profile.user_type in ['admin', 'staff']
    
    if not (is_owner or is_staff or is_admin_or_staff):
        messages.error(request, 'You do not have permission to view this request.')
        return redirect('my_requests')
    
    tracking_history = recycling_request.tracking.all()
    
    return render(request, 'recycling_requests/detail.html', {
        'recycling_request': recycling_request,
        'tracking_history': tracking_history,
    })

@login_required
def my_requests(request):
    all_requests = RecyclingRequest.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate statistics for all requests
    pending_count = all_requests.filter(status='pending').count()
    completed_count = all_requests.filter(status='completed').count()
    
    # Filter by status for display
    requests = all_requests
    status_filter = request.GET.get('status')
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    return render(request, 'recycling_requests/my_requests.html', {
        'requests': requests,
        'status_choices': RecyclingRequest.STATUS_CHOICES,
        'selected_status': status_filter,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'total_count': all_requests.count(),
    })

@login_required
def staff_requests(request):
    """View for staff to manage requests"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type not in ['admin', 'staff']:
        messages.error(request, 'Access denied. Staff access required.')
        return redirect('dashboard')
    
    # Get requests for centers where user is staff
    if user_profile.user_type == 'admin':
        requests = RecyclingRequest.objects.all()
    else:
        centers = user_profile.recyclingcenter_set.all()
        requests = RecyclingRequest.objects.filter(recycling_center__in=centers)
    
    # Filter by status
    status_filter = request.GET.get('status', 'pending')
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    requests = requests.order_by('-created_at')
    
    return render(request, 'recycling_requests/staff_requests.html', {
        'requests': requests,
        'status_choices': RecyclingRequest.STATUS_CHOICES,
        'selected_status': status_filter,
    })

@login_required
def approve_request(request, request_id):
    """Staff view to approve/reject requests"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type not in ['admin', 'staff']:
        messages.error(request, 'Access denied. Staff access required.')
        return redirect('dashboard')
    
    recycling_request = get_object_or_404(RecyclingRequest, id=request_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        staff_notes = request.POST.get('staff_notes', '')
        
        if action == 'approve':
            recycling_request.status = 'approved'
            recycling_request.approved_by = request.user
            recycling_request.approved_at = timezone.now()
            recycling_request.staff_notes = staff_notes
            recycling_request.save()
            
            # Create tracking entry
            RequestTracking.objects.create(
                request=recycling_request,
                status='approved',
                description=f'Request approved by {request.user.username}. {staff_notes}',
                updated_by=request.user
            )
            
            # Notify user
            Notification.objects.create(
                user=recycling_request.user,
                title='Request Approved',
                message=f'Your recycling request for {recycling_request.material_type} has been approved!',
                notification_type='request_approved',
                related_request=recycling_request
            )
            
            messages.success(request, 'Request approved successfully!')
            
        elif action == 'reject':
            recycling_request.status = 'rejected'
            recycling_request.staff_notes = staff_notes
            recycling_request.save()
            
            # Create tracking entry
            RequestTracking.objects.create(
                request=recycling_request,
                status='rejected',
                description=f'Request rejected by {request.user.username}. {staff_notes}',
                updated_by=request.user
            )
            
            # Notify user
            Notification.objects.create(
                user=recycling_request.user,
                title='Request Rejected',
                message=f'Your recycling request for {recycling_request.material_type} has been rejected. Reason: {staff_notes}',
                notification_type='request_rejected',
                related_request=recycling_request
            )
            
            messages.success(request, 'Request rejected.')
        
        return redirect('staff_requests')
    
    # Calculate user statistics
    user_total_requests = recycling_request.user.recycling_requests.count()
    user_completed_requests = recycling_request.user.recycling_requests.filter(status='completed').count()
    
    return render(request, 'recycling_requests/approve.html', {
        'recycling_request': recycling_request,
        'user_total_requests': user_total_requests,
        'user_completed_requests': user_completed_requests,
    })

@login_required 
def complete_request(request, request_id):
    """Mark request as completed"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type not in ['admin', 'staff']:
        messages.error(request, 'Access denied. Staff access required.')
        return redirect('dashboard')
    
    recycling_request = get_object_or_404(RecyclingRequest, id=request_id)
    
    if request.method == 'POST':
        recycling_request.status = 'completed'
        recycling_request.completed_at = timezone.now()
        recycling_request.save()
        
        # Update user's recycled items count
        user_profile_obj, created = UserProfile.objects.get_or_create(user=recycling_request.user)
        user_profile_obj.total_items_recycled += recycling_request.quantity
        user_profile_obj.save()
        
        # Create tracking entry
        RequestTracking.objects.create(
            request=recycling_request,
            status='completed',
            description=f'Recycling completed by {request.user.username}',
            updated_by=request.user
        )
        
        # Notify user
        Notification.objects.create(
            user=recycling_request.user,
            title='Recycling Completed',
            message=f'Your {recycling_request.material_type} has been successfully recycled!',
            notification_type='recycling_completed',
            related_request=recycling_request
        )
        
        messages.success(request, 'Request marked as completed!')
        return redirect('staff_requests')
    
    return render(request, 'recycling_requests/complete.html', {
        'request': recycling_request,
    })

@login_required
def reject_request(request, request_id):
    """AJAX endpoint to reject a request"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type not in ['admin', 'staff']:
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        try:
            recycling_request = get_object_or_404(RecyclingRequest, id=request_id)
            reason = request.POST.get('reason', '')
            
            if not reason.strip():
                return JsonResponse({'success': False, 'error': 'Please provide a reason for rejection'})
            
            recycling_request.status = 'rejected'
            recycling_request.staff_notes = reason
            recycling_request.save()
            
            # Create tracking entry
            RequestTracking.objects.create(
                request=recycling_request,
                status='rejected',
                description=f'Request rejected by {request.user.username}. Reason: {reason}',
                updated_by=request.user
            )
            
            # Notify user
            Notification.objects.create(
                user=recycling_request.user,
                title='Request Rejected',
                message=f'Your recycling request for {recycling_request.material_type} has been rejected. Reason: {reason}',
                notification_type='request_rejected',
                related_request=recycling_request
            )
            
            return JsonResponse({'success': True, 'message': 'Request rejected successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@login_required
def mark_in_progress(request, request_id):
    """AJAX endpoint to mark request as in progress"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type not in ['admin', 'staff']:
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        try:
            recycling_request = get_object_or_404(RecyclingRequest, id=request_id)
            recycling_request.status = 'in_progress'
            recycling_request.save()
            
            # Create tracking entry
            RequestTracking.objects.create(
                request=recycling_request,
                status='in_progress',
                description=f'Pickup in progress - started by {request.user.username}',
                updated_by=request.user
            )
            
            # Notify user
            Notification.objects.create(
                user=recycling_request.user,
                title='Pickup In Progress',
                message=f'Your recycling request for {recycling_request.material_type} is now in progress!',
                notification_type='request_updated',
                related_request=recycling_request
            )
            
            return JsonResponse({'success': True, 'message': 'Request marked as in progress'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@login_required
def bulk_action(request):
    """AJAX endpoint for bulk actions on requests"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type not in ['admin', 'staff']:
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            action = data.get('action')
            request_ids = data.get('request_ids', [])
            notes = data.get('notes', '')
            
            if not action or not request_ids:
                return JsonResponse({'success': False, 'error': 'Missing action or request IDs'})
            
            requests_to_update = RecyclingRequest.objects.filter(id__in=request_ids)
            
            if action == 'approve':
                for req in requests_to_update:
                    req.status = 'approved'
                    req.approved_by = request.user
                    req.approved_at = timezone.now()
                    req.save()
                    
                    RequestTracking.objects.create(
                        request=req,
                        status='approved',
                        description=f'Bulk approved by {request.user.username}',
                        updated_by=request.user
                    )
                    
                    Notification.objects.create(
                        user=req.user,
                        title='Request Approved',
                        message=f'Your recycling request for {req.material_type} has been approved!',
                        notification_type='request_approved',
                        related_request=req
                    )
                
                message = f'{len(request_ids)} request(s) approved successfully'
                
            elif action == 'reject':
                if not notes:
                    return JsonResponse({'success': False, 'error': 'Please provide notes for rejection'})
                
                for req in requests_to_update:
                    req.status = 'rejected'
                    req.staff_notes = notes
                    req.save()
                    
                    RequestTracking.objects.create(
                        request=req,
                        status='rejected',
                        description=f'Bulk rejected by {request.user.username}. Reason: {notes}',
                        updated_by=request.user
                    )
                    
                    Notification.objects.create(
                        user=req.user,
                        title='Request Rejected',
                        message=f'Your recycling request for {req.material_type} has been rejected. Reason: {notes}',
                        notification_type='request_rejected',
                        related_request=req
                    )
                
                message = f'{len(request_ids)} request(s) rejected'
                
            elif action == 'mark_in_progress':
                for req in requests_to_update:
                    req.status = 'in_progress'
                    req.save()
                    
                    RequestTracking.objects.create(
                        request=req,
                        status='in_progress',
                        description=f'Bulk marked in progress by {request.user.username}',
                        updated_by=request.user
                    )
                    
                    # Notify user
                    Notification.objects.create(
                        user=req.user,
                        title='Pickup In Progress',
                        message=f'Your recycling request for {req.material_type} is now in progress!',
                        notification_type='request_updated',
                        related_request=req
                    )
                
                message = f'{len(request_ids)} request(s) marked as in progress'
            
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action'})
            
            return JsonResponse({'success': True, 'message': message})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)