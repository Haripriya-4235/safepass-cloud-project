import os
import uuid
from werkzeug.utils import secure_filename
from config import Config

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_DOCUMENTS = {'pdf', 'doc', 'docx', 'txt', 'xlsx', 'xls', 'odt', 'csv'}
ALL_ALLOWED = ALLOWED_EXTENSIONS | ALLOWED_DOCUMENTS

DOC_CONTENT_TYPES = {
    'pdf':  'application/pdf',
    'doc':  'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'txt':  'text/plain',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'xls':  'application/vnd.ms-excel',
    'csv':  'text/csv',
    'odt':  'application/vnd.oasis.opendocument.text',
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_document(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOCUMENTS

def allowed_any(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALL_ALLOWED

def get_s3_client():
    if Config.S3_BUCKET:
        try:
            import boto3
            if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
                return boto3.client(
                    's3',
                    region_name=Config.AWS_REGION,
                    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
                )
            else:
                # Uses EC2 IAM Role if running on AWS EC2
                return boto3.client('s3', region_name=Config.AWS_REGION)
        except Exception as e:
            print(f"[Storage Warning] S3 client creation failed: {e}")
    return None

def upload_file(file_storage, folder_prefix='incidents'):
    """
    Uploads a file to Amazon S3 if configured, else saves locally.
    Returns dict: {'url': ..., 's3_key': ..., 'storage_type': 's3'|'local'}
    """
    if not file_storage or file_storage.filename == '':
        return None

    if not allowed_file(file_storage.filename):
        raise ValueError("Unsupported file type. Please upload an image (PNG, JPG, JPEG, WEBP).")

    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{folder_prefix}/{uuid.uuid4().hex}.{ext}"

    s3_client = get_s3_client()
    if s3_client and Config.S3_BUCKET:
        try:
            # Upload directly to S3
            s3_client.upload_fileobj(
                file_storage,
                Config.S3_BUCKET,
                unique_filename,
                ExtraArgs={'ContentType': file_storage.content_type}
            )
            s3_url = f"https://{Config.S3_BUCKET}.s3.{Config.AWS_REGION}.amazonaws.com/{unique_filename}"
            return {
                'url': s3_url,
                's3_key': unique_filename,
                'storage_type': 's3'
            }
        except Exception as e:
            print(f"[Storage Warning] Failed to upload to S3 ({e}), falling back to local storage.")

    # Local fallback storage
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    local_name = f"{uuid.uuid4().hex}.{ext}"
    local_path = os.path.join(Config.UPLOAD_FOLDER, local_name)
    file_storage.seek(0)
    file_storage.save(local_path)
    
    return {
        'url': f"/uploads/{local_name}",
        's3_key': local_name,
        'storage_type': 'local'
    }

def upload_document(file_storage, original_name=None, folder_prefix='documents'):
    """
    Uploads a document (PDF, DOC, DOCX, TXT, etc.) to S3 or local storage.
    Returns dict: {'url': ..., 's3_key': ..., 'storage_type': ..., 'original_name': ...}
    """
    if not file_storage or file_storage.filename == '':
        return None

    fname = secure_filename(file_storage.filename)
    ext = fname.rsplit('.', 1)[-1].lower() if '.' in fname else 'bin'
    if ext not in ALLOWED_DOCUMENTS:
        raise ValueError(f"Unsupported document type '.{ext}'. Allowed: PDF, DOC, DOCX, TXT, XLSX, CSV")

    saved_name = original_name or fname
    unique_filename = f"{folder_prefix}/{uuid.uuid4().hex}_{fname}"
    content_type = DOC_CONTENT_TYPES.get(ext, 'application/octet-stream')

    s3_client = get_s3_client()
    if s3_client and Config.S3_BUCKET:
        try:
            s3_client.upload_fileobj(
                file_storage,
                Config.S3_BUCKET,
                unique_filename,
                ExtraArgs={'ContentType': content_type}
            )
            s3_url = f"https://{Config.S3_BUCKET}.s3.{Config.AWS_REGION}.amazonaws.com/{unique_filename}"
            return {'url': s3_url, 's3_key': unique_filename,
                    'storage_type': 's3', 'original_name': saved_name}
        except Exception as e:
            print(f"[Storage Warning] S3 doc upload failed ({e}), falling back to local.")

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    local_name = f"{uuid.uuid4().hex}.{ext}"
    local_path = os.path.join(Config.UPLOAD_FOLDER, local_name)
    file_storage.seek(0)
    file_storage.save(local_path)
    return {'url': f"/uploads/{local_name}", 's3_key': local_name,
            'storage_type': 'local', 'original_name': saved_name}

def check_s3_status():
    """Diagnostic check to test AWS S3 connection for viva/rubric presentation."""
    if not Config.S3_BUCKET:
        return {'connected': False, 'message': 'S3_BUCKET not configured in environment.'}
    try:
        s3 = get_s3_client()
        s3.head_bucket(Bucket=Config.S3_BUCKET)
        return {'connected': True, 'bucket': Config.S3_BUCKET, 'region': Config.AWS_REGION}
    except Exception as e:
        return {'connected': False, 'message': str(e)}
