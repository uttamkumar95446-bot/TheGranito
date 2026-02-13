"""
==========================================
THE GRANITO PORTFOLIO - MAIN APPLICATION
Version: 2.0 Professional
Author: Uttam Kumar
==========================================
"""

from flask import (
    Flask, render_template, request, jsonify, 
    send_file, redirect, url_for, flash, session
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import os
import json
from datetime import datetime
from functools import wraps

from config import Config
from utils import sanitize_input, validate_email, log_error
from visitor_tracker import track_visitor, get_visitor_stats

# ==================== APP INITIALIZATION ====================

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# ==================== CONSTANTS ====================

DATA_DIR = "data"
CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.json")
VISITORS_FILE = os.path.join(DATA_DIR, "visitors.json")
RESUME_FILE = "resume/your_resume.pdf"

# ==================== HELPER FUNCTIONS ====================

def load_json_file(filepath, default=None):
    """Load JSON file with error handling"""
    if default is None:
        default = []
    
    if not os.path.exists(filepath):
        return default
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        log_error(f"JSON decode error in {filepath}: {e}")
        return default
    except Exception as e:
        log_error(f"Error loading {filepath}: {e}")
        return default


def save_json_file(filepath, data):
    """Save data to JSON file"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log_error(f"Error saving to {filepath}: {e}")
        return False


def require_admin(f):
    """Decorator for admin-only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== BEFORE REQUEST ====================
from flask import send_from_directory

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')


@app.before_request
def before_request():
    """Track visitors before each request"""
    if request.endpoint == 'home':
        ip = request.remote_addr or "127.0.0.1"
        user_agent = request.headers.get("User-Agent", "Unknown")
        track_visitor(ip, user_agent)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    log_error(f"Internal server error: {error}")
    return render_template('500.html'), 500


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit errors"""
    return jsonify(error="Rate limit exceeded. Please try again later."), 429


# ==================== STATIC ROUTES ====================

@app.route("/favicon.ico")
def favicon():
    """Serve favicon"""
    return send_file(
        os.path.join(app.root_path, "static/images/favicon.ico"),
        mimetype="image/x-icon"
    )


@app.route("/manifest.json")
def manifest():
    """Serve PWA manifest"""
    return send_file(
        os.path.join(app.static_folder, "manifest.json"),
        mimetype="application/json"
    )


@app.route("/robots.txt")
def robots():
    """Serve robots.txt for SEO"""
    return send_file("static/robots.txt", mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    """Serve sitemap for SEO"""
    return send_file("static/sitemap.xml", mimetype="application/xml")


# ==================== MAIN PAGES ====================

@app.route("/")
def home():
    """Homepage"""
    stats = get_visitor_stats()
    return render_template(
        "index.html",
        visitor_count=stats.get('total', 0),
        today_count=stats.get('today', 0)
    )


@app.route("/about")
def about():
    """About page"""
    return render_template("about.html")


@app.route("/projects")
def projects():
    """Projects showcase page"""
    projects_data = [
        {
            "id": 1,
            "title": "TheGranito Portfolio",
            "description": "Professional portfolio website with PWA support, admin dashboard, and analytics",
            "tech": ["Python", "Flask", "JavaScript", "Bootstrap", "PWA"],
            "github": "https://github.com/uttamkumar95446-bot/TheGranito",
            "live": "https://thegranito.onrender.com",
            "image": "project1.jpg",
            "featured": True
        },
        {
            "id": 2,
            "title": "E-Commerce Platform",
            "description": "Full-stack e-commerce solution with payment integration",
            "tech": ["Python", "Flask", "SQLite", "Stripe API"],
            "github": "#",
            "live": "#",
            "image": "project2.jpg",
            "featured": False
        },
        {
            "id": 3,
            "title": "Blog CMS",
            "description": "Content management system for blogs with Markdown support",
            "tech": ["Flask", "SQLAlchemy", "Markdown", "TinyMCE"],
            "github": "#",
            "live": "#",
            "image": "project3.jpg",
            "featured": False
        }
    ]
    
    return render_template("projects.html", projects=projects_data)


@app.route("/blog")
def blog():
    """Blog page"""
    blog_posts = [
        {
            "id": 1,
            "title": "My Journey in Web Development",
            "excerpt": "Starting my journey as a web developer and the lessons learned along the way...",
            "content": "Full blog post content here...",
            "author": "Uttam Kumar",
            "date": "2024-01-15",
            "tags": ["Web Development", "Career", "Learning"],
            "image": "blog1.jpg"
        },
        {
            "id": 2,
            "title": "Building Progressive Web Apps with Flask",
            "excerpt": "A comprehensive guide to creating PWAs using Python Flask framework...",
            "content": "Full blog post content here...",
            "author": "Uttam Kumar",
            "date": "2024-01-20",
            "tags": ["PWA", "Flask", "Tutorial"],
            "image": "blog2.jpg"
        }
    ]
    
    return render_template("blog.html", posts=blog_posts)


@app.route("/contact", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def contact():
    """Contact form page"""
    if request.method == "POST":
        try:
            # Get form data
            name = sanitize_input(request.form.get("name", ""))
            email = request.form.get("email", "")
            subject = sanitize_input(request.form.get("subject", "General Inquiry"))
            message = sanitize_input(request.form.get("message", ""))
            
            # Validate
            if not name or not email or not message:
                return jsonify(success=False, error="All fields are required"), 400
            
            if not validate_email(email):
                return jsonify(success=False, error="Invalid email address"), 400
            
            # Save contact
            contact_data = {
                "name": name,
                "email": email,
                "subject": subject,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "ip": request.remote_addr,
                "status": "new"
            }
            
            contacts = load_json_file(CONTACTS_FILE)
            contacts.append(contact_data)
            save_json_file(CONTACTS_FILE, contacts)
            
            return jsonify(success=True, message="Message sent successfully!")
            
        except Exception as e:
            log_error(f"Contact form error: {e}")
            return jsonify(success=False, error="Something went wrong"), 500
    
    return render_template("contact.html")


@app.route("/offline")
def offline():
    """Offline page for PWA"""
    return render_template("offline.html")


# ==================== ADMIN ROUTES ====================

@app.route("/admin/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def admin_login():
    """Admin login"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Simple auth (use proper auth in production)
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['is_admin'] = True
            session.permanent = True
            return redirect(url_for('admin'))
        else:
            flash("Invalid credentials", "error")
    
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    """Admin logout"""
    session.pop('is_admin', None)
    return redirect(url_for('home'))


@app.route("/admin")
@require_admin
def admin():
    """Admin dashboard"""
    contacts = load_json_file(CONTACTS_FILE)
    stats = get_visitor_stats()
    
    return render_template(
        "admin.html",
        contacts=contacts,
        stats=stats
    )


@app.route("/admin/contacts/delete/<int:index>", methods=["POST"])
@require_admin
def delete_contact(index):
    """Delete a contact"""
    try:
        contacts = load_json_file(CONTACTS_FILE)
        if 0 <= index < len(contacts):
            contacts.pop(index)
            save_json_file(CONTACTS_FILE, contacts)
            return jsonify(success=True)
        return jsonify(success=False, error="Invalid index"), 400
    except Exception as e:
        log_error(f"Delete contact error: {e}")
        return jsonify(success=False, error=str(e)), 500


# ==================== API ROUTES ====================

@app.route("/api/stats")
def api_stats():
    """Get visitor statistics"""
    stats = get_visitor_stats()
    return jsonify(stats)


@app.route("/api/skills")
def api_skills():
    """Get skills data"""
    skills = {
        "technical": [
            {"name": "Python", "level": 90},
            {"name": "Flask", "level": 85},
            {"name": "JavaScript", "level": 80},
            {"name": "HTML/CSS", "level": 95},
            {"name": "Bootstrap", "level": 88},
            {"name": "Git", "level": 75}
        ],
        "soft": [
            "Problem Solving",
            "Communication",
            "Teamwork",
            "Time Management",
            "Creativity"
        ]
    }
    return jsonify(skills)


@app.route("/download-resume")
def download_resume():
    """Download resume"""
    if os.path.exists(RESUME_FILE):
        return send_file(RESUME_FILE, as_attachment=True, download_name="Uttam_Kumar_Resume.pdf")
    else:
        return jsonify(error="Resume not found"), 404


# ==================== UTILITY ROUTES ====================

@app.route("/search")
def search():
    """Search functionality"""
    query = request.args.get('q', '')
    # Implement search logic here
    return render_template("search.html", query=query, results=[])


@app.route("/share")
def share():
    """Handle shared content from PWA"""
    title = request.args.get('title', '')
    text = request.args.get('text', '')
    url = request.args.get('url', '')
    
    return render_template("share.html", title=title, text=text, url=url)


# ==================== CONTEXT PROCESSORS ====================

@app.context_processor
def inject_globals():
    """Inject global variables into templates"""
    return {
        'site_name': 'TheGranito',
        'author': 'Uttam Kumar',
        'current_year': datetime.now().year,
        'is_admin': session.get('is_admin', False)
    }


# ==================== MAIN ====================

if __name__ == "__main__":
    # Ensure data directories exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs('resume', exist_ok=True)
    
    # Run app
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )
