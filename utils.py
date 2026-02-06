import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, Any
from flask import request

# Global tracker instance
tracker = None

class VisitorTracker:
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.log_file = os.path.join(data_dir, 'visitors.json')
        os.makedirs(data_dir, exist_ok=True)

    def log_visitor(self):
        """Log current visitor."""
        visitor_data = {
            'timestamp': datetime.now().isoformat(),
            'ip': request.remote_addr if request else 'unknown',
            'path': request.path if request else '/'
        }
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {'visits': [], 'total': 0}
        
        data['visits'].append(visitor_data)
        data['total'] += 1
        
        # Cleanup old data (30 days)
        cutoff = datetime.now() - timedelta(days=30)
        data['visits'] = [v for v in data['visits'] 
                         if datetime.fromisoformat(v['timestamp']) > cutoff]
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return data['total']

    def get_visitor_count(self) -> int:
        """Get total visitor count."""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data['total']
        except:
            return 0

# Initialize global tracker
tracker = VisitorTracker()

# BACKWARD COMPATIBLE FUNCTIONS (what your app expects)
def log_visitor():
    """Direct function call - works with your existing app.py"""
    return tracker.log_visitor()

def get_visitor_count():
    """Direct function call - works with your existing templates"""
    return tracker.get_visitor_count()

# Export everything
__all__ = ['log_visitor', 'get_visitor_count', 'tracker']
