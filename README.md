# IoT Device Interface API Emulator

This project emulates an IoT device interface API with support for MQTT and Webhook publishers. The emulator can stream tag events and publish them to configured MQTT brokers and HTTP servers.

## Features

- Emulate tag event streaming
- Publish events to MQTT brokers
- Publish events to HTTP servers via Webhooks

## Setup Development Environment

### Prerequisites

- Python 3.x
- Git

### Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/suporterfid/iot-dev-if-emu.git
    cd iot-dev-if-emu
    ```

2. **Create and activate a virtual environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Run the Flask application**:
    ```sh
    python app.py
    ```

## API Endpoints

**Start Stream**

Start streaming tag events.

```sh
curl -X POST http://127.0.0.1:5000/api/v1/profiles/inventory/presets/default/start
```

**Stop Stream**

Stop streaming tag events.

```sh
curl -X POST http://127.0.0.1:5000/api/v1/profiles/stop
```

**Get Data Stream**

Get the streamed tag events.

```sh
curl http://127.0.0.1:5000/api/v1/data/stream
```

**Expected Output**
```json
data: {"timestamp": "2024-08-06T12:00:00Z", "hostname": "r700-emulator", "eventType": "tagInventory", "tagInventoryEvent": {"epc": "2U3T7XY4z5tHhbvN", "epcHex": "3500B6D9801234567890ABCDEF", "antennaPort": 1, "antennaName": "Antenna 1"}}
data: {"timestamp": "2024-08-06T12:00:02Z", "hostname": "r700-emulator", "eventType": "tagInventory", "tagInventoryEvent": {"epc": "1B6M3HjA9z7Yp5tD", "epcHex": "3500B6D9800987654321FEDCBA", "antennaPort": 1, "antennaName": "Antenna 1"}}
```

**Configure MQTT Settings**

Configure MQTT publisher settings.

```sh
curl -X PUT http://127.0.0.1:5000/api/v1/mqtt -H "Content-Type: application/json" -d '{
    "brokerHostname": "mqtt.example.com",
    "clientId": "Nq4PfQD",
    "eventTopic": "l",
    "active": true,
    "brokerPort": 1883,
    "cleanSession": false,
    "connectMessage": "connected",
    "disconnectMessage": "",
    "eventBufferSize": 100000,
    "eventPendingDeliveryLimit": 10,
    "eventPerSecondLimit": 0,
    "eventQualityOfService": 0,
    "keepAliveIntervalSeconds": 60,
    "password": "",
    "tlsEnabled": false,
    "username": "",
    "willMessage": "connection lost",
    "willQualityOfService": 1,
    "willTopic": ""
}'
```

**Configure Webhook Settings**

Configure Webhook publisher settings.

```sh
curl -X PUT http://127.0.0.1:5000/api/v1/webhooks/event -H "Content-Type: application/json" -d '{
    "active": true,
    "eventBatchLimit": 10000,
    "eventBatchLingerMilliseconds": 1000,
    "eventBufferSize": 100000,
    "retry": {},
    "serverConfiguration": {
        "url": "https://your-webhook-url",
        "authentication": {
            "username": "your-username",
            "password": "your-password"
        },
        "port": 443,
        "tls": {}
    }
}'
```

Additional Information
Flask: A lightweight WSGI web application framework in Python.
Flask-RESTful: An extension for Flask that adds support for quickly building REST APIs.
paho-mqtt: The Paho Python Client provides a client class that enables applications to connect to an MQTT broker.
requests: A simple, yet elegant HTTP library for Python.
For more information, please refer to the official documentation.
