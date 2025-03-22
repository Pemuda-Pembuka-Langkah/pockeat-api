import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Get configuration environment from environment variable or default to development
env = os.getenv('FLASK_ENV', 'development')

# Create the Flask application
app = create_app(env)

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    
    # Run the Flask application
    app.run(
        host='0.0.0.0',
        port=port, 
        debug=app.config.get('DEBUG', env == 'development')
    ) 