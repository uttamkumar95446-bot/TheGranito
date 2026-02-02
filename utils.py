# utils.py - Fixed for Render.com deployment
import json
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from flask import request

class VisitorTracker:
    """Professional visitor tracking system."""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.log_file = os.path.join(data_dir, 'visitors.json')
        os.makedirs(data_dir, exist_ok=True)
    
    def log_visitor(self) -> None:
        """Log current visitor."""
        try:
            visitors = self._load_visitors()
        except:
            visitors = []
        
        visitor_data = {
            'timestamp': datetime.now().isoformat(),
            'ip': request.remote_addr if request else '127.0.0.1',
            'user_agent': getattr(request, 'user_agent', 'Unknown').string if request else 'Unknown',
            'path': getattr(request, 'path', '/')
        }
        
        visitors.append(visitor_data)
        if len(visitors) > 5000:
            visitors = visitors[-5000:]
        
        self._save_visitors(visitors)
    
    def get_visitor_count(self) -> int:
        """Get total visitor count (BACKWARD COMPATIBLE)."""
        return self.get_total_count()
    
    def get_today_visitors(self) -> int:
        """Get today's visitor count (BACKWARD COMPATIBLE)."""
        today = date.today()
        return sum(1 for v in self._load_visitors() 
                  if datetime.fromisoformat(v['timestamp']).date() == today)
    
    def get_total_count(self) -> int:
        """Total visits ever."""
        try:
            return len(self._load_visitors())
        except:
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Comprehensive statistics."""
        return {
            'total_visits': self.get_total_count(),
            'today_visits': self.get_today_visitors(),
            'last_updated': datetime.now().isoformat()
        }
    
    def _load_visitors(self) -> List[Dict]:
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_visitors(self, visitors: List[Dict]) -> None:
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(visitors, f, indent=2, ensure_ascii=False)

# BACKWARD COMPATIBILITY - Functions your app expects
tracker = VisitorTracker()

def log_visitor():
    """Function version for backward compatibility."""
    tracker.log_visitor()

def get_visitor_count():
    """Total count function."""
    return tracker.get_visitor_count()

def get_today_visitors():
    """Today's count function."""
    return tracker.get_today_visitors()

# Export for easy import
__all__ = ['log_visitor', 'get_visitor_count', 'get_today_visitors', 'VisitorTracker', 'tracker']

