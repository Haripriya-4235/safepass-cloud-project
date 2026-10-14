// Safe Route Finder & Leaflet Map Controller

let map;
let routePolylines = [];
let incidentMarkers = [];
let originMarker = null;
let destMarker = null;
let currentRoutes = [];
let clickMode = null; // 'origin' | 'dest' | null
let searchDebounceTimer = null;

// ── City Presets ─────────────────────────────────────────────────────────────
const CITY_PRESETS = {
    chennai:    { oName: 'Chennai Central',        oLat: 13.0827,  oLng: 80.2707,  dName: 'Guindy Industrial Hub',     dLat: 13.0067, dLng: 80.2030 },
    coimbatore: { oName: 'Gandhipuram Bus Stand',  oLat: 11.0168,  oLng: 76.9558,  dName: 'RS Puram',                  dLat: 11.0118, dLng: 76.9382 },
    bengaluru:  { oName: 'Kempegowda Bus Station', oLat: 12.9767,  oLng: 77.5713,  dName: 'Koramangala',               dLat: 12.9352, dLng: 77.6245 },
    hyderabad:  { oName: 'Secunderabad Station',   oLat: 17.4399,  oLng: 78.4983,  dName: 'Hitec City',                dLat: 17.4435, dLng: 78.3772 },
    mumbai:     { oName: 'CST Mumbai',             oLat: 18.9398,  oLng: 72.8355,  dName: 'Bandra Station',            dLat: 19.0544, dLng: 72.8405 },
    delhi:      { oName: 'Connaught Place',        oLat: 28.6315,  oLng: 77.2167,  dName: 'Hauz Khas Village',         dLat: 28.5494, dLng: 77.2001 },
    kolkata:    { oName: 'Howrah Station',         oLat: 22.5839,  oLng: 88.3427,  dName: 'Park Street Kolkata',       dLat: 22.5517, dLng: 88.3511 },
    pune:       { oName: 'Pune Railway Station',   oLat: 18.5284,  oLng: 73.8742,  dName: 'Koregaon Park Pune',        dLat: 18.5363, dLng: 73.8941 },
    ahmedabad:  { oName: 'Ahmedabad Station',      oLat: 23.0268,  oLng: 72.6022,  dName: 'Satellite Area Ahmedabad',  dLat: 23.0193, dLng: 72.5101 },
    jaipur:     { oName: 'Jaipur Railway Station', oLat: 26.9185,  oLng: 75.7868,  dName: 'MI Road Jaipur',            dLat: 26.9124, dLng: 75.7873 },
};

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadIncidentReports();
    tryGPSInit();
});

function initMap() {
    map = L.map('map').setView([20.5937, 78.9629], 5); // India overview
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    // Click-on-map handler
    map.on('click', (e) => {
        if (!clickMode) return;
        const { lat, lng } = e.latlng;
        reverseGeocode(lat, lng, clickMode);
        setClickMode(null);
    });
}

function tryGPSInit() {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;
            setOriginCoords(lat, lng, 'My GPS Location');
            map.setView([lat, lng], 14);
        },
        () => { /* GPS denied — leave map at India overview */ },
        { timeout: 5000 }
    );
}

// ── Coords / Marker helpers ───────────────────────────────────────────────────
function setOriginCoords(lat, lng, label) {
    document.getElementById('originLat').value = lat;
    document.getElementById('originLng').value = lng;
    document.getElementById('originInput').value = label;
    const badge = document.getElementById('originCoordsBadge');
    if (badge) badge.textContent = `${parseFloat(lat).toFixed(4)}, ${parseFloat(lng).toFixed(4)}`;
    placeOriginMarker(lat, lng);
}

function setDestCoords(lat, lng, label) {
    document.getElementById('destLat').value = lat;
    document.getElementById('destLng').value = lng;
    document.getElementById('destInput').value = label;
    const badge = document.getElementById('destCoordsBadge');
    if (badge) badge.textContent = `${parseFloat(lat).toFixed(4)}, ${parseFloat(lng).toFixed(4)}`;
    placeDestMarker(lat, lng);
}

function placeOriginMarker(lat, lng) {
    if (originMarker) map.removeLayer(originMarker);
    originMarker = L.marker([lat, lng], { draggable: true, title: 'Start' })
        .addTo(map).bindPopup('<b>Start Point</b>');
    originMarker.on('dragend', (e) => {
        const pos = e.target.getLatLng();
        reverseGeocode(pos.lat, pos.lng, 'origin');
    });
}

function placeDestMarker(lat, lng) {
    if (destMarker) map.removeLayer(destMarker);
    destMarker = L.marker([lat, lng], { draggable: true, title: 'Destination' })
        .addTo(map).bindPopup('<b>Destination</b>');
    destMarker.on('dragend', (e) => {
        const pos = e.target.getLatLng();
        reverseGeocode(pos.lat, pos.lng, 'dest');
    });
}

// ── Nominatim Address Search ───────────────────────────────────────────────────
function onAddressInput(type) {
    clearTimeout(searchDebounceTimer);
    const inputId    = type === 'origin' ? 'originInput' : 'destInput';
    const dropdownId = type === 'origin' ? 'originSearchResults' : 'destSearchResults';
    const query = document.getElementById(inputId).value.trim();
    const dropdown = document.getElementById(dropdownId);
    if (query.length < 3) { dropdown.classList.add('d-none'); return; }
    searchDebounceTimer = setTimeout(() => nominatimSearch(query, type), 400);
}

function searchAddress(type) {
    const inputId = type === 'origin' ? 'originInput' : 'destInput';
    const query = document.getElementById(inputId).value.trim();
    if (query.length < 2) return;
    nominatimSearch(query, type);
}

function nominatimSearch(query, type) {
    const dropdownId = type === 'origin' ? 'originSearchResults' : 'destSearchResults';
    const dropdown   = document.getElementById(dropdownId);
    dropdown.innerHTML = '<div class="search-result-item text-muted"><i class="fa-solid fa-spinner fa-spin me-1"></i> Searching...</div>';
    dropdown.classList.remove('d-none');

    fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=6&addressdetails=1`, {
        headers: { 'Accept-Language': 'en' }
    })
    .then(r => r.json())
    .then(results => {
        if (!results.length) {
            dropdown.innerHTML = '<div class="search-result-item text-muted">No results found. Try a different term.</div>';
            return;
        }
        dropdown.innerHTML = '';
        results.forEach(r => {
            const item = document.createElement('div');
            item.className = 'search-result-item';
            item.innerHTML = `<i class="fa-solid fa-location-dot text-danger me-1"></i>${r.display_name}`;
            item.onclick = () => {
                const lat = parseFloat(r.lat);
                const lng = parseFloat(r.lon);
                const label = r.display_name.split(',').slice(0, 3).join(', ');
                if (type === 'origin') setOriginCoords(lat, lng, label);
                else setDestCoords(lat, lng, label);
                dropdown.classList.add('d-none');
                document.getElementById('citySelector').value = 'custom';
                map.setView([lat, lng], 14);
            };
            dropdown.appendChild(item);
        });
    })
    .catch(() => {
        dropdown.innerHTML = '<div class="search-result-item text-danger">Search failed. Check your connection.</div>';
    });
}

function reverseGeocode(lat, lng, type) {
    fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
    .then(r => r.json())
    .then(data => {
        const label = data.display_name
            ? data.display_name.split(',').slice(0, 3).join(', ')
            : `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
        if (type === 'origin') setOriginCoords(lat, lng, label);
        else setDestCoords(lat, lng, label);
    })
    .catch(() => {
        const label = `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
        if (type === 'origin') setOriginCoords(lat, lng, label);
        else setDestCoords(lat, lng, label);
    });
}

// ── City Selector ─────────────────────────────────────────────────────────────
function onCitySelected(value) {
    if (value === 'gps') { getCurrentLocationForOrigin(); return; }
    if (value === 'custom') return;
    const p = CITY_PRESETS[value];
    if (!p) return;
    setOriginCoords(p.oLat, p.oLng, p.oName);
    setDestCoords(p.dLat, p.dLng, p.dName);
    map.setView([(p.oLat + p.dLat) / 2, (p.oLng + p.dLng) / 2], 13);
    findRoutes();
}

// ── GPS ───────────────────────────────────────────────────────────────────────
function getCurrentLocationForOrigin() {
    if (!navigator.geolocation) { alert('Geolocation not supported by your browser.'); return; }
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;
            reverseGeocode(lat, lng, 'origin');
            map.setView([lat, lng], 14);
            document.getElementById('citySelector').value = 'gps';
        },
        (err) => alert('GPS error: ' + err.message)
    );
}

// ── Click Mode ────────────────────────────────────────────────────────────────
function setClickMode(mode) {
    clickMode = mode;
    const help = document.getElementById('clickModeHelp');
    const btnO = document.getElementById('btnSetOriginMode');
    const btnD = document.getElementById('btnSetDestMode');

    if (mode === 'origin') {
        help.innerHTML = '<span class="text-success fw-semibold">🟢 Click the map to set your Start point</span>';
        btnO.className = 'btn btn-sm btn-success flex-fill';
        btnD.className = 'btn btn-sm btn-outline-danger flex-fill';
        map.getContainer().style.cursor = 'crosshair';
    } else if (mode === 'dest') {
        help.innerHTML = '<span class="text-danger fw-semibold">🔴 Click the map to set Destination</span>';
        btnD.className = 'btn btn-sm btn-danger flex-fill';
        btnO.className = 'btn btn-sm btn-outline-success flex-fill';
        map.getContainer().style.cursor = 'crosshair';
    } else {
        help.innerHTML = '(Or drag the markers on the map!)';
        btnO.className = 'btn btn-sm btn-outline-success flex-fill';
        btnD.className = 'btn btn-sm btn-outline-danger flex-fill';
        map.getContainer().style.cursor = '';
    }
}

// ── Incident Reports ──────────────────────────────────────────────────────────
function loadIncidentReports() {
    fetch('/api/reports')
    .then(res => res.json())
    .then(data => {
        if (data.success && data.reports) {
            data.reports.forEach(r => {
                const iconColor = r.severity === 'high' ? 'red' : (r.category === 'safe_zone' ? 'green' : 'orange');
                const marker = L.circleMarker([r.latitude, r.longitude], {
                    radius: 8, fillColor: iconColor,
                    color: '#ffffff', weight: 2, opacity: 1, fillOpacity: 0.85
                }).addTo(map);
                marker.bindPopup(`
                    <div class="p-1">
                        <strong>${r.title}</strong><br>
                        <span class="badge bg-secondary">${r.category}</span>
                        <span class="badge bg-danger">${r.severity.toUpperCase()}</span><br>
                        <small class="text-muted">${r.description || ''}</small>
                    </div>
                `);
                incidentMarkers.push(marker);
            });
        }
    });
}

// ── Route Finding ─────────────────────────────────────────────────────────────
function findRoutes() {
    const originLat = parseFloat(document.getElementById('originLat').value);
    const originLng = parseFloat(document.getElementById('originLng').value);
    const destLat   = parseFloat(document.getElementById('destLat').value);
    const destLng   = parseFloat(document.getElementById('destLng').value);

    if (isNaN(originLat) || isNaN(originLng) || isNaN(destLat) || isNaN(destLng)) {
        alert('Please set both a Start Location and a Destination first.');
        return;
    }

    const loadingEl = document.getElementById('routeLoading');
    loadingEl.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-1"></i> Fetching real road routes from OpenStreetMap...';
    loadingEl.classList.remove('d-none');
    document.getElementById('routesContainer').innerHTML = '';

    fetch('/api/routes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ origin_lat: originLat, origin_lng: originLng, dest_lat: destLat, dest_lng: destLng })
    })
    .then(res => res.json())
    .then(data => {
        loadingEl.classList.add('d-none');
        if (data.success && data.routes) {
            currentRoutes = data.routes;
            renderRoutesOnMap(data.routes, originLat, originLng, destLat, destLng);
            renderRouteCards(data.routes);
        } else {
            document.getElementById('routesContainer').innerHTML =
                '<div class="alert alert-warning small">No routes could be calculated for this location.</div>';
        }
    })
    .catch(err => {
        loadingEl.classList.add('d-none');
        document.getElementById('routesContainer').innerHTML =
            '<div class="alert alert-danger small">Network error fetching routes. Please check your connection.</div>';
        console.error(err);
    });
}

function renderRoutesOnMap(routes, originLat, originLng, destLat, destLng) {
    routePolylines.forEach(p => map.removeLayer(p));
    routePolylines = [];
    placeOriginMarker(originLat, originLng);
    placeDestMarker(destLat, destLng);

    const bounds = L.latLngBounds([[originLat, originLng], [destLat, destLng]]);
    routes.forEach((route, idx) => {
        const latlngs  = route.waypoints.map(w => [w.lat, w.lng]);
        const isPrimary = (idx === 0);
        const polyline  = L.polyline(latlngs, {
            color: route.safety.color,
            weight: isPrimary ? 6 : 4,
            opacity: isPrimary ? 0.9 : 0.6,
            dashArray: isPrimary ? null : '5, 8'
        }).addTo(map);
        polyline.bindPopup(`<b>${route.name}</b><br>Safety: <b>${route.safety.score}/100</b> (${route.safety.level})`);
        routePolylines.push(polyline);
        latlngs.forEach(ll => bounds.extend(ll));
    });
    map.fitBounds(bounds, { padding: [50, 50] });
}

function renderRouteCards(routes) {
    const container = document.getElementById('routesContainer');
    container.innerHTML = '';
    routes.forEach((r, idx) => {
        const s = r.safety;
        const isReal = r.source && r.source !== 'estimated';
        const sourcePill = isReal
            ? `<span class="badge bg-success-subtle text-success border border-success" style="font-size:0.65rem;"><i class="fa-solid fa-road me-1"></i>REAL ROADS</span>`
            : `<span class="badge bg-secondary-subtle text-secondary border" style="font-size:0.65rem;"><i class="fa-solid fa-wave-square me-1"></i>ESTIMATED</span>`;
        const card = document.createElement('div');
        card.className = `card border-0 shadow-sm p-3 route-card rounded-4 ${idx === 0 ? 'selected' : ''}`;
        card.onclick = () => selectRoute(idx);
        card.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-1">
                <h6 class="fw-bold mb-0 text-dark" style="font-size:0.88rem;">${r.name}</h6>
                <span class="badge" style="background-color:${s.color};color:white;">${s.score}/100</span>
            </div>
            <div class="mb-1">${sourcePill}</div>
            <p class="text-muted small mb-2">${r.description || ''}</p>
            <div class="d-flex justify-content-between align-items-center small text-secondary mb-2">
                <span><i class="fa-solid fa-road me-1"></i>${r.distance}</span>
                <span><i class="fa-solid fa-stopwatch me-1"></i>${r.duration}</span>
                <span class="fw-semibold" style="color:${s.color};">${s.level}</span>
            </div>
            <div class="progress mb-2" style="height:6px;">
                <div class="progress-bar" style="width:${s.score}%;background-color:${s.color};"></div>
            </div>
            <button class="btn btn-outline-success btn-sm w-100 fw-semibold mt-1"
                    onclick="startJourney('${r.name.replace(/'/g, "\\'")}',${ s.score})">
                <i class="fa-solid fa-play me-1"></i> Start Journey with Live Tracking
            </button>
        `;
        container.appendChild(card);
    });
}

function selectRoute(idx) {
    document.querySelectorAll('.route-card').forEach((c, i) => {
        c.classList.toggle('selected', i === idx);
    });
    routePolylines.forEach((line, i) => {
        line.setStyle(i === idx ? { weight: 7, opacity: 1.0 } : { weight: 4, opacity: 0.5 });
        if (i === idx) line.bringToFront();
    });
}

function startJourney(routeName, score) {
    fetch('/api/journey/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            origin_name:  document.getElementById('originInput').value,
            dest_name:    document.getElementById('destInput').value,
            origin_lat:   document.getElementById('originLat').value,
            origin_lng:   document.getElementById('originLng').value,
            dest_lat:     document.getElementById('destLat').value,
            dest_lng:     document.getElementById('destLng').value,
            route_name:   routeName,
            safety_score: score
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert(`Journey started via '${routeName}'! Live location updates are now active.`);
            window.location.href = '/dashboard';
        }
    });
}

// Close dropdowns when clicking outside
document.addEventListener('click', (e) => {
    ['originSearchResults', 'destSearchResults'].forEach(id => {
        const el = document.getElementById(id);
        if (el && !el.contains(e.target)) el.classList.add('d-none');
    });
});
