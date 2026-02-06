import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, Any
from flask import request  # For Flask

class VisitorTracker:
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.log_file = os.path.join(data_dir, 'visitors.json')
        os.makedirs(data_dir, exist_ok=True)
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('CHAT_ID')

    def log_visitor(self):
        """Log current visitor with IP, user agent, timestamp."""
        visitor_data = {
            'timestamp': datetime.now().isoformat(),
            'ip': request.remote_addr if request else 'unknown',
            'user_agent': request.user_agent.string if request else 'unknown',
            'path': request.path if request else '/'
        }
        
        # Load existing data
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {'visits': [], 'total': 0}
        
        data['visits'].append(visitor_data)
        data['total'] += 1
        
        # Cleanup: Keep last 30 days
        cutoff = datetime.now() - timedelta(days=30)
        data['visits'] = [v for v in data['visits'] if datetime.fromisoformat(v['timestamp']) > cutoff]
        
        # Save back
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        self.send_telegram_alert(visitor_data)
        return data['total']

    def get_stats(self) -> Dict[str, Any]:
        """Get total visitors and today's count."""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            today = date.today().isoformat()
            today_count = len([v for v in data['visits'] 
                             if v['timestamp'].startswith(today)])
            return {'total': data['total'], 'today': today_count}
        except:
            return {'total': 0, 'today': 0}

    def send_telegram_alert(self, visitor_data):
        """Optional: Send alert to Telegram (if env vars set)."""
        if not self.telegram_token or not self.chat_id:
            return
        message = f"New visitor!\nIP: {visitor_data['ip']}\nUA: {visitor_data['user_agent'][:100]}...\nPath: {visitor_data['path']}"
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage?chat_id={self.chat_id}&text={message}"
        requests.get(url)  # Add import requests at top if needed

# Global instance
tracker = VisitorTracker()
