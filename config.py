import os
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'women-safety-cloud-secret-key-2025')
    
    # Database Configuration (AWS RDS MySQL / SQLite fallback)
    DB_TYPE = os.environ.get('DB_TYPE', 'sqlite')  # 'mysql' for AWS RDS or 'sqlite'
    DB_HOST = os.environ.get('DB_HOST', '')        # e.g., mydb.czk2...us-east-1.rds.amazonaws.com
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'admin')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'womensafety')
    
    # AWS S3 Storage Configuration
    AWS_REGION = os.environ.get('AWS_REGION', 'ap-south-1') # Default to ap-south-1 (Mumbai) or us-east-1
    S3_BUCKET = os.environ.get('S3_BUCKET', '')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    
    # Local Uploads Folder fallback
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    
    # External APIs
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    
    # Emergency Alerts (SMS/Email simulation or AWS SNS)
    ENABLE_SMS_SIMULATION = True
