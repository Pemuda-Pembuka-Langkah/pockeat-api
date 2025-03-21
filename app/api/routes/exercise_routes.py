"""
Exercise analysis routes.
"""
from flask import Blueprint, request, jsonify
from app.services.exercise.exercise_analysis_service import ExerciseAnalysisService
from app.services.exercise.exercise_correction_service import ExerciseCorrectionService
from app.services.gemini.gemini_client import GeminiClient
import os

exercise_bp = Blueprint('exercise', __name__, url_prefix='/exercise')

# Initialize services
gemini_client = GeminiClient(api_key=os.environ.get('GEMINI_API_KEY'))
exercise_analysis_service = ExerciseAnalysisService(gemini_client=gemini_client)
exercise_correction_service = ExerciseCorrectionService(gemini_client=gemini_client)


@exercise_bp.route('/analyze', methods=['POST'])
def analyze_exercise():
    """
    Analyze an exercise description using Gemini API.
    
    Expected input: JSON with description field
    """
    data = request.json
    
    if not data or 'description' not in data:
        return jsonify({"error": "Missing exercise description"}), 400
    
    # Analyze the exercise
    try:
        result = exercise_analysis_service.analyze_exercise(data['description'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@exercise_bp.route('/correct', methods=['POST'])
def correct_exercise_entry():
    """
    Correct an exercise entry using Gemini API.
    
    Expected input: JSON with exercise_entry and user_correction fields
    """
    data = request.json
    
    if not data or 'exercise_entry' not in data or 'user_correction' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        result = exercise_correction_service.correct_exercise_entry(
            data['exercise_entry'], 
            data['user_correction']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500 