from datetime import datetime
from services.database import query_db, execute_db
from config import Config

def trigger_sos(user_id, latitude, longitude, address="Current Device Location"):
    """
    Triggers an emergency SOS event:
    1. Records alert in database.
    2. Builds precise Google Maps coordinates link.
    3. Notifies all configured emergency contacts.
    """
    # Fetch user details
    user = query_db("SELECT name, phone FROM users WHERE id = ?", (user_id,), one=True)
    user_name = user['name'] if user else "A user"

    maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"

    # Record in database
    alert_id = execute_db(
        "INSERT INTO sos_alerts (user_id, latitude, longitude, address, status, google_maps_url) VALUES (?, ?, ?, ?, 'active', ?)",
        (user_id, latitude, longitude, address, maps_url)
    )

    # Fetch emergency contacts
    contacts = query_db("SELECT contact_name, phone_number, relationship FROM emergency_contacts WHERE user_id = ?", (user_id,))

    # Dispatch alerts (Simulated SMS/Email/AWS SNS)
    dispatched_notifications = []
    message_body = (
        f"[EMERGENCY SOS ALERT]\n"
        f"{user_name} needs immediate assistance!\n"
        f"Location: {maps_url}\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}\n"
        f"Status: Active Distress Signal"
    )

    for c in contacts:
        # In a production cloud system, trigger AWS SNS or Twilio SMS here:
        # sns_client.publish(PhoneNumber=c['phone_number'], Message=message_body)
        print(f"[SOS] Notifying: {c['contact_name']} ({c['phone_number']})")
        dispatched_notifications.append({
            'contact_name': c['contact_name'],
            'phone_number': c['phone_number'],
            'status': 'DELIVERED (SIMULATED)',
            'timestamp': datetime.now().isoformat()
        })

    return {
        'alert_id': alert_id,
        'status': 'triggered',
        'latitude': latitude,
        'longitude': longitude,
        'maps_url': maps_url,
        'contacts_notified': dispatched_notifications,
        'message': f"Distress signal transmitted to {len(contacts)} emergency contacts."
    }

def get_recent_alerts(limit=10):
    """Fetches recent SOS alerts for admin dashboard."""
    return query_db(
        """SELECT s.*, u.name as user_name, u.phone as user_phone 
        FROM sos_alerts s 
        JOIN users u ON s.user_id = u.id 
        ORDER BY s.triggered_at DESC LIMIT ?""",
        (limit,)
    )

def resolve_sos(alert_id):
    """Marks an SOS alert as resolved."""
    execute_db("UPDATE sos_alerts SET status = 'resolved' WHERE id = ?", (alert_id,))
    return True
