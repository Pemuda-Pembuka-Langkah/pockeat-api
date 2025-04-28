"""
Exercise analysis service using Gemini API.
"""

import json
import logging
from typing import Dict, Any, Optional

from api.services.gemini.base_service import BaseLangChainService
from api.services.gemini.exceptions import GeminiServiceException
from api.services.gemini.utils.json_parser import (
    extract_json_from_text,
    parse_json_safely,
)
from api.models.exercise_analysis import ExerciseAnalysisResult

# Configure logger
logger = logging.getLogger(__name__)


class ExerciseAnalysisService(BaseLangChainService):
    """Exercise analysis service using Gemini API."""

    def __init__(self):
        """Initialize the service."""
        super().__init__()
        logger.info("Initializing ExerciseAnalysisService")

    async def analyze(
        self, description: str, user_weight_kg: Optional[float] = None
    ) -> ExerciseAnalysisResult:
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
            logger.error(f"Error in analyze: {str(e)}")  # pragma: no cover
            error_message = f"Failed to analyze exercise: {str(e)}"

            # Return result with error
            return ExerciseAnalysisResult(
                exercise_type="unknown",
                calories_burned=0,
                duration="unknown",
                intensity="unknown",
                error=error_message,
            )

    async def correct_analysis(
        self, previous_result: ExerciseAnalysisResult, user_comment: str
    ) -> ExerciseAnalysisResult:
        """Correct a previous exercise analysis based on user feedback.

        Args:
            previous_result: The previous exercise analysis result.
            user_comment: The user's feedback.

        Returns:
            The corrected exercise analysis result.

        Raises:
            GeminiServiceException: If the correction fails.
        """
        logger.info(
            f"Correcting exercise analysis for {previous_result.exercise_type} with comment: {user_comment}"
        )

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
        except Exception as e:  # pragma: no cover
            logger.error(f"Error in correct_analysis: {str(e)}")  # pragma: no cover
            error_message = f"Failed to correct exercise analysis: {str(e)}"

            # Return original result with error
            previous_result.error = error_message
            return previous_result

    def _generate_exercise_analysis_prompt(
        self, description: str, user_weight_kg: Optional[float] = None
    ) -> str:
        """Generate a prompt for exercise analysis.

        Args:
            description: The exercise description.
            user_weight_kg: The user's weight in kilograms.

        Returns:
            The prompt.
        """
        weight_info = (
            f"The user weighs {user_weight_kg} kg."
            if user_weight_kg
            else "Assume an average adult weight for calorie calculations."
        )

        return f"""
    Analyze the following exercise description and provide detailed information. 
First, evaluate if the description clearly mentions:
1. The type of exercise (what activity)
2. Duration of the exercise (how long)
3. Intensity of the exercise (how hard)

If ANY of these three elements are missing, return this error format:
{{{{
  "error": "Error in describing exercise",
  "exercise_type": "unknown",
  "calories_burned": 0,
  "duration": "unknown",
  "intensity": "unknown"
}}}}

Otherwise, if all elements are present, return your response as a JSON object with this structure:
{{{{
  "exercise_type": "Concise name of exercise based on description (e.g. 'Pushups', 'Running', 'Yoga', 'etc')",
  "calories_burned": 0,
  "duration": "xx seconds/minutes/hours",
  "intensity": "Low/Medium/High"
}}}}

Exercise description: {description}

{weight_info}

Please estimate calorie burn based on the exercise intensity and duration. Estimate using a concrete proven formula to get the calories burned. 
"""

    def _generate_correction_prompt(
        self, previous_result: Dict[str, Any], user_comment: str
    ) -> str:
        """Generate a prompt for correction.

        Args:
            previous_result: The previous exercise analysis result as a dictionary.
            user_comment: The user's feedback.

        Returns:
            The prompt.
        """
        # Convert the previous result to a formatted JSON string
        previous_result_json = json.dumps(previous_result, indent=2)

        return f"""
I previously analyzed an exercise and provided the following information:

{previous_result_json}

The user has provided this feedback to correct or improve the analysis:
"{user_comment}"

Please correct the analysis based on this feedback. Return your corrected response as a complete JSON object with the same structure as the original analysis.
Estimate using a concrete proven formula to get the calories burned. 
"""

    def _parse_exercise_analysis_response(
        self, response_text: str
    ) -> ExerciseAnalysisResult:
        """Parse the response from the Gemini API for exercise analysis.

        Args:
            response_text: The response text from the Gemini API.

        Returns:
            The exercise analysis result.
        """
        try:
            print(f"Exercise Analysis Raw Response: {response_text}")
            # Extract JSON from the response
            json_str = extract_json_from_text(response_text)
            if not json_str:  # pragma: no cover
                logger.warning("No JSON found in response, returning raw response")
                return self._create_error_result(
                    f"Failed to parse response: {response_text[:100]}..."
                )

            # Parse the JSON
            data = parse_json_safely(json_str)

            # Extract basic fields
            exercise_type = data.get("exercise_type", "unknown")
            error = data.get("error", None)

            # Extract numeric and string fields
            calories_burned = self._extract_calories_burned(data)
            duration = self._extract_duration(data)
            intensity = self._extract_intensity(data)

            # Create and return the result
            return ExerciseAnalysisResult(
                exercise_type=exercise_type,
                calories_burned=calories_burned,
                duration=duration,
                intensity=intensity,
                error=error,
            )

        except Exception as e:
            logger.error(
                f"Error parsing exercise analysis response: {str(e)}"
            )  # pragma: no cover
            # Instead of raising an exception, return a result with the error
            return ExerciseAnalysisResult(  # pragma: no cover
                exercise_type="unknown",
                calories_burned=0,
                duration="unknown",
                intensity="unknown",
                error=f"Failed to parse response: {str(e)}",
            )

    def _extract_calories_burned(self, data: Dict[str, Any]) -> float:
        """Extract calories burned from parsed data.

        Args:
            data: The parsed JSON data.

        Returns:
            Calories burned value.
        """
        try:
            return float(data.get("calories_burned", 0))
        except (ValueError, TypeError):  # pragma: no cover
            return 0

    def _extract_duration(self, data: Dict[str, Any]) -> str:
        """Extract duration from parsed data.

        Args:
            data: The parsed JSON data.

        Returns:
            Duration string.
        """
        try:
            return str(data.get("duration", "unknown"))
        except (ValueError, TypeError):  # pragma: no cover
            return "unknown"

    def _extract_intensity(self, data: Dict[str, Any]) -> str:
        """Extract intensity from parsed data.

        Args:
            data: The parsed JSON data.

        Returns:
            Intensity level.
        """
        intensity = data.get("intensity", "unknown").lower()
        valid_intensities = ["low", "medium", "high", "unknown"]
        if intensity not in valid_intensities:  # pragma: no cover
            intensity = "unknown"
        return intensity

    def _create_error_result(self, error_message: str) -> ExerciseAnalysisResult:
        """Create an error result.

        Args:
            error_message: The error message.

        Returns:
            Exercise analysis result with error.
        """
        return ExerciseAnalysisResult(
            exercise_type="unknown",
            calories_burned=0,
            duration="unknown",
            intensity="unknown",
            error=error_message,
        )
