"""
==========================================
THE GRANITO PORTFOLIO - VISITOR TRACKING
Version: 2.0
==========================================
"""

import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# File paths
VISITORS_FILE = "data/visitors.json"


# ==================== DATA PERSISTENCE ====================

def load_visitors():
    """Load visitors data from JSON file"""
    if not os.path.exists(VISITORS_FILE):
        return []
    
    try:
        with open(VISITORS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in visitors file")
        return []
    except Exception as e:
        logger.error(f"Error loading visitors: {e}")
        return []


def save_visitors(visitors):
    """Save visitors data to JSON file"""
    try:
        os.makedirs(os.path.dirname(VISITORS_FILE), exist_ok=True)
        with open(VISITORS_FILE, 'w', encoding='utf-8') as f:
            json.dump(visitors, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving visitors: {e}")
        return False


# ==================== VISITOR TRACKING ====================

def track_visitor(ip_address, user_agent, page="/"):
    """
    Track a visitor
    
    Args:
        ip_address (str): Visitor's IP address
        user_agent (str): Visitor's user agent string
        page (str): Page visited
    
    Returns:
        bool: True if tracked successfully
    """
    try:
        visitors = load_visitors()
        
        # Create visitor record
        visitor_data = {
            "ip": ip_address,
            "user_agent": user_agent,
            "page": page,
            "timestamp": datetime.utcnow().isoformat(),
            "date": datetime.utcnow().date().isoformat()
        }
        
        visitors.append(visitor_data)
        
        # Keep only last 10,000 visitors to prevent file from getting too large
        if len(visitors) > 10000:
            visitors = visitors[-10000:]
        
        return save_visitors(visitors)
        
    except Exception as e:
        logger.error(f"Error tracking visitor: {e}")
        return False


# ==================== STATISTICS ====================

def get_visitor_stats():
    """
    Get visitor statistics
    
    Returns:
        dict: Statistics including total, today, this week, this month
    """
    try:
        visitors = load_visitors()
        
        if not visitors:
            return {
                'total': 0,
                'today': 0,
                'this_week': 0,
                'this_month': 0,
                'unique_ips': 0,
                'pages': {},
                'recent': []
            }
        
        now = datetime.utcnow()
        today = now.date()
        week_ago = (now - timedelta(days=7)).date()
        month_ago = (now - timedelta(days=30)).date()
        
        # Calculate stats
        total = len(visitors)
        today_count = 0
        week_count = 0
        month_count = 0
        unique_ips = set()
        page_counts = defaultdict(int)
        
        for visitor in visitors:
            try:
                visitor_date = datetime.fromisoformat(visitor['date']).date()
                
                unique_ips.add(visitor['ip'])
                page_counts[visitor.get('page', '/')] += 1
                
                if visitor_date == today:
                    today_count += 1
                
                if visitor_date >= week_ago:
                    week_count += 1
                
                if visitor_date >= month_ago:
                    month_count += 1
                    
            except (KeyError, ValueError) as e:
                logger.warning(f"Invalid visitor record: {e}")
                continue
        
        # Get recent visitors
        recent = visitors[-10:][::-1]  # Last 10, most recent first
        
        return {
            'total': total,
            'today': today_count,
            'this_week': week_count,
            'this_month': month_count,
            'unique_ips': len(unique_ips),
            'pages': dict(page_counts),
            'recent': recent
        }
        
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        return {
            'total': 0,
            'today': 0,
            'this_week': 0,
            'this_month': 0,
            'unique_ips': 0,
            'pages': {},
            'recent': []
        }


def get_daily_stats(days=30):
    """
    Get daily visitor statistics for the last N days
    
    Args:
        days (int): Number of days to include
    
    Returns:
        dict: Daily visitor counts
    """
    try:
        visitors = load_visitors()
        
        if not visitors:
            return {}
        
        now = datetime.utcnow()
        start_date = (now - timedelta(days=days)).date()
        
        daily_counts = defaultdict(int)
        
        for visitor in visitors:
            try:
                visitor_date = datetime.fromisoformat(visitor['date']).date()
                
                if visitor_date >= start_date:
                    daily_counts[visitor_date.isoformat()] += 1
                    
            except (KeyError, ValueError):
                continue
        
        return dict(daily_counts)
        
    except Exception as e:
        logger.error(f"Error calculating daily stats: {e}")
        return {}


def get_page_stats():
    """
    Get statistics per page
    
    Returns:
        dict: Page visit counts
    """
    try:
        visitors = load_visitors()
        
        page_counts = defaultdict(int)
        
        for visitor in visitors:
            page = visitor.get('page', '/')
            page_counts[page] += 1
        
        # Sort by count (descending)
        sorted_pages = dict(sorted(
            page_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        return sorted_pages
        
    except Exception as e:
        logger.error(f"Error calculating page stats: {e}")
        return {}


def get_hourly_distribution():
    """
    Get visitor distribution by hour of day
    
    Returns:
        dict: Visitor counts per hour (0-23)
    """
    try:
        visitors = load_visitors()
        
        hourly_counts = defaultdict(int)
        
        for visitor in visitors:
            try:
                timestamp = datetime.fromisoformat(visitor['timestamp'])
                hour = timestamp.hour
                hourly_counts[hour] += 1
            except (KeyError, ValueError):
                continue
        
        # Ensure all hours are present
        for hour in range(24):
            if hour not in hourly_counts:
                hourly_counts[hour] = 0
        
        return dict(sorted(hourly_counts.items()))
        
    except Exception as e:
        logger.error(f"Error calculating hourly distribution: {e}")
        return {}


# ==================== CLEANUP ====================

def cleanup_old_visitors(days=90):
    """
    Remove visitor records older than specified days
    
    Args:
        days (int): Number of days to keep
    
    Returns:
        int: Number of records removed
    """
    try:
        visitors = load_visitors()
        
        if not visitors:
            return 0
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).date()
        
        original_count = len(visitors)
        
        # Keep only recent visitors
        visitors = [
            v for v in visitors
            if datetime.fromisoformat(v['date']).date() >= cutoff_date
        ]
        
        save_visitors(visitors)
        
        removed = original_count - len(visitors)
        logger.info(f"Cleaned up {removed} old visitor records")
        
        return removed
        
    except Exception as e:
        logger.error(f"Error cleaning up visitors: {e}")
        return 0


# ==================== EXPORT ====================

def export_visitors_csv(filepath="exports/visitors.csv"):
    """
    Export visitors data to CSV file
    
    Args:
        filepath (str): Path to export file
    
    Returns:
        bool: True if successful
    """
    try:
        import csv
        
        visitors = load_visitors()
        
        if not visitors:
            return False
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['ip', 'user_agent', 'page', 'timestamp', 'date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for visitor in visitors:
                writer.writerow(visitor)
        
        logger.info(f"Exported {len(visitors)} visitor records to {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting visitors: {e}")
        return False


# ==================== ADMIN FUNCTIONS ====================

def get_unique_visitors(days=7):
    """
    Get unique visitor count for the last N days
    
    Args:
        days (int): Number of days to check
    
    Returns:
        int: Number of unique visitors
    """
    try:
        visitors = load_visitors()
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).date()
        unique_ips = set()
        
        for visitor in visitors:
            try:
                visitor_date = datetime.fromisoformat(visitor['date']).date()
                if visitor_date >= cutoff_date:
                    unique_ips.add(visitor['ip'])
            except (KeyError, ValueError):
                continue
        
        return len(unique_ips)
        
    except Exception as e:
        logger.error(f"Error calculating unique visitors: {e}")
        return 0


def get_top_pages(limit=10):
    """
    Get most visited pages
    
    Args:
        limit (int): Number of pages to return
    
    Returns:
        list: List of (page, count) tuples
    """
    try:
        page_stats = get_page_stats()
        return list(page_stats.items())[:limit]
    except Exception as e:
        logger.error(f"Error getting top pages: {e}")
        return []
