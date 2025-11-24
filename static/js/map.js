// map.js - helper to initialize a center map
// Usage: include this file on pages that render a <div id="center-map"></div>
// Then call `initCenterMap(lat, lng, zoom)` or rely on auto-init if data attributes are present.

function initCenterMap(lat, lng, zoom = 13) {
  if (typeof L !== 'undefined') {
    // Leaflet is available
    const mapEl = document.getElementById('center-map');
    if (!mapEl) return;
    const map = L.map('center-map').setView([lat, lng], zoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    L.marker([lat, lng]).addTo(map);
    return map;
  }

  if (typeof google !== 'undefined' && google.maps) {
    // Google Maps fallback
    const mapEl = document.getElementById('center-map');
    if (!mapEl) return;
    const center = { lat: parseFloat(lat), lng: parseFloat(lng) };
    const map = new google.maps.Map(mapEl, { zoom: zoom, center: center });
    new google.maps.Marker({ position: center, map: map });
    return map;
  }

  console.warn('No mapping library detected. Please include Leaflet or Google Maps.');
}

// Auto-initialize if element present and data attributes set
document.addEventListener('DOMContentLoaded', function () {
  const mapEl = document.getElementById('center-map');
  if (!mapEl) return;
  const lat = mapEl.dataset.lat;
  const lng = mapEl.dataset.lng;
  const zoom = mapEl.dataset.zoom ? parseInt(mapEl.dataset.zoom, 10) : 13;
  if (lat && lng) {
    initCenterMap(parseFloat(lat), parseFloat(lng), zoom);
  }
});
