
from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
from app.utils import save_settings, mqtt_config
from app.mqtt import start_mqtt_thread
import paho.mqtt.client as mqtt

mqtt_settings_bp = Blueprint('mqtt_settings', __name__)
api = Api(mqtt_settings_bp)

class MqttSettings(Resource):
    def get(self):
        """
        Get MQTT settings.
        ---
        responses:
          200:
            description: MQTT settings
        """
        return jsonify(mqtt_config)
    
    def put(self):
        """
        Update MQTT settings.
        ---
        parameters:
          - in: body
            name: body
            schema:
              type: object
              properties:
                brokerHostname:
                  type: string
                clientId:
                  type: string
                eventTopic:
                  type: string
                active:
                  type: boolean
                brokerPort:
                  type: integer
                cleanSession:
                  type: boolean
                connectMessage:
                  type: string
                disconnectMessage:
                  type: string
                eventBufferSize:
                  type: integer
                eventPendingDeliveryLimit:
                  type: integer
                eventPerSecondLimit:
                  type: integer
                eventQualityOfService:
                  type: integer
                keepAliveIntervalSeconds:
                  type: integer
                password:
                  type: string
                tlsEnabled:
                  type: boolean
                username:
                  type: string
                willMessage:
                  type: string
                willQualityOfService:
                  type: integer
                willTopic:
                  type: string
        responses:
          204:
            description: MQTT settings updated
        """
        global mqtt_config
        data = request.get_json()
        # Always update mqtt_config with all keys from the request
        mqtt_config.clear()
        mqtt_config.update(data)
        save_settings()
        return '', 204

api.add_resource(MqttSettings, '/api/v1/mqtt')
