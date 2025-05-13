"""
WSGI entry point file for Azure Web App deployment.
This resolves the module not found issue with wsgi.py
"""

# Import the Flask app instance directly from app.py
from app import app as application

# This makes the 'application' variable directly accessible to Gunicorn
app = application

if __name__ == "__main__":
    app.run()