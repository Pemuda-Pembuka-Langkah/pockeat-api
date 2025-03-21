from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__, url_prefix='/api/v1')

@main_bp.route('/')
def index():
    """Root endpoint for the API."""
    return jsonify({
        'message': 'Welcome to PockEat API',
        'version': '1.0.0',
        'status': 'active'
    }) 