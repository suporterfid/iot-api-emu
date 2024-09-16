from app import create_app
import os
from flask import request, Response
from functools import wraps

app = create_app()

# Configuration for HTTPS and Basic Authentication
USE_HTTPS = os.getenv('USE_HTTPS', 'True') == 'True'
USE_BASIC_AUTH = os.getenv('USE_BASIC_AUTH', 'False') == 'True'
USERNAME = os.getenv('BASIC_AUTH_USERNAME', 'admin')
PASSWORD = os.getenv('BASIC_AUTH_PASSWORD', 'password')

def check_auth(username, password):
    """Check if a username/password combination is valid."""
    return username == USERNAME and password == PASSWORD

def authenticate():
    """Send a 401 response to enable basic auth."""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Apply authentication to all routes if enabled
if USE_BASIC_AUTH:
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            app.view_functions[rule.endpoint] = requires_auth(app.view_functions[rule.endpoint])

if __name__ == '__main__':
    if USE_HTTPS:
        context = ('cert.pem', 'key.pem')
        app.run(debug=True, ssl_context=context, host='0.0.0.0')
    else:
        app.run(debug=True, host='0.0.0.0')
