#!/bin/bash

# Enable error logging
set -e
echo "Starting container deployment script..."

# Create necessary directories
mkdir -p /home/site/wwwroot/flask_session

# Install gunicorn
echo "Installing gunicorn..."
pip install gunicorn

# Print debug information
echo "Workspace structure:"
ls -la /home/site/wwwroot/
echo "Python version:"
python --version

# Start the application
echo "Starting gunicorn server..."
cd /home/site/wwwroot/
gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app
