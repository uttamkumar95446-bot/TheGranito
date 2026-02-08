import json
import os
from datetime import datetime
from flask import request  # Optional for IP/user-agent

def log_visitor():
    """Log a page view. Called on every request."""
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    count_file = os.path.join(data_dir, 'views.json')
    
    # Atomic increment (safe for multiple visitors)
    try:
        if os.path.exists(count_file):
            with open(count_file, 'r') as f:
                data = json.load(f)
                total_views = data.get('total_views', 0) + 1
        else:
            total_views = 1
        
        data = {
            'total_views': total_views,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(count_file, 'w') as f:
            json.dump(data, f)
            
    except Exception:
        pass  # Graceful fail if file locked

def get_visitor_count():
    """Get formatted total previous views."""
    count_file = 'data/views.json'
    if os.path.exists(count_file):
        try:
            with open(count_file, 'r') as f:
                data = json.load(f)
                return data.get('total_views', 0)
        except:
            return 0
    return 0

