import os
import sqlite3
import pymysql
from pymysql.cursors import DictCursor
from config import Config
from werkzeug.security import generate_password_hash

def get_db_connection():
    """
    Returns a database connection.
    If DB_TYPE is 'mysql' and DB_HOST is set, connects to Amazon RDS MySQL.
    Otherwise, gracefully connects to local SQLite database.
    """
    if Config.DB_TYPE == 'mysql' and Config.DB_HOST:
        try:
            connection = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                cursorclass=DictCursor,
                autocommit=True,
                connect_timeout=5
            )
            return connection, 'mysql'
        except Exception as e:
            print(f"[DB Warning] Could not connect to Amazon RDS MySQL ({e}). Falling back to local SQLite.")
    
    # SQLite Fallback
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'women_safety.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn, 'sqlite'

def query_db(query, args=(), one=False):
    """Executes a SELECT query and returns list of dictionaries or a single dict."""
    conn, engine = get_db_connection()
    try:
        if engine == 'mysql':
            with conn.cursor() as cursor:
                cursor.execute(query, args)
                rv = cursor.fetchall()
                return (rv[0] if rv else None) if one else rv
        else:
            # SQLite
            # Replace MySQL specific syntax if necessary
            cur = conn.cursor()
            cur.execute(query, args)
            rv = [dict(row) for row in cur.fetchall()]
            return (rv[0] if rv else None) if one else rv
    finally:
        conn.close()

def execute_db(query, args=()):
    """Executes an INSERT, UPDATE, or DELETE query and returns the last inserted row id."""
    conn, engine = get_db_connection()
    try:
        if engine == 'mysql':
            with conn.cursor() as cursor:
                cursor.execute(query, args)
                last_id = cursor.lastrowid
                return last_id
        else:
            cur = conn.cursor()
            cur.execute(query, args)
            conn.commit()
            return cur.lastrowid
    finally:
        conn.close()

def init_db():
    """Initializes tables and seeds default demo data if not already present."""
    conn, engine = get_db_connection()
    try:
        if engine == 'mysql':
            with conn.cursor() as cursor:
                # Read schema.sql
                schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'schema.sql')
                if os.path.exists(schema_path):
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        sql_commands = f.read().split(';')
                        for cmd in sql_commands:
                            cmd = cmd.strip()
                            if cmd:
                                cursor.execute(cmd)
        else:
            cur = conn.cursor()
            # SQLite Table definitions
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS emergency_contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    contact_name TEXT NOT NULL,
                    phone_number TEXT NOT NULL,
                    relationship TEXT DEFAULT 'Family',
                    is_primary INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS journeys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    origin_name TEXT NOT NULL,
                    destination_name TEXT NOT NULL,
                    origin_lat REAL NOT NULL,
                    origin_lng REAL NOT NULL,
                    dest_lat REAL NOT NULL,
                    dest_lng REAL NOT NULL,
                    chosen_route_name TEXT,
                    safety_score INTEGER DEFAULT 100,
                    status TEXT DEFAULT 'active',
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS location_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    journey_id INTEGER NULL,
                    user_id INTEGER NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    speed REAL DEFAULT 0,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS sos_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    address TEXT,
                    status TEXT DEFAULT 'active',
                    google_maps_url TEXT,
                    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS safety_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    severity TEXT DEFAULT 'medium',
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    image_url TEXT,
                    s3_key TEXT,
                    document_url TEXT,
                    document_key TEXT,
                    document_name TEXT,
                    witness_name TEXT,
                    incident_time TEXT,
                    status TEXT DEFAULT 'approved',
                    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            ''')
            # Migrate existing DB — add new columns if they don't exist yet
            for col, col_def in [
                ('document_url',  'TEXT'),
                ('document_key',  'TEXT'),
                ('document_name', 'TEXT'),
                ('witness_name',  'TEXT'),
                ('incident_time', 'TEXT'),
            ]:
                try:
                    cur.execute(f'ALTER TABLE safety_reports ADD COLUMN {col} {col_def}')
                except Exception:
                    pass  # Column already exists — safe to ignore
            cur.execute('''
                CREATE TABLE IF NOT EXISTS safety_ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    route_name TEXT NOT NULL,
                    lighting_score INTEGER DEFAULT 3,
                    crowd_score INTEGER DEFAULT 3,
                    police_presence_score INTEGER DEFAULT 3,
                    overall_score INTEGER DEFAULT 3,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            ''')
            conn.commit()
    finally:
        conn.close()

    # Seed demo user & sample safety reports if empty
    users = query_db("SELECT * FROM users")
    if not users:
        admin_pass = generate_password_hash("admin123")
        demo_pass = generate_password_hash("demo123")
        admin_id = execute_db("INSERT INTO users (name, email, password_hash, phone, role) VALUES (?, ?, ?, ?, ?)",
                   ("Admin Safety Officer", "admin@cloudsafety.org", admin_pass, "+919876543210", "admin"))
        user_id = execute_db("INSERT INTO users (name, email, password_hash, phone, role) VALUES (?, ?, ?, ?, ?)",
                   ("Priya Sharma", "priya@example.com", demo_pass, "+919123456789", "user"))
        
        # Add sample emergency contacts
        execute_db("INSERT INTO emergency_contacts (user_id, contact_name, phone_number, relationship, is_primary) VALUES (?, ?, ?, ?, ?)",
                   (user_id, "Mom (Anjali)", "+919876501234", "Parent", 1))
        execute_db("INSERT INTO emergency_contacts (user_id, contact_name, phone_number, relationship, is_primary) VALUES (?, ?, ?, ?, ?)",
                   (user_id, "Sister (Kavita)", "+919876505678", "Sibling", 0))
        
        # Add sample safety reports
        sample_reports = [
            (user_id, "Broken Streetlights on Main Avenue", "All streetlights between Metro Gate 2 and Bus Stop are off after 8 PM.", "poorly_lit", "high", 13.0827, 80.2707, None, None, "approved"),
            (user_id, "Isolated Alley near Park", "Very deserted alleyway with no police patrol.", "isolated_area", "medium", 13.0850, 80.2730, None, None, "approved"),
            (user_id, "Well Lit Police Booth", "24/7 Women Help Desk and active police patrolling.", "safe_zone", "low", 13.0810, 80.2680, None, None, "approved")
        ]
        for r in sample_reports:
            execute_db("INSERT INTO safety_reports (user_id, title, description, category, severity, latitude, longitude, image_url, s3_key, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", r)
            
        print("[Database] Initialized and seeded with default admin and demo records.")
