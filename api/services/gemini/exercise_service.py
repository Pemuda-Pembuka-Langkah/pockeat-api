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
        self, 
        description: str, 
        user_weight_kg: Optional[float] = None,
        user_height_cm: Optional[float] = None,
        user_age: Optional[int] = None,
        user_gender: Optional[str] = None
    ) -> ExerciseAnalysisResult:
        """Analyze an exercise description.

        Args:
            description: The exercise description.
            user_weight_kg: The user's weight in kilograms.
            user_height_cm: The user's height in centimeters.
            user_age: The user's age in years.
            user_gender: The user's gender (male/female).

        Returns:
            The exercise analysis result.

        Raises:
            GeminiServiceException: If the analysis fails.
        """
        logger.info(f"Analyzing exercise: {description[:50]}...")

        # Generate the prompt with all health metrics
        prompt = self._generate_exercise_analysis_prompt(
            description, 
            user_weight_kg,
            user_height_cm, 
            user_age, 
            user_gender
        )
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
        self, 
        previous_result: ExerciseAnalysisResult, 
        user_comment: Optional[str] = None,
        user_weight_kg: Optional[float] = None,
        user_height_cm: Optional[float] = None,
        user_age: Optional[int] = None,
        user_gender: Optional[str] = None
    ) -> ExerciseAnalysisResult:
        try:
            # Convert the previous result to a dict for the prompt
            previous_result_dict = previous_result.dict(exclude={"timestamp", "id"})

            # Generate the prompt for correction with health metrics
            prompt = self._generate_correction_prompt(
                previous_result_dict, 
                user_comment,
                user_weight_kg,
                user_height_cm,
                user_age,
                user_gender
            )

            # Rest of the method remains the same
            response_text = await self._invoke_text_model(prompt)
            logger.debug(f"Received correction response: {response_text[:100]}...")
            corrected_result = self._parse_exercise_analysis_response(response_text)
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
        self, 
        description: str, 
        user_weight_kg: Optional[float] = None,
        user_height_cm: Optional[float] = None,
        user_age: Optional[int] = None,
        user_gender: Optional[str] = None
    ) -> str:
        # Create health metrics information string
        health_info = []
        if user_weight_kg:
            health_info.append(f"Weight: {user_weight_kg} kg")
        if user_height_cm:
            health_info.append(f"Height: {user_height_cm} cm")
        if user_age:
            health_info.append(f"Age: {user_age} years")
        if user_gender:
            health_info.append(f"Gender: {user_gender}")
        
        health_info_str = ", ".join(health_info) if health_info else "Assume average adult metrics for calculations"

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
    "intensity": "unknown",
    "met_value": 0.0
    }}}}

    Otherwise, if all elements are present, return your response as a JSON object with this structure (NOTE: Choose exactly ONE type of intensity):
    {{{{
    "exercise_type": "Concise name of exercise based on description",
    "calories_burned": 0,
    "duration": "xx seconds/minutes/hours",
    "intensity": "Low/Medium/High",
    "met_value": 0.0
    }}}}

    Exercise description: {description}

    User health data: {health_info_str}

    For calorie calculations, use the Mifflin-St Jeor equation to first calculate BMR:
    - For males: BMR = (10 × weight [kg]) + (6.25 × height [cm]) – (5 × age [years]) + 5
    - For females: BMR = (10 × weight [kg]) + (6.25 × height [cm]) – (5 × age [years]) – 161

    Then calculate calories burned as: (BMR / 24) × MET value × duration in hours

    Please identify the appropriate MET value for the exercise and include it in the response.
    """

    def _generate_correction_prompt(
        self, previous_result: Dict[str, Any],
        user_comment: Optional[str] = None, 
        user_weight_kg: Optional[float] = None,
        user_height_cm: Optional[float] = None,
        user_age: Optional[int] = None,
        user_gender: Optional[str] = None
    ) -> str:
        """Generate a prompt for correction."""
        # Convert the previous result to a formatted JSON string
        previous_result_json = json.dumps(previous_result, indent=2)
        
        # Extract original input if available
        original_input = previous_result.get("original_input", "Unknown")
        
        # Create health metrics information string
        health_info = []
        if user_weight_kg:
            health_info.append(f"Weight: {user_weight_kg} kg")
        if user_height_cm:
            health_info.append(f"Height: {user_height_cm} cm")
        if user_age:
            health_info.append(f"Age: {user_age} years")
        if user_gender:
            health_info.append(f"Gender: {user_gender}")
        
        health_info_str = ", ".join(health_info) if health_info else "No health metrics provided"

        return f"""
    I previously analyzed an exercise with description: "{original_input}"

    Here is the previous analysis:
    {previous_result_json}

    The user has provided this feedback to correct or improve the analysis:
    "{user_comment}"

    User health data: {health_info_str}

    Please correct the analysis based on this feedback. Return your corrected response as a complete JSON object with the same structure as the original analysis.
    Estimate using a concrete proven formula to get the calories burned.
    IMPORTANT: If the pace increases, you MUST INCREASE the MET. If the pace decreases, you MUST MAINTAIN the MET. UNLESS the user feedback explicitly mentions a different MET value.
    
    IMPORTANT: When user feedback only mentions correcting one parameter (e.g., only duration or only distance):
    - If only duration is corrected, assume the same distance as originally stated
    - If only distance is corrected, assume the same duration as originally stated

    For calorie calculations, use the Mifflin-St Jeor equation to first calculate BMR:
    - For males: BMR = (10 × weight [kg]) + (6.25 × height [cm]) – (5 × age [years]) + 5
    - For females: BMR = (10 × weight [kg]) + (6.25 × height [cm]) – (5 × age [years]) – 161

    Then calculate calories burned as: (BMR / 24) × MET value × duration in hours

    RETURN THE OCORRECTED ANALYSIS JSON ONLY
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
            met_value = self._extract_met_value(data)

            # Create and return the result
            return ExerciseAnalysisResult(
                exercise_type=exercise_type,
                calories_burned=calories_burned,
                duration=duration,
                intensity=intensity,
                met_value=met_value,
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
    
    def _extract_met_value(self, data: Dict[str, Any]) -> float:
        """Extract MET value from parsed data.

        Args:
            data: The parsed JSON data.

        Returns:
            MET value.
        """
        try:
            return float(data.get("met_value", 0.0))
        except (ValueError, TypeError):
            return 0.0
    

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
