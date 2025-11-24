// map.js - mapping logic for Recycling Centers
// Expects the page to set `window.centersData` (array) and optionally
// `window.selected_material` before loading this script.

let map = null;
let allMarkers = [];
let userLocationMarker = null;

function ensureMap() {
    if (map) return map;
    const mapEl = document.getElementById('center-map');
    if (!mapEl) return null;
    const lat = parseFloat(mapEl.dataset.lat || '42.3149');
    const lng = parseFloat(mapEl.dataset.lng || '-82.9891');
    const zoom = mapEl.dataset.zoom ? parseInt(mapEl.dataset.zoom, 10) : 11;
    map = L.map('center-map').setView([lat, lng], zoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    return map;
}

function getMarkerColor(availability) {
    if (availability >= 70) return '#28a745';
    if (availability >= 40) return '#ffc107';
    return '#dc3545';
}

function createCustomIcon(color) {
    return L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 5px rgba(0,0,0,0.3);"></div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10],
        popupAnchor: [0, -10]
    });
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

function clearMarkers() {
    allMarkers.forEach(m => map.removeLayer(m));
    allMarkers = [];
}

function addCentersToMap(centers, userLat = null, userLon = null) {
    map = ensureMap();
    if (!map) return;
    clearMarkers();

    centers.forEach(center => {
        const color = getMarkerColor(center.availability_percentage || 0);
        const icon = createCustomIcon(color);

        let popupContent = `<div class="custom-popup"><h6>${escapeHtml(center.name)}</h6>`;
        popupContent += `<p class="mb-2"><i class="fas fa-map-marker-alt text-success me-1"></i>${escapeHtml(center.address || '')}</p>`;
        popupContent += `<p class="mb-2"><i class="fas fa-phone text-success me-1"></i>${escapeHtml(center.phone_number || '')}</p>`;

        if (userLat && userLon) {
            const distance = calculateDistance(userLat, userLon, center.latitude, center.longitude);
            popupContent += `<div class="distance-info"><i class="fas fa-route me-1"></i>Distance: <strong>${distance.toFixed(1)} km</strong></div>`;
        }

        popupContent += `<div class="mb-2"><small class="text-muted">Availability:</small><div class="progress" style="height:6px;"><div class="progress-bar" style="width:${(center.availability_percentage||0)}%; background-color:${color}"></div></div><small>${(center.availability_percentage||0).toFixed(1)}%</small></div>`;

        popupContent += `<div class="mb-2"><small class="text-muted">Accepted Materials:</small><div class="material-tags">`;
        (center.accepted_materials || []).forEach(material => {
            popupContent += `<span class="material-tag">${escapeHtml(capitalize(material))}</span>`;
        });
        popupContent += `</div></div>`;

        popupContent += `<div class="mt-2"><a href="/centers/${center.id}/" class="btn btn-success btn-sm me-1"><i class="fas fa-info-circle me-1"></i>Details</a>`;
        if (window.userIsAuthenticated) {
            popupContent += `<a href="/requests/create/?center=${center.id}" class="btn btn-outline-success btn-sm"><i class="fas fa-plus me-1"></i>Request</a>`;
        }
        popupContent += `</div></div>`;

        const marker = L.marker([center.latitude, center.longitude], { icon }).addTo(map).bindPopup(popupContent, { maxWidth: 300, className: 'custom-popup-container' });
        marker.centerData = center;
        allMarkers.push(marker);
    });
}

function filterCenters() {
    const materialFilterEl = document.getElementById('materialFilter');
    if (!materialFilterEl) return;
    const materialFilter = materialFilterEl.value;

    allMarkers.forEach(marker => {
        const center = marker.centerData;
        let show = true;
        if (materialFilter && !(center.accepted_materials || []).includes(materialFilter)) show = false;
        if (show) marker.addTo(map); else map.removeLayer(marker);
    });
}

function getCurrentLocation(event) {
    if (!navigator.geolocation) { alert('Geolocation not supported'); return; }
    const button = event ? event.target : null;
    const originalText = button ? button.innerHTML : null;
    if (button) { button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Locating...'; button.disabled = true; }

    navigator.geolocation.getCurrentPosition(function(position) {
        const lat = position.coords.latitude; const lng = position.coords.longitude;
        if (userLocationMarker) map.removeLayer(userLocationMarker);
        const userIcon = createCustomIcon('#007bff');
        userLocationMarker = L.marker([lat, lng], { icon: userIcon }).addTo(map).bindPopup(`<div class="custom-popup"><h6><i class="fas fa-user-circle me-1"></i>Your Location</h6><p class="mb-0">Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}</p></div>`);
        map.setView([lat, lng], 13);
        addCentersToMap(window.centersData || [], lat, lng);
        filterCenters();
        if (button) { button.innerHTML = originalText; button.disabled = false; }
    }, function(err) {
        if (button) { button.innerHTML = originalText; button.disabled = false; }
        alert('Unable to get your location: ' + (err.message || 'unknown error'));
    }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 });
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/[&"'<>]/g, function (s) { return ({'&':'&amp;','"':'&quot;',"'":'&#39;','<':'&lt;','>':'&gt;'})[s]; });
}

function capitalize(s) { if (!s) return ''; return s.charAt(0).toUpperCase() + s.slice(1); }

document.addEventListener('DOMContentLoaded', function() {
    // ensure Leaflet available
    if (typeof L === 'undefined') { console.warn('Leaflet not loaded'); return; }
    map = ensureMap();
    const centers = window.centersData || [];
    addCentersToMap(centers);
    const filterEl = document.getElementById('materialFilter');
    if (filterEl) filterEl.addEventListener('change', filterCenters);
    const initialFilter = window.selected_material || '';
    if (initialFilter && filterEl) { filterEl.value = initialFilter; filterCenters(); }
    // expose helper globally
    window.getCurrentLocation = getCurrentLocation;
    window.filterCenters = filterCenters;
});