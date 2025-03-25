from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

from src.services.gemini_service import GeminiService
from src.services.gemini.exceptions import GeminiServiceException

# Load environment variables
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
gemini_service = None

def create_app(config=None):
    app = Flask(__name__)
    
    # Configure the Flask application
    if config is None:
        # Default configuration
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    else:
        # Override with passed config
        app.config.update(config)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Gemini service
    try:
        global gemini_service
        gemini_service = GeminiService()
    except GeminiServiceException as e:
        app.logger.error(f"Failed to initialize Gemini service: {str(e)}")
    
    # Register blueprints
    from src.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app 