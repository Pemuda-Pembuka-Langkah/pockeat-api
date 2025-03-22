import os
from flask import Flask
from flask_cors import CORS
from app.api.routes import register_routes
from app.config import config_by_name

def create_app(config_name='development'):
    """
    Create and configure a Flask application instance.
    
    Args:
        config_name: The configuration environment name ('development', 'testing', 'production').
                    Defaults to 'development'.
    
    Returns:
        A configured Flask application instance.
    """
    app = Flask(__name__)
    
    # Load configuration based on environment
    app.config.from_object(config_by_name[config_name])
    
    # Enable CORS
    CORS(app)
    
    # Register API routes
    register_routes(app)
    
    @app.route('/health')
    def health_check():
        """Health check endpoint to verify the application is running."""
        return {'status': 'healthy', 'environment': config_name}
    
    return app