"""
==========================================
THE GRANITO PORTFOLIO - UTILITY FUNCTIONS
Version: 2.0
==========================================
"""

import re
import os
import json
import logging
from datetime import datetime
from functools import wraps
from flask import request, jsonify
import bleach


# ==================== LOGGING SETUP ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ==================== INPUT SANITIZATION ====================

def sanitize_input(text, max_length=1000):
    """
    Sanitize user input to prevent XSS attacks
    
    Args:
        text (str): Input text to sanitize
        max_length (int): Maximum allowed length
    
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Limit length
    text = text[:max_length]
    
    # Remove potentially dangerous HTML
    allowed_tags = []  # No HTML tags allowed
    allowed_attributes = {}
    
    cleaned = bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    
    return cleaned.strip()


def sanitize_html(html, max_length=10000):
    """
    Sanitize HTML while preserving safe tags
    
    Args:
        html (str): HTML content to sanitize
        max_length (int): Maximum allowed length
    
    Returns:
        str: Sanitized HTML
    """
    if not html:
        return ""
    
    html = html[:max_length]
    
    # Allow safe HTML tags
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'blockquote', 'code', 'pre', 'ul', 'ol', 'li', 'a', 'img'
    ]
    
    allowed_attributes = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height']
    }
    
    cleaned = bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    
    return cleaned


# ==================== VALIDATION FUNCTIONS ====================

def validate_email(email):
    """
    Validate email address format
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False
    
    # Email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    return bool(re.match(pattern, email))


def validate_url(url):
    """
    Validate URL format
    
    Args:
        url (str): URL to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not url:
        return False
    
    pattern = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$'
    
    return bool(re.match(pattern, url))


def validate_phone(phone):
    """
    Validate phone number (Indian format)
    
    Args:
        phone (str): Phone number to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove spaces and special characters
    phone = re.sub(r'[^\d]', '', phone)
    
    # Check if it's a valid Indian phone number (10 digits)
    return len(phone) == 10 and phone[0] in ['6', '7', '8', '9']


# ==================== FILE OPERATIONS ====================

def allowed_file(filename, allowed_extensions=None):
    """
    Check if file extension is allowed
    
    Args:
        filename (str): Filename to check
        allowed_extensions (set): Set of allowed extensions
    
    Returns:
        bool: True if allowed, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_file_size(filepath):
    """
    Get file size in bytes
    
    Args:
        filepath (str): Path to file
    
    Returns:
        int: File size in bytes, or 0 if file doesn't exist
    """
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0


def format_file_size(size_bytes):
    """
    Format file size to human-readable format
    
    Args:
        size_bytes (int): Size in bytes
    
    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


# ==================== DATE/TIME UTILITIES ====================

def format_datetime(dt, format_str="%Y-%m-%d %H:%M:%S"):
    """
    Format datetime object to string
    
    Args:
        dt (datetime): Datetime object
        format_str (str): Format string
    
    Returns:
        str: Formatted datetime string
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    
    return dt.strftime(format_str)


def get_time_ago(dt):
    """
    Get human-readable time difference
    
    Args:
        dt (datetime): Datetime object or ISO string
    
    Returns:
        str: Time ago string (e.g., "2 hours ago")
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return "Unknown"
    
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return format_datetime(dt, "%B %d, %Y")


# ==================== JSON UTILITIES ====================

def load_json_safe(filepath, default=None):
    """
    Safely load JSON file
    
    Args:
        filepath (str): Path to JSON file
        default: Default value if file doesn't exist or is invalid
    
    Returns:
        Data from JSON file or default value
    """
    if default is None:
        default = {}
    
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
    
    return default


def save_json_safe(filepath, data):
    """
    Safely save data to JSON file
    
    Args:
        filepath (str): Path to JSON file
        data: Data to save
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")
        return False


# ==================== ERROR LOGGING ====================

def log_error(message, level='error'):
    """
    Log error message
    
    Args:
        message (str): Error message
        level (str): Log level (debug, info, warning, error, critical)
    """
    log_method = getattr(logger, level, logger.error)
    log_method(message)


def log_request(func):
    """Decorator to log requests"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
        return func(*args, **kwargs)
    return wrapper


# ==================== API UTILITIES ====================

def api_response(success=True, data=None, error=None, status_code=200):
    """
    Create standardized API response
    
    Args:
        success (bool): Success status
        data: Response data
        error (str): Error message
        status_code (int): HTTP status code
    
    Returns:
        Response object
    """
    response = {'success': success}
    
    if data is not None:
        response['data'] = data
    
    if error:
        response['error'] = error
    
    return jsonify(response), status_code


def require_api_key(f):
    """Decorator to require API key for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = os.environ.get('API_KEY')
        
        if not api_key or api_key != expected_key:
            return api_response(
                success=False,
                error="Invalid or missing API key",
                status_code=401
            )
        
        return f(*args, **kwargs)
    return decorated_function


# ==================== TEXT UTILITIES ====================

def truncate_text(text, length=100, suffix='...'):
    """
    Truncate text to specified length
    
    Args:
        text (str): Text to truncate
        length (int): Maximum length
        suffix (str): Suffix to add if truncated
    
    Returns:
        str: Truncated text
    """
    if not text:
        return ""
    
    if len(text) <= length:
        return text
    
    return text[:length].rsplit(' ', 1)[0] + suffix


def slugify(text):
    """
    Convert text to URL-friendly slug
    
    Args:
        text (str): Text to slugify
    
    Returns:
        str: Slugified text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    
    # Remove special characters
    text = re.sub(r'[^a-z0-9-]', '', text)
    
    # Remove multiple hyphens
    text = re.sub(r'-+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text


# ==================== IP UTILITIES ====================

def get_client_ip():
    """
    Get client IP address
    
    Returns:
        str: Client IP address
    """
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr or '127.0.0.1'


# ==================== SECURITY UTILITIES ====================

def generate_token(length=32):
    """
    Generate random token
    
    Args:
        length (int): Token length
    
    Returns:
        str: Random token
    """
    import secrets
    return secrets.token_urlsafe(length)


def hash_password(password):
    """
    Hash password using werkzeug
    
    Args:
        password (str): Plain text password
    
    Returns:
        str: Hashed password
    """
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password)


def verify_password(password_hash, password):
    """
    Verify password against hash
    
    Args:
        password_hash (str): Hashed password
        password (str): Plain text password
    
    Returns:
        bool: True if password matches, False otherwise
    """
    from werkzeug.security import check_password_hash
    return check_password_hash(password_hash, password)
