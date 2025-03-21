"""
API routes package initialization.
Register all API route blueprints here.
"""
from flask import Blueprint

# Create main API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Import and register route blueprints
from app.api.routes.food_routes import food_bp
from app.api.routes.exercise_routes import exercise_bp

api_bp.register_blueprint(food_bp)
api_bp.register_blueprint(exercise_bp) 