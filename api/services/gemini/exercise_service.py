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
            return self._parse_exercise_analysis_response(response_text)
        except GeminiServiceException:
            # Re-raise GeminiServiceExceptions
            raise
        except Exception as e:
            logger.error(f"Error in analyze: {str(e)}")
            error_message = f"Failed to analyze exercise: {str(e)}"
            
            # Return result with error
            return ExerciseAnalysisResult(
                exercise_name="Unknown Exercise",
                exercise_type="unknown",
                calories_burned=0,
                duration_minutes=0,
                intensity="unknown",
                muscles_worked=[],
                equipment_needed=[],
                benefits=[],
                warnings=[],
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
        logger.info(f"Correcting exercise analysis for {previous_result.exercise_name} with comment: {user_comment}")
        
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
            
            # Preserve the original ID
            corrected_result.id = previous_result.id
            
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
        weight_info = f"The user weighs {user_weight_kg} kg." if user_weight_kg else "Assume an average adult weight for calorie calculations."
        
        return f"""Analyze the following exercise description and provide detailed information. 
Return your response as a JSON object with the following structure:

{{
  "exercise_name": "Name of the exercise",
  "exercise_type": "cardio/strength/flexibility/balance",
  "calories_burned": 0,
  "duration_minutes": 0,
  "intensity": "low/medium/high",
  "muscles_worked": ["Muscle 1", "Muscle 2"],
  "equipment_needed": ["Equipment 1", "Equipment 2"],
  "benefits": ["Benefit 1", "Benefit 2"],
  "warnings": ["Warning 1", "Warning 2"]
}}

Exercise description: {description}

{weight_info}

Please estimate calorie burn based on the exercise intensity and duration. 
Include any health warnings in the warnings array (e.g., "High impact on joints", "Not recommended for people with back problems").
"""
    
    def _generate_correction_prompt(self, previous_result: Dict[str, Any], user_comment: str) -> str:
        """Generate a prompt for correction.
        
        Args:
            previous_result: The previous exercise analysis result as a dictionary.
            user_comment: The user's feedback.
            
        Returns:
            The prompt.
        """
        # Convert the previous result to a formatted JSON string
        previous_result_json = json.dumps(previous_result, indent=2)
        
        return f"""I previously analyzed an exercise and provided the following information:

{previous_result_json}

The user has provided this feedback to correct or improve the analysis:
"{user_comment}"

Please correct the analysis based on this feedback. Return your corrected response as a complete JSON object with the same structure as the original analysis.
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
                    exercise_name="Unknown Exercise",
                    exercise_type="unknown",
                    calories_burned=0,
                    duration_minutes=0,
                    intensity="unknown",
                    muscles_worked=[],
                    equipment_needed=[],
                    benefits=[],
                    warnings=[],
                    error=f"Failed to parse response: {response_text[:100]}..."
                )
            
            # Parse the JSON
            data = parse_json_safely(json_str)
            
            # Extract and validate required fields
            exercise_name = data.get("exercise_name", "Unknown Exercise")
            exercise_type = data.get("exercise_type", "unknown")
            
            # Ensure exercise_type is one of the allowed values
            valid_types = ["cardio", "strength", "flexibility", "balance", "unknown"]
            if exercise_type.lower() not in valid_types:
                exercise_type = "unknown"
            
            # Extract numeric fields with validation
            try:
                calories_burned = float(data.get("calories_burned", 0))
            except (ValueError, TypeError):
                calories_burned = 0
            
            try:
                duration_minutes = float(data.get("duration_minutes", 0))
            except (ValueError, TypeError):
                duration_minutes = 0
            
            # Extract intensity
            intensity = data.get("intensity", "unknown").lower()
            valid_intensities = ["low", "medium", "high", "unknown"]
            if intensity not in valid_intensities:
                intensity = "unknown"
            
            # Extract list fields
            muscles_worked = []
            if "muscles_worked" in data and isinstance(data["muscles_worked"], list):
                muscles_worked = [str(m) for m in data["muscles_worked"]]
            
            equipment_needed = []
            if "equipment_needed" in data and isinstance(data["equipment_needed"], list):
                equipment_needed = [str(e) for e in data["equipment_needed"]]
            
            benefits = []
            if "benefits" in data and isinstance(data["benefits"], list):
                benefits = [str(b) for b in data["benefits"]]
            
            warnings = []
            if "warnings" in data and isinstance(data["warnings"], list):
                warnings = [str(w) for w in data["warnings"]]
            
            # Create and return the result
            return ExerciseAnalysisResult(
                exercise_name=exercise_name,
                exercise_type=exercise_type,
                calories_burned=calories_burned,
                duration_minutes=duration_minutes,
                intensity=intensity,
                muscles_worked=muscles_worked,
                equipment_needed=equipment_needed,
                benefits=benefits,
                warnings=warnings
            )
        
        except Exception as e:
            logger.error(f"Error parsing exercise analysis response: {str(e)}")
            # Instead of raising an exception, return a result with the error
            return ExerciseAnalysisResult(
                exercise_name="Unknown Exercise",
                exercise_type="unknown",
                calories_burned=0,
                duration_minutes=0,
                intensity="unknown",
                muscles_worked=[],
                equipment_needed=[],
                benefits=[],
                warnings=[],
                error=f"Failed to parse response: {str(e)}"
            ) 