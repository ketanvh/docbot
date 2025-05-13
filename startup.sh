#!/bin/bash

# Make the script executable
chmod +x startup.sh

# Install any dependencies if needed
pip install -r requirements.txt

# Start Gunicorn server with the correct entry point
gunicorn --bind=0.0.0.0 --timeout 600 application:app