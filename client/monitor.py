#!/usr/bin/env python3
"""
Laptop Time Monitor - Client Script
Monitors active applications and screen time, sends data to server.
"""

import psutil
import requests
import time
import json
from datetime import datetime

# Configuration
SERVER_URL = "http://localhost:5000"
USER_ID = "daughter1"  # Change this for each user
CHECK_INTERVAL = 30  # seconds

def get_active_window():
    """Get the currently active window/application."""
    try:
        # Get the process with highest CPU usage as a proxy for active app
        # In production, you'd use platform-specific APIs
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu': proc.info['cpu_percent'] or 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage and get top process
        processes.sort(key=lambda x: x['cpu'], reverse=True)
        if processes:
            return processes[0]['name']
        return "Unknown"
    except Exception as e:
        print(f"Error getting active window: {e}")
        return "Unknown"

def get_screen_status():
    """Check if screen is active (simplified version)."""
    try:
        # Check system idle time
        return True  # Simplified - always active
    except:
        return False

def send_usage_data(app_name, is_active):
    """Send usage data to the server."""
    try:
        data = {
            'user_id': USER_ID,
            'timestamp': datetime.now().isoformat(),
            'application': app_name,
            'is_active': is_active
        }
        
        response = requests.post(
            f"{SERVER_URL}/api/usage",
            json=data,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Logged: {app_name}")
        else:
            print(f"Server error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("Cannot connect to server. Is it running?")
    except Exception as e:
        print(f"Error sending data: {e}")

def main():
    """Main monitoring loop."""
    print("=" * 50)
    print("Laptop Time Monitor - Client")
    print("=" * 50)
    print(f"User ID: {USER_ID}")
    print(f"Server: {SERVER_URL}")
    print(f"Check Interval: {CHECK_INTERVAL}s")
    print("=" * 50)
    print("Monitoring started... (Press Ctrl+C to stop)")
    print()
    
    last_app = None
    
    while True:
        try:
            current_app = get_active_window()
            is_active = get_screen_status()
            
            # Only send if app changed or every 5 intervals
            if current_app != last_app:
                send_usage_data(current_app, is_active)
                last_app = current_app
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
