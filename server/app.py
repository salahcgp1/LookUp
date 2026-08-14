#!/usr/bin/env python3
"""
Laptop Time Monitor - Server Application
Flask web server with API endpoints and dashboard.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import database as db
import os

app = Flask(__name__, static_folder='../dashboard', static_url_path='')
CORS(app)

# Initialize database on startup
db.init_db()

@app.route('/')
def dashboard():
    """Serve the main dashboard."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/usage', methods=['POST'])
def log_usage():
    """API endpoint to log usage data from client."""
    try:
        data = request.json
        
        if not data or 'user_id' not in data or 'application' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        db.log_usage(
            user_id=data['user_id'],
            timestamp=data.get('timestamp'),
            application=data['application'],
            is_active=data.get('is_active', True)
        )
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get list of all users."""
    try:
        users = db.get_all_users()
        return jsonify({'users': users}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usage/<user_id>', methods=['GET'])
def get_user_usage(user_id):
    """Get usage data for a specific user."""
    try:
        days = request.args.get('days', default=7, type=int)
        usage_data = db.get_usage_by_user(user_id, days)
        return jsonify({'usage': usage_data, 'days': days}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/activity', methods=['GET'])
def get_recent_activity():
    """Get recent activity across all users."""
    try:
        limit = request.args.get('limit', default=50, type=int)
        activity = db.get_recent_activity(limit)
        return jsonify({'activity': activity}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("Laptop Time Monitor - Server")
    print("=" * 50)
    print("Starting server on http://localhost:5000")
    print("Dashboard: http://localhost:5000")
    print("API Docs: http://localhost:5000/api/users")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
