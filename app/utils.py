import json
import os

SETTINGS_FILE = "settings.json"
reference_list_file = "reference-list.txt"
reference_list_unique_file = "reference-list-unique.txt"
mqtt_config = {}
webhook_config = {}
epc_list = []
unique_epc_list = []

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

def load_epc_list(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            return [line.strip() for line in f.readlines()]
    return []

def init_epc_lists():
    global epc_list, unique_epc_list
    epc_list = load_epc_list(reference_list_file)
    unique_epc_list = load_epc_list(reference_list_unique_file)
