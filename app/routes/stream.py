from flask import Blueprint, Response, jsonify, request
from flask_restful import Api, Resource
import json
import time
import threading
import os
from app.utils import load_settings, save_settings, mqtt_config, webhook_config, epc_list, unique_epc_list, reference_list_file, reference_list_unique_file
from app.mqtt import mqtt_client, start_mqtt_thread
from app.events import TagEvent
from app.epc import EPC
import app.config as config

stream_bp = Blueprint('stream', __name__)
api = Api(stream_bp)

# Initialize global variables
epc_index = 0
unique_epc_sent = False

class DataStream(Resource):
    def get(self):
        """
        Get the streamed tag events.
        ---
        responses:
          200:
            description: Streamed tag events
        """
        from app.mqtt import send_iothub_message_http
        def generate():
            while config.streaming:
                epc = get_next_epc()
                if epc is None:
                    break
                event = TagEvent(epc)
                event_data = event.to_dict()
                # Always attempt to send to IoT Hub if active
                if mqtt_config.get('active', False):
                    print(f"[STREAM] Sending event to IoT Hub: {event_data}")
                    send_iothub_message_http(mqtt_config, event_data)
                yield f"{json.dumps(event_data)}\n\n"
                time.sleep(2)  # Simulate delay between events
        return Response(generate(), content_type='text/event-stream')

class StartStream(Resource):
        def post(self, preset_id):
                """
                Start streaming tag events and send them to IoT Hub in a background thread.
                ---
                parameters:
                    - in: path
                        name: preset_id
                        required: true
                        type: string
                responses:
                    204:
                        description: Stream started
                    404:
                        description: Preset not found
                """
                import threading
                from app.mqtt import send_iothub_message_http
                global epc_index, unique_epc_sent
                print(f"preset_id {preset_id}")
                if preset_id == 'default':
                    import app.utils as utils
                    utils.load_settings()
                    current_config = utils.mqtt_config
                    required_keys = ['brokerHostname', 'clientId', 'password']
                    if not all(k in current_config and current_config[k] for k in required_keys):
                        print(f"[START STREAM] ERROR: MQTT config missing required keys: {required_keys}. Not starting stream thread.")
                        return {"error": "MQTT config missing required keys."}, 400
                    config.streaming = True
                    print(f"streaming {config.streaming}")
                    epc_index = 0
                    unique_epc_sent = False

                    def stream_to_iothub():
                        while config.streaming:
                            utils.load_settings()
                            current_config = utils.mqtt_config
                            if not all(k in current_config and current_config[k] for k in required_keys):
                                print(f"[BG STREAM] ERROR: MQTT config missing required keys: {required_keys}. Stopping stream thread.")
                                break
                            # Always generate a new event and send only the event payload
                            epc = get_next_epc()
                            event = TagEvent(epc)
                            event_data = event.to_dict()
                            print(f"[BG STREAM] Sending event to IoT Hub: {event_data}")
                            send_iothub_message_http(current_config, event_data)
                            time.sleep(2)

                    t = threading.Thread(target=stream_to_iothub, daemon=True)
                    t.start()
                    return '', 204
                return '', 404

class StopStream(Resource):
    def post(self):
        """
        Stop streaming tag events.
        ---
        responses:
          204:
            description: Stream stopped
        """
        config.streaming = False  # Set streaming to False
        return '', 204

def get_next_epc():
    global epc_index, unique_epc_sent
    if os.path.exists(reference_list_unique_file) and not unique_epc_sent:
        if epc_index < len(unique_epc_list):
            epc = EPC()
            epc.header = int(unique_epc_list[epc_index][0:2], 16)
            epc.manager = int(unique_epc_list[epc_index][2:9], 16)
            epc.class_ = int(unique_epc_list[epc_index][9:15], 16)
            epc.serial = int(unique_epc_list[epc_index][15:24], 16)
            epc_index += 1
            if epc_index == len(unique_epc_list):
                unique_epc_sent = True
            return epc
        else:
            return None
    elif os.path.exists(reference_list_file):
        if epc_index >= len(epc_list):
            epc_index = 0
        epc = EPC()
        epc.header = int(epc_list[epc_index][0:2], 16)
        epc.manager = int(epc_list[epc_index][2:9], 16)
        epc.class_ = int(epc_list[epc_index][9:15], 16)
        epc.serial = int(epc_list[epc_index][15:24], 16)
        epc_index += 1
        return epc
    else:
        # Always generate a new random EPC if no file exists
        return EPC()

api.add_resource(DataStream, '/api/v1/data/stream')
api.add_resource(StartStream, '/api/v1/profiles/inventory/presets/<string:preset_id>/start')
api.add_resource(StopStream, '/api/v1/profiles/stop')