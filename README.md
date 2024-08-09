# IoT Device Interface API Emulator

This project **emulates basic operations** of the IoT device interface API with support for MQTT and Webhook publishers. The emulator can stream tag events and publish them to configured MQTT brokers and HTTP servers.

## Features

- Emulate tag event streaming
- Publish events to MQTT brokers
- Publish events to HTTP servers via Webhooks
- Support for predefined EPC lists from files
- HTTPS support with self-signed certificate
- HTTPS support with self-signed certificate
- Configurable basic authentication
- Management API for handling reference lists

## Setup Development Environment

### Prerequisites

- Python 3.x
- Git

### Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/suporterfid/iot-api-emu.git
    cd iot-api-emu
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

4. **Generate a self-signed certificate**:
    ```sh
    docker run --rm -v %cd%:/output -w /output alpine/openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 3650 -nodes -subj "/C=NA/ST=NA/L=Lab/O=My Organization/OU=Emulator/CN=localhost"
    ```

5. **Run the Flask application**:
    ```sh
    python run.py
    ```

## Running the Application with Docker

### Prerequisites

- Docker
- Docker Compose

### Build and Run the Docker Container

1. **Build and run the Docker container using Docker Compose**:
    ```sh
    docker-compose up --build
    ```

2. **Access the application**:
    - The application will be available at `https://localhost:5000`
    - The Swagger UI will be accessible at `https://localhost:5000/swagger/`

### Environment Variables

- `USE_HTTPS`: Set to `True` to enable HTTPS (default: `True`).
- `USE_BASIC_AUTH`: Set to `True` to enable basic authentication (default: `False`).
- `BASIC_AUTH_USERNAME`: Username for basic authentication (default: `admin`).
- `BASIC_AUTH_PASSWORD`: Password for basic authentication (default: `password`).

## EPC List Enhancements

The emulator now supports loading predefined EPC lists from local files. There are two modes of operation based on the presence of these files:

### 1. `reference-list.txt`

- If a file named `reference-list.txt` is present in the same directory as `app.py`, the EPCs from this file will be sent in the tag events repeatedly.
- Each line in this file should contain a single EPC in hexadecimal format.

#### Example `reference-list.txt`
```sh
3500B6D9801234567890ABCDEF
3500B6D9800987654321FEDCBA
3500B6D9801122334455667788
3500B6D980AABBCCDDEEFF0011
3500B6D9802233445566778899
```

### 2. `reference-list-unique.txt`

- If a file named `reference-list-unique.txt` is present, the EPCs from this file will be sent only once between the start and stop of the stream.
- Each line in this file should also contain a single EPC in hexadecimal format.

#### Example `reference-list-unique.txt`
```sh
3500B6D9801234567890ABCDEF
3500B6D9800987654321FEDCBA
3500B6D9801122334455667788
3500B6D980AABBCCDDEEFF0011
3500B6D9802233445566778899
```
### 3. Default Behavior

- If neither `reference-list.txt` nor `reference-list-unique.txt` is present, the emulator will generate random EPCs for the tag events.


## API Endpoints

**Start Stream**

Start streaming tag events.

```sh
curl -X POST http://127.0.0.1:5000/api/v1/profiles/inventory/presets/default/start --insecure
```

**Stop Stream**

Stop streaming tag events.

```sh
curl -X POST http://127.0.0.1:5000/api/v1/profiles/stop --insecure
```

**Get Data Stream**

Get the streamed tag events.

```sh
curl http://127.0.0.1:5000/api/v1/data/stream --insecure
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
}' --insecure
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
}' --insecure
```

## Reference List Management API

This section describes the API endpoints for managing the reference lists (`reference-list.txt` and `reference-list-unique.txt`).

### Create or Update a Reference List

- **URL**: `POST /manage/ref-lists/<list_type>`
- **Description**: Create or replace the content of the reference list. `<list_type>` can be `default` for `reference-list.txt` or `unique` for `reference-list-unique.txt`.
- **Request Body**: A JSON array of EPC strings.

**Example**:
```sh
curl -X POST https://localhost:5000/manage/ref-lists/default -H "Content-Type: application/json" -d '[
    "3500B6D9801234567890ABCDEF",
    "3500B6D9800987654321FEDCBA"
]'  --insecure
```
### Append to a Reference List
- **URL**: `PUT /manage/ref-lists/<list_type>`
- **Description**: Append EPCs to the reference list. <list_type> can be default for reference-list.txt or unique for reference-list-unique.txt.
- **Request Body**: A JSON array of EPC strings.

**Example**:
```sh
curl -X PUT https://localhost:5000/manage/ref-lists/default -H "Content-Type: application/json" -d '[
    "3500B6D9801122334455667788"
]' --insecure
```

### Query a Reference List
- **URL**: `GET /manage/ref-lists/<list_type>`
- **Description**: Retrieve the content of a reference list. <list_type> can be default for reference-list.txt or unique for reference-list-unique.txt.

**Example**:
```sh
curl https://localhost:5000/manage/ref-lists/default --insecure
```

### Delete a Reference List
- **URL**: `DELETE /manage/ref-lists/<list_type>`
- **Description**: Delete the reference list file. <list_type> can be default for reference-list.txt or unique for reference-list-unique.txt.

**Example**:
```sh
curl -X DELETE https://localhost:5000/manage/ref-lists/default  --insecure
```


## Disclaimer

This emulator is designed to accelerate the initial development process for new adopters of RAIN RFID who are in the process of acquiring an Impinj R700 RAIN RFID reader with the IoT Device Interface. **It does not aim to replace the hardware** and comes with no guarantee of updates in accordance with new released versions of the API. Use it at your own risk. **This code is neither supported nor endorsed by Impinj Inc.**

### WARRANTY DISCLAIMER

This software is provided “as is” without quality check, and there is no warranty that the software will operate without error or interruption or meet any performance standard or other expectation. All warranties, express or implied, including the implied warranties of merchantability, non-infringement, quality, accuracy, and fitness for a particular purpose are expressly disclaimed. The developers of this software are not obligated in any way to provide support or other maintenance with respect to this software.

### LIMITATION OF LIABILITY

The total liability arising out of or related to the use of this software will not exceed the total amount paid by the user for this software, which in this case is zero as the software is provided free of charge. In no event will the developers have liability for any indirect, incidental, special, or consequential damages, even if advised of the possibility of these damages. These limitations will apply notwithstanding any failure of essential purpose of any limited remedy provided.

### Additional Information
Flask: A lightweight WSGI web application framework in Python.
Flask-RESTful: An extension for Flask that adds support for quickly building REST APIs.
paho-mqtt: The Paho Python Client provides a client class that enables applications to connect to an MQTT broker.
requests: A simple, yet elegant HTTP library for Python.
Flasgger: A Flask extension to provide Swagger UI for your API.
For more information, please refer to the official documentation.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
