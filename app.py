import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from services.database import query_db, execute_db, init_db, get_db_connection
from services.storage_service import upload_file, upload_document, check_s3_status
from services.maps_service import get_routes
from services.safety_score import calculate_route_safety
from services.location_service import start_journey, record_location_ping, end_journey, get_active_journey, get_latest_user_location
from services.sos_service import trigger_sos, get_recent_alerts, resolve_sos

app = Flask(__name__)
app.config.from_object(Config)

# Ensure database is initialized on startup
with app.app_context():
    init_db()

# Decorator to enforce authentication
def login_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this feature.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

# Serve uploaded photos when running locally
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

# ----------------- AUTHENTICATION -----------------

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = query_db("SELECT * FROM users WHERE email = ?", (email,), one=True)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            flash(f"Welcome back, {user['name']}!", "success")
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email address or password.", "danger")
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')
            
        existing = query_db("SELECT id FROM users WHERE email = ?", (email,), one=True)
        if existing:
            flash("An account with this email already exists.", "warning")
            return render_template('register.html')
            
        hashed = generate_password_hash(password)
        user_id = execute_db(
            "INSERT INTO users (name, email, password_hash, phone, role) VALUES (?, ?, ?, ?, 'user')",
            (name, email, hashed, phone)
        )
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_role'] = 'user'
        flash("Registration successful! Welcome to Women Safety Portal.", "success")
        return redirect(url_for('dashboard'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for('login'))

# ----------------- MAIN PAGES -----------------

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    contacts = query_db("SELECT * FROM emergency_contacts WHERE user_id = ?", (user_id,))
    recent_reports = query_db("SELECT * FROM safety_reports WHERE status = 'approved' ORDER BY reported_at DESC LIMIT 5")
    active_journey = get_active_journey(user_id)
    return render_template('dashboard.html', 
                           contacts_count=len(contacts), 
                           recent_reports=recent_reports, 
                           active_journey=active_journey)

@app.route('/safe-route')
@login_required
def safe_route():
    return render_template('safe_route.html')

@app.route('/contacts', methods=['GET', 'POST'])
@login_required
def contacts():
    user_id = session['user_id']
    if request.method == 'POST':
        contact_name = request.form.get('contact_name', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        relationship = request.form.get('relationship', 'Family').strip()
        is_primary = 1 if request.form.get('is_primary') else 0
        
        if contact_name and phone_number:
            if is_primary:
                execute_db("UPDATE emergency_contacts SET is_primary = 0 WHERE user_id = ?", (user_id,))
            execute_db(
                "INSERT INTO emergency_contacts (user_id, contact_name, phone_number, relationship, is_primary) VALUES (?, ?, ?, ?, ?)",
                (user_id, contact_name, phone_number, relationship, is_primary)
            )
            flash("Emergency contact added successfully.", "success")
        return redirect(url_for('contacts'))
        
    contacts_list = query_db("SELECT * FROM emergency_contacts WHERE user_id = ? ORDER BY is_primary DESC, id ASC", (user_id,))
    return render_template('contacts.html', contacts=contacts_list)

@app.route('/contacts/delete/<int:contact_id>', methods=['POST'])
@login_required
def delete_contact(contact_id):
    user_id = session['user_id']
    execute_db("DELETE FROM emergency_contacts WHERE id = ? AND user_id = ?", (contact_id, user_id))
    flash("Contact removed.", "info")
    return redirect(url_for('contacts'))

@app.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    user_id = session['user_id']
    if request.method == 'POST':
        title        = request.form.get('title', '').strip()
        category     = request.form.get('category', 'poorly_lit')
        severity     = request.form.get('severity', 'medium')
        description  = request.form.get('description', '').strip()
        witness_name = request.form.get('witness_name', '').strip()
        incident_time= request.form.get('incident_time', '').strip()
        latitude     = float(request.form.get('latitude', 13.0827))
        longitude    = float(request.form.get('longitude', 80.2707))

        # ── Photo evidence upload ──────────────────────────────────────────
        image_file = request.files.get('incident_image')
        image_url  = None
        s3_key     = None
        if image_file and image_file.filename:
            try:
                res = upload_file(image_file, folder_prefix='incident_reports')
                if res:
                    image_url = res['url']
                    s3_key    = res['s3_key']
            except Exception as e:
                flash(f"Photo upload error: {e}", "warning")

        # ── Document evidence upload ───────────────────────────────────────
        doc_file     = request.files.get('incident_document')
        document_url  = None
        document_key  = None
        document_name = None
        if doc_file and doc_file.filename:
            try:
                dres = upload_document(doc_file, original_name=doc_file.filename,
                                       folder_prefix='incident_docs')
                if dres:
                    document_url  = dres['url']
                    document_key  = dres['s3_key']
                    document_name = dres['original_name']
            except Exception as e:
                flash(f"Document upload error: {e}", "warning")

        execute_db(
            """INSERT INTO safety_reports
            (user_id, title, description, category, severity, latitude, longitude,
             image_url, s3_key, document_url, document_key, document_name,
             witness_name, incident_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'approved')""",
            (user_id, title, description, category, severity, latitude, longitude,
             image_url, s3_key, document_url, document_key, document_name,
             witness_name, incident_time)
        )
        flash("Thank you! Your safety report with evidence has been logged and shared to protect others.", "success")
        return redirect(url_for('reports'))

    all_reports = query_db(
        """SELECT r.*, u.name as reporter_name
        FROM safety_reports r
        LEFT JOIN users u ON r.user_id = u.id
        ORDER BY r.reported_at DESC"""
    )
    return render_template('reports.html', reports=all_reports)

@app.route('/admin')
@login_required
def admin_dashboard():
    # Only allow admin role
    if session.get('user_role') != 'admin':
        flash("Admin access restricted.", "danger")
        return redirect(url_for('dashboard'))

    _, db_type = get_db_connection()
    s3_status = check_s3_status()
    
    recent_alerts = get_recent_alerts(limit=15)
    all_reports = query_db("SELECT * FROM safety_reports ORDER BY reported_at DESC")
    all_users = query_db("SELECT id, name, email, phone, role, created_at FROM users ORDER BY id ASC")
    
    cloud_status = {
        'database_engine': 'Amazon RDS (MySQL)' if db_type == 'mysql' else 'Local SQLite (Ready for RDS Switch)',
        'database_connected': True,
        's3_status': s3_status,
        'app_host': 'Amazon EC2 (Linux VM) / Flask Runtime',
        'active_alerts': len([a for a in recent_alerts if a['status'] == 'active'])
    }
    
    return render_template('admin.html', 
                           cloud_status=cloud_status, 
                           alerts=recent_alerts, 
                           reports=all_reports, 
                           users=all_users)

# ----------------- REST APIs FOR MAPS & SOS -----------------

@app.route('/api/geocode', methods=['GET'])
def api_geocode():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'success': False, 'results': []})
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {'q': query, 'format': 'json', 'limit': 5, 'addressdetails': 1}
        headers = {'User-Agent': 'WomenSafetyCloudPortal/1.0'}
        r = requests.get(url, params=params, headers=headers, timeout=5)
        if r.status_code == 200:
            results = [{
                'display_name': item['display_name'],
                'lat': float(item['lat']),
                'lng': float(item['lon'])
            } for item in r.json()]
            return jsonify({'success': True, 'results': results})
    except Exception as e:
        print(f"[Geocode Error] {e}")
    return jsonify({'success': False, 'results': []})

@app.route('/api/routes', methods=['POST'])
def api_get_routes():
    data = request.get_json() or {}
    try:
        origin_lat = float(data.get('origin_lat', 13.0827))
        origin_lng = float(data.get('origin_lng', 80.2707))
        dest_lat = float(data.get('dest_lat', 13.0475))
        dest_lng = float(data.get('dest_lng', 80.2090))
        
        routes = get_routes(origin_lat, origin_lng, dest_lat, dest_lng)
        return jsonify({'success': True, 'routes': routes})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/sos', methods=['POST'])
def api_trigger_sos():
    data = request.get_json() or {}
    user_id = session.get('user_id', 1)
    lat = float(data.get('latitude', 13.0827))
    lng = float(data.get('longitude', 80.2707))
    address = data.get('address', 'Current GPS Location')
    
    result = trigger_sos(user_id, lat, lng, address)
    return jsonify({'success': True, 'alert': result})

@app.route('/api/sos/resolve/<int:alert_id>', methods=['POST'])
@login_required
def api_resolve_sos(alert_id):
    resolve_sos(alert_id)
    return jsonify({'success': True, 'message': 'SOS alert resolved.'})

@app.route('/api/contacts', methods=['GET'])
def api_get_contacts():
    """Returns emergency contacts for current session user (used by SOS modal phone-call UI)."""
    user_id = session.get('user_id', 1)
    contacts = query_db(
        "SELECT contact_name, phone_number, relationship, is_primary FROM emergency_contacts WHERE user_id = ? ORDER BY is_primary DESC",
        (user_id,)
    )
    return jsonify({'success': True, 'contacts': [dict(c) for c in contacts]})

@app.route('/api/reports', methods=['GET'])
def api_get_reports():
    reports_data = query_db("SELECT id, title, category, severity, latitude, longitude, description FROM safety_reports WHERE status = 'approved'")
    return jsonify({'success': True, 'reports': reports_data})

@app.route('/api/journey/start', methods=['POST'])
@login_required
def api_start_journey():
    data = request.get_json() or {}
    user_id = session['user_id']
    journey_id = start_journey(
        user_id=user_id,
        origin_name=data.get('origin_name', 'Start Point'),
        dest_name=data.get('dest_name', 'Destination'),
        origin_lat=float(data.get('origin_lat', 13.0827)),
        origin_lng=float(data.get('origin_lng', 80.2707)),
        dest_lat=float(data.get('dest_lat', 13.0475)),
        dest_lng=float(data.get('dest_lng', 80.2090)),
        route_name=data.get('route_name', 'Primary Route'),
        safety_score=int(data.get('safety_score', 90))
    )
    return jsonify({'success': True, 'journey_id': journey_id})

@app.route('/api/journey/end', methods=['POST'])
@login_required
def api_end_journey():
    data = request.get_json() or {}
    user_id = session['user_id']
    journey_id = data.get('journey_id')
    if journey_id:
        end_journey(journey_id, user_id)
    return jsonify({'success': True, 'message': 'Journey marked safe and finished.'})

@app.route('/api/location/ping', methods=['POST'])
def api_location_ping():
    data = request.get_json() or {}
    user_id = session.get('user_id', 1)
    lat = float(data.get('latitude', 13.0827))
    lng = float(data.get('longitude', 80.2707))
    speed = float(data.get('speed', 0))
    journey_id = data.get('journey_id')
    
    update_id = record_location_ping(user_id, lat, lng, speed, journey_id)
    return jsonify({'success': True, 'update_id': update_id})

if __name__ == '__main__':
    # Listen on 0.0.0.0 so that on EC2 it is immediately publicly accessible
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
