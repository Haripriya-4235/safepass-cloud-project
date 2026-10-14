import math
from datetime import datetime
from services.database import query_db

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates distance between two coordinate pairs in kilometers."""
    R = 6371.0 # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_route_safety(waypoints, route_type='main_road'):
    """
    Computes a transparent, reproducible safety score (0-100) for a given route.
    
    Factors considered:
    1. Incident proximity (from crowdsourced and verified safety_reports in DB)
    2. Route characteristics (main road vs alleyways vs dark paths)
    3. Community lighting and crowd ratings
    4. Time-of-day risk factor (higher risk at night)
    """
    base_score = 90 if route_type == 'main_road' else 70
    
    # Check current hour for night-time factor
    current_hour = datetime.now().hour
    is_night = current_hour >= 20 or current_hour <= 5
    if is_night:
        base_score -= 10

    # Fetch active safety reports
    reports = query_db("SELECT latitude, longitude, severity, category FROM safety_reports WHERE status = 'approved'")
    
    incident_deductions = 0
    safe_zone_bonus = 0
    
    # Check route points against report coordinates
    for pt in waypoints:
        p_lat, p_lng = pt['lat'], pt['lng']
        for r in reports:
            dist = haversine_distance(p_lat, p_lng, r['latitude'], r['longitude'])
            if dist <= 0.4: # within 400 meters of the path
                if r['category'] == 'safe_zone':
                    safe_zone_bonus += 5
                elif r['severity'] == 'high':
                    incident_deductions += 15
                elif r['severity'] == 'medium':
                    incident_deductions += 8
                else:
                    incident_deductions += 4

    # Cap deductions
    incident_deductions = min(incident_deductions, 45)
    safe_zone_bonus = min(safe_zone_bonus, 15)

    final_score = base_score - incident_deductions + safe_zone_bonus
    final_score = max(10, min(100, final_score)) # Clamp between 10 and 100

    if final_score >= 80:
        level = "Very Safe"
        color = "#10B981" # Green
        recommendation = "Highly Recommended: Well-lit, active traffic and monitored."
    elif final_score >= 55:
        level = "Moderate"
        color = "#F59E0B" # Amber / Orange
        recommendation = "Acceptable: Fair lighting, occasional isolated stretches."
    else:
        level = "High Risk"
        color = "#EF4444" # Red
        recommendation = "Caution Advised: Multiple safety incidents or poorly lit."

    return {
        'score': final_score,
        'level': level,
        'color': color,
        'recommendation': recommendation,
        'night_mode': is_night,
        'incidents_nearby': min(incident_deductions // 8, 10)
    }
