from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
from app.utils import save_settings, webhook_config

webhook_settings_bp = Blueprint('webhook_settings', __name__)
api = Api(webhook_settings_bp)

class WebhookSettings(Resource):
    def get(self):
        """
        Get Webhook settings.
        ---
        responses:
          200:
            description: Webhook settings
        """
        return jsonify(webhook_config)
    
    def put(self):
        """
        Update Webhook settings.
        ---
        parameters:
          - in: body
            name: body
            schema:
              type: object
              properties:
                active:
                  type: boolean
                eventBatchLimit:
                  type: integer
                eventBatchLingerMilliseconds:
                  type: integer
                eventBufferSize:
                  type: integer
                retry:
                  type: object
                serverConfiguration:
                  type: object
                  properties:
                    url:
                      type: string
                    authentication:
                      type: object
                      properties:
                        password:
                          type: string
                        username:
                          type: string
                    port:
                      type: integer
                    tls:
                      type: object
        responses:
          204:
            description: Webhook settings updated
        """
        global webhook_config
        data = request.get_json()
        webhook_config = {key: value for key, value in data.items() if value is not None and value != ""}
        save_settings()
        return '', 204

api.add_resource(WebhookSettings, '/api/v1/webhooks/event')
