// EcoTracker JavaScript Application
// Enhanced user interactions and functionality

// Initialize tooltips and other components
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize enhanced features
    initializeEnhancedFeatures();
});

// Enhanced features initialization
function initializeEnhancedFeatures() {
    // Animate cards on load
    animateElements();
    
    // Initialize form enhancements
    enhanceForms();
    
    // Initialize notification system
    setupNotifications();
    
    // Initialize toast system
    initializeToastSystem();
}

// Animate elements on page load
function animateElements() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Enhanced form functionality
function enhanceForms() {
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
    
    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            previewUploadedFile(e.target);
        });
    });
}

// File preview function
function previewUploadedFile(input) {
    const file = input.files[0];
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            let preview = input.parentNode.querySelector('.file-preview');
            if (!preview) {
                preview = document.createElement('div');
                preview.className = 'file-preview mt-2';
                input.parentNode.appendChild(preview);
            }
            preview.innerHTML = `
                <img src="${e.target.result}" alt="Preview" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
                <p class="small text-muted mt-1">${file.name}</p>
            `;
        };
        reader.readAsDataURL(file);
    }
}

// Enhanced notification system
function setupNotifications() {
    // Show toast notifications
    window.showToast = function(message, type = 'info') {
        const toastContainer = getOrCreateToastContainer();
        const toastId = 'toast-' + Date.now();
        
        const colors = {
            success: 'success',
            error: 'danger', 
            warning: 'warning',
            info: 'info'
        };
        
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${colors[type] || 'info'}" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        toastElement.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    };
}

function getOrCreateToastContainer() {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    return container;
}

// Location functions
function getUserLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation is not supported by this browser.'));
            return;
        }

        navigator.geolocation.getCurrentPosition(
            position => {
                resolve({
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                });
            },
            error => {
                reject(error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000
            }
        );
    });
}

// Distance calculation
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Format distance
function formatDistance(distance) {
    if (distance < 1) {
        return (distance * 1000).toFixed(0) + ' m';
    }
    return distance.toFixed(1) + ' km';
}

// Image preview
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById(previewId);
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        }
    });

    return isValid;
}

// Show loading spinner
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="spinner"></div>';
    }
}

// Hide loading spinner
function hideLoading(elementId, content = '') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = content;
    }
}

// Toast notifications
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

// Auto-complete address
function initAddressAutocomplete(inputId) {
    const input = document.getElementById(inputId);
    if (!input || !google || !google.maps || !google.maps.places) {
        return;
    }

    const autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.addListener('place_changed', function() {
        const place = autocomplete.getPlace();
        if (place.geometry) {
            // Update hidden fields if they exist
            const latField = document.getElementById(inputId + '_latitude');
            const lngField = document.getElementById(inputId + '_longitude');
            
            if (latField) latField.value = place.geometry.location.lat();
            if (lngField) lngField.value = place.geometry.location.lng();
        }
    });
}

// Filter functions
function filterCenters() {
    const materialType = document.getElementById('material-filter')?.value;
    const searchQuery = document.getElementById('search-filter')?.value;
    
    const params = new URLSearchParams();
    if (materialType) params.append('material_type', materialType);
    if (searchQuery) params.append('search', searchQuery);
    
    // Add user location if available
    getUserLocation().then(location => {
        params.append('lat', location.lat);
        params.append('lon', location.lng);
        window.location.href = `${window.location.pathname}?${params.toString()}`;
    }).catch(() => {
        window.location.href = `${window.location.pathname}?${params.toString()}`;
    });
}

// AJAX helpers
function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        },
        credentials: 'same-origin'
    };

    // Add CSRF token for POST requests
    if (options.method === 'POST') {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            defaultOptions.headers['X-CSRFToken'] = csrfToken;
        }
    }

    return fetch(url, { ...defaultOptions, ...options });
}

// Real-time search
function setupSearch(inputId, resultsId, searchUrl) {
    const input = document.getElementById(inputId);
    const results = document.getElementById(resultsId);
    
    if (!input || !results) return;
    
    let searchTimeout;
    
    input.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            results.innerHTML = '';
            return;
        }
        
        searchTimeout = setTimeout(() => {
            showLoading(resultsId);
            
            makeRequest(`${searchUrl}?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    displaySearchResults(data, resultsId);
                })
                .catch(error => {
                    console.error('Search error:', error);
                    results.innerHTML = '<div class="alert alert-danger">Search failed. Please try again.</div>';
                });
        }, 300);
    });
}

function displaySearchResults(data, resultsId) {
    const results = document.getElementById(resultsId);
    if (!results) return;
    
    if (data.length === 0) {
        results.innerHTML = '<div class="alert alert-info">No results found.</div>';
        return;
    }
    
    let html = '<div class="list-group">';
    data.forEach(item => {
        html += `
            <a href="${item.url}" class="list-group-item list-group-item-action">
                <h6 class="mb-1">${item.title}</h6>
                <p class="mb-1">${item.description}</p>
                ${item.distance ? `<small class="text-muted">${formatDistance(item.distance)}</small>` : ''}
            </a>
        `;
    });
    html += '</div>';
    
    results.innerHTML = html;
}

// Map utilities
function initMap(mapId, centers = []) {
    if (!google || !google.maps) {
        console.error('Google Maps API not loaded');
        return;
    }
    
    const mapElement = document.getElementById(mapId);
    if (!mapElement) return;
    
    const map = new google.maps.Map(mapElement, {
        zoom: 12,
        center: { lat: 40.7128, lng: -74.0060 }, // Default to NYC
        styles: [
            {
                featureType: 'poi',
                elementType: 'labels',
                stylers: [{ visibility: 'off' }]
            }
        ]
    });
    
    // Add markers for centers
    const markers = [];
    const infoWindow = new google.maps.InfoWindow();
    
    centers.forEach(center => {
        const marker = new google.maps.Marker({
            position: { lat: center.latitude, lng: center.longitude },
            map: map,
            title: center.name,
            icon: {
                url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
                        <circle cx="16" cy="16" r="12" fill="#28a745" stroke="#fff" stroke-width="2"/>
                        <text x="16" y="20" text-anchor="middle" fill="white" font-size="16">♻</text>
                    </svg>
                `),
                scaledSize: new google.maps.Size(32, 32)
            }
        });
        
        marker.addListener('click', () => {
            const content = `
                <div style="max-width: 300px;">
                    <h6>${center.name}</h6>
                    <p><strong>Address:</strong> ${center.address}</p>
                    <p><strong>Phone:</strong> ${center.phone_number}</p>
                    <p><strong>Availability:</strong> ${center.availability_percentage}%</p>
                    <div class="mt-2">
                        <a href="/centers/${center.id}/" class="btn btn-sm btn-success">View Details</a>
                    </div>
                </div>
            `;
            infoWindow.setContent(content);
            infoWindow.open(map, marker);
        });
        
        markers.push(marker);
    });
    
    // Fit map to show all markers
    if (markers.length > 0) {
        const bounds = new google.maps.LatLngBounds();
        markers.forEach(marker => bounds.extend(marker.getPosition()));
        map.fitBounds(bounds);
    }
    
    // Try to get user location and center map
    getUserLocation().then(location => {
        const userMarker = new google.maps.Marker({
            position: { lat: location.lat, lng: location.lng },
            map: map,
            title: 'Your Location',
            icon: {
                url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                        <circle cx="12" cy="12" r="8" fill="#007bff" stroke="#fff" stroke-width="2"/>
                    </svg>
                `),
                scaledSize: new google.maps.Size(24, 24)
            }
        });
        
        if (markers.length === 0) {
            map.setCenter({ lat: location.lat, lng: location.lng });
            map.setZoom(12);
        }
    }).catch(error => {
        console.log('Could not get user location:', error);
    });
    
    return map;
}

// Initialize page-specific functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize image preview for file inputs
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const previewId = this.dataset.preview;
            if (previewId) {
                previewImage(this, previewId);
            }
        });
    });
    
    // Initialize form validation
    const forms = document.querySelectorAll('form[data-validate="true"]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this.id)) {
                e.preventDefault();
                showToast('Please fill in all required fields.', 'danger');
            }
        });
    });
    
    // Initialize address autocomplete
    const addressInputs = document.querySelectorAll('input[data-autocomplete="address"]');
    addressInputs.forEach(input => {
        initAddressAutocomplete(input.id);
    });
});

// Enhanced Toast Notification System
function initializeToastSystem() {
    // Create toast container if it doesn't exist
    if (!document.getElementById('toast-container')) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1070';
        document.body.appendChild(container);
    }
}

function showToast(message, type = 'info', title = '', duration = 5000) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toastId = 'toast-' + Date.now();
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    const colors = {
        success: 'text-success',
        error: 'text-danger',
        warning: 'text-warning',
        info: 'text-info'
    };
    
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="${icons[type]} ${colors[type]} me-2"></i>
                <strong class="me-auto">${title || type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                <small class="text-muted">Just now</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: duration
    });
    
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Enhanced notification functionality
function setupNotifications() {
    // Update notification badge periodically
    setInterval(updateNotificationBadge, 30000); // Every 30 seconds
    
    // Setup notification click handlers
    document.addEventListener('click', function(e) {
        if (e.target.matches('.notification-mark-read')) {
            e.preventDefault();
            markNotificationAsRead(e.target.dataset.notificationId);
        }
        
        if (e.target.matches('.notification-delete')) {
            e.preventDefault();
            deleteNotification(e.target.dataset.notificationId);
        }
    });
}

function updateNotificationBadge() {
    fetch('/notifications/unread-count/')
        .then(response => response.json())
        .then(data => {
            const badge = document.querySelector('.notification-badge');
            if (badge) {
                if (data.count > 0) {
                    badge.textContent = data.count > 99 ? '99+' : data.count;
                    badge.style.display = 'block';
                } else {
                    badge.style.display = 'none';
                }
            }
        })
        .catch(error => console.log('Error updating notification badge:', error));
}

function markNotificationAsRead(notificationId) {
    fetch(`/notifications/${notificationId}/mark-read/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notificationElement) {
                notificationElement.classList.remove('unread');
                notificationElement.classList.add('read');
            }
            updateNotificationBadge();
            showToast('Notification marked as read', 'success');
        } else {
            showToast('Error marking notification as read', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error marking notification as read', 'error');
    });
}

function deleteNotification(notificationId) {
    if (!confirm('Are you sure you want to delete this notification?')) {
        return;
    }
    
    fetch(`/notifications/${notificationId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notificationElement) {
                notificationElement.style.transition = 'all 0.3s ease';
                notificationElement.style.opacity = '0';
                notificationElement.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    notificationElement.remove();
                }, 300);
            }
            updateNotificationBadge();
            showToast('Notification deleted', 'success');
        } else {
            showToast('Error deleting notification', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error deleting notification', 'error');
    });
}

function markAllNotificationsAsRead() {
    fetch('/notifications/mark-all-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const unreadNotifications = document.querySelectorAll('.notification-item.unread');
            unreadNotifications.forEach(notification => {
                notification.classList.remove('unread');
                notification.classList.add('read');
            });
            updateNotificationBadge();
            showToast('All notifications marked as read', 'success');
        } else {
            showToast('Error marking notifications as read', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error marking notifications as read', 'error');
    });
}

// Utility function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Export functions for global use
window.EcoTracker = {
    getUserLocation,
    calculateDistance,
    formatDistance,
    previewImage,
    validateForm,
    showToast,
    makeRequest,
    initMap,
    showLoading,
    hideLoading,
    markNotificationAsRead,
    deleteNotification,
    markAllNotificationsAsRead,
    updateNotificationBadge
};