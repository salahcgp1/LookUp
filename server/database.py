"""
Database operations for Laptop Time Monitor
"""

import sqlite3
from datetime import datetime, timedelta

DB_PATH = "usage.db"

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            application TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_user_timestamp 
        ON usage_logs(user_id, timestamp)
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def log_usage(user_id, timestamp, application, is_active=True):
    """Log usage data to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO usage_logs (user_id, timestamp, application, is_active)
        VALUES (?, ?, ?, ?)
    ''', (user_id, timestamp, application, is_active))
    
    conn.commit()
    conn.close()

def get_usage_by_user(user_id, days=7):
    """Get usage data for a specific user for the last N days."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    start_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    cursor.execute('''
        SELECT application, COUNT(*) as time_blocks, 
               MIN(timestamp) as first_seen, MAX(timestamp) as last_seen
        FROM usage_logs
        WHERE user_id = ? AND timestamp >= ?
        GROUP BY application
        ORDER BY time_blocks DESC
    ''', (user_id, start_date))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'application': row[0],
            'time_blocks': row[1],
            'first_seen': row[2],
            'last_seen': row[3]
        }
        for row in results
    ]

def get_all_users():
    """Get list of all users."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT user_id FROM usage_logs
        ORDER BY user_id
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    return [row[0] for row in results]

def get_recent_activity(limit=50):
    """Get recent activity across all users."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, application, timestamp
        FROM usage_logs
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'user_id': row[0],
            'application': row[1],
            'timestamp': row[2]
        }
        for row in results
    ]
