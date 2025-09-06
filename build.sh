#!/bin/bash
# Build script for Render.com deployment

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Initializing database..."
python init_db.py

echo "Build completed successfully!"
