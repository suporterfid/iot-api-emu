import paho.mqtt.client as mqtt
import threading
import time

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

def start_mqtt_thread(mqtt_config):
    threading.Thread(target=connect_mqtt, args=(mqtt_config,), daemon=True).start()
