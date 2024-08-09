import paho.mqtt.client as mqtt
import threading
import time
import ssl

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print(f"Failed to connect to MQTT broker, return code {rc}")

def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT broker")

def on_publish(client, userdata, mid):
    print(f"Message {mid} published")

def connect_mqtt(mqtt_config):
    global mqtt_client
    
    # Configure TLS if enabled
    if mqtt_config.get('tlsEnabled', False):
        tls_certfile = mqtt_config.get('tlsCertfile', None)  # Client certificate
        tls_keyfile = mqtt_config.get('tlsKeyfile', None)    # Client private key
        tls_cafile = mqtt_config.get('tlsCafile', None)      # CA certificate
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
    
    # Connect to the MQTT broker
    while mqtt_config.get('active', False):
        try:
            broker_port = mqtt_config.get('brokerPort', 8883 if mqtt_config.get('tlsEnabled', False) else 1883)
            mqtt_client.connect(mqtt_config['brokerHostname'], broker_port, mqtt_config.get('keepAliveIntervalSeconds', 60))
            mqtt_client.loop_start()
            break
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")
            time.sleep(5)

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_publish = on_publish

def start_mqtt_thread(mqtt_config):
    threading.Thread(target=connect_mqtt, args=(mqtt_config,), daemon=True).start()
