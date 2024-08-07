from flask import Blueprint, jsonify

status_bp = Blueprint('status', __name__)

@status_bp.route('/api/v1/status', methods=['GET'])
def get_status():
    """
    Get the status of the reader.
    ---
    responses:
      200:
        description: Reader status
    """
    return jsonify({"status": "Reader is active and running"})
