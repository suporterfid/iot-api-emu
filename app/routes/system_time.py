from flask import Blueprint, jsonify
from datetime import datetime
import app.config as config

system_time_bp = Blueprint('system_time', __name__)

@system_time_bp.route('/api/v1/system/time', methods=['GET'])
def get_system_time():
    # Get current system time in UTC and RFC-3339 compliant format
    system_time = datetime.utcnow().isoformat() + 'Z'
    
    # Calculate uptime in seconds
    up_time = (datetime.utcnow() - config.system_start_time).total_seconds()
    
    # Construct the response
    response = {
        "systemTime": system_time,
        "upTime": int(up_time)
    }
    
    return jsonify(response)
