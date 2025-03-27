"""
Routes for the Gemini API.
"""

import os
from flask import Blueprint, jsonify, request, current_app
from werkzeug.exceptions import BadRequest, InternalServerError

from src import gemini_service
from src.services.gemini.exceptions import GeminiServiceException

api_bp = Blueprint('api', __name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint.
    
    Returns:
        JSON: Health check response.
    """
    is_gemini_available = gemini_service is not None
    
    return jsonify({
        "status": "healthy" if is_gemini_available else "degraded",
        "message": "API is running" + ("" if is_gemini_available else ", but Gemini service is unavailable")
    }), 200


@api_bp.route('/food/analyze/text', methods=['POST'])
async def analyze_food_by_text():
    """Analyze food from text.
    
    Returns:
        JSON: Food analysis result.
    """
    if gemini_service is None:
        raise InternalServerError("Gemini service is unavailable")
    
    data = request.get_json()
    
    if not data or 'description' not in data:
        raise BadRequest("Missing required field: description")
    
    try:
        result = await gemini_service.analyze_food_by_text(data['description'])
        return jsonify(result.to_dict()), 200
    except GeminiServiceException as e:
        raise BadRequest(str(e))


@api_bp.route('/food/analyze/image', methods=['POST'])
async def analyze_food_by_image():
    """Analyze food from image."""
    if 'image' not in request.files:
        # Return error with proper JSON structure instead of raising exception
        error_data = {
            "error": "Missing required field: image",
            "food_name": "Unknown",
            "ingredients": [],
            "nutrition_info": {
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0,
                "sodium": 0,
                "fiber": 0,
                "sugar": 0
            },
            "warnings": []
        }
        return jsonify(error_data), 400
    
    try:
        result = await gemini_service.analyze_food_by_image(request.files['image'])
        return jsonify(result.to_dict()), 200
    except Exception as e:
        # Log the full exception details for debugging
        import traceback
        print(f"Food image analysis error: {str(e)}")
        print(traceback.format_exc())
        
        # Return error with proper JSON structure
        error_data = {
            "error": f"Failed to analyze food image: {str(e)}",
            "food_name": "Unknown",
            "ingredients": [],
            "nutrition_info": {
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0,
                "sodium": 0,
                "fiber": 0,
                "sugar": 0
            },
            "warnings": []
        }
        return jsonify(error_data), 400


@api_bp.route('/food/analyze/nutrition-label', methods=['POST'])
async def analyze_nutrition_label():
    """Analyze nutrition label from image.
    
    Returns:
        JSON: Food analysis result.
    """
    if gemini_service is None:
        raise InternalServerError("Gemini service is unavailable")
    
    if 'image' not in request.files:
        raise BadRequest("Missing required field: image")
    
    # Get servings from form data
    servings = 1.0
    if 'servings' in request.form:
        try:
            servings = float(request.form['servings'])
        except ValueError:
            raise BadRequest("Invalid servings value: must be a number")
    
    try:
        result = await gemini_service.analyze_nutrition_label(request.files['image'], servings)
        return jsonify(result.to_dict()), 200
    except GeminiServiceException as e:
        raise BadRequest(str(e))


@api_bp.route('/exercise/analyze', methods=['POST'])
async def analyze_exercise():
    """Analyze exercise from text.
    
    Returns:
        JSON: Exercise analysis result.
    """
    if gemini_service is None:
        raise InternalServerError("Gemini service is unavailable")
    
    data = request.get_json()
    
    if not data or 'description' not in data:
        raise BadRequest("Missing required field: description")
    
    # Get user weight from JSON data
    user_weight_kg = None
    if 'user_weight_kg' in data:
        try:
            user_weight_kg = float(data['user_weight_kg'])
        except ValueError:
            raise BadRequest("Invalid user_weight_kg value: must be a number")
    
    try:
        result = await gemini_service.analyze_exercise(data['description'], user_weight_kg)
        return jsonify(result.to_dict()), 200
    except GeminiServiceException as e:
        raise BadRequest(str(e))


@api_bp.route('/food/correct/text', methods=['POST'])
async def correct_food_text_analysis():
    """Correct food text analysis.
    
    Returns:
        JSON: Corrected food analysis result.
    """
    if gemini_service is None:
        raise InternalServerError("Gemini service is unavailable")
    
    data = request.get_json()
    
    if not data or 'previous_result' not in data or 'user_comment' not in data:
        raise BadRequest("Missing required fields: previous_result, user_comment")
    
    try:
        from src.models.food_analysis import FoodAnalysisResult
        previous_result = FoodAnalysisResult.from_dict(data['previous_result'])
        result = await gemini_service.correct_food_text_analysis(previous_result, data['user_comment'])
        return jsonify(result.to_dict()), 200
    except GeminiServiceException as e:
        raise BadRequest(str(e))
    except Exception as e:
        raise BadRequest(f"Invalid previous_result: {str(e)}")


@api_bp.route('/food/correct/image', methods=['POST'])
async def correct_food_image_analysis():
    """Correct food image analysis.
    
    Returns:
        JSON: Corrected food analysis result.
    """
    if gemini_service is None:
        raise InternalServerError("Gemini service is unavailable")
    
    data = request.get_json()
    
    if not data or 'previous_result' not in data or 'user_comment' not in data:
        raise BadRequest("Missing required fields: previous_result, user_comment")
    
    try:
        from src.models.food_analysis import FoodAnalysisResult
        previous_result = FoodAnalysisResult.from_dict(data['previous_result'])
        result = await gemini_service.correct_food_image_analysis(previous_result, data['user_comment'])
        return jsonify(result.to_dict()), 200
    except GeminiServiceException as e:
        raise BadRequest(str(e))
    except Exception as e:
        raise BadRequest(f"Invalid previous_result: {str(e)}")


@api_bp.route('/food/correct/nutrition-label', methods=['POST'])
async def correct_nutrition_label_analysis():
    """Correct nutrition label analysis.
    
    Returns:
        JSON: Corrected food analysis result.
    """
    if gemini_service is None:
        raise InternalServerError("Gemini service is unavailable")
    
    data = request.get_json()
    
    if not data or 'previous_result' not in data or 'user_comment' not in data:
        raise BadRequest("Missing required fields: previous_result, user_comment")
    
    # Get servings from JSON data
    servings = 1.0
    if 'servings' in data:
        try:
            servings = float(data['servings'])
        except ValueError:
            raise BadRequest("Invalid servings value: must be a number")
    
    try:
        from src.models.food_analysis import FoodAnalysisResult
        previous_result = FoodAnalysisResult.from_dict(data['previous_result'])
        result = await gemini_service.correct_nutrition_label_analysis(
            previous_result, data['user_comment'], servings
        )
        return jsonify(result.to_dict()), 200
    except GeminiServiceException as e:
        raise BadRequest(str(e))
    except Exception as e:
        raise BadRequest(f"Invalid previous_result: {str(e)}")


@api_bp.route('/exercise/correct', methods=['POST'])
async def correct_exercise_analysis():
    """Correct exercise analysis.
    
    Returns:
        JSON: Corrected exercise analysis result.
    """
    if gemini_service is None:
        raise InternalServerError("Gemini service is unavailable")
    
    data = request.get_json()
    
    if not data or 'previous_result' not in data or 'user_comment' not in data:
        raise BadRequest("Missing required fields: previous_result, user_comment")
    
    try:
        from src.models.exercise_analysis import ExerciseAnalysisResult
        previous_result = ExerciseAnalysisResult.from_dict(data['previous_result'])
        result = await gemini_service.correct_exercise_analysis(previous_result, data['user_comment'])
        return jsonify(result.to_dict()), 200
    except GeminiServiceException as e:
        raise BadRequest(str(e))
    except Exception as e:
        raise BadRequest(f"Invalid previous_result: {str(e)}")

@api_bp.route('/debug-env')
def debug_env():
    return jsonify({
        "has_key": bool(os.getenv("GOOGLE_API_KEY")),
        "env_vars": list(os.environ.keys())
    })


# Error handlers
@api_bp.errorhandler(BadRequest)
def handle_bad_request(e):
    """Handle bad request errors.
    
    Args:
        e: The error.
        
    Returns:
        JSON: Error response.
    """
    print(f"Bad Request Error: {str(e)}")
    return jsonify({'error': str(e)}), 400


@api_bp.errorhandler(InternalServerError)
def handle_internal_server_error(e):
    """Handle internal server errors.
    
    Args:
        e: The error.
        
    Returns:
        JSON: Error response.
    """
    print(f"Internal Server Error: {str(e)}")
    return jsonify({'error': str(e)}), 500 