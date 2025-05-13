"""
WSGI entry point file for the application.
This resolves the naming conflict between app.py and the app/ directory.
"""

from app import app

if __name__ == "__main__":
    app.run()