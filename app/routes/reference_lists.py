from flask import Blueprint, jsonify, request, abort
from flask_restful import Api, Resource
import os

reference_lists_bp = Blueprint('reference_lists', __name__)
api = Api(reference_lists_bp)

REFERENCE_LIST_FILE = "reference-list.txt"
REFERENCE_LIST_UNIQUE_FILE = "reference-list-unique.txt"

def read_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            return [line.strip() for line in f.readlines()]
    return []

def write_file(file_name, content):
    with open(file_name, 'w') as f:
        f.write("\n".join(content) + "\n")

def append_to_file(file_name, content):
    with open(file_name, 'a') as f:
        f.write("\n".join(content) + "\n")

def delete_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)

class ReferenceList(Resource):
    def get(self, list_type):
        """
        Query the content of a reference list.
        ---
        tags:
          - Reference List Management
        parameters:
          - in: path
            name: list_type
            type: string
            enum: [default, unique]
            required: true
            description: The type of the reference list (default or unique).
        responses:
          200:
            description: The content of the reference list.
            schema:
              type: array
              items:
                type: string
          400:
            description: Invalid list type.
        """
        file_name = REFERENCE_LIST_FILE if list_type == "default" else REFERENCE_LIST_UNIQUE_FILE
        return jsonify(read_file(file_name))

    def post(self, list_type):
        """
        Create or update a reference list.
        ---
        tags:
          - Reference List Management
        parameters:
          - in: path
            name: list_type
            type: string
            enum: [default, unique]
            required: true
            description: The type of the reference list (default or unique).
          - in: body
            name: body
            schema:
              type: array
              items:
                type: string
            required: true
            description: The list of EPCs to create or update the reference list with.
        responses:
          204:
            description: The reference list was created or updated successfully.
          400:
            description: Invalid input format or list type.
        """
        file_name = REFERENCE_LIST_FILE if list_type == "default" else REFERENCE_LIST_UNIQUE_FILE
        data = request.get_json()

        if not data or not isinstance(data, list):
            abort(400, description="Invalid data format. Expected a list of EPCs.")

        write_file(file_name, data)
        return '', 204

    def put(self, list_type):
        """
        Append EPCs to a reference list.
        ---
        tags:
          - Reference List Management
        parameters:
          - in: path
            name: list_type
            type: string
            enum: [default, unique]
            required: true
            description: The type of the reference list (default or unique).
          - in: body
            name: body
            schema:
              type: array
              items:
                type: string
            required: true
            description: The list of EPCs to append to the reference list.
        responses:
          204:
            description: The EPCs were appended to the reference list successfully.
          400:
            description: Invalid input format or list type.
        """
        file_name = REFERENCE_LIST_FILE if list_type == "default" else REFERENCE_LIST_UNIQUE_FILE
        data = request.get_json()

        if not data or not isinstance(data, list):
            abort(400, description="Invalid data format. Expected a list of EPCs.")

        append_to_file(file_name, data)
        return '', 204

    def delete(self, list_type):
        """
        Delete a reference list.
        ---
        tags:
          - Reference List Management
        parameters:
          - in: path
            name: list_type
            type: string
            enum: [default, unique]
            required: true
            description: The type of the reference list to delete (default or unique).
        responses:
          204:
            description: The reference list was deleted successfully.
          400:
            description: Invalid list type.
        """
        file_name = REFERENCE_LIST_FILE if list_type == "default" else REFERENCE_LIST_UNIQUE_FILE
        delete_file(file_name)
        return '', 204

api.add_resource(ReferenceList, '/ref-lists/<string:list_type>')
