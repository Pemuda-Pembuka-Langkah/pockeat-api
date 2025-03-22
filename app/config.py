import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API
    API_TITLE = 'PockEat API'
    API_VERSION = 'v1'
    
    # Gemini API
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        # Only print this warning during development, not in production
        print("WARNING: GEMINI_API_KEY environment variable is not set. Gemini API features will not work correctly.")

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # In production, ensure SECRET_KEY is properly set as an environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Check that secret key is set in production
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production environment")

# Configuration dictionary to map configuration names to classes
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 