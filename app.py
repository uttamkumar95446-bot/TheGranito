# app.py
from flask import (
    Flask, render_template, request,
    jsonify, send_file, send_from_directory
)
import os
import json
from datetime import datetime

from utils import log_visitor, get_visitor_count
from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

DATA_DIR = "data"
CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.json")


# -------------------- Helpers --------------------

def load_contacts():
    if not os.path.exists(CONTACTS_FILE):
        return []
    try:
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_contact(data: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    contacts = load_contacts()
    contacts.append(data)
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)


# -------------------- System Routes --------------------

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static/images"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon"
    )


@app.route("/manifest.json")
def manifest():
    return send_from_directory(
        app.static_folder,
        "manifest.json",
        mimetype="application/json"
    )


@app.before_request
def track_visitors():
    if request.endpoint == "home":
        log_visitor(
            ip=request.remote_addr or "127.0.0.1",
            user_agent=request.headers.get("User-Agent", "Unknown")
        )


# -------------------- Pages --------------------

@app.route("/")
def home():
    return render_template(
        "index.html",
        visitor_count=get_visitor_count()
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/projects")
def projects():
    return render_template("projects.html", projects=[
        {
            "id": 1,
            "title": "Portfolio Website",
            "description": "Personal portfolio built with Flask",
            "tech": ["Python", "Flask", "HTML", "CSS", "JS"],
            "github": "#",
            "live": "#"
        }
    ])


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        save_contact({
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "subject": request.form.get("subject", "No Subject"),
            "message": request.form.get("message"),
            "timestamp": datetime.utcnow().isoformat()
        })
        return jsonify(success=True)

    return render_template("contact.html")


@app.route("/admin")
def admin():
    return render_template("admin.html", contacts=load_contacts())


@app.route("/blog")
def blog():
    return render_template("blog.html", posts=[
        {
            "id": 1,
            "title": "My Journey in Web Development",
            "date": "2024-01-15",
            "author": "Uttam Kumar",
            "content": "Starting my journey with Flask..."
        }
    ])


@app.route("/download-resume")
def download_resume():
    resume_path = "resume/your_resume.pdf"
    if not os.path.exists(resume_path):
        return jsonify(error="Resume not found"), 404
    return send_file(resume_path, as_attachment=True)


# -------------------- APIs --------------------

@app.route("/api/skills")
def skills():
    return jsonify({
        "technical": ["Python", "Flask", "HTML", "CSS", "JavaScript"],
        "soft": ["Problem Solving", "Communication", "Teamwork"]
    })


@app.route("/api/stats")
def stats():
    return jsonify({
        "total_visitors": get_visitor_count(),
        "total_messages": len(load_contacts()),
        "last_updated": datetime.utcnow().date().isoformat()
    })


# -------------------- Errors --------------------

@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(_):
    return render_template("500.html"), 500


# -------------------- Run --------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

