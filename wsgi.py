#!/usr/bin/env python3
"""
WSGI entry point for Expiry Tracker
"""

import os
from simple_app import app

# This is the WSGI application that Gunicorn will use
application = app

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
