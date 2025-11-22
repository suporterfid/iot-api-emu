import requests
import json

# Send device-to-cloud message to Azure IoT Hub using HTTPS REST API
def send_iothub_message_http(mqtt_config, payload):
    # Build URL and headers from config
    url = f"https://{mqtt_config['brokerHostname']}/devices/{mqtt_config['clientId']}/messages/events?api-version=2021-04-12"
    headers = {
        'Authorization': mqtt_config['password'],
        'iothub-to': f"/devices/{mqtt_config['clientId']}/messages/events",
        'Content-Type': 'application/json',
    }
    print(f"[HTTP] Sending message to {url} with payload: {payload}")
    response = requests.post(url, headers=headers, data=json.dumps(payload), verify=True)
    print(f"[HTTP] API response: {response.status_code} {response.text}")
    return response
import paho.mqtt.client as mqtt
import threading
import time
import ssl

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] Connected to MQTT broker")
        # Publish a test message to the event topic after connecting
        if hasattr(client, 'event_topic'):
            test_topic = client.event_topic
        else:
            test_topic = getattr(userdata, 'event_topic', None) if userdata else None
        if not test_topic and hasattr(userdata, 'get'):
            test_topic = userdata.get('eventTopic', 'test/topic')
        test_payload = '{"message": "Test from IoT API Emulator"}'
        if test_topic:
            print(f"[MQTT] Publishing test message to topic: {test_topic}")
            result = client.publish(test_topic, test_payload)
            print(f"[MQTT] Publish result: {result}")
        else:
            print("[MQTT] No event topic specified, not publishing test message.")
    else:
        print(f"[MQTT] Failed to connect to MQTT broker, return code {rc}")
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("[MQTT] Connected to MQTT broker")
            # Instead of MQTT, send message via HTTP API using actual request body
            if hasattr(client, 'mqtt_config') and hasattr(client, 'last_payload'):
                send_iothub_message_http(client.mqtt_config, client.last_payload)
            else:
                print("[HTTP] No payload or config found for HTTP send.")
        else:
            print(f"[MQTT] Failed to connect to MQTT broker, return code {rc}")

def on_disconnect(client, userdata, rc):
    print(f"[MQTT] Disconnected from MQTT broker, rc={rc}")

def on_publish(client, userdata, mid):
    print(f"[MQTT] Message {mid} published")

def connect_mqtt(mqtt_config):
    global mqtt_client
    
    # Configure TLS if enabled
    if mqtt_config.get('tlsEnabled', False):
        # Always use Baltimore CyberTrust Root for Azure IoT Hub
        # Use absolute path for Docker
        tls_cafile = mqtt_config.get('tlsCafile', '/app/baltimore_cybertrust_root.pem')
        tls_certfile = mqtt_config.get('tlsCertfile', None)  # Client certificate
        tls_keyfile = mqtt_config.get('tlsKeyfile', None)    # Client private key
        tls_insecure = mqtt_config.get('tlsInsecure', False) # Whether to bypass the server certificate verification

        # Set up TLS/SSL
        mqtt_client.tls_set(
            ca_certs=tls_cafile,
            certfile=tls_certfile,
            keyfile=tls_keyfile,
            cert_reqs=ssl.CERT_NONE if tls_insecure else ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS,
            ciphers=None
        )
        # Allow unsecure or self-signed certificates
        mqtt_client.tls_insecure_set(tls_insecure)
    
    # Set username and password if provided
    if mqtt_config.get('username'):
        mqtt_client.username_pw_set(mqtt_config['username'], mqtt_config.get('password', ''))
    
    # Attach the event topic to the client for use in on_connect
    mqtt_client.event_topic = mqtt_config.get('eventTopic', 'test/topic')
    # Connect to the MQTT broker
    while mqtt_config.get('active', False):
        try:
            broker_port = mqtt_config.get('brokerPort', 8883 if mqtt_config.get('tlsEnabled', False) else 1883)
            print(f"[MQTT] Connecting to {mqtt_config['brokerHostname']}:{broker_port} as {mqtt_config.get('clientId', '')}")
            mqtt_client.connect(mqtt_config['brokerHostname'], broker_port, mqtt_config.get('keepAliveIntervalSeconds', 60))
            mqtt_client.loop_start()
            break
        except Exception as e:
            print(f"[MQTT] Error connecting to MQTT broker: {e}")
            time.sleep(5)
        # Azure IoT Hub MQTT strict requirements
        tls_cafile = '/app/baltimore_cybertrust_root.pem'
        mqtt_client.tls_set(
            ca_certs=tls_cafile,
            certfile=None,
            keyfile=None,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS,
            ciphers=None
        )
        # Do NOT set tls_insecure_set(True) for Azure

        # Set username and password (SAS token)
        if mqtt_config.get('username'):
            mqtt_client.username_pw_set(mqtt_config['username'], mqtt_config.get('password', ''))

        # Enforce correct topic and clientId for Azure
        event_topic = f"devices/{mqtt_config.get('clientId','')}/messages/events/"
        mqtt_client.event_topic = event_topic

        # Connect to the MQTT broker
        while mqtt_config.get('active', False):
            try:
                broker_port = 8883
                print(f"[MQTT] Connecting to {mqtt_config['brokerHostname']}:{broker_port} as {mqtt_config.get('clientId', '')}")
                mqtt_client.connect(mqtt_config['brokerHostname'], broker_port, mqtt_config.get('keepAliveIntervalSeconds', 60))
                mqtt_client.loop_start()
                break
            except Exception as e:
                print(f"[MQTT] Error connecting to MQTT broker: {e}")
                time.sleep(5)

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_publish = on_publish

def start_mqtt_thread(mqtt_config):
    threading.Thread(target=connect_mqtt, args=(mqtt_config,), daemon=True).start()
