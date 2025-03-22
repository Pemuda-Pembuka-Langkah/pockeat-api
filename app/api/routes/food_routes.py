"""
Food analysis routes.
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import tempfile
from app.services.gemini.food_text_analysis_service import FoodTextAnalysisService
from app.services.gemini.food_image_analysis_service import FoodImageAnalysisService
from app.services.gemini.nutrition_label_analysis_service import NutritionLabelAnalysisService
from app.services.gemini.base_gemini_service import GeminiServiceException
from app.api.models.food_analysis import FoodAnalysisResult

food_bp = Blueprint('food', __name__, url_prefix='/food')

# Initialize services
food_text_analysis_service = None
food_image_analysis_service = None
nutrition_label_analysis_service = None


def get_services():
    """Initialize services if not already initialized."""
    global food_text_analysis_service, food_image_analysis_service, nutrition_label_analysis_service
    
    if food_text_analysis_service is None:
        api_key = current_app.config.get('GEMINI_API_KEY')
        food_text_analysis_service = FoodTextAnalysisService(api_key=api_key)
        food_image_analysis_service = FoodImageAnalysisService(api_key=api_key)
        nutrition_label_analysis_service = NutritionLabelAnalysisService(api_key=api_key)


@food_bp.route('/text', methods=['POST'])
def analyze_food_text():
    """
    Analyze a food description and estimate nutritional content.
    
    Request Body:
        - food_description (str): The food description to analyze.
        
    Returns:
        A JSON object with the food analysis result.
    """
    try:
        # Initialize services
        get_services()
        
        # Extract data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        food_description = data.get('food_description')
        if not food_description:
            return jsonify({'error': 'Food description is required'}), 400
        
        # Analyze food description
        result = food_text_analysis_service.analyze(food_description)
        
        # Return the result
        return jsonify(result.dict()), 200
    
    except GeminiServiceException as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Error in analyze_food_text: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@food_bp.route('/analyze', methods=['POST'])
def analyze_food_image():
    """
    Analyze a food image and estimate nutritional content.
    
    Request:
        - image (file): The food image to analyze.
        
    Returns:
        A JSON object with the food analysis result.
    """
    try:
        # Initialize services
        get_services()
        
        # Check if image file is included in the request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'Empty image file name'}), 400
        
        # Read the image file
        image_bytes = image_file.read()
        if not image_bytes:
            return jsonify({'error': 'Empty image file'}), 400
        
        # Analyze food image
        result = food_image_analysis_service.analyze(image_bytes)
        
        # Return the result
        return jsonify(result.dict()), 200
    
    except GeminiServiceException as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Error in analyze_food_image: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@food_bp.route('/nutrition-label', methods=['POST'])
def analyze_nutrition_label():
    """
    Analyze a nutrition label image and estimate nutritional content.
    
    Request:
        - image (file): The nutrition label image to analyze.
        - servings (float): The number of servings the user will consume.
        
    Returns:
        A JSON object with the food analysis result.
    """
    try:
        # Initialize services
        get_services()
        
        # Check if image file is included in the request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'Empty image file name'}), 400
        
        # Get servings from request
        servings = request.form.get('servings', '1.0')
        try:
            servings = float(servings)
            if servings <= 0:
                return jsonify({'error': 'Servings must be a positive number'}), 400
        except ValueError:
            return jsonify({'error': 'Servings must be a valid number'}), 400
        
        # Read the image file
        image_bytes = image_file.read()
        if not image_bytes:
            return jsonify({'error': 'Empty image file'}), 400
        
        # Analyze nutrition label image
        result = nutrition_label_analysis_service.analyze(image_bytes, servings)
        
        # Return the result
        return jsonify(result.dict()), 200
    
    except GeminiServiceException as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Error in analyze_nutrition_label: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@food_bp.route('/correct', methods=['POST'])
def correct_food_analysis():
    """
    Correct a food analysis based on user feedback.
    
    Request Body:
        - food_entry (dict): The previous food analysis result.
        - user_correction (str): The user's correction comment.
        - servings (float, optional): The number of servings for nutrition label corrections.
        
    Returns:
        A JSON object with the corrected food analysis result.
    """
    try:
        # Initialize services
        get_services()
        
        # Extract data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        food_entry = data.get('food_entry')
        if not food_entry:
            return jsonify({'error': 'Previous food entry is required'}), 400
        
        user_correction = data.get('user_correction')
        if not user_correction:
            return jsonify({'error': 'User correction is required'}), 400
        
        # Convert the JSON to a FoodAnalysisResult object
        try:
            previous_result = FoodAnalysisResult(**food_entry)
        except Exception as e:
            return jsonify({'error': f'Invalid food entry format: {str(e)}'}), 400
        
        # Get servings if provided for nutrition label corrections
        servings = data.get('servings')
        if servings is not None:
            try:
                servings = float(servings)
                if servings <= 0:
                    return jsonify({'error': 'Servings must be a positive number'}), 400
                    
                # If servings are provided, use the nutrition label correction service
                result = nutrition_label_analysis_service.correct_analysis(
                    previous_result, user_correction, servings
                )
            except ValueError:
                return jsonify({'error': 'Servings must be a valid number'}), 400
        else:
            # Use the food text analysis service for corrections if no servings are provided
            result = food_text_analysis_service.correct_analysis(
                previous_result, user_correction
            )
        
        # Return the result
        return jsonify(result.dict()), 200
    
    except GeminiServiceException as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Error in correct_food_analysis: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 