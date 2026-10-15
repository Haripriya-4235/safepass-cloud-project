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
    // Tamil Nadu
    chennai:     { oName: 'Chennai Central',              oLat: 13.0827,  oLng: 80.2707,  dName: 'Guindy Industrial Hub',        dLat: 13.0067, dLng: 80.2030 },
    coimbatore:  { oName: 'Gandhipuram Bus Stand',        oLat: 11.0168,  oLng: 76.9558,  dName: 'RS Puram Coimbatore',          dLat: 11.0118, dLng: 76.9382 },
    madurai:     { oName: 'Meenakshi Temple Madurai',     oLat: 9.9195,   oLng: 78.1193,  dName: 'Mattuthavani Bus Terminus',    dLat: 9.9391,  dLng: 78.1565 },
    trichy:      { oName: 'Tiruchirappalli Central Bus',  oLat: 10.7905,  oLng: 78.6946,  dName: 'Srirangam Temple Area',        dLat: 10.8625, dLng: 78.6900 },
    salem:       { oName: 'Salem New Bus Stand',          oLat: 11.6643,  oLng: 78.1460,  dName: 'Fairlands Salem',              dLat: 11.6780, dLng: 78.1340 },
    tirunelveli: { oName: 'Tirunelveli Junction',         oLat: 8.7286,   oLng: 77.7282,  dName: 'Palayamkottai Central',        dLat: 8.7139,  dLng: 77.7567 },
    tiruppur:    { oName: 'Tiruppur Old Bus Stand',       oLat: 11.1085,  oLng: 77.3411,  dName: 'Avinashi Road Tiruppur',       dLat: 11.1271, dLng: 77.3550 },
    erode:       { oName: 'Erode Central Bus Stand',      oLat: 11.3410,  oLng: 77.7172,  dName: 'Perundurai Road Erode',        dLat: 11.3265, dLng: 77.6890 },
    vellore:     { oName: 'Vellore Fort Anna Salai',      oLat: 12.9165,  oLng: 79.1325,  dName: 'Katpadi Railway Junction',     dLat: 12.9704, dLng: 79.1390 },
    thanjavur:   { oName: 'Brihadisvara Big Temple',      oLat: 10.7870,  oLng: 79.1378,  dName: 'New Bus Stand Thanjavur',      dLat: 10.7680, dLng: 79.1220 },
    dindigul:    { oName: 'Dindigul Rock Fort',           oLat: 10.3673,  oLng: 77.9803,  dName: 'Dindigul Bus Stand',           dLat: 10.3580, dLng: 77.9690 },
    kanchipuram: { oName: 'Kanchipuram Bus Stand',        oLat: 12.8342,  oLng: 79.7036,  dName: 'Ekambareswarar Temple Area',   dLat: 12.8420, dLng: 79.6980 },
    nagercoil:   { oName: 'Vadasery Bus Stand Nagercoil', oLat: 8.1833,   oLng: 77.4119,  dName: 'Kanyakumari Cape Point',       dLat: 8.0883,  dLng: 77.5385 },
    pondicherry: { oName: 'Promenade Beach White Town',   oLat: 11.9338,  oLng: 79.8350,  dName: 'JIPMER Campus Gorimedu',       dLat: 11.9540, dLng: 79.8120 },

    // Kerala
    kochi:       { oName: 'Marine Drive Kochi',           oLat: 9.9816,   oLng: 76.2798,  dName: 'Kakkanad InfoPark Hub',        dLat: 10.0159, dLng: 76.3419 },
    trivandrum:  { oName: 'East Fort Trivandrum',         oLat: 8.4875,   oLng: 76.9486,  dName: 'Technopark Campus',            dLat: 8.5581,  dLng: 76.8814 },
    kozhikode:   { oName: 'Calicut Beach Kozhikode',      oLat: 11.2588,  oLng: 75.7804,  dName: 'Mavoor Road Calicut',          dLat: 11.2618, dLng: 75.8050 },

    // Karnataka
    bengaluru:   { oName: 'Kempegowda Bus Station',       oLat: 12.9767,  oLng: 77.5713,  dName: 'Koramangala Bengaluru',        dLat: 12.9352, dLng: 77.6245 },
    mysuru:      { oName: 'Mysore Palace Central',        oLat: 12.3051,  oLng: 76.6551,  dName: 'Infosys Campus Hebbal',        dLat: 12.3556, dLng: 76.5947 },
    mangaluru:   { oName: 'Hampankatta Mangaluru',        oLat: 12.8698,  oLng: 74.8430,  dName: 'Kadri Hills Mangaluru',        dLat: 12.8830, dLng: 74.8580 },

    // Andhra Pradesh & Telangana
    hyderabad:     { oName: 'Secunderabad Station',       oLat: 17.4399,  oLng: 78.4983,  dName: 'Hitec City Hyderabad',         dLat: 17.4435, dLng: 78.3772 },
    visakhapatnam: { oName: 'RTC Complex Visakhapatnam',  oLat: 17.7231,  oLng: 83.3013,  dName: 'RK Beach Road Vizag',          dLat: 17.7164, dLng: 83.3340 },
    vijayawada:    { oName: 'Pandit Nehru Bus Station',   oLat: 16.5178,  oLng: 80.6200,  dName: 'Benz Circle Vijayawada',       dLat: 16.5000, dLng: 80.6500 },

    // Maharashtra, Gujarat & Rajasthan
    mumbai:      { oName: 'CST Mumbai',                   oLat: 18.9398,  oLng: 72.8355,  dName: 'Bandra Station Mumbai',        dLat: 19.0544, dLng: 72.8405 },
    pune:        { oName: 'Pune Railway Station',         oLat: 18.5284,  oLng: 73.8742,  dName: 'Koregaon Park Pune',           dLat: 18.5363, dLng: 73.8941 },
    nagpur:      { oName: 'Sitabuldi Nagpur',             oLat: 21.1458,  oLng: 79.0882,  dName: 'Dharampeth Nagpur',            dLat: 21.1390, dLng: 79.0550 },
    ahmedabad:   { oName: 'Ahmedabad Station',            oLat: 23.0268,  oLng: 72.6022,  dName: 'Satellite Area Ahmedabad',     dLat: 23.0193, dLng: 72.5101 },
    surat:       { oName: 'Surat Central Station',        oLat: 21.2049,  oLng: 72.8406,  dName: 'VR Mall Dumas Road Surat',     dLat: 21.1590, dLng: 72.7720 },
    jaipur:      { oName: 'Jaipur Railway Station',       oLat: 26.9185,  oLng: 75.7868,  dName: 'MI Road Jaipur',               dLat: 26.9124, dLng: 75.7873 },

    // North & East India
    delhi:       { oName: 'Connaught Place Delhi',        oLat: 28.6315,  oLng: 77.2167,  dName: 'Hauz Khas Village',            dLat: 28.5494, dLng: 77.2001 },
    kolkata:     { oName: 'Howrah Station Kolkata',       oLat: 22.5839,  oLng: 88.3427,  dName: 'Park Street Kolkata',          dLat: 22.5517, dLng: 88.3511 },
    lucknow:     { oName: 'Charbagh Station Lucknow',     oLat: 26.8310,  oLng: 80.9230,  dName: 'Hazratganj Market Lucknow',    dLat: 26.8520, dLng: 80.9460 },
    chandigarh:  { oName: 'Sector 17 Plaza Chandigarh',   oLat: 30.7333,  oLng: 76.7794,  dName: 'Phase 7 Mohali',               dLat: 30.7046, dLng: 76.7179 },
    patna:       { oName: 'Patna Junction Central',       oLat: 25.6022,  oLng: 85.1376,  dName: 'Boring Road Patna',            dLat: 25.6190, dLng: 85.1180 },
    bhopal:      { oName: 'MP Nagar Bhopal',              oLat: 23.2332,  oLng: 77.4343,  dName: 'New Market Bhopal',            dLat: 23.2450, dLng: 77.4010 },

    // International Metros
    london:      { oName: 'Trafalgar Square London',      oLat: 51.5080,  oLng: -0.1281,  dName: 'Westminster Abbey London',     dLat: 51.4995, dLng: -0.1248 },
    newyork:     { oName: 'Times Square New York',        oLat: 40.7580,  oLng: -73.9855, dName: 'Brooklyn Bridge NYC',          dLat: 40.7061, dLng: -73.9969 },
    dubai:       { oName: 'Burj Khalifa Downtown Dubai',  oLat: 25.1972,  oLng: 55.2744,  dName: 'Dubai Marina Walk',            dLat: 25.0805, dLng: 55.1403 },
    singapore:   { oName: 'Marina Bay Sands Singapore',   oLat: 1.2838,   oLng: 103.8591, dName: 'Orchard Road Singapore',       dLat: 1.3048,  dLng: 103.8318 },
};

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadIncidentReports();
    tryGPSInit();

    // Keydown listener for City Search input
    const cityInp = document.getElementById('citySearchInput');
    if (cityInp) {
        cityInp.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchCityRegion();
            }
        });
    }

    // Dismiss search dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('#citySearchResults') && !e.target.closest('#citySearchInput')) {
            const el = document.getElementById('citySearchResults');
            if (el) el.classList.add('d-none');
        }
        if (!e.target.closest('#originSearchResults') && !e.target.closest('#originInput')) {
            const el = document.getElementById('originSearchResults');
            if (el) el.classList.add('d-none');
        }
        if (!e.target.closest('#destSearchResults') && !e.target.closest('#destInput')) {
            const el = document.getElementById('destSearchResults');
            if (el) el.classList.add('d-none');
        }
    });
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

// ── Universal City / Region Search & Selector ──────────────────────────────
let citySearchDebounceTimer = null;

function onCitySearchInput(query) {
    clearTimeout(citySearchDebounceTimer);
    const dropdown = document.getElementById('citySearchResults');
    if (!dropdown) return;

    const trimmed = (query || '').trim();
    if (trimmed.length < 2) {
        dropdown.classList.add('d-none');
        dropdown.innerHTML = '';
        return;
    }

    citySearchDebounceTimer = setTimeout(() => {
        executeCitySearch(trimmed);
    }, 350);
}

function searchCityRegion() {
    const input = document.getElementById('citySearchInput');
    if (!input) return;
    const query = input.value.trim();
    if (!query) {
        input.focus();
        return;
    }
    executeCitySearch(query);
}

function clearCitySearch() {
    const input = document.getElementById('citySearchInput');
    const dropdown = document.getElementById('citySearchResults');
    if (input) input.value = '';
    if (dropdown) {
        dropdown.classList.add('d-none');
        dropdown.innerHTML = '';
    }
}

function executeCitySearch(query) {
    const dropdown = document.getElementById('citySearchResults');
    if (!dropdown) return;

    dropdown.innerHTML = '<div class="search-result-item text-muted"><i class="fa-solid fa-spinner fa-spin me-1"></i> Searching cities worldwide...</div>';
    dropdown.classList.remove('d-none');

    fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=8&addressdetails=1`, {
        headers: { 'Accept-Language': 'en' }
    })
    .then(r => r.json())
    .then(results => {
        if (!results || !results.length) {
            dropdown.innerHTML = '<div class="search-result-item text-muted">No city or region found. Check spelling or try a broader term.</div>';
            return;
        }

        dropdown.innerHTML = '';
        results.forEach(r => {
            const item = document.createElement('div');
            item.className = 'search-result-item d-flex align-items-center';
            const shortName = r.display_name.split(',')[0].trim();
            const rest = r.display_name.split(',').slice(1, 4).join(', ').trim();
            item.innerHTML = `
                <div class="me-2 text-primary"><i class="fa-solid fa-city"></i></div>
                <div>
                    <div class="fw-bold text-dark">${shortName}</div>
                    <small class="text-muted" style="font-size: 0.72rem;">${rest || r.display_name}</small>
                </div>
            `;
            item.onclick = () => selectCityFromSearch(r);
            dropdown.appendChild(item);
        });
    })
    .catch(err => {
        dropdown.innerHTML = '<div class="search-result-item text-danger">Search error. Please verify network connection.</div>';
        console.error('City search failed:', err);
    });
}

function selectCityFromSearch(r) {
    const dropdown = document.getElementById('citySearchResults');
    if (dropdown) dropdown.classList.add('d-none');

    const lat = parseFloat(r.lat);
    const lng = parseFloat(r.lon);
    const parts = r.display_name.split(',');
    const shortCity = parts[0].trim();
    const regionText = parts.slice(1, 3).join(', ').trim();

    // Update city search input
    const input = document.getElementById('citySearchInput');
    if (input) input.value = shortCity;

    // Update active badge
    updateActiveRegionBadge(shortCity);

    // Dynamic option in citySelector
    const selector = document.getElementById('citySelector');
    if (selector) {
        let opt = document.getElementById('optCustomCityRegion');
        if (!opt) {
            opt = document.createElement('option');
            opt.id = 'optCustomCityRegion';
            selector.prepend(opt);
        }
        opt.value = `custom_${lat}_${lng}`;
        opt.textContent = `📍 ${shortCity} (${regionText || 'Custom Region'})`;
        opt.selected = true;
    }

    // Set Origin to City Center
    setOriginCoords(lat, lng, `${shortCity} (City Center)`);

    // Set Destination slightly offset (~2 km) to create a ready-to-calculate route immediately
    const dLat = lat + 0.015;
    const dLng = lng + 0.015;
    setDestCoords(dLat, dLng, `${shortCity} (North Safe Hub)`);

    // Smoothly fly map to selected city
    if (map) {
        map.flyTo([lat, lng], 13, { duration: 1.2 });
    }

    // Automatically calculate initial safe routes for this new city
    setTimeout(() => {
        findRoutes();
    }, 400);
}

function updateActiveRegionBadge(label) {
    const badge = document.getElementById('activeCityBadge');
    if (badge) {
        badge.innerHTML = `<i class="fa-solid fa-location-dot me-1 text-success"></i>${label}`;
        badge.className = 'badge bg-success-subtle text-success border border-success-subtle';
    }
}

// ── City Selector (Dropdown) ──────────────────────────────────────────────────
function onCitySelected(value) {
    if (value === 'gps') {
        getCurrentLocationForOrigin();
        updateActiveRegionBadge('Live GPS');
        return;
    }
    if (value === 'custom_search') {
        const inp = document.getElementById('citySearchInput');
        if (inp) {
            inp.focus();
            inp.select();
        }
        return;
    }
    if (value.startsWith('custom_')) {
        return; // already active
    }

    const p = CITY_PRESETS[value];
    if (!p) return;

    setOriginCoords(p.oLat, p.oLng, p.oName);
    setDestCoords(p.dLat, p.dLng, p.dName);

    const prettyName = value.charAt(0).toUpperCase() + value.slice(1);
    updateActiveRegionBadge(prettyName);

    // Sync search input
    const inp = document.getElementById('citySearchInput');
    if (inp) inp.value = prettyName;

    map.flyTo([(p.oLat + p.dLat) / 2, (p.oLng + p.dLng) / 2], 13, { duration: 1.0 });
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
