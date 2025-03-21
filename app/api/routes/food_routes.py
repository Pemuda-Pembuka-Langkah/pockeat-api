"""
Food analysis routes.
"""
from flask import Blueprint, request, jsonify
from app.services.food.food_analysis_service import FoodAnalysisService
from app.services.food.food_correction_service import FoodCorrectionService
from app.services.gemini.gemini_client import GeminiClient
import os

food_bp = Blueprint('food', __name__, url_prefix='/food')

# Initialize services
gemini_client = GeminiClient(api_key=os.environ.get('GEMINI_API_KEY'))
food_analysis_service = FoodAnalysisService(gemini_client=gemini_client)
food_correction_service = FoodCorrectionService(gemini_client=gemini_client)


@food_bp.route('/analyze', methods=['POST'])
def analyze_food():
    """
    Analyze a food image using Gemini API.
    
    Expected input: Multipart form data with an image file
    """
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No image selected"}), 400
    
    # Read the image file
    image_data = file.read()
    
    # Analyze the food image
    try:
        result = food_analysis_service.analyze_food_image(image_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@food_bp.route('/correct', methods=['POST'])
def correct_food_entry():
    """
    Correct a food entry using Gemini API.
    
    Expected input: JSON with food_entry and user_correction fields
    """
    data = request.json
    
    if not data or 'food_entry' not in data or 'user_correction' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        result = food_correction_service.correct_food_entry(
            data['food_entry'], 
            data['user_correction']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500 