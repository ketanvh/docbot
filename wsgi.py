"""
WSGI entry point file for the application.
This resolves the naming conflict between app.py and the app/ directory.
"""

from app import app

# This makes the 'app' variable directly accessible to Gunicorn
application = app

if __name__ == "__main__":
    app.run()