# utils.py - TheGranito Visitor Tracker with Telegram
import json, os, requests
from datetime import datetime, date
from flask import request

class VisitorTracker:
    def __init__(self):
        self.data_dir = 'data'
        self.log_file = os.path.join(self.data_dir, 'visitors.json')
        os.makedirs(self.data_dir, exist_ok=True)
        self.telegram_token = os.getenv(8184363319:AAHjMm5xKmv99n4L0ODmBjYmNTkcK4t98dE)
        self.chat_id = os.getenv(5891930140)
    
    def log_visitor(self):
        ua = request.headers.get('User-Agent', 'Unknown')
        device = 'Mobile' if any(x in ua.lower() for x in ['mobile', 'android', 'iphone', 'ipad']) else 'Desktop'
        
        visitor = {
            'time': datetime.now().isoformat(),
            'ip': request.remote_addr or 'Unknown',
            'device': device,
            'browser': ua[:100],
            'page': request.path,
            'referrer': request.referrer or 'Direct'
        }
        
        visitors = self._load()
        visitors.append(visitor)
        if len(visitors) > 1000: visitors = visitors[-1000:]
        self._save(visitors)
        
        # Telegram alert (sirf new visitor)
        if self.telegram_token and self.chat_id and self._is_new_today(visitor['ip']):
            self.send_telegram(visitor)
    
    def send_telegram(self, visitor):
        msg = f"""🚀 NEW VISITOR on THEGRANITO!

👤 **Uttam Kumar Portfolio**
📱 **{visitor['device']}**
🌐 **IP:** `{visitor['ip']}`
📱 **Browser:** {visitor['browser'][:50]}...
📄 **Page:** {visitor['page']}
🔗 **From:** {visitor['referrer'][:50]}
⏰ **Time:** {visitor['time'][:19]}

👥 **Total:** {len(self._load())}"""
        
        url = f"https://api.telegram.org/bot8184363319:AAHjMm5xKmv99n4L0ODmBjYmNTkcK4t98dE/sendMessage"
        try:
            requests.post(url, data={'chat_id': self.chat_id, 'text': msg, 'parse_mode': 'Markdown'})
        except:
            pass  # Silent fail
    
    def get_stats(self):
        visitors = self._load()
        today = sum(1 for v in visitors if v['time'][:10] == str(date.today()))
        return {'total_visitors': len(visitors), 'today': today}
    
    def _load(self):
        try:
            with open(self.log_file, 'r') as f: return json.load(f)
        except: return []
    
    def _save(self, data):
        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _is_new_today(self, ip):
        today_str = str(date.today())
        return not any(v['ip'] == ip and v['time'][:10] == today_str for v in self._load())

# Global instance
tracker = VisitorTracker()

def log_visitor(): tracker.log_visitor()
def get_stats(): return tracker.get_stats()
