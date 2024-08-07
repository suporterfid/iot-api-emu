from flask import Flask, jsonify, request, Response
from flask_restful import Api, Resource
import time
import json
import random
import base64
import threading
import paho.mqtt.client as mqtt
import requests
import os

app = Flask(__name__)
api = Api(app)

SETTINGS_FILE = "settings.json"

class EPC:
    DefaultHeader = 0x35
    DefaultManager = 759936
    MaxHeader = 0xFF
    MaxManager = 0xFFFFFFF
    MaxClass = 0xFFFFFF
    MaxSerial = 0xFFFFFFFFF

    def __init__(self, header=None, manager=None, class_=None, serial=None):
        self.header = header if header is not None else self.DefaultHeader
        self.manager = manager if manager is not None else self.DefaultManager
        self.class_ = class_ if class_ is not None else random.randint(0, self.MaxClass)
        self.serial = serial if serial is not None else random.randint(0, self.MaxSerial)
    
    def hex(self):
        return f"{self.header:02X}{self.manager:07X}{self.class_:06X}{self.serial:09X}"

    def b64(self):
        hex_string = self.hex()
        binary_data = bytes.fromhex(hex_string)
        return base64.b64encode(binary_data).decode('utf-8')

class TagEvent:
    def __init__(self, epc):
        self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.hostname = "r700-emulator"
        self.eventType = "tagInventory"
        self.tagInventoryEvent = {
            "epc": epc.b64(),
            "epcHex": epc.hex(),
            "antennaPort": 1,
            "antennaName": "Antenna 1"
        }

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "hostname": self.hostname,
            "eventType": self.eventType,
            "tagInventoryEvent": self.tagInventoryEvent
        }

# Variables to control the streaming state and MQTT/Webhook configurations
streaming = False
mqtt_config = {}
webhook_config = {}
mqtt_client = mqtt.Client()

def load_settings():
    global mqtt_config, webhook_config
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
            mqtt_config = settings.get("mqtt_config", {})
            webhook_config = settings.get("webhook_config", {})
            print("Settings loaded from file")

def save_settings():
    with open(SETTINGS_FILE, 'w') as f:
        settings = {
            "mqtt_config": mqtt_config,
            "webhook_config": webhook_config
        }
        json.dump(settings, f)
        print("Settings saved to file")

# Load settings at startup
load_settings()

# MQTT functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        if 'connectMessage' in mqtt_config:
            mqtt_client.publish(mqtt_config.get('willTopic', ''), mqtt_config['connectMessage'], qos=mqtt_config.get('willQualityOfService', 0))
    else:
        print(f"Failed to connect to MQTT broker, return code {rc}")

def on_disconnect(client, userdata, rc):
    if 'disconnectMessage' in mqtt_config and mqtt_config['disconnectMessage']:
        mqtt_client.publish(mqtt_config.get('willTopic', ''), mqtt_config['disconnectMessage'], qos=mqtt_config.get('willQualityOfService', 0))

def on_publish(client, userdata, mid):
    print(f"Message {mid} published")

def connect_mqtt():
    global mqtt_client
    while mqtt_config.get('active', False):
        try:
            mqtt_client.connect(mqtt_config['brokerHostname'], mqtt_config.get('brokerPort', 1883), mqtt_config.get('keepAliveIntervalSeconds', 60))
            mqtt_client.loop_start()
            break
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")
            time.sleep(5)

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_publish = on_publish

# Webhook functions
def webhook_publisher():
    while True:
        if webhook_config.get('active', False):
            events = []
            linger_ms = webhook_config.get('eventBatchLingerMilliseconds', 1000)
            start_time = time.time()
            while time.time() - start_time < linger_ms / 1000.0:
                if not streaming and not events:
                    break
                if streaming:
                    epc = EPC()
                    event = TagEvent(epc)
                    events.append(event.to_dict())
                time.sleep(0.1)  # Slight delay to simulate event collection
            
            if not events and not streaming:
                events = []  # Send keepalive with empty list
            
            if events or not streaming:
                try:
                    url = webhook_config['serverConfiguration']['url']
                    auth = webhook_config['serverConfiguration']['authentication']
                    headers = {'Content-Type': 'application/json'}
                    verify_ssl = webhook_config['serverConfiguration'].get('tls', {}).get('verify', True)
                    response = requests.post(url, json=events, headers=headers, auth=(auth['username'], auth['password']), verify=verify_ssl)
                    if response.status_code == 200:
                        print("Events successfully sent to webhook")
                    else:
                        print(f"Failed to send events to webhook, status code: {response.status_code}, response: {response.text}")
                except Exception as e:
                    print(f"Error sending events to webhook: {e}")
        else:
            time.sleep(1)  # Sleep if webhook is not active

# Start the webhook publisher in a separate thread
threading.Thread(target=webhook_publisher, daemon=True).start()

# API endpoints
class DataStream(Resource):
    def get(self):
        def generate():
            while streaming:
                epc = EPC()
                event = TagEvent(epc)
                event_data = event.to_dict()
                yield f"data: {json.dumps(event_data)}\n\n"
                if mqtt_config.get('active', False):
                    mqtt_client.publish(mqtt_config.get('eventTopic', 'default/topic'), json.dumps(event_data), qos=mqtt_config.get('eventQualityOfService', 0))
                time.sleep(2)  # Simulate delay between events
                
        return Response(generate(), content_type='text/event-stream')

class StartStream(Resource):
    def post(self, preset_id):
        global streaming
        if preset_id == 'default':
            streaming = True
            return '', 204
        return '', 404

class StopStream(Resource):
    def post(self):
        global streaming
        streaming = False
        return '', 204

class MqttSettings(Resource):
    def get(self):
        return jsonify(mqtt_config)
    
    def put(self):
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
            threading.Thread(target=connect_mqtt).start()
        
        save_settings()
        return '', 204

class WebhookSettings(Resource):
    def get(self):
        return jsonify(webhook_config)
    
    def put(self):
        global webhook_config
        data = request.get_json()
        webhook_config = {key: value for key, value in data.items() if value is not None and value != ""}
        save_settings()
        return '', 204

class OpenAPIDocument(Resource):
    def get(self):
        return jsonify({"swagger": "2.0", "info": {"version": "1.8.0"}})

class Status(Resource):
    def get(self):
        return jsonify({"status": "Reader is active and running"})

class HttpStreamSettings(Resource):
    def get(self):
        return jsonify({"streamSettings": "Current HTTP stream settings"})
    
    def put(self):
        data = request.get_json()
        return '', 204

class KafkaSettings(Resource):
    def get(self):
        return jsonify({"kafkaSettings": "Current Kafka settings"})
    
    def put(self):
        data = request.get_json()
        return '', 204

class Profiles(Resource):
    def get(self):
        return jsonify(["inventory", "location", "direction"])

class StopProfile(Resource):
    def post(self):
        return '', 204

class EventWebhookConfiguration(Resource):
    def get(self):
        return jsonify(webhook_config)
    
    def put(self):
        global webhook_config
        data = request.get_json()
        webhook_config = {key: value for key, value in data.items() if value is not None and value != ""}
        save_settings()
        return '', 204

class SystemInfo(Resource):
    def get(self):
        return jsonify({"systemInfo": "Details about the reader hardware"})

class AuthenticationConfig(Resource):
    def get(self):
        return jsonify({"authConfig": "Current authentication configuration"})
    
    def put(self):
        data = request.get_json()
        return '', 204

class Users(Resource):
    def get(self):
        return jsonify([{"userId": 1, "username": "admin"}])

class UserPassword(Resource):
    def put(self, userId):
        data = request.get_json()
        return '', 204

class AntennaHubInfo(Resource):
    def get(self):
        return jsonify({"antennaHubInfo": "Current antenna hub status"})
    
class EnableAntennaHub(Resource):
    def post(self):
        return '', 202

class DisableAntennaHub(Resource):
    def post(self):
        return '', 202

class CaCertificates(Resource):
    def get(self):
        return jsonify([{"certId": 1, "certInfo": "CA Certificate info"}])
    
    def post(self):
        file = request.files['certFile']
        return jsonify([{"certId": 1}])

class CaCertificate(Resource):
    def get(self, certId):
        return jsonify({"certId": certId, "certInfo": "CA Certificate info"})
    
    def delete(self, certId):
        return '', 204

class TlsCertificates(Resource):
    def get(self):
        return jsonify([{"certId": 1, "certInfo": "TLS Certificate info"}])
    
    def post(self):
        file = request.files['certFile']
        password = request.form.get('password')
        return jsonify([{"certId": 1}])

class TlsCertificate(Resource):
    def get(self, certId):
        return jsonify({"certId": certId, "certInfo": "TLS Certificate info"})
    
    def delete(self, certId):
        return '', 204

# Add routes
api.add_resource(OpenAPIDocument, '/api/v1/openapi.json')
api.add_resource(DataStream, '/api/v1/data/stream')
api.add_resource(Status, '/api/v1/status')
api.add_resource(HttpStreamSettings, '/api/v1/http-stream')
api.add_resource(MqttSettings, '/api/v1/mqtt')
api.add_resource(WebhookSettings, '/api/v1/webhooks/event')
api.add_resource(KafkaSettings, '/api/v1/kafka')
api.add_resource(Profiles, '/api/v1/profiles')
api.add_resource(StopProfile, '/api/v1/profiles/stop')
api.add_resource(EventWebhookConfiguration, '/api/v1/webhooks/event')
api.add_resource(SystemInfo, '/api/v1/system')
api.add_resource(AuthenticationConfig, '/api/v1/system/access/authentication')
api.add_resource(Users, '/api/v1/system/access/users')
api.add_resource(UserPassword, '/api/v1/system/access/users/<int:userId>/password')
api.add_resource(AntennaHubInfo, '/api/v1/system/antenna-hub')
api.add_resource(EnableAntennaHub, '/api/v1/system/antenna-hub/enable')
api.add_resource(DisableAntennaHub, '/api/v1/system/antenna-hub/disable')
api.add_resource(CaCertificates, '/api/v1/system/certificates/ca/certs')
api.add_resource(CaCertificate, '/api/v1/system/certificates/ca/certs/<int:certId>')
api.add_resource(TlsCertificates, '/api/v1/system/certificates/tls/certs')
api.add_resource(TlsCertificate, '/api/v1/system/certificates/tls/certs/<int:certId>')
api.add_resource(StartStream, '/api/v1/profiles/inventory/presets/<string:preset_id>/start')
api.add_resource(StopStream, '/api/v1/profiles/stop')

if __name__ == '__main__':
    app.run(debug=True)
