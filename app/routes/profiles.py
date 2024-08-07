from flask import Blueprint, jsonify
from flask_restful import Api, Resource

profiles_bp = Blueprint('profiles', __name__)
api = Api(profiles_bp)

class Profiles(Resource):
    def get(self):
        """
        Get profiles.
        ---
        responses:
          200:
            description: List of profiles
        """
        return jsonify(["inventory", "location", "direction"])

class StopProfile(Resource):
    def post(self):
        """
        Stop a profile.
        ---
        responses:
          204:
            description: Profile stopped
        """
        return '', 204

api.add_resource(Profiles, '/api/v1/profiles')
api.add_resource(StopProfile, '/api/v1/profiles/stop')
