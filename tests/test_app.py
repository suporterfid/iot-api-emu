import unittest
from flask import Flask
from flask_testing import TestCase
from app import app, mqtt_config, webhook_config, SETTINGS_FILE
import os
import json

class TestIoTDeviceEmulator(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def setUp(self):
        # Ensure the settings file does not interfere with tests
        if os.path.exists(SETTINGS_FILE):
            os.remove(SETTINGS_FILE)

    def tearDown(self):
        # Clean up any created files
        if os.path.exists(SETTINGS_FILE):
            os.remove(SETTINGS_FILE)

    def test_start_stream(self):
        response = self.client.post('/api/v1/profiles/inventory/presets/default/start')
        self.assertEqual(response.status_code, 204)

    def test_stop_stream(self):
        self.client.post('/api/v1/profiles/inventory/presets/default/start')
        response = self.client.post('/api/v1/profiles/stop')
        self.assertEqual(response.status_code, 204)

    def test_get_mqtt_settings(self):
        response = self.client.get('/api/v1/mqtt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, mqtt_config)

    def test_update_mqtt_settings(self):
        data = {
            "brokerHostname": "mqtt.example.com",
            "clientId": "Nq4PfQD",
            "eventTopic": "l",
            "active": True,
            "brokerPort": 1883
        }
        response = self.client.put('/api/v1/mqtt', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(mqtt_config['brokerHostname'], "mqtt.example.com")
        self.assertTrue(mqtt_config['active'])

    def test_get_webhook_settings(self):
        response = self.client.get('/api/v1/webhooks/event')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, webhook_config)

    def test_update_webhook_settings(self):
        data = {
            "active": True,
            "eventBatchLimit": 10000,
            "eventBatchLingerMilliseconds": 1000,
            "eventBufferSize": 100000,
            "serverConfiguration": {
                "url": "https://example.com",
                "authentication": {
                    "username": "user",
                    "password": "pass"
                }
            }
        }
        response = self.client.put('/api/v1/webhooks/event', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 204)
        self.assertTrue(webhook_config['active'])
        self.assertEqual(webhook_config['serverConfiguration']['url'], "https://example.com")

    def test_data_stream(self):
        self.client.post('/api/v1/profiles/inventory/presets/default/start')
        response = self.client.get('/api/v1/data/stream')
        self.assertEqual(response.status_code, 200)
        self.client.post('/api/v1/profiles/stop')

if __name__ == '__main__':
    unittest.main()
