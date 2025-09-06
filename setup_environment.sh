#!/bin/bash

# Receipt Database Project - Environment Setup Script
# This script sets up a Python virtual environment and installs dependencies

echo "Setting up Receipt Database Project Environment..."
echo "================================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python version: $PYTHON_VERSION"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing project dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating project directories..."
mkdir -p receipts
mkdir -p processed_receipts
mkdir -p logs
mkdir -p data

# Create a basic .env file template
echo "Creating environment configuration template..."
cat > .env.template << EOF
# Receipt Database Configuration
# Copy this file to .env and update with your actual values

# Database Configuration
DATABASE_URL=sqlite:///receipt_database.db
# For PostgreSQL: DATABASE_URL=postgresql://username:password@localhost/receipt_db

# OCR Configuration
TESSERACT_CMD=/usr/local/bin/tesseract  # Update path as needed

# Application Settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# File Upload Settings
MAX_FILE_SIZE=10485760  # 10MB in bytes
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf,tiff,bmp
EOF

echo ""
echo "Environment setup complete!"
echo "=========================="
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate the virtual environment, run:"
echo "  deactivate"
echo ""
echo "Next steps:"
echo "1. Copy .env.template to .env and update with your configuration"
echo "2. Start developing your receipt database application"
echo ""
echo "Happy coding! 🚀"
