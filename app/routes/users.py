from flask import Blueprint, jsonify, request

users_bp = Blueprint('users', __name__)

@users_bp.route('/api/v1/system/access/users', methods=['GET'])
def get_users():
    """
    Get users.
    ---
    responses:
      200:
        description: List of users
    """
    return jsonify([{"userId": 1, "username": "admin"}])

@users_bp.route('/api/v1/system/access/users/<int:userId>/password', methods=['PUT'])
def update_user_password(userId):
    """
    Update user password.
    ---
    parameters:
      - in: path
        name: userId
        required: true
        type: integer
    responses:
      204:
        description: User password updated
    """
    data = request.get_json()
    # Process data as needed
    return '', 204
