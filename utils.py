import json
import os
from datetime import datetime, date
from typing import List, Dict, Any
from flask import request  # For Flask integration

class VisitorTracker:
    """
    Professional visitor tracking system for web applications.
    Features:
    - Automatic logging on each page visit
    - Total, daily, and unique visitor counts
    - Data cleanup (30 days retention)
    - Flask integration ready
    - JSON-based storage for easy portability
    """
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.log_file = os.path.join(data_dir, 'visitors.json')
        os.makedirs(data_dir, exist_ok=True)
    
    def log_visitor(self) -> None:
        """Log current visitor with comprehensive details."""
        try:
            visitors = self._load_visitors()
        except:
            visitors = []
        
        visitor_data = {
            'timestamp': datetime.now().isoformat(),
            'ip': request.remote_addr if 'request' in globals() else '127.0.0.1',
            'user_agent': request.user_agent.string if 'request' in globals() else 'Unknown',
            'referrer': request.referrer if 'request' in globals() else None,
            'path': request.path if 'request' in globals() else '/'
        }
        
        visitors.append(visitor_data)
        
        # Limit to last 5000 entries for performance
        if len(visitors) > 5000:
            visitors = visitors[-5000:]
        
        self._save_visitors(visitors)
    
    def get_total_count(self) -> int:
        """Get total number of visits ever."""
        try:
            return len(self._load_visitors())
        except:
            return 0
    
    def get_today_count(self) -> int:
        """Get visitor count for today."""
        today = date.today()
        return sum(1 for v in self._load_visitors() 
                  if datetime.fromisoformat(v['timestamp']).date() == today)
    
    def get_unique_today(self) -> int:
        """Get unique visitors today (by IP)."""
        today = date.today()
        ips = set()
        for v in self._load_visitors():
            dt = datetime.fromisoformat(v['timestamp']).date()
            if dt == today:
                ips.add(v['ip'])
        return len(ips)
    
    def get_weekly_count(self) -> int:
        """Get visitor count for last 7 days."""
        week_ago = date.today() - timedelta(days=7)
        return sum(1 for v in self._load_visitors()
                  if datetime.fromisoformat(v['timestamp']).date() >= week_ago)
    
    def clean_old_data(self, days: int = 30) -> int:
        """Clean data older than specified days. Returns number of deleted records."""
        try:
            visitors = self._load_visitors()
            cutoff = datetime.now().timestamp() - (days * 24 * 3600)
            
            filtered = [v for v in visitors 
                       if datetime.fromisoformat(v['timestamp']).timestamp() > cutoff]
            deleted = len(visitors) - len(filtered)
            
            self._save_visitors(filtered)
            return deleted
        except:
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        total = self.get_total_count()
        today = self.get_today_count()
        unique_today = self.get_unique_today()
        weekly = self.get_weekly_count()
        return {
            'total_visits': total,
            'today_visits': today,
            'today_unique': unique_today,
            'weekly_visits': weekly,
            'last_updated': datetime.now().isoformat()
        }
    
    def _load_visitors(self) -> List[Dict]:
        """Load visitors from JSON file."""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_visitors(self, visitors: List[Dict]) -> None:
        """Save visitors to JSON file."""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(visitors, f, indent=2, ensure_ascii=False)


# Flask Integration Example (utils.py)
from flask import Flask, request, jsonify, render_template_string
from datetime import timedelta  # Add this import at top

# Initialize tracker
tracker = VisitorTracker()

# Flask app example for testing
app = Flask(__name__)

@app.before_request
def track_every_visit():
    """Automatically track every page visit."""
    tracker.log_visitor()

@app.route('/')
def home():
    stats = tracker.get_stats()
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>Visitor Counter Demo</title>
    <style>body{font-family:Arial; max-width:600px; margin:50px auto;}</style>
    </head>
    <body>
        <h1>🧑‍💻 Professional Visitor Tracker</h1>
        <div style="background:#f0f8ff; padding:20px; border-radius:10px;">
            <h2>📊 Live Statistics</h2>
            <p><strong>Total Visits:</strong> {{ total_visits }}</p>
            <p><strong>Today's Visits:</strong> {{ today_visits }}</p>
            <p><strong>Unique Today:</strong> {{ today_unique }}</p>
            <p><strong>This Week:</strong> {{ weekly_visits }}</p>
        </div>
        <p><small>Last updated: {{ last_updated }}</small></p>
    </body>
    </html>
    """, **stats)

@app.route('/api/stats')
def api_stats():
    return jsonify(tracker.get_stats())

@app.route('/admin/clean')
def clean_data():
    deleted = tracker.clean_old_data()
    return f"Cleaned {deleted} old records."

if __name__ == '__main__':
    print("🚀 Starting Visitor Tracker Demo...")
    print("Visit http://localhost:5000")
    print("API: http://localhost:5000/api/stats")
    app.run(debug=True, host='0.0.0.0', port=5000)
