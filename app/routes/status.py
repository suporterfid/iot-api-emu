from flask import Blueprint, jsonify
from datetime import datetime
from app.mqtt import mqtt_client
import app.config as config
from app.utils import streaming, mqtt_config, webhook_config, last_http_status, last_http_timestamp

status_bp = Blueprint('status', __name__)

SERIAL_NUMBER = "370-17-16-0022"

@status_bp.route('/api/v1/status', methods=['GET'])
def get_status():
    """
    Get the status of the reader.
    ---
    responses:
      200:
        description: Reader status
    """
    current_time = datetime.utcnow().isoformat() + 'Z'
    
    print(f"streaming {config.streaming}") 

     # Determine stream status
    stream_status = "running" if config.streaming else "idle"
    
    # Determine MQTT connection status
    mqtt_status = "connected" if mqtt_client.is_connected() else "disconnected"
    
    # Determine Webhook status
    webhook_status = {
        "status": "enabled" if webhook_config.get('active', False) else "disabled",
        "httpStatusCode": last_http_status,
        "timestamp": last_http_timestamp or current_time
    }
    
    # Construct the response
    response = {
        "status": stream_status,
        "time": current_time,
        "serialNumber": SERIAL_NUMBER,
        "mqttBrokerConnectionStatus": mqtt_status,
        "eventWebhookStatus": webhook_status
    }
    
    return jsonify(response)
