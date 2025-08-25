"""Main application entry point for Flask application to handle import errors"""

import sys  # Used to add src to path directory python can access
import os  # Used to convert relative path to src to absolute path

# Add src to path
sys.path.insert(0, os.path.abspath("src"))

# Now import can work with or without src prefix
from src.main import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
