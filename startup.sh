#!/bin/bash

# Enable error logging
set -e
echo "Starting deployment script..."

# Install required packages
echo "Installing Python dependencies..."
pip install -r /home/site/wwwroot/requirements.txt
pip install gunicorn

# Ensure session directory exists
mkdir -p /home/site/wwwroot/flask_session

# Print debug information
echo "Workspace structure:"
ls -la /home/site/wwwroot/
echo "App directory structure:"
ls -la /home/site/wwwroot/app/
echo "Python version:"
python --version

# Start the application
echo "Starting gunicorn server..."
cd /home/site/wwwroot/
gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app