from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
from app.utils import save_settings, mqtt_config
from app.mqtt import start_mqtt_thread

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
        global mqtt_config, mqtt_client
        data = request.get_json()
        mqtt_config = {key: value for key, value in data.items() if value is not None and value != ""}
        
        # Apply MQTT configuration
        mqtt_client = mqtt.Client(client_id=mqtt_config.get('clientId', ''), clean_session=mqtt_config.get('cleanSession', True))
        
        if mqtt_config.get('username'):
            mqtt_client.username_pw_set(mqtt_config['username'], mqtt_config.get('password', ''))
        
        if mqtt_config.get('tlsEnabled', False):
            mqtt_client.tls_set()
        
        if 'willMessage' in mqtt_config and 'willTopic' in mqtt_config:
            mqtt_client.will_set(mqtt_config['willTopic'], mqtt_config['willMessage'], qos=mqtt_config.get('willQualityOfService', 0))
        
        if mqtt_config.get('active', False):
            start_mqtt_thread(mqtt_config)
        
        save_settings()
        return '', 204

api.add_resource(MqttSettings, '/api/v1/mqtt')
