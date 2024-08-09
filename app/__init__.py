from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from .routes.stream import stream_bp
from .routes.status import status_bp
from .routes.mqtt_settings import mqtt_settings_bp
from .routes.webhook_settings import webhook_settings_bp
from .routes.profiles import profiles_bp
from .routes.system_info import system_info_bp
from .routes.auth_config import auth_config_bp
from .routes.users import users_bp
from .routes.certificates import certificates_bp
from app.routes.reference_lists import reference_lists_bp

def create_app():
    app = Flask(__name__)
    api = Api(app)

    # Configure Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/swagger/"
    }
    
    Swagger(app, config=swagger_config)

    app.register_blueprint(stream_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(mqtt_settings_bp)
    app.register_blueprint(webhook_settings_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(system_info_bp)
    app.register_blueprint(auth_config_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(certificates_bp)
    # Register the reference lists blueprint
    app.register_blueprint(reference_lists_bp, url_prefix='/manage')

    return app
