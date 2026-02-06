from utils import tracker  # Adjust import if filename different
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.before_request
def track_visitors():
    tracker.log_visitor()

@app.route('/api/stats')
def stats():
    return jsonify(tracker.get_stats())

# Your existing routes...

from flask import Flask, render_template, request, jsonify
from visitor_tracker import log_visitor, get_stats  # Changed from utils

app = Flask(__name__)

@app.before_request
def track_all_pages():
    log_visitor()

@app.route('/api/stats')
def api_stats():
    return jsonify(get_stats())

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import os
import json
from datetime import datetime
from utils import log_visitor, get_visitor_count
app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

# Favicon route
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Manifest route for PWA
@app.route('/manifest.json')
def manifest():
    return send_from_directory(app.static_folder, 'manifest.json', mimetype='application/json')

@app.before_request
def before_request():
    if request.endpoint == 'home':
        log_visitor()

@app.route('/')
def home():
    visitor_count = get_visitor_count()
    return render_template('index.html', visitor_count=visitor_count)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    projects_data = [
        {
            'id': 1,
            'title': 'Portfolio Website',
            'description': 'Personal portfolio built with Flask and modern web technologies',
            'tech': ['Python', 'Flask', 'HTML', 'CSS', 'JavaScript', 'Bootstrap'],
            'github': 'https://github.com/yourusername/portfolio',
            'live': 'https://yoursite.netlify.app'
        },
        {
            'id': 2,
            'title': 'E-Commerce Platform',
            'description': 'Full-stack e-commerce solution with payment integration',
            'tech': ['Python', 'Flask', 'SQLite', 'Bootstrap', 'JavaScript'],
            'github': 'https://github.com/yourusername/ecommerce',
            'live': 'https://ecommerce-demo.netlify.app'
        },
        {
            'id': 3,
            'title': 'Task Management App',
            'description': 'Collaborative task management with real-time updates',
            'tech': ['React', 'Node.js', 'MongoDB', 'Socket.io'],
            'github': 'https://github.com/yourusername/taskmanager',
            'live': 'https://taskmanager-app.netlify.app'
        }
    ]
    return render_template('projects.html', projects=projects_data)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'subject': request.form.get('subject', 'No Subject'),
            'message': request.form.get('message'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        save_contact_message(data)
        return jsonify({'status': 'success', 'message': 'Message sent successfully!'})
    
    return render_template('contact.html')

@app.route('/admin')
def admin():
    try:
        with open('data/contacts.json', 'r', encoding='utf-8') as f:
            contacts = json.load(f)
    except:
        contacts = []
    
    return render_template('admin.html', contacts=contacts)

@app.route('/blog')
def blog():
    posts = [
        {
            'id': 1,
            'title': 'My Journey in Web Development',
            'content': 'Starting my journey with Python and Flask, I discovered the power of web development...',
            'date': '2024-01-15',
            'author': 'Your Name'
        },
        {
            'id': 2,
            'title': 'Building Responsive Websites',
            'content': 'Learn how to create beautiful, responsive websites using modern CSS techniques...',
            'date': '2024-01-10',
            'author': 'Your Name'
        }
    ]
    return render_template('blog.html', posts=posts)

@app.route('/download-resume')
def download_resume():
    try:
        return send_file('resume/your_resume.pdf', as_attachment=True, download_name='Resume.pdf')
    except:
        return jsonify({'error': 'Resume not found'}), 404

# API endpoints
@app.route('/api/skills')
def get_skills():
    skills = {
        'technical': ['Python', 'JavaScript', 'HTML/CSS', 'Flask', 'Git', 'Bootstrap', 'SQLite'],
        'soft': ['Problem Solving', 'Communication', 'Team Work', 'Leadership', 'Time Management']
    }
    return jsonify(skills)

@app.route('/api/experience')
def get_experience():
    experience = [
        {
            'title': 'Web Developer',
            'company': 'Tech Solutions Pvt. Ltd.',
            'duration': '2023 - Present',
            'description': 'Developing responsive web applications using Flask, JavaScript, and modern web technologies'
        },
        {
            'title': 'Frontend Developer Intern',
            'company': 'StartUp Inc.',
            'duration': '2022 - 2023',
            'description': 'Worked on UI/UX improvements and built responsive websites using HTML, CSS, and JavaScript'
        }
    ]
    return jsonify(experience)

@app.route('/api/stats')
def get_stats():
    stats = {
        'total_visitors': get_visitor_count(),
        'total_projects': 8,
        'total_messages': len(get_contacts()),
        'last_updated': datetime.now().strftime('%Y-%m-%d')
    }
    return jsonify(stats)

# Helper functions
def save_contact_message(data):
    contacts_file = 'data/contacts.json'
    os.makedirs('data', exist_ok=True)
    
    try:
        with open(contacts_file, 'r', encoding='utf-8') as f:
            contacts = json.load(f)
    except:
        contacts = []
    
    contacts.append(data)
    
    with open(contacts_file, 'w', encoding='utf-8') as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

def get_contacts():
    try:
        with open('data/contacts.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
