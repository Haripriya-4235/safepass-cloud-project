from datetime import datetime
from services.database import query_db, execute_db

def start_journey(user_id, origin_name, dest_name, origin_lat, origin_lng, dest_lat, dest_lng, route_name, safety_score):
    """Initializes a new tracking journey for a user."""
    journey_id = execute_db(
        """INSERT INTO journeys 
        (user_id, origin_name, destination_name, origin_lat, origin_lng, dest_lat, dest_lng, chosen_route_name, safety_score, status) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')""",
        (user_id, origin_name, dest_name, origin_lat, origin_lng, dest_lat, dest_lng, route_name, safety_score)
    )
    # Log initial location
    record_location_ping(user_id, origin_lat, origin_lng, journey_id=journey_id)
    return journey_id

def record_location_ping(user_id, lat, lng, speed=0, journey_id=None):
    """Records a live GPS update during an active journey."""
    update_id = execute_db(
        "INSERT INTO location_updates (journey_id, user_id, latitude, longitude, speed) VALUES (?, ?, ?, ?, ?)",
        (journey_id, user_id, lat, lng, speed)
    )
    return update_id

def get_latest_user_location(user_id):
    """Returns the most recent coordinates recorded for this user."""
    row = query_db(
        "SELECT latitude, longitude, speed, recorded_at FROM location_updates WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,), one=True
    )
    return row

def end_journey(journey_id, user_id):
    """Marks a journey as safely completed."""
    execute_db(
        "UPDATE journeys SET status = 'completed', ended_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?",
        (journey_id, user_id)
    )
    return True

def get_active_journey(user_id):
    """Fetches currently ongoing journey for the user."""
    return query_db(
        "SELECT * FROM journeys WHERE user_id = ? AND status = 'active' ORDER BY id DESC LIMIT 1",
        (user_id,), one=True
    )
