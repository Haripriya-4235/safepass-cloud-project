import math
import requests
from config import Config
from services.safety_score import calculate_route_safety, haversine_distance


# ─── Geometry helpers ────────────────────────────────────────────────────────

def math_bell_curve(t):
    return 4 * t * (1 - t)


def generate_interpolated_waypoints(start_lat, start_lng, end_lat, end_lng,
                                    detour_lat=0, detour_lng=0, steps=10):
    """Generates smoothly curved waypoints (fallback when no real router available)."""
    points = []
    for i in range(steps + 1):
        ratio = i / steps
        lat = start_lat + (end_lat - start_lat) * ratio
        lng = start_lng + (end_lng - start_lng) * ratio
        if detour_lat or detour_lng:
            curve = math_bell_curve(ratio)
            lat += detour_lat * curve
            lng += detour_lng * curve
        points.append({'lat': round(lat, 6), 'lng': round(lng, 6)})
    return points


# ─── Real Road Routers ───────────────────────────────────────────────────────

HEADERS = {'User-Agent': 'WomenSafetyCloudPortal/1.0 (educational project)'}


def fetch_osrm_routes(origin_lat, origin_lng, dest_lat, dest_lng):
    """
    Calls the public OSRM demo server asking for up to 3 road-following alternatives.
    Returns list of (waypoints, dist_km, duration_min) tuples.
    """
    try:
        url = (
            f"https://router.project-osrm.org/route/v1/driving/"
            f"{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
            f"?overview=full&geometries=geojson&alternatives=3&steps=false"
        )
        resp = requests.get(url, headers=HEADERS, timeout=6)
        if resp.status_code != 200:
            return []
        data = resp.json()
        results = []
        for r in data.get('routes', []):
            coords = r['geometry']['coordinates']
            waypoints = [{'lat': round(c[1], 6), 'lng': round(c[0], 6)} for c in coords]
            dist_km = round(r['distance'] / 1000.0, 2)
            dur_min = max(1, int(r['duration'] / 60.0))
            results.append((waypoints, dist_km, dur_min))
        return results
    except Exception as e:
        print(f"[OSRM] Error: {e}")
        return []


def fetch_ors_routes(origin_lat, origin_lng, dest_lat, dest_lng):
    """
    Calls OpenRouteService (free public API, no key) for real road alternatives.
    Returns list of (waypoints, dist_km, duration_min) tuples.
    """
    try:
        url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
        payload = {
            "coordinates": [
                [origin_lng, origin_lat],
                [dest_lng, dest_lat]
            ],
            "alternative_routes": {
                "target_count": 3,
                "weight_factor": 1.6,
                "share_factor": 0.6
            },
            "geometry_simplify": False
        }
        # ORS requires an API key — use OSRM as primary, skip ORS if no key
        api_key = getattr(Config, 'ORS_API_KEY', None)
        if not api_key:
            return []
        resp = requests.post(url, json=payload,
                             headers={**HEADERS, 'Authorization': api_key,
                                      'Content-Type': 'application/json'},
                             timeout=6)
        if resp.status_code != 200:
            return []
        data = resp.json()
        results = []
        for feature in data.get('features', []):
            coords = feature['geometry']['coordinates']
            props = feature.get('properties', {})
            seg = props.get('segments', [{}])[0]
            waypoints = [{'lat': round(c[1], 6), 'lng': round(c[0], 6)} for c in coords]
            dist_km = round(seg.get('distance', 0) / 1000.0, 2)
            dur_min = max(1, int(seg.get('duration', 0) / 60.0))
            results.append((waypoints, dist_km, dur_min))
        return results
    except Exception as e:
        print(f"[ORS] Error: {e}")
        return []


def fetch_google_routes(origin_lat, origin_lng, dest_lat, dest_lng):
    """Calls Google Directions API if a key is configured."""
    try:
        key = getattr(Config, 'GOOGLE_MAPS_API_KEY', None)
        if not key:
            return []
        url = (
            f"https://maps.googleapis.com/maps/api/directions/json"
            f"?origin={origin_lat},{origin_lng}"
            f"&destination={dest_lat},{dest_lng}"
            f"&alternatives=true&key={key}"
        )
        resp = requests.get(url, headers=HEADERS, timeout=6).json()
        if resp.get('status') != 'OK':
            return []
        results = []
        for r in resp.get('routes', []):
            leg = r['legs'][0]
            waypoints = [
                {'lat': s['end_location']['lat'], 'lng': s['end_location']['lng']}
                for s in leg['steps']
            ]
            dist_km = leg['distance']['value'] / 1000.0
            dur_min = max(1, int(leg['duration']['value'] / 60))
            results.append((waypoints, dist_km, dur_min))
        return results
    except Exception as e:
        print(f"[Google Maps] Error: {e}")
        return []


# ─── Route name generator ────────────────────────────────────────────────────

ROUTE_PROFILES = [
    {
        'name_suffix': 'Main Road Route',
        'description': 'Follows primary roads with good lighting, active traffic, and monitored intersections.',
        'route_type': 'main_road',
    },
    {
        'name_suffix': 'Alternative Route',
        'description': 'Secondary roads — may pass through quieter neighbourhoods.',
        'route_type': 'secondary',
    },
    {
        'name_suffix': 'Scenic / Bypass Route',
        'description': 'Longer outer path using arterial roads and transit corridors.',
        'route_type': 'main_road',
    },
]

FALLBACK_PROFILES = [
    {
        'name_suffix': 'Main Road Route',
        'description': 'Primary arterial via main roads (estimated, no real road data).',
        'route_type': 'main_road',
        'detour_scale': 0.55,
        'dist_factor': 1.15,
        'dur_factor': 2.8,
    },
    {
        'name_suffix': 'Direct Shortcut',
        'description': 'Shorter inner-colony path — lower lighting, less traffic.',
        'route_type': 'shortcut',
        'detour_scale': -0.7,
        'dist_factor': 1.05,
        'dur_factor': 2.2,
    },
    {
        'name_suffix': 'Outer Bypass Corridor',
        'description': 'Well-lit outer loop with frequent public transport stops.',
        'route_type': 'main_road',
        'detour_scale': 1.1,
        'dist_factor': 1.30,
        'dur_factor': 3.2,
    },
]


# ─── Main entry point ─────────────────────────────────────────────────────────

def get_routes(origin_lat, origin_lng, dest_lat, dest_lng):
    """
    Returns up to 3 route alternatives with real road geometries and safety scores
    for ANY origin & destination worldwide.

    Priority:
      1. Google Maps Directions API  (if GOOGLE_MAPS_API_KEY set in config)
      2. OSRM public demo server     (free, no key, real roads)
      3. OpenRouteService            (if ORS_API_KEY set in config)
      4. Algorithmic curved fallback (always works, estimated lines)
    """

    straight_dist_km = haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
    if straight_dist_km < 0.05:
        straight_dist_km = 0.5

    # ── 1. Google Maps ──
    raw_routes = fetch_google_routes(origin_lat, origin_lng, dest_lat, dest_lng)

    # ── 2. OSRM ──
    if not raw_routes:
        raw_routes = fetch_osrm_routes(origin_lat, origin_lng, dest_lat, dest_lng)

    # ── 3. ORS ──
    if not raw_routes:
        raw_routes = fetch_ors_routes(origin_lat, origin_lng, dest_lat, dest_lng)

    # ── 4. Algorithmic fallback ──
    if not raw_routes:
        print("[Routes] All routers failed — using algorithmic fallback")
        d_lat = dest_lat - origin_lat
        d_lng = dest_lng - origin_lng
        perp_lat = -d_lng * 0.22
        perp_lng = d_lat * 0.22

        routes = []
        for i, p in enumerate(FALLBACK_PROFILES):
            ds = p['detour_scale']
            pts = generate_interpolated_waypoints(
                origin_lat, origin_lng, dest_lat, dest_lng,
                detour_lat=perp_lat * ds, detour_lng=perp_lng * ds,
                steps=14
            )
            dist_km = straight_dist_km * p['dist_factor']
            dur_min = max(2, int(straight_dist_km * p['dur_factor']))
            safety = calculate_route_safety(pts, route_type=p['route_type'])
            routes.append({
                'id': f'route_{i + 1}',
                'name': f"Route {i + 1} — {p['name_suffix']}",
                'description': p['description'],
                'distance': f"{dist_km:.1f} km",
                'duration': f"{dur_min} mins",
                'safety': safety,
                'is_recommended': (i == 0),
                'waypoints': pts,
                'source': 'estimated'
            })
        return routes

    # ── Build route objects from real road data ──
    routes = []
    for i, (pts, dist_km, dur_min) in enumerate(raw_routes[:3]):
        profile = ROUTE_PROFILES[i] if i < len(ROUTE_PROFILES) else ROUTE_PROFILES[-1]
        safety = calculate_route_safety(pts, route_type=profile['route_type'])
        routes.append({
            'id': f'route_{i + 1}',
            'name': f"Route {i + 1} — {profile['name_suffix']}",
            'description': profile['description'],
            'distance': f"{dist_km:.1f} km",
            'duration': f"{dur_min} mins",
            'safety': safety,
            'is_recommended': (i == 0),
            'waypoints': pts,
            'source': 'osrm' if not getattr(Config, 'GOOGLE_MAPS_API_KEY', None) else 'google'
        })

    # If only 1 real route found, generate 2 synthetic alternatives offset from it
    if len(routes) == 1:
        d_lat = dest_lat - origin_lat
        d_lng = dest_lng - origin_lng
        perp_lat = -d_lng * 0.22
        perp_lng = d_lat * 0.22
        for i, p in enumerate(FALLBACK_PROFILES[1:3], start=1):
            ds = p['detour_scale']
            pts = generate_interpolated_waypoints(
                origin_lat, origin_lng, dest_lat, dest_lng,
                detour_lat=perp_lat * ds, detour_lng=perp_lng * ds,
                steps=14
            )
            dist_km = straight_dist_km * p['dist_factor']
            dur_min = max(2, int(straight_dist_km * p['dur_factor']))
            safety = calculate_route_safety(pts, route_type=p['route_type'])
            routes.append({
                'id': f'route_{i + 1}',
                'name': f"Route {i + 1} — {p['name_suffix']}",
                'description': p['description'],
                'distance': f"{dist_km:.1f} km",
                'duration': f"{dur_min} mins",
                'safety': safety,
                'is_recommended': False,
                'waypoints': pts,
                'source': 'estimated'
            })

    return routes
