#!/usr/bin/env python
"""
Run script for PockEat API Flask application.

This script handles the startup of the Flask application with proper configuration,
environment loading, and debugging options.
"""

import os
from dotenv import load_dotenv
from src import create_app

# Load environment variables from .env file
load_dotenv()

# Create Flask application instance
app = create_app()

if __name__ == "__main__":
    # Get host and port from environment variables or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8080))
    # debug = os.getenv("FLASK_ENV", "development").lower() == "development"
    
    print(f"Starting PockEat API on {host}:{port} ")
    
    # Run the Flask application
    app.run(host=host, port=port) 