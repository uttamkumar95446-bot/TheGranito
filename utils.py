import json
import os
from datetime import datetime

def log_visitor():
    """Log website visitors"""
    log_file = 'data/visitors.json'
    os.makedirs('data', exist_ok=True)
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            visitors = json.load(f)
    except:
        visitors = []
    
    visitor_data = {
        'timestamp': datetime.now().isoformat(),
        'ip': '127.0.0.1',  # Limited in mobile environment
        'user_agent': 'Pydroid3-Browser'
    }
    
    visitors.append(visitor_data)
    
    # Keep only last 1000 visitors
    if len(visitors) > 1000:
        visitors = visitors[-1000:]
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(visitors, f, indent=2, ensure_ascii=False)

def get_visitor_count():
    """Get total visitor count"""
    try:
        with open('data/visitors.json', 'r', encoding='utf-8') as f:
            visitors = json.load(f)
        return len(visitors)
    except:
        return 0

def get_today_visitors():
    """Get today's visitor count"""
    try:
        with open('data/visitors.json', 'r', encoding='utf-8') as f:
            visitors = json.load(f)
        
        today = datetime.now().date()
        today_count = 0
        
        for visitor in visitors:
            visitor_date = datetime.fromisoformat(visitor['timestamp']).date()
            if visitor_date == today:
                today_count += 1
        
        return today_count
    except:
        return 0

def clean_old_data():
    """Clean old visitor data (older than 30 days)"""
    try:
        with open('data/visitors.json', 'r', encoding='utf-8') as f:
            visitors = json.load(f)
        
        cutoff_date = datetime.now().timestamp() - (30 * 24 * 60 * 60)  # 30 days ago
        
        filtered_visitors = []
        for visitor in visitors:
            visitor_timestamp = datetime.fromisoformat(visitor['timestamp']).timestamp()
            if visitor_timestamp > cutoff_date:
                filtered_visitors.append(visitor)
        
        with open('data/visitors.json', 'w', encoding='utf-8') as f:
            json.dump(filtered_visitors, f, indent=2, ensure_ascii=False)
        
        return len(visitors) - len(filtered_visitors)
    except:
        return 0
