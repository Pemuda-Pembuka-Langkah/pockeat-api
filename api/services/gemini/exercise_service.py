"""
Exercise analysis service using Gemini API.
"""

import json
import logging
from typing import Dict, Any, Optional

from api.services.gemini.base_service import BaseLangChainService
from api.services.gemini.exceptions import GeminiServiceException, GeminiParsingError
from api.services.gemini.utils.json_parser import extract_json_from_text, parse_json_safely
from api.models.exercise_analysis import ExerciseAnalysisResult

# Configure logger
logger = logging.getLogger(__name__)


class ExerciseAnalysisService(BaseLangChainService):
    """Exercise analysis service using Gemini API."""
    
    def __init__(self):
        """Initialize the service."""
        super().__init__()
        logger.info("Initializing ExerciseAnalysisService")
    
    async def analyze(self, description: str, user_weight_kg: Optional[float] = None) -> ExerciseAnalysisResult:
        """Analyze an exercise description.
        
        Args:
            description: The exercise description.
            user_weight_kg: The user's weight in kilograms.
            
        Returns:
            The exercise analysis result.
            
        Raises:
            GeminiServiceException: If the analysis fails.
        """
        logger.info(f"Analyzing exercise: {description[:50]}...")
        
        # Generate the prompt for exercise analysis
        prompt = self._generate_exercise_analysis_prompt(description, user_weight_kg)
        
        try:
            # Invoke the model
            response_text = await self._invoke_text_model(prompt)
            logger.debug(f"Received response: {response_text[:100]}...")
            
            # Parse the response
            result = self._parse_exercise_analysis_response(response_text)
            
            # Set the original input
            result.original_input = description
            
            return result
        except GeminiServiceException:
            # Re-raise GeminiServiceExceptions
            raise
        except Exception as e:
            logger.error(f"Error in analyze: {str(e)}")
            error_message = f"Failed to analyze exercise: {str(e)}"
            
            # Return result with error
            return ExerciseAnalysisResult(
                exercise_type="unknown",
                duration="Not specified",
                intensity="unknown",
                calories_burned=0,
                met_value=0.0,
                summary=f"Could not analyze exercise: {str(e)}",
                original_input=description,
                missing_info=["exercise_type", "duration", "intensity"],
                error=error_message
            )
    
    async def correct_analysis(self, previous_result: ExerciseAnalysisResult, user_comment: str) -> ExerciseAnalysisResult:
        """Correct a previous exercise analysis based on user feedback.
        
        Args:
            previous_result: The previous exercise analysis result.
            user_comment: The user's feedback.
            
        Returns:
            The corrected exercise analysis result.
            
        Raises:
            GeminiServiceException: If the correction fails.
        """
        logger.info(f"Correcting exercise analysis for {previous_result.exercise_type} with comment: {user_comment}")
        
        # Convert the previous result to a dict for the prompt
        previous_result_dict = previous_result.dict(exclude={"timestamp", "id"})
        
        # Generate the prompt for correction
        prompt = self._generate_correction_prompt(previous_result_dict, user_comment)
        
        try:
            # Invoke the model
            response_text = await self._invoke_text_model(prompt)
            logger.debug(f"Received correction response: {response_text[:100]}...")
            
            # Parse the response
            corrected_result = self._parse_exercise_analysis_response(response_text)
            
            # Preserve the original information
            corrected_result.id = previous_result.id
            corrected_result.original_input = previous_result.original_input
            
            return corrected_result
        except GeminiServiceException:
            # Re-raise GeminiServiceExceptions
            raise
        except Exception as e:
            logger.error(f"Error in correct_analysis: {str(e)}")
            error_message = f"Failed to correct exercise analysis: {str(e)}"
            
            # Return original result with error
            previous_result.error = error_message
            return previous_result
    
    def _generate_exercise_analysis_prompt(self, description: str, user_weight_kg: Optional[float] = None) -> str:
        """Generate a prompt for exercise analysis.
        
        Args:
            description: The exercise description.
            user_weight_kg: The user's weight in kilograms.
            
        Returns:
            The prompt.
        """
        weight_info = f"The user weighs {user_weight_kg} kg." if user_weight_kg else ""
        
        return f"""
        Calculate calories burned from this exercise description: "{description}"
        {weight_info}

        
        Please analyze this exercise and provide:
        - Type of exercise
        - Calories burned
        - Duration in minutes
        - Intensity level into only three of this (Low, Medium, High, Unknown) #don't forget its Capitalized
        - MET value
        

        Do not include any other text in your response, even comments.
        Return your response as a strict JSON object with this exact format:
        (
          "exercise_type": "string",
          "calories_burned": number,
          "duration_minutes": number,
          "intensity_level": "string",
          "met_value": number
        )
        
        If you cannot determine the exercise details, use this format:
        (
          "error": "Could not determine exercise details",
          "exercise_type": "Unknown",
          "calories_burned": 0,
          "duration_minutes": 0,
          "intensity_level": "Unknown",
          "met_value": 0
        )

        Change () to curly braces
        """
    
    def _generate_correction_prompt(self, previous_result: Dict[str, Any], user_comment: str) -> str:
        """Generate a prompt for correction.
        
        Args:
            previous_result: The previous exercise analysis result as a dictionary.
            user_comment: The user's feedback.
            
        Returns:
            The prompt.
        """
        exercise_type = previous_result.get("exercise_type", "Unknown")
        duration = previous_result.get("duration", "Not specified")
        intensity = previous_result.get("intensity", "Not specified")
        estimated_calories = previous_result.get("calories_burned", 0)
        met_value = previous_result.get("met_value", 0.0)
        
        return f"""
        Original exercise analysis:
        - Exercise type: {exercise_type}
        - Duration: {duration}
        - Intensity: {intensity}
        - Calories burned: {estimated_calories}
        - MET value: {met_value}
        
        User correction comment: "{user_comment}"
        
        Please correct the exercise analysis based on the user's comment. 
        Only modify values that need to be changed according to the user's feedback.
        
        Return your response as a strict JSON object with this exact format:
        (
          "exercise_type": "string",
          "calories_burned": number,
          "duration_minutes": number,
          "intensity_level": "string",
          "met_value": number,
          "correction_applied": "string explaining what was corrected"
        )

        Change () to curly braces
        """
    
    def _parse_exercise_analysis_response(self, response_text: str) -> ExerciseAnalysisResult:
        """Parse the response from the Gemini API for exercise analysis.
        
        Args:
            response_text: The response text from the Gemini API.
            
        Returns:
            The exercise analysis result.
            
        Raises:
            GeminiParsingError: If the response cannot be parsed.
        """
        try:
            # Extract JSON from the response
            json_str = extract_json_from_text(response_text)
            if not json_str:
                logger.warning("No JSON found in response, returning raw response")
                return ExerciseAnalysisResult(
                    exercise_type="unknown",
                    duration="Not specified",
                    intensity="unknown",
                    calories_burned=0,
                    met_value=0.0,
                    summary="Could not analyze exercise: Failed to parse response",
                    original_input="",
                    missing_info=["exercise_type", "duration", "intensity"],
                    error=f"Failed to parse response: {response_text[:100]}..."
                )
            
            # Parse the JSON
            data = parse_json_safely(json_str)
            
            # Check for error
            if "error" in data:
                logger.warning(f"Error in exercise analysis response: {data['error']}")
                return ExerciseAnalysisResult(
                    exercise_type="unknown" if not data.get("exercise_type") else data["exercise_type"],
                    duration="Not specified",
                    intensity="unknown",
                    calories_burned=0,
                    met_value=0.0,
                    summary=f"Could not analyze exercise: {data['error']}",
                    original_input="",
                    missing_info=["exercise_type", "duration", "intensity"],
                    error=data["error"]
                )
            
            # Extract required fields
            exercise_type = data.get("exercise_type", "unknown")
            
            # Extract numeric fields with validation
            try:
                calories_burned = float(data.get("calories_burned", 0))
            except (ValueError, TypeError):
                calories_burned = 0
            
            # Extract duration as a string
            duration_minutes = data.get("duration_minutes", 0)
            duration = f"{duration_minutes} minutes" if duration_minutes else "Not specified"
            
            # Extract intensity (could be intensity or intensity_level)
            intensity = data.get("intensity_level", data.get("intensity", "unknown")).lower()
            valid_intensities = ["low", "medium", "high", "Unknown"]
            if intensity not in valid_intensities:
                intensity = "unknown"
            
            # Extract MET value
            try:
                met_value = float(data.get("met_value", 0))
            except (ValueError, TypeError):
                met_value = 0.0
            
            # Create a summary
            summary = f"You performed {exercise_type} for {duration_minutes} minutes at {intensity} intensity, burning approximately {calories_burned} calories."
            
            # Identify missing information
            missing_info = []
            if not exercise_type or exercise_type == "unknown":
                missing_info.append("exercise_type")
            if not duration_minutes:
                missing_info.append("duration")
            if intensity == "unknown":
                missing_info.append("intensity")
            
            # Create and return the result
            return ExerciseAnalysisResult(
                exercise_type=exercise_type,
                duration=duration,
                intensity=intensity,
                calories_burned=calories_burned,
                met_value=met_value,
                summary=summary,
                original_input=data.get("description", ""),
                missing_info=missing_info if missing_info else None
            )
        
        except Exception as e:
            logger.error(f"Error parsing exercise analysis response: {str(e)}")
            # Instead of raising an exception, return a result with the error
            return ExerciseAnalysisResult(
                exercise_type="unknown",
                duration="Not specified",
                intensity="unknown",
                calories_burned=0,
                met_value=0.0,
                summary=f"Could not analyze exercise: {str(e)}",
                original_input="",
                missing_info=["exercise_type", "duration", "intensity"],
                error=f"Failed to parse response: {str(e)}"
            ) 