"""
Exercise analysis routes.
"""
from flask import Blueprint, request, jsonify, current_app
from app.services.gemini.exercise_analysis_service import ExerciseAnalysisService, GeminiServiceException
from app.api.models.exercise_analysis import ExerciseAnalysisResult

exercise_bp = Blueprint('exercise', __name__, url_prefix='/exercise')

# Initialize services
exercise_analysis_service = None


def get_services():
    """Initialize services if not already initialized."""
    global exercise_analysis_service
    if exercise_analysis_service is None:
        api_key = current_app.config.get('GEMINI_API_KEY')
        exercise_analysis_service = ExerciseAnalysisService(api_key=api_key)


@exercise_bp.route('/analyze', methods=['POST'])
def analyze_exercise():
    """
    Analyze an exercise description and estimate calories burned.
    
    Request Body:
        - description (str): The exercise description to analyze.
        - user_weight (float, optional): The user's weight in kilograms.
        
    Returns:
        A JSON object with the exercise analysis result.
    """
    try:
        # Initialize services
        get_services()
        
        # Extract data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        description = data.get('description')
        if not description:
            return jsonify({'error': 'Exercise description is required'}), 400
        
        # Check if user_weight is provided and validate it
        user_weight = data.get('user_weight')
        if user_weight is not None:
            try:
                user_weight = float(user_weight)
                if user_weight <= 0:
                    return jsonify({'error': 'User weight must be a positive number'}), 400
            except ValueError:
                return jsonify({'error': 'User weight must be a valid number'}), 400
        
        # Analyze exercise
        result = exercise_analysis_service.analyze(description, user_weight_kg=user_weight)
        
        # Return the result
        return jsonify(result.dict()), 200
    
    except GeminiServiceException as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Error in analyze_exercise: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@exercise_bp.route('/correct', methods=['POST'])
def correct_exercise_entry():
    """
    Correct an exercise analysis based on user feedback.
    
    Request Body:
        - exercise_entry (dict): The previous exercise analysis result.
        - user_correction (str): The user's correction comment.
        
    Returns:
        A JSON object with the corrected exercise analysis result.
    """
    try:
        # Initialize services
        get_services()
        
        # Extract data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        exercise_entry = data.get('exercise_entry')
        if not exercise_entry:
            return jsonify({'error': 'Previous exercise entry is required'}), 400
        
        user_correction = data.get('user_correction')
        if not user_correction:
            return jsonify({'error': 'User correction is required'}), 400
        
        # Convert the JSON to an ExerciseAnalysisResult object
        try:
            previous_result = ExerciseAnalysisResult(**exercise_entry)
        except Exception as e:
            return jsonify({'error': f'Invalid exercise entry format: {str(e)}'}), 400
        
        # Correct exercise analysis
        result = exercise_analysis_service.correct_analysis(previous_result, user_correction)
        
        # Return the result
        return jsonify(result.dict()), 200
    
    except GeminiServiceException as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Error in correct_exercise_entry: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 