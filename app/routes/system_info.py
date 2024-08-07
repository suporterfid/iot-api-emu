from flask import Blueprint, jsonify

system_info_bp = Blueprint('system_info', __name__)

@system_info_bp.route('/api/v1/system', methods=['GET'])
def get_system_info():
    """
    Get system information.
    ---
    responses:
      200:
        description: System information
    """
    return jsonify({"systemInfo": "Details about the reader hardware"})
