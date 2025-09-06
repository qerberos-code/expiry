#!/usr/bin/env python3
"""
Debug script to test environment and dependencies
"""

import os
import sys

print("=== Expiry Tracker Debug Info ===")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

print("\n=== Environment Variables ===")
env_vars = ['DATABASE_URL', 'SECRET_KEY', 'FLASK_ENV', 'PORT']
for var in env_vars:
    value = os.getenv(var)
    if value:
        if var == 'DATABASE_URL':
            print(f"{var}: {value[:20]}...")
        else:
            print(f"{var}: {value}")
    else:
        print(f"{var}: Not set")

print("\n=== Testing Imports ===")
try:
    import flask
    print(f"✓ Flask {flask.__version__}")
except ImportError as e:
    print(f"✗ Flask: {e}")

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv")
except ImportError as e:
    print(f"✗ python-dotenv: {e}")

try:
    import sqlalchemy
    print(f"✓ SQLAlchemy {sqlalchemy.__version__}")
except ImportError as e:
    print(f"✗ SQLAlchemy: {e}")

try:
    import psycopg2
    print("✓ psycopg2")
except ImportError as e:
    print(f"✗ psycopg2: {e}")

print("\n=== Testing Database Connection ===")
database_url = os.getenv('DATABASE_URL')
if database_url:
    try:
        from sqlalchemy import create_engine
        engine = create_engine(database_url)
        connection = engine.connect()
        connection.close()
        print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
else:
    print("! No DATABASE_URL set")

print("\n=== Testing Flask App ===")
try:
    from simple_app import app
    print("✓ Flask app created successfully")
    
    with app.app_context():
        print("✓ App context works")
        
except Exception as e:
    print(f"✗ Flask app error: {e}")

print("\n=== Debug Complete ===")
