import json
import os

SETTINGS_FILE = "settings.json"
reference_list_file = "reference-list.txt"
reference_list_unique_file = "reference-list-unique.txt"
mqtt_config = {}
webhook_config = {}
epc_list = []
unique_epc_list = []

last_http_status = 0
last_http_timestamp = None
streaming = False

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

# Modify the webhook function to update these variables
def webhook_publisher():
    global last_http_status, last_http_timestamp
    while True:
        if webhook_config.get('active', False):
            events = []
            linger_ms = webhook_config.get('eventBatchLingerMilliseconds', 1000)
            start_time = time.time()
            while time.time() - start_time < linger_ms / 1000.0:
                if not streaming and not events:
                    break
                if streaming:
                    epc = get_next_epc()
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
                    
                    last_http_status = response.status_code
                    last_http_timestamp = datetime.utcnow().isoformat() + 'Z'
                    
                    if response.status_code == 200:
                        print("Events successfully sent to webhook")
                    else:
                        print(f"Failed to send events to webhook, status code: {response.status_code}, response: {response.text}")
                except Exception as e:
                    print(f"Error sending events to webhook: {e}")
        else:
            time.sleep(1)  # Sleep if webhook is not active
