#!/usr/bin/env bash

# Enable error logging
set -e
echo "Starting deployment script..."

# Check for a marker file indicating packages have been installed
if [ ! -f /home/site/.packages_installed ]; then
    # Install required packages only on first run
    echo "First run: Installing Python dependencies..."
    pip install -r /home/site/wwwroot/requirements.txt
    pip install gunicorn

    # Ensure session directory exists
    mkdir -p /home/site/wwwroot/flask_session
    
    # Create marker file to indicate packages have been installed
    touch /home/site/.packages_installed
    echo "Python dependencies installed."
else
    echo "Python dependencies already installed. Skipping installation."
fi

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