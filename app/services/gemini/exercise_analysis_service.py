from datetime import datetime
from typing import Dict, Any, Optional

from app.services.gemini.base_gemini_service import BaseGeminiService, GeminiServiceException
from app.api.models.exercise_analysis import ExerciseAnalysisResult


class ExerciseAnalysisService(BaseGeminiService):
    """Service for analyzing exercise descriptions using Gemini API."""
    
    def analyze(self, description: str, user_weight_kg: Optional[float] = None) -> ExerciseAnalysisResult:
        """
        Analyze an exercise description and estimate calories burned.
        
        Args:
            description: The exercise description to analyze.
            user_weight_kg: Optional user weight in kilograms for more accurate calorie estimation.
            
        Returns:
            An ExerciseAnalysisResult with the analysis details.
            
        Raises:
            GeminiServiceException: If there's an error analyzing the exercise.
        """
        try:
            weight_info = f"The user weighs {user_weight_kg} kg." if user_weight_kg is not None else ""
            
            prompt = f"""
            Calculate calories burned from this exercise description: "{description}"
            {weight_info}
            
            Please analyze this exercise and provide:
            - Type of exercise
            - Calories burned
            - Duration in minutes
            - Intensity level
            - MET value
            
            Return your response as a strict JSON object with this exact format:
            {{
              "exercise_type": "string",
              "calories_burned": number,
              "duration_minutes": number,
              "intensity_level": "string",
              "met_value": number
            }}
            
            If you cannot determine the exercise details, use this format:
            {{
              "error": "Could not determine exercise details",
              "exercise_type": "Unknown",
              "calories_burned": 0,
              "duration_minutes": 0,
              "intensity_level": "Unknown",
              "met_value": 0
            }}
            """
            
            response_text = self.generate_content([prompt])
            return self._parse_exercise_response(response_text, description)
        except Exception as e:
            if isinstance(e, GeminiServiceException):
                raise
            raise GeminiServiceException(f"Error analyzing exercise: {str(e)}")
    
    def correct_analysis(self, previous_result: ExerciseAnalysisResult, user_comment: str) -> ExerciseAnalysisResult:
        """
        Correct an exercise analysis based on user feedback.
        
        Args:
            previous_result: The previous exercise analysis result.
            user_comment: The user's correction comment.
            
        Returns:
            A corrected ExerciseAnalysisResult.
            
        Raises:
            GeminiServiceException: If there's an error correcting the analysis.
        """
        try:
            prompt = f"""
            Original exercise analysis:
            - Exercise type: {previous_result.exercise_type}
            - Duration: {previous_result.duration}
            - Intensity: {previous_result.intensity}
            - Calories burned: {previous_result.estimated_calories}
            - MET value: {previous_result.met_value}
            
            User correction comment: "{user_comment}"
            
            Please correct the exercise analysis based on the user's comment. 
            Only modify values that need to be changed according to the user's feedback.
            
            Return your response as a strict JSON object with this exact format:
            {{
              "exercise_type": "string",
              "calories_burned": number,
              "duration_minutes": number,
              "intensity_level": "string",
              "met_value": number,
              "correction_applied": "string explaining what was corrected"
            }}
            """
            
            response_text = self.generate_content([prompt])
            return self._parse_correction_response(response_text, previous_result, user_comment)
        except Exception as e:
            if isinstance(e, GeminiServiceException):
                raise
            raise GeminiServiceException(f"Error correcting exercise analysis: {str(e)}")
    
    def _parse_exercise_response(self, response_text: str, original_input: str) -> ExerciseAnalysisResult:
        """
        Parse the exercise analysis response from Gemini.
        
        Args:
            response_text: The text response from Gemini.
            original_input: The original exercise description.
            
        Returns:
            An ExerciseAnalysisResult with the parsed data.
            
        Raises:
            GeminiServiceException: If parsing fails.
        """
        try:
            json_data = self.extract_json(response_text)
            
            # Check for error
            if 'error' in json_data:
                return ExerciseAnalysisResult(
                    exercise_type='Unknown',
                    duration='Not specified',
                    intensity='Not specified',
                    estimated_calories=0,
                    met_value=0.0,
                    summary=f"Could not analyze exercise: {json_data.get('error', 'Unknown error')}",
                    timestamp=datetime.now(),
                    original_input=original_input,
                    missing_info=['exercise_type', 'duration', 'intensity']
                )
            
            exercise_type = json_data.get('exercise_type', 'Unknown')
            calories_burned = json_data.get('calories_burned', 0)
            duration_minutes = json_data.get('duration_minutes', 0)
            intensity_level = json_data.get('intensity_level', 'Unknown')
            met_value = float(json_data.get('met_value', 0.0))
            
            # Create a summary
            summary = f"You performed {exercise_type} for {duration_minutes} minutes at {intensity_level} intensity, burning approximately {calories_burned} calories."
            
            # Determine duration string format
            duration = f"{duration_minutes} minutes"
            
            return ExerciseAnalysisResult(
                exercise_type=exercise_type,
                duration=duration,
                intensity=intensity_level,
                estimated_calories=int(calories_burned),
                met_value=met_value,
                summary=summary,
                timestamp=datetime.now(),
                original_input=original_input
            )
        except Exception as e:
            raise GeminiServiceException(f"Failed to parse exercise analysis response: {str(e)}")
    
    def _parse_correction_response(
        self, response_text: str, previous_result: ExerciseAnalysisResult, user_comment: str
    ) -> ExerciseAnalysisResult:
        """
        Parse the exercise correction response from Gemini.
        
        Args:
            response_text: The text response from Gemini.
            previous_result: The previous analysis result.
            user_comment: The user's correction comment.
            
        Returns:
            A corrected ExerciseAnalysisResult.
            
        Raises:
            GeminiServiceException: If parsing fails.
        """
        try:
            json_data = self.extract_json(response_text)
            
            # Extract values from JSON, defaulting to previous values if not provided
            exercise_type = json_data.get('exercise_type', previous_result.exercise_type)
            calories_burned = json_data.get('calories_burned', previous_result.estimated_calories)
            
            # Handle duration which might be in string format in previous_result
            if 'duration_minutes' in json_data:
                duration_minutes = json_data['duration_minutes']
            else:
                # Try to extract numbers from the previous duration string
                import re
                duration_string = previous_result.duration
                numbers = re.findall(r'\d+', duration_string)
                duration_minutes = int(numbers[0]) if numbers else 0
            
            intensity_level = json_data.get('intensity_level', previous_result.intensity)
            met_value = float(json_data.get('met_value', previous_result.met_value))
            correction_applied = json_data.get('correction_applied', 'Adjustments applied based on user feedback')
            
            # Create a summary incorporating the correction information
            summary = f"You performed {exercise_type} for {duration_minutes} minutes at {intensity_level} intensity, burning approximately {calories_burned} calories. ({correction_applied})"
            
            # Determine duration string format
            duration = f"{duration_minutes} minutes"
            
            return ExerciseAnalysisResult(
                exercise_type=exercise_type,
                duration=duration,
                intensity=intensity_level,
                estimated_calories=int(calories_burned),
                met_value=met_value,
                summary=summary,
                timestamp=datetime.now(),
                original_input=previous_result.original_input
            )
        except Exception as e:
            raise GeminiServiceException(f"Failed to parse exercise correction response: {str(e)}") 